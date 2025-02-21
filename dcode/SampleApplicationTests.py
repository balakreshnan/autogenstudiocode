# File: sample_application.py
from flask import Flask

app = Flask(__name__)

@app.route('/')

def home():

    return "Hello, World!"

if __name__ == '__main__':
    app.run()

# File: test_sample_application.py
import unittest
from sample_application import app

class SampleApplicationTests(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        # Test the home route
        response = self.app.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"Hello, World!")

if __name__ == '__main__':
    unittest.main()