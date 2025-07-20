from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import sqlite3
from datetime import datetime, timedelta
import calendar
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database initialization
def init_db():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
            user_id INTEGER,
            is_community BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create meal_plan table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            meal_id INTEGER,
            meal_type TEXT,
            user_id INTEGER,
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Initialize database
init_db()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('meal_planner.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
        if cursor.fetchone():
            flash('Username or email already exists!')
            conn.close()
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                      (username, email, password_hash))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('meal_planner.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/meals')
@login_required
def meals():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get personal meals
    cursor.execute('SELECT * FROM meals WHERE user_id = ? AND is_community = FALSE ORDER BY name', (session['user_id'],))
    personal_meals = cursor.fetchall()
    
    # Get community meals (shared by other users)
    cursor.execute('SELECT m.*, u.username FROM meals m JOIN users u ON m.user_id = u.id WHERE m.is_community = TRUE ORDER BY m.name')
    community_meals = cursor.fetchall()
    
    # Get default meals (system meals)
    cursor.execute('SELECT * FROM meals WHERE user_id IS NULL ORDER BY name')
    default_meals = cursor.fetchall()
    
    conn.close()
    
    personal_list = []
    for meal in personal_meals:
        personal_list.append({
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2],
            'instructions': meal[3],
            'prep_time': meal[4],
            'cook_time': meal[5],
            'servings': meal[6],
            'category': meal[7],
            'user_id': meal[8],
            'is_community': meal[9],
            'type': 'personal'
        })
    
    community_list = []
    for meal in community_meals:
        community_list.append({
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2],
            'instructions': meal[3],
            'prep_time': meal[4],
            'cook_time': meal[5],
            'servings': meal[6],
            'category': meal[7],
            'user_id': meal[8],
            'is_community': meal[9],
            'username': meal[10],
            'type': 'community'
        })
    
    default_list = []
    for meal in default_meals:
        default_list.append({
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2],
            'instructions': meal[3],
            'prep_time': meal[4],
            'cook_time': meal[5],
            'servings': meal[6],
            'category': meal[7],
            'user_id': meal[8],
            'type': 'default'
        })
    
    return render_template('meals.html', 
                         personal_meals=personal_list, 
                         community_meals=community_list, 
                         default_meals=default_list)

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['ingredients'], data['instructions'], 
          data['prep_time'], data['cook_time'], data['servings'], data['category'], 
          session['user_id'], data.get('is_community', False)))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/delete_meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal(meal_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM meals WHERE id = ? AND user_id = ?', (meal_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/ingredients')
@login_required
def ingredients():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ingredients WHERE user_id = ? ORDER BY name', (session['user_id'],))
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
@login_required
def add_ingredient():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO ingredients (name, quantity, unit, category, expiry_date, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['quantity'], data['unit'], data['category'], data['expiry_date'], session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/delete_ingredient/<int:ingredient_id>', methods=['DELETE'])
@login_required
def delete_ingredient(ingredient_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ingredients WHERE id = ? AND user_id = ?', (ingredient_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/calendar')
@login_required
def calendar_view():
    # Get current month
    now = datetime.now()
    year = now.year
    month = now.month
    
    # Get calendar data
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Get meals for meal planning (personal + community + default meals)
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get personal meals
    cursor.execute('''
        SELECT id, name FROM meals 
        WHERE user_id = ? AND is_community = FALSE
        ORDER BY name
    ''', (session['user_id'],))
    personal_meals = cursor.fetchall()
    
    # Get community meals (including former default meals)
    cursor.execute('''
        SELECT id, name FROM meals 
        WHERE is_community = TRUE
        ORDER BY name
    ''')
    community_meals = cursor.fetchall()
    
    # Combine all meals for backward compatibility
    meals = personal_meals + community_meals
    
    # Get ingredients for the user
    cursor.execute('SELECT * FROM ingredients WHERE user_id = ? ORDER BY name', (session['user_id'],))
    ingredients_data = cursor.fetchall()
    
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
    
    # Get existing meal plan for this month
    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()
    
    cursor.execute('''
        SELECT mp.date, mp.meal_type, m.name 
        FROM meal_plan mp 
        JOIN meals m ON mp.meal_id = m.id 
        WHERE mp.date BETWEEN ? AND ? AND mp.user_id = ?
        ORDER BY mp.date
    ''', (start_date, end_date, session['user_id']))
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
                         personal_meals=personal_meals,
                         community_meals=community_meals,
                         ingredients=ingredients_list,
                         meal_plan=meal_plan_dict)

@app.route('/get_day_meals/<date>')
@login_required
def get_day_meals(date):
    """Get detailed meal information for a specific day"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get meal plan for the specific date
    cursor.execute('''
        SELECT mp.meal_type, m.id, m.name, m.ingredients, m.instructions, m.prep_time, m.cook_time, m.servings, m.category
        FROM meal_plan mp 
        JOIN meals m ON mp.meal_id = m.id 
        WHERE mp.date = ? AND mp.user_id = ?
        ORDER BY mp.meal_type
    ''', (date, session['user_id']))
    meal_plans = cursor.fetchall()
    
    # Organize meals by type
    day_meals = {}
    for meal in meal_plans:
        meal_type = meal[0]
        day_meals[meal_type] = {
            'id': meal[1],
            'name': meal[2],
            'ingredients': meal[3],
            'instructions': meal[4],
            'prep_time': meal[5],
            'cook_time': meal[6],
            'servings': meal[7],
            'category': meal[8]
        }
    
    conn.close()
    return jsonify(day_meals)

@app.route('/get_meal_details/<int:meal_id>')
@login_required
def get_meal_details(meal_id):
    """Get detailed meal information"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community
        FROM meals 
        WHERE id = ?
    ''', (meal_id,))
    meal = cursor.fetchone()
    conn.close()
    
    if meal:
        return jsonify({
            'id': meal[0],
            'name': meal[1],
            'ingredients': meal[2],
            'instructions': meal[3],
            'prep_time': meal[4],
            'cook_time': meal[5],
            'servings': meal[6],
            'category': meal[7],
            'user_id': meal[8],
            'is_community': meal[9]
        })
    else:
        return jsonify({'error': 'Meal not found'}), 404

@app.route('/save_meal_plan', methods=['POST'])
@login_required
def save_meal_plan():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Clear existing meal plan for this specific meal type, date and user
    cursor.execute('DELETE FROM meal_plan WHERE date = ? AND meal_type = ? AND user_id = ?', 
                   (data['date'], data['meal_type'], session['user_id']))
    
    # Add new meal plan
    if data['meal_id']:
        cursor.execute('''
            INSERT INTO meal_plan (date, meal_id, meal_type, user_id)
            VALUES (?, ?, ?, ?)
        ''', (data['date'], data['meal_id'], data['meal_type'], session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/auto_generate_plan', methods=['POST'])
@login_required
def auto_generate_plan():
    data = request.get_json()
    year = data['year']
    month = data['month']
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get available meals (personal + community + default)
    cursor.execute('''
        SELECT id FROM meals 
        WHERE (user_id = ? AND is_community = FALSE) 
           OR (is_community = TRUE) 
           OR (user_id IS NULL)
    ''', (session['user_id'],))
    meal_ids = [row[0] for row in cursor.fetchall()]
    
    if not meal_ids:
        conn.close()
        return jsonify({'success': False, 'message': 'No meals available'})
    
    # Clear existing meal plan for this month and user
    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()
    cursor.execute('DELETE FROM meal_plan WHERE date BETWEEN ? AND ? AND user_id = ?', (start_date, end_date, session['user_id']))
    
    # Generate meal plan
    current_date = start_date
    meal_types = ['breakfast', 'lunch', 'dinner']
    
    while current_date <= end_date:
        for meal_type in meal_types:
            # Randomly select a meal
            import random
            meal_id = random.choice(meal_ids)
            cursor.execute('''
                INSERT INTO meal_plan (date, meal_id, meal_type, user_id)
                VALUES (?, ?, ?, ?)
            ''', (current_date, meal_id, meal_type, session['user_id']))
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
