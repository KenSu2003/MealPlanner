"""
Test suite for MealPlanner Flask application
Tests core functionality including routes, database operations, and user authentication
"""

import pytest
import tempfile
import os
import sqlite3
from datetime import datetime, timedelta
from planner import app, init_db
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    # Create a temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['DATABASE'] = db_path
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            init_db(db_path)
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def auth_client(client):
    """Create an authenticated test client"""
    # Register a test user
    client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    # Login the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    
    return client

def test_index_route(client):
    """Test the index route returns 200"""
    response = client.get('/')
    assert response.status_code == 200

def test_register_route_get(client):
    """Test register route GET method"""
    response = client.get('/register')
    assert response.status_code == 200

def test_register_route_post(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123'
    })
    # Check if registration was successful (302 redirect) or failed (200 with error)
    if response.status_code == 200:
        # Registration failed, check if it's due to existing user
        assert 'already exists' in response.get_data(as_text=True)
    else:
        assert response.status_code == 302  # Redirect after successful registration

def test_login_route_get(client):
    """Test login route GET method"""
    response = client.get('/login')
    assert response.status_code == 200

def test_login_route_post(client):
    """Test user login"""
    # First register a user
    client.post('/register', data={
        'username': 'loginuser',
        'email': 'loginuser@example.com',
        'password': 'password123'
    })
    
    # Then login
    response = client.post('/login', data={
        'username': 'loginuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect after successful login

def test_dashboard_requires_auth(client):
    """Test that dashboard requires authentication"""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login

def test_dashboard_with_auth(auth_client):
    """Test dashboard with authenticated user"""
    response = auth_client.get('/dashboard')
    assert response.status_code == 200

def test_meals_route_requires_auth(client):
    """Test that meals route requires authentication"""
    response = client.get('/meals')
    assert response.status_code == 302  # Redirect to login

def test_meals_route_with_auth(auth_client):
    """Test meals route with authenticated user"""
    response = auth_client.get('/meals')
    assert response.status_code == 200

def test_add_meal(auth_client):
    """Test adding a new meal"""
    response = auth_client.post('/add_meal', 
        json={
            'name': 'Test Meal',
            'ingredients': 'ingredient1, ingredient2',
            'instructions': 'Test instructions',
            'prep_time': '15',
            'cook_time': '30',
            'servings': '4',
            'category': 'Dinner'
        }
    )
    assert response.status_code == 200

def test_calendar_route_requires_auth(client):
    """Test that calendar route requires authentication"""
    response = client.get('/calendar')
    assert response.status_code == 302  # Redirect to login

def test_calendar_route_with_auth(auth_client):
    """Test calendar route with authenticated user"""
    response = auth_client.get('/calendar')
    assert response.status_code == 200

def test_ingredients_route_requires_auth(client):
    """Test that ingredients route requires authentication"""
    response = client.get('/ingredients')
    assert response.status_code == 302  # Redirect to login

def test_ingredients_route_with_auth(auth_client):
    """Test ingredients route with authenticated user"""
    response = auth_client.get('/ingredients')
    assert response.status_code == 200

def test_add_ingredient(auth_client):
    """Test adding a new ingredient"""
    response = auth_client.post('/add_ingredient', 
        json={
            'name': 'Test Ingredient',
            'quantity': '2.5',
            'unit': 'cups',
            'category': 'Produce',
            'expiry_date': '2024-12-31'
        }
    )
    assert response.status_code == 200

def test_shopping_list_route_requires_auth(client):
    """Test that shopping list route requires authentication"""
    response = client.get('/shopping_list')
    assert response.status_code == 302  # Redirect to login

def test_shopping_list_route_with_auth(auth_client):
    """Test shopping list route with authenticated user"""
    response = auth_client.get('/shopping_list')
    assert response.status_code == 200

def test_friends_route_requires_auth(client):
    """Test that friends route requires authentication"""
    response = client.get('/friends')
    assert response.status_code == 302  # Redirect to login

def test_friends_route_with_auth(auth_client):
    """Test friends route with authenticated user"""
    response = auth_client.get('/friends')
    assert response.status_code == 200

def test_logout(auth_client):
    """Test user logout"""
    response = auth_client.get('/logout')
    assert response.status_code == 302  # Redirect after logout

def test_database_initialization():
    """Test that database initialization creates all required tables"""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    try:
        # Configure app to use the temporary database
        app.config['DATABASE'] = db_path
        
        # Initialize database
        with app.app_context():
            init_db(db_path)
        
        # Check that tables exist
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for required tables
        required_tables = ['users', 'meals', 'ingredients', 'meal_plan', 'favorites', 'shopping_list']
        for table in required_tables:
            assert table in tables, f"Table {table} not found in database"
        
        conn.close()
    finally:
        os.close(db_fd)
        os.unlink(db_path)

if __name__ == '__main__':
    pytest.main([__file__]) 