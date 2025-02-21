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
        # Send a GET request to the '/' route
        response = self.app.get('/')

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        # Check that the response data is "Hello, World!"
        self.assertEqual(response.data.decode('utf-8')
, "Hello, World!")

if __name__ == '__main__':
    unittest.main()