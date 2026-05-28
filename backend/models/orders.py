from backend.models.db_crud import *

ALLOWED_STATUSES = {"saved", "pending payment"} 
 
class Order:
    def create(self, customer_id, items):
        if not items:
            return {"error": "Order must contain at least one device item"}
 
        validated_lines = []
        order_total = 0.0
 
        for item in items:
            if "device_id" not in item or "quantity" not in item:
                return {"error": "Each item requires a device_id and quantity"}
 
            quantity = item["quantity"]
 
            if quantity <= 0:
                return {"error": "Quantity must be a positive integer"}
 
            device = next((dict(d) for d in get_devices() if d["device_id"] == item["device_id"]), None)
            if device is None:
                return {"error": "Device not found"}
 
            if quantity > device["stock"]:
                return {"error": f"{device['name']}: requested {quantity} but only {device['stock']} in stock"}
 
            order_total += quantity * device["unit_price"]
            validated_lines.append({
                "device_id":   device["device_id"],
                "device_name": device["name"],
                "unit_price":  device["unit_price"],
                "quantity":    quantity,
                "total_price": quantity * device["unit_price"],
            })
 
        order_id = create_order(customer_id, order_total)
        for line in validated_lines:
            create_order_item(order_id, line["device_id"], line["quantity"], line["total_price"])
            decrement_stock(line["device_id"], line["quantity"])
 
        return self.get_detail(order_id)
 
    def get_customer(self, customer_id):
        orders = get_customer_orders(customer_id)
        return [dict(x) for x in orders]
 
    def get_all(self):
        orders = get_all_orders()
        return [dict(x) for x in orders]
 
    def get_detail(self, order_id):
        order = get_order(order_id)
        if order is None:
            return {"error": "Order not found"}
 
        items = get_order_items(order_id)
        return {
            "order": dict(order),
            "items": [dict(i) for i in items],
        }
    def search(self, customer_id, order_id=None, date=None):
        orders = search_customer_orders(customer_id, order_id=order_id, date=date)
        return [dict(x) for x in orders]

    def update(self, order_id, customer_id, role, items):
        if role != "customer":
            return {"error": "Only customers can update orders"}
 
        order = get_order(order_id)
        if order is None:
            return {"error": "Order not found"}
 
        if order["customer_id"] != customer_id:
            return {"error": "You can only update your own orders"}
 
        if order["status"] not in ALLOWED_STATUSES:
            return {"error": f"Orders with status '{order['status']}' cannot be edited"}
 
        if not items:
            return {"error": "Updated order must contain at least one device item"}
 
        validated_lines = []
        order_total = 0.0
 
        for item in items:
            if "device_id" not in item or "quantity" not in item:
                return {"error": "Each item requires a device_id and quantity"}
 
            quantity = item["quantity"]
 
            if quantity <= 0:
                return {"error": "Quantity must be a positive integer"}
 
            device = next((dict(d) for d in get_devices() if d["device_id"] == item["device_id"]), None)
            if device is None:
                return {"error": "Device not found"}
 
            if quantity > device["stock"]:
                return {"error": f"{device['name']}: requested {quantity} but only {device['stock']} in stock"}
 
            order_total += quantity * device["unit_price"]
            validated_lines.append({
                "device_id":   device["device_id"],
                "quantity":    quantity,
                "total_price": quantity * device["unit_price"],
            })
 
        replace_order_items(order_id, validated_lines, order_total)
        return self.get_detail(order_id)
 
    def cancel(self, order_id, customer_id, role):
        if role != "customer":
            return {"error": "Only customers can cancel orders"}
 
        order = get_order(order_id)
        if order is None:
            return {"error": "Order not found"}
 
        if order["status"] not in ALLOWED_STATUSES:
            return {"error": "Order cannot be cancelled"}
 
        cancel_order(order_id)
        return {"message": "Order cancelled", "order_id": order_id}
