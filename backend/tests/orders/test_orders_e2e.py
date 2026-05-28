import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestCreateOrderE2E(unittest.TestCase):

    def setUp(self):
        opts = Options()
        self.driver = webdriver.Chrome(options=opts)
        self.driver.get("http://127.0.0.1:5500/login.html")
        self.driver.find_element(By.ID, "email").send_keys("alice@iotbay.com")
        self.driver.find_element(By.ID, "password").send_keys("password123")
        self.driver.find_element(By.ID, "loginButton").click()
        WebDriverWait(self.driver, 5).until(EC.url_contains("welcome.html"))
        self.driver.get("http://127.0.0.1:5500/orders.html")

    def tearDown(self):
        self.driver.quit()

    def test_ac1_select_single_device(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "device-card")))
        add_button = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart button")
        add_button.click()
        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart-item")
        self.assertGreater(len(cart_items), 0)

    def test_ac1_select_multiple_devices(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "device-card")))
        add_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".add-to-cart button")
        self.assertGreaterEqual(len(add_buttons), 2)
        add_buttons[0].click()
        add_buttons[1].click()
        cart_items = self.driver.find_elements(By.CLASS_NAME, "cart-item")
        self.assertGreaterEqual(len(cart_items), 2)

    def test_ac2_specify_quantity(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "device-card")))
        quantity_input = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart input")
        quantity_input.clear()
        quantity_input.send_keys("3")
        add_button = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart button")
        add_button.click()
        cart_text = self.driver.find_element(By.CLASS_NAME, "cart-item").text
        self.assertIn("3 x", cart_text)

    def test_ac3_insufficient_stock_shows_error(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "device-card")))
        quantity_input = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart input")
        quantity_input.clear()
        quantity_input.send_keys("999")
        add_button = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart button")
        add_button.click()
        error_element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "errorMessage")))
        self.assertIn("stock", error_element.text.lower())

    def test_ac4_cannot_submit_empty_order(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "submitOrderBtn")))
        self.driver.find_element(By.ID, "submitOrderBtn").click()
        error_element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.ID, "errorMessage")))
        self.assertIn("at least one", error_element.text.lower())

    def test_ac5_total_updates_when_adding_items(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "showFormBtn")))
        self.driver.find_element(By.ID, "showFormBtn").click()
        total_span = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "cartTotal")))
        initial_total = total_span.text
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "device-card")))
        add_button = self.driver.find_element(By.CSS_SELECTOR, ".add-to-cart button")
        add_button.click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "cart-item")))
        self.assertNotEqual(total_span.text, initial_total)

    def test_ac6_orders_displayed_on_page(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "order-card")))
        order_cards = self.driver.find_elements(By.CLASS_NAME, "order-card")
        self.assertGreater(len(order_cards), 0)


if __name__ == "__main__":
    unittest.main()