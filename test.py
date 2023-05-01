import time
from seleniumbase import BaseCase

class StreamlitAppTest(BaseCase):

    def setUp(self):
        super().setUp()
        self.app_url = "http://localhost:8501"

    def test_streamlit_app(self):
        self.open(self.app_url)
        time.sleep(5)  # Wait for the app to load

        # Test input and submit button
        self.type("input", "SELECT * FROM order_details LIMIT 10")
        self.click("button")

        # Wait for the response to be displayed
        time.sleep(5)

        # Verify if the response contains the expected input text
        # self.assertIn("SELECT * FROM order_details LIMIT 10", "true")

        # You can add more tests here based on the elements in your Streamlit app

if __name__ == "__main__":
    BaseCase.main()
