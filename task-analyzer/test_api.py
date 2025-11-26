"""Test script to verify task scoring functionality."""
import os
import sys
import django
import json

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, r'C:\Users\sureshraj\task-analyzer')
django.setup()

from views import analyze_tasks
from django.http import QueryDict
from io import BytesIO

# Create a test request
class FakeRequest:
    def __init__(self, body):
        self.body = body
        self.method = 'POST'

# Load test data
with open('tasks.json', 'r') as f:
    test_data = f.read().encode('utf-8')

# Create request
request = FakeRequest(test_data)

# Call the view
response = analyze_tasks(request)

# Print response
print("Response status:", response.status_code)
print("Response content:", response.content.decode('utf-8'))
