from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime, timedelta
import calendar
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Create meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT,
            prep_time INTEGER,
            cook_time INTEGER,
            servings INTEGER,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create ingredients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL,
            unit TEXT,
            category TEXT,
            expiry_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create meal_plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            meal_id INTEGER,
            meal_type TEXT,
            FOREIGN KEY (meal_id) REFERENCES meals (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/meals')
def meals():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM meals ORDER BY name')
    meals_data = cursor.fetchall()
    conn.close()
    
    meals_list = []
    for meal in meals_data:
        meals_list.append({
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2],
            'instructions': meal[3],
            'prep_time': meal[4],
            'cook_time': meal[5],
            'servings': meal[6],
            'category': meal[7]
        })
    
    return render_template('meals.html', meals=meals_list)

@app.route('/add_meal', methods=['POST'])
def add_meal():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['ingredients'], data['instructions'], 
          data['prep_time'], data['cook_time'], data['servings'], data['category']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/delete_meal/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/ingredients')
def ingredients():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ingredients ORDER BY name')
    ingredients_data = cursor.fetchall()
    conn.close()
    
    ingredients_list = []
    for ingredient in ingredients_data:
        ingredients_list.append({
            'id': ingredient[0],
            'name': ingredient[1],
            'quantity': ingredient[2],
            'unit': ingredient[3],
            'category': ingredient[4],
            'expiry_date': ingredient[5]
        })
    
    return render_template('ingredients.html', ingredients=ingredients_list)

@app.route('/add_ingredient', methods=['POST'])
def add_ingredient():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ingredients (name, quantity, unit, category, expiry_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['quantity'], data['unit'], data['category'], data['expiry_date']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/delete_ingredient/<int:ingredient_id>', methods=['DELETE'])
def delete_ingredient(ingredient_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ingredients WHERE id = ?', (ingredient_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/calendar')
def calendar_view():
    # Get current month
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get meals for meal planning
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM meals ORDER BY name')
    meals = cursor.fetchall()
    
    # Get existing meal plan for this month
    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()
    
    cursor.execute('''
        SELECT mp.date, mp.meal_type, m.name 
        FROM meal_plan mp 
        JOIN meals m ON mp.meal_id = m.id 
        WHERE mp.date BETWEEN ? AND ?
        ORDER BY mp.date
    ''', (start_date, end_date))
    meal_plan = cursor.fetchall()
    conn.close()
    
    # Organize meal plan by date
    meal_plan_dict = {}
    for plan in meal_plan:
        date_str = plan[0]
        if date_str not in meal_plan_dict:
            meal_plan_dict[date_str] = {}
        meal_plan_dict[date_str][plan[1]] = plan[2]
    
    return render_template('calendar.html', 
                         calendar=cal, 
                         month_name=month_name, 
                         year=year,
                         month=month,
                         meals=meals,
                         meal_plan=meal_plan_dict)

@app.route('/save_meal_plan', methods=['POST'])
def save_meal_plan():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Clear existing meal plan for this date
    cursor.execute('DELETE FROM meal_plan WHERE date = ?', (data['date'],))
    
    # Add new meal plan
    if data['meal_id']:
        cursor.execute('''
            INSERT INTO meal_plan (date, meal_id, meal_type)
            VALUES (?, ?, ?)
        ''', (data['date'], data['meal_id'], data['meal_type']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/auto_generate_plan', methods=['POST'])
def auto_generate_plan():
    data = request.get_json()
    year = data['year']
    month = data['month']
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get all meals
    cursor.execute('SELECT id FROM meals')
    meal_ids = [row[0] for row in cursor.fetchall()]
    
    if not meal_ids:
        conn.close()
        return jsonify({'success': False, 'message': 'No meals available'})
    
    # Clear existing meal plan for this month
    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()
    cursor.execute('DELETE FROM meal_plan WHERE date BETWEEN ? AND ?', (start_date, end_date))
    
    # Generate meal plan
    current_date = start_date
    meal_types = ['breakfast', 'lunch', 'dinner']
    
    while current_date <= end_date:
        for meal_type in meal_types:
            # Randomly select a meal
            import random
            meal_id = random.choice(meal_ids)
            cursor.execute('''
                INSERT INTO meal_plan (date, meal_id, meal_type)
                VALUES (?, ?, ?)
            ''', (current_date, meal_id, meal_type))
        current_date += timedelta(days=1)
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Get port from environment variable (for production) or use 5000 for development
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
