from datetime import date
from flask import Blueprint, request, jsonify, session

from backend.models.payment_method_crud import (
    create_payment_method,
    delete_payment_method,
    get_payment_method,
    is_customer,
    list_payment_methods,
    update_payment_method,
)

payment_methods_bp = Blueprint("payment_methods", __name__, url_prefix="/payment-methods")

VALID_TYPES = {"card", "bank", "paypal"}


def numbers_only(value):
    return "".join(character for character in (value or "") if character.isdigit())


def get_card_brand(card_number):
    if card_number.startswith("4"):
        return "Visa"
    if len(card_number) >= 2 and card_number[0] == "5" and card_number[1] in "12345":
        return "Mastercard"
    if len(card_number) >= 2 and card_number[0] == "3" and card_number[1] in "47":
        return "American Express"
    return "Card"


def mask_email(email):
    name, domain = email.split("@", 1)
    visible_name = name[0] if len(name) <= 2 else name[:2]
    return f"{visible_name}***@{domain}"


def is_valid_expiry(expiry_date):
    if not expiry_date or len(expiry_date) != 5 or expiry_date[2] != "/":
        return False

    month_text, year_text = expiry_date.split("/")

    if not month_text.isdigit() or not year_text.isdigit():
        return False

    month = int(month_text)
    if month < 1 or month > 12:
        return False

    year = int(f"20{year_text}")
    today = date.today()
    return year > today.year or (year == today.year and month >= today.month)


def is_valid_email(email):
    if not email or email.count("@") != 1:
        return False

    name, domain = email.split("@", 1)
    if not name or not domain or " " in email:
        return False

    if "." not in domain:
        return False

    domain_parts = domain.split(".")
    return all(domain_parts)


def current_customer_id():
    user_id = session.get("user_id")
    if user_id:
        return user_id if is_customer(user_id) else None

    stored_user_id = request.args.get("user_id")
    if not stored_user_id:
        return None

    try:
        user_id = int(stored_user_id)
    except ValueError:
        return None

    return user_id if is_customer(user_id) else None


def require_customer():
    user_id = current_customer_id()
    if not user_id:
        if session.get("user_id") or request.args.get("user_id"):
            return None, (jsonify({"error": "Only customers can manage payment methods"}), 403)
        return None, (jsonify({"error": "Login is required"}), 401)

    return user_id, None


def parse_payment_method(payload, existing_method=None):
    errors = {}
    method_type = (payload.get("type") or "").strip().lower()
    nickname = payload.get("nickname") or ""
    data = {
        "type": method_type,
        "nickname": nickname,
        "cardholder_name": None,
        "card_brand": None,
        "card_last_four": None,
        "expiry_date": None,
        "account_name": None,
        "bsb_last_three": None,
        "account_last_four": None,
        "paypal_email_masked": None,
    }

    if method_type not in VALID_TYPES:
        errors["paymentType"] = "Choose a valid payment type"

    if method_type == "card":
        cardholder_name = (payload.get("cardholderName") or "").strip()
        card_number = numbers_only(payload.get("cardNumber"))
        expiry_date = (payload.get("expiryDate") or "").strip()

        if not cardholder_name:
            errors["cardholderName"] = "Cardholder name is required"

        if not existing_method and len(card_number) < 12:
            errors["cardNumber"] = "Enter a valid card number"

        if existing_method and not card_number:
            data["card_last_four"] = existing_method.card_last_four
            data["card_brand"] = existing_method.card_brand
        elif card_number:
            data["card_last_four"] = card_number[-4:]
            data["card_brand"] = get_card_brand(card_number)

        if not is_valid_expiry(expiry_date):
            errors["expiryDate"] = "Use a valid future expiry date"

        data["cardholder_name"] = cardholder_name
        data["expiry_date"] = expiry_date

    if method_type == "bank":
        account_name = (payload.get("accountName") or "").strip()
        bsb = numbers_only(payload.get("bsb"))
        account_number = numbers_only(payload.get("accountNumber"))

        if not account_name:
            errors["accountName"] = "Account name is required"

        if not existing_method and len(bsb) != 6:
            errors["bsb"] = "BSB must be 6 digits"

        if not existing_method and len(account_number) < 6:
            errors["accountNumber"] = "Enter a valid account number"

        if existing_method and not bsb:
            data["bsb_last_three"] = existing_method.bsb_last_three
        elif bsb:
            data["bsb_last_three"] = bsb[-3:]

        if existing_method and not account_number:
            data["account_last_four"] = existing_method.account_last_four
        elif account_number:
            data["account_last_four"] = account_number[-4:]

        data["account_name"] = account_name

    if method_type == "paypal":
        paypal_email = (payload.get("paypalEmail") or "").strip()

        if existing_method and not paypal_email:
            data["paypal_email_masked"] = existing_method.paypal_email_masked
        elif is_valid_email(paypal_email):
            data["paypal_email_masked"] = mask_email(paypal_email)
        else:
            errors["paypalEmail"] = "Enter a valid PayPal email"

    return data, errors


@payment_methods_bp.route("/", methods=["GET"])
def get_payment_methods():
    user_id, error_response = require_customer()
    if error_response:
        return error_response

    method_type = request.args.get("type")
    if method_type and method_type not in VALID_TYPES:
        return jsonify({"error": "Invalid payment type"}), 400

    methods = list_payment_methods(user_id, method_type)
    return jsonify([method.to_dict() for method in methods])


@payment_methods_bp.route("/", methods=["POST"])
def add_payment_method():
    user_id, error_response = require_customer()
    if error_response:
        return error_response

    method_data, errors = parse_payment_method(request.get_json(silent=True) or {})
    if errors:
        return jsonify({"errors": errors}), 400

    method = create_payment_method(user_id, method_data)
    return jsonify(method.to_dict()), 201


@payment_methods_bp.route("/<int:payment_method_id>", methods=["GET"])
def get_single_payment_method(payment_method_id):
    user_id, error_response = require_customer()
    if error_response:
        return error_response

    method = get_payment_method(user_id, payment_method_id)
    if not method:
        return jsonify({"error": "Payment method not found"}), 404

    return jsonify(method.to_dict())


@payment_methods_bp.route("/<int:payment_method_id>", methods=["PUT"])
def edit_payment_method(payment_method_id):
    user_id, error_response = require_customer()
    if error_response:
        return error_response

    existing_method = get_payment_method(user_id, payment_method_id)
    if not existing_method:
        return jsonify({"error": "Payment method not found"}), 404

    method_data, errors = parse_payment_method(
        request.get_json(silent=True) or {},
        existing_method=existing_method,
    )
    if errors:
        return jsonify({"errors": errors}), 400

    method = update_payment_method(user_id, payment_method_id, method_data)
    return jsonify(method.to_dict())


@payment_methods_bp.route("/<int:payment_method_id>", methods=["DELETE"])
def remove_payment_method(payment_method_id):
    user_id, error_response = require_customer()
    if error_response:
        return error_response

    if not delete_payment_method(user_id, payment_method_id):
        return jsonify({"error": "Payment method not found"}), 404

    return "", 204
