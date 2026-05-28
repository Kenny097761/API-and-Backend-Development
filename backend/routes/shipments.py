from flask import Blueprint, request, jsonify, session

from backend.models.db_crud import (
    get_shipment_by_id,
    get_shipments_by_customer,
    get_all_shipments,
    get_paid_orders_without_shipment,
    get_order_with_customer_address,
    is_staff,
    create_shipment as crud_create_shipment,
    update_shipment_status,
    cancel_shipment as crud_cancel_shipment,
    is_valid_transition,
    ShipmentAlreadyExistsError,
)

VALID_STATUSES = ("pending", "shipped", "delivered")

shipments_bp = Blueprint("shipments", __name__, url_prefix="/shipments")


@shipments_bp.route("/my", methods=["GET"])
def my_shipments():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    shipments = get_shipments_by_customer(user_id)
    return jsonify({"shipments": shipments}), 200


@shipments_bp.route("/orders-available", methods=["GET"])
def orders_available():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({"orders": get_paid_orders_without_shipment()}), 200


@shipments_bp.route("/", methods=["GET"])
def list_shipments():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Only staff can view all shipments"}), 403
    return jsonify({"shipments": get_all_shipments()}), 200


@shipments_bp.route("/", methods=["POST"])
def create_shipment():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    if not isinstance(order_id, int) or isinstance(order_id, bool):
        return jsonify({"error": "order_id is required and must be an integer"}), 400

    order = get_order_with_customer_address(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    if order["status"] != "paid":
        return jsonify({"error": "Order must be paid before creating shipment"}), 400

    address_dict = {
        "street_number": order["street_number"],
        "street_name": order["street_name"],
        "suburb": order["suburb"],
        "postcode": order["postcode"],
    }
    try:
        new_id = crud_create_shipment(order_id, user_id, address_dict)
    except ShipmentAlreadyExistsError:
        return jsonify({"error": "Shipment already exists for this order"}), 409

    shipment = get_shipment_by_id(new_id)
    if shipment:
        shipment.pop("customer_id", None)
    return jsonify({"shipment": shipment}), 201


@shipments_bp.route("/me/session", methods=["GET"])
def me_session():
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"logged_in": False}), 200
    staff = is_staff(user_id)
    return (
        jsonify(
            {
                "logged_in": True,
                "user_id": user_id,
                "is_staff": staff,
                "is_customer": not staff,
            }
        ),
        200,
    )


@shipments_bp.route("/<int:shipment_id>", methods=["GET"])
def get_shipment(shipment_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    shipment = get_shipment_by_id(shipment_id)
    if shipment is None:
        return jsonify({"error": "Shipment not found"}), 404
    if not is_staff(user_id) and shipment["customer_id"] != user_id:
        return jsonify({"error": "Forbidden"}), 403
    shipment.pop("customer_id", None)
    return jsonify({"shipment": shipment}), 200


@shipments_bp.route("/<int:shipment_id>", methods=["PUT"])
def update_shipment(shipment_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Forbidden"}), 403

    shipment = get_shipment_by_id(shipment_id)
    if shipment is None:
        return jsonify({"error": "Shipment not found"}), 404
    if shipment["staff_id"] != user_id:
        return jsonify({"error": "Only the assigned staff can update this shipment"}), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if new_status not in VALID_STATUSES:
        return (
            jsonify({"error": "status must be one of " + ", ".join(VALID_STATUSES)}),
            400,
        )

    if not is_valid_transition(shipment["status"], new_status):
        return jsonify({"error": "Invalid transition"}), 400

    update_shipment_status(shipment_id, new_status)
    updated = get_shipment_by_id(shipment_id)
    if updated:
        updated.pop("customer_id", None)
    return jsonify({"shipment": updated}), 200


@shipments_bp.route("/<int:shipment_id>", methods=["DELETE"])
def delete_shipment(shipment_id):
    user_id = session.get("user_id")
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401
    if not is_staff(user_id):
        return jsonify({"error": "Forbidden"}), 403

    shipment = get_shipment_by_id(shipment_id)
    if shipment is None:
        return jsonify({"error": "Shipment not found"}), 404
    if shipment["staff_id"] != user_id:
        return jsonify({"error": "Only the assigned staff can cancel this shipment"}), 403
    if shipment["status"] != "pending":
        return jsonify({"error": "Only pending shipments can be cancelled"}), 400

    crud_cancel_shipment(shipment_id)
    return jsonify({"shipment_id": shipment_id, "status": "cancelled"}), 200


@shipments_bp.route("/debug/login-as/<int:user_id>", methods=["GET"])
def debug_login_as(user_id):
    session["user_id"] = user_id
    return jsonify({"logged_in_as": user_id})
