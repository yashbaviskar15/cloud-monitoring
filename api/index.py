import sys
import os

# Add demo-app directory to sys.path so app can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'demo-app'))

from app import app
