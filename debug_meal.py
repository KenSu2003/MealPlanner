#!/usr/bin/env python3

import sqlite3
import json
from planner import app

def debug_meal_details():
    """Debug the meal details endpoint"""
    
    # Check what meals exist
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM meals WHERE id = 33')
    meal = cursor.fetchone()
    print(f"Meal 33 in database: {meal}")
    conn.close()
    
    # Test the endpoint
    with app.test_client() as client:
        # Create a session (simulate login)
        with client.session_transaction() as sess:
            sess['user_id'] = 1  # Assuming user ID 1 exists
        
        # Test the meal details endpoint
        response = client.get('/get_meal_details/33')
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.get_json()
            print(f"Response JSON: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Raw response: {response.data}")

if __name__ == "__main__":
    debug_meal_details() 