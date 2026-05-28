from flask import Blueprint, request, jsonify
from backend.models.db_crud import *

device_bp = Blueprint("device_bp", __name__)

@device_bp.route("/devices")
def devices():
    devices = get_devices()

    device_list = []
    for device in devices:
        device_list.append(dict(device))

    return jsonify(device_list)

@device_bp.route("/devices/add", methods=["POST"])
def add_device_route():
    name = request.form["name"]
    type = request.form["type"]
    unit_price = request.form["unit_price"]
    stock = request.form["stock"]

    if name == "" or type == "" or unit_price == "" or stock == "":
        return "All fields are required", 400
    if float(unit_price) <= 0:
        return "Price must be a positive number", 400
    if int(stock) < 0:
        return "Stock must be zero or more", 400
    if device_exists(name):
        return "Device already exists", 400

    add_device(name, type, unit_price, stock)

    return "Device added successfully"

@device_bp.route("/devices/update/<int:device_id>", methods=["PUT"])
def update_device_route(device_id):
    name = request.form["name"]
    type = request.form["type"]
    unit_price = request.form["unit_price"]
    stock = request.form["stock"]

    if name == "" or type == "" or unit_price == "" or stock == "":
        return "All fields are required", 400
    if float(unit_price) <= 0:
        return "Price must be a positive number", 400
    if int(stock) < 0:
        return "Stock must be zero or more", 400

    update_device(device_id, name, type, unit_price, stock)

    return "Device updated successfully"

@device_bp.route("/devices/delete/<int:device_id>", methods=["DELETE"])
def delete_device_route(device_id):
    delete_device(device_id)

    return "Device deleted successfully"

@device_bp.route("/devices/search")
def search_devices_route():
    name = request.args.get("name", "")
    type = request.args.get("type", "")

    devices = search_devices(name, type)

    device_list = []
    for device in devices:
        device_list.append(dict(device))

    return jsonify(device_list)