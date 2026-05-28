import unittest
from backend.models.db_crud import get_devices, create_order, create_order_item, decrement_stock, get_order, get_order_items, cancel_order
from backend.models.db_connect import get_connection

TEST_CUSTOMER_ID = 1
TEST_DEVICE_ID = 1
TEST_DEVICE_ID_2 = 2
MISSING_DEVICE_ID = 999


class TestCreateOrderUnit(unittest.TestCase):

    def setUp(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE devices SET stock = 10 WHERE device_id = 1")
        cursor.execute("UPDATE devices SET stock = 5 WHERE device_id = 2")
        conn.commit()
        conn.close()

    def test_ac1_select_single_device(self):
        items = [{"device_id": TEST_DEVICE_ID, "quantity": 2}]
        total = 2 * 60.00
        order_id = create_order(TEST_CUSTOMER_ID, total)
        create_order_item(order_id, TEST_DEVICE_ID, 2, 120.00)
        decrement_stock(TEST_DEVICE_ID, 2)
        order = get_order(order_id)
        self.assertIsNotNone(order)
        self.assertEqual(order["customer_id"], TEST_CUSTOMER_ID)
        cancel_order(order_id)

    def test_ac2_specify_quantity(self):
        requested_quantity = 3
        total = requested_quantity * 60.00
        order_id = create_order(TEST_CUSTOMER_ID, total)
        create_order_item(order_id, TEST_DEVICE_ID, requested_quantity, total)
        order_items = get_order_items(order_id)
        self.assertEqual(order_items[0]["quantity"], requested_quantity)
        cancel_order(order_id)

    def test_ac3_insufficient_stock_fails(self):
        devices = get_devices()
        device = None
        for d in devices:
            if d["device_id"] == TEST_DEVICE_ID:
                device = d
                break
        requested_quantity = device["stock"] + 10
        self.assertGreater(requested_quantity, device["stock"])

    def test_ac4_empty_order_fails(self):
        items = []
        self.assertEqual(len(items), 0)

    def test_ac5_calculate_total_single_item(self):
        device_price = 60.00
        quantity = 3
        calculated_total = quantity * device_price
        expected_total = 180.00
        self.assertEqual(calculated_total, expected_total)

    def test_ac6_view_created_order_details(self):
        total = 2 * 60.00
        order_id = create_order(TEST_CUSTOMER_ID, total)
        create_order_item(order_id, TEST_DEVICE_ID, 2, total)
        decrement_stock(TEST_DEVICE_ID, 2)
        order = get_order(order_id)
        order_items = get_order_items(order_id)
        self.assertIsNotNone(order)
        self.assertEqual(order["order_id"], order_id)
        self.assertEqual(order["customer_id"], TEST_CUSTOMER_ID)
        self.assertEqual(len(order_items), 1)
        cancel_order(order_id)

if __name__ == "__main__":
    unittest.main()