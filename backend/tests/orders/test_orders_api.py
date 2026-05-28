import unittest
import requests

BASE_URL = "http://127.0.0.1:8080"
TEST_DEVICE_ID = 1
TEST_DEVICE_ID_2 = 2
MISSING_DEVICE_ID = 999


def login_as(client):
    response = client.post(f"{BASE_URL}/login", json={
        "email": "alice@iotbay.com",
        "password": "password123"
    })
    assert response.status_code == 200
    return client


def cancel_order(client, order_id):
    try:
        client.put(f"{BASE_URL}/orders/cancel/{order_id}", json={"confirmed": True})
    except:
        pass


class TestCreateOrderAPI(unittest.TestCase):

    def setUp(self):
        self.client = requests.Session()
        login_as(self.client)

    def tearDown(self):
        if hasattr(self, 'order_id'):
            cancel_order(self.client, self.order_id)

    def test_ac1_create_order_single_device(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": TEST_DEVICE_ID, "quantity": 2}]
        })
        if response.status_code == 400:
            print(f"Error response: {response.json()}")
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("order", data)
        self.assertIn("items", data)
        self.assertEqual(len(data["items"]), 1)
        self.order_id = data["order"]["order_id"]

    def test_ac1_create_order_multiple_devices(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [
                {"device_id": TEST_DEVICE_ID, "quantity": 1},
                {"device_id": TEST_DEVICE_ID_2, "quantity": 2}
            ]
        })
        if response.status_code == 400:
            print(f"Error response: {response.json()}")
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(len(data["items"]), 2)
        self.order_id = data["order"]["order_id"]

    def test_ac2_specify_quantity(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": TEST_DEVICE_ID, "quantity": 5}]
        })
        
        if response.status_code == 400:
            print(f"Error response: {response.json()}")
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["items"][0]["quantity"], 5)
        self.order_id = data["order"]["order_id"]

    def test_ac3_device_not_found_returns_400(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": MISSING_DEVICE_ID, "quantity": 1}]
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_ac3_insufficient_stock_returns_400(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": TEST_DEVICE_ID, "quantity": 100}]
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertIn("stock", response.json()["error"].lower())

    def test_ac4_empty_items_returns_400(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": []
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_ac5_total_price_calculated_correctly(self):
        response = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": TEST_DEVICE_ID, "quantity": 3}]
        })
        
        if response.status_code == 400:
            print(f"Error response: {response.json()}")
        
        self.assertEqual(response.status_code, 201)
        data = response.json()

        self.assertEqual(data["order"]["total_price"], 180.00)
        self.order_id = data["order"]["order_id"]

    def test_ac6_view_order_details(self):
        create_resp = self.client.post(f"{BASE_URL}/orders/create", json={
            "items": [{"device_id": TEST_DEVICE_ID, "quantity": 2}]
        })

        if create_resp.status_code != 201:
            self.skipTest(f"Cannot create order: {create_resp.json() if create_resp.text else 'Unknown error'}")
        
        order_id = create_resp.json()["order"]["order_id"]

        view_resp = self.client.get(f"{BASE_URL}/orders/{order_id}")
        self.assertEqual(view_resp.status_code, 200)
        data = view_resp.json()
        self.assertEqual(data["order"]["order_id"], order_id)
        self.assertEqual(data["order"]["customer_id"], 1)

        cancel_order(self.client, order_id)


if __name__ == "__main__":
    unittest.main()