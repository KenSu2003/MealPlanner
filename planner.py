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
def init_db(db_path='meal_planner.db'):
    conn = sqlite3.connect(db_path)
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
    
    # Create favorites table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            meal_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            UNIQUE(user_id, meal_id)
        )
    ''')
    
    # Create shopping_list table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL,
            unit TEXT,
            category TEXT,
            is_purchased BOOLEAN DEFAULT FALSE,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    # Get user's favorites
    cursor.execute('SELECT meal_id FROM favorites WHERE user_id = ?', (session['user_id'],))
    user_favorites = {row[0] for row in cursor.fetchall()}
    
    # Get personal meals
    cursor.execute('SELECT * FROM meals WHERE user_id = ? AND is_community = FALSE ORDER BY name', (session['user_id'],))
    personal_meals = cursor.fetchall()
    
    # Get community meals (including former default meals)
    cursor.execute('''
        SELECT m.*, COALESCE(u.username, 'System') as username 
        FROM meals m 
        LEFT JOIN users u ON m.user_id = u.id 
        WHERE m.is_community = TRUE 
        ORDER BY m.name
    ''')
    community_meals = cursor.fetchall()
    
    # Get favorite meals
    cursor.execute('''
        SELECT m.*, COALESCE(u.username, 'System') as username 
        FROM favorites f
        JOIN meals m ON f.meal_id = m.id
        LEFT JOIN users u ON m.user_id = u.id
        WHERE f.user_id = ?
        ORDER BY m.name
    ''', (session['user_id'],))
    favorite_meals = cursor.fetchall()
    
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
            'is_favorited': meal[0] in user_favorites,
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
            'is_favorited': meal[0] in user_favorites,
            'type': 'community'
        })
    
    favorite_list = []
    for meal in favorite_meals:
        favorite_list.append({
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
            'is_favorited': True,
            'type': 'favorite'
        })
    
    return render_template('meals.html', 
                         personal_meals=personal_list, 
                         community_meals=community_list, 
                         favorite_meals=favorite_list)

@app.route('/add_meal', methods=['POST'])
@login_required
def add_meal():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Always add to personal meals first
    cursor.execute('''
        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE)
    ''', (data['name'], data['ingredients'], data['instructions'], 
          data['prep_time'], data['cook_time'], data['servings'], data['category'], 
          session['user_id']))
    
    # If user wants to share with community, also add a community version
    if data.get('is_community', False):
        cursor.execute('''
            INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, TRUE)
        ''', (data['name'], data['ingredients'], data['instructions'], 
              data['prep_time'], data['cook_time'], data['servings'], data['category'], 
              session['user_id']))
    
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

@app.route('/edit_meal/<int:meal_id>', methods=['PUT'])
@login_required
def edit_meal(meal_id):
    """Edit an existing meal"""
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Check if meal exists and belongs to user
    cursor.execute('SELECT id FROM meals WHERE id = ? AND user_id = ?', (meal_id, session['user_id']))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Meal not found or access denied'})
    
    # Update the meal
    cursor.execute('''
        UPDATE meals 
        SET name = ?, ingredients = ?, instructions = ?, prep_time = ?, 
            cook_time = ?, servings = ?, category = ?
        WHERE id = ? AND user_id = ?
    ''', (data['name'], data['ingredients'], data['instructions'], 
          data['prep_time'], data['cook_time'], data['servings'], 
          data['category'], meal_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Meal updated successfully'})

@app.route('/add_to_my_meals/<int:meal_id>', methods=['POST'])
@login_required
def add_to_my_meals(meal_id):
    """Copy a community meal to user's personal meals"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get the meal details
    cursor.execute('''
        SELECT name, ingredients, instructions, prep_time, cook_time, servings, category
        FROM meals WHERE id = ?
    ''', (meal_id,))
    meal = cursor.fetchone()
    
    if meal:
        # Check if user already has this meal
        cursor.execute('''
            SELECT id FROM meals 
            WHERE user_id = ? AND name = ? AND is_community = FALSE
        ''', (session['user_id'], meal[0]))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': 'You already have this meal in your collection'})
        
        # Add the meal to user's personal meals
        cursor.execute('''
            INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE)
        ''', (meal[0], meal[1], meal[2], meal[3], meal[4], meal[5], meal[6], session['user_id']))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Meal added to your collection'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Meal not found'})

@app.route('/friends')
@login_required
def friends():
    """Friends page showing other users' meal plans"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get all users except current user
    cursor.execute('''
        SELECT id, username 
        FROM users 
        WHERE id != ? 
        ORDER BY username
    ''', (session['user_id'],))
    users = cursor.fetchall()
    
    # Get today's date and week dates
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Get current month's dates for full month view
    now = datetime.now()
    year = now.year
    month = now.month
    start_date = datetime(year, month, 1).date()
    end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).date()
    
    friends_data = []
    for user in users:
        # Get today's meals
        cursor.execute('''
            SELECT mp.meal_type, m.name 
            FROM meal_plan mp 
            JOIN meals m ON mp.meal_id = m.id 
            WHERE mp.date = ? AND mp.user_id = ?
            ORDER BY mp.meal_type
        ''', (today, user[0]))
        today_meals = cursor.fetchall()
        
        # Get weekly meals
        cursor.execute('''
            SELECT mp.date, mp.meal_type, m.name 
            FROM meal_plan mp 
            JOIN meals m ON mp.meal_id = m.id 
            WHERE mp.date BETWEEN ? AND ? AND mp.user_id = ?
            ORDER BY mp.date, mp.meal_type
        ''', (week_start, week_end, user[0]))
        weekly_meals = cursor.fetchall()
        
        # Get monthly meals
        cursor.execute('''
            SELECT mp.date, mp.meal_type, m.name 
            FROM meal_plan mp 
            JOIN meals m ON mp.meal_id = m.id 
            WHERE mp.date BETWEEN ? AND ? AND mp.user_id = ?
            ORDER BY mp.date, mp.meal_type
        ''', (start_date, end_date, user[0]))
        monthly_meals = cursor.fetchall()
        
        # Organize meals by date
        today_dict = {}
        for meal in today_meals:
            today_dict[meal[0]] = meal[1]
        
        weekly_dict = {}
        for meal in weekly_meals:
            date_str = meal[0]
            if date_str not in weekly_dict:
                weekly_dict[date_str] = {}
            weekly_dict[date_str][meal[1]] = meal[2]
        
        monthly_dict = {}
        for meal in monthly_meals:
            date_str = meal[0]
            if date_str not in monthly_dict:
                monthly_dict[date_str] = {}
            monthly_dict[date_str][meal[1]] = meal[2]
        
        friends_data.append({
            'id': user[0],
            'username': user[1],
            'today_meals': today_dict,
            'weekly_meals': weekly_dict,
            'monthly_meals': monthly_dict
        })
    
    conn.close()
    
    return render_template('friends.html', friends=friends_data, month_name=calendar.month_name[month], year=year, today=today)

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
        # Convert expiry_date string to date object if it exists
        expiry_date = None
        if ingredient[5]:
            try:
                expiry_date = datetime.strptime(ingredient[5], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                expiry_date = None
        
        ingredients_list.append({
            'id': ingredient[0],
            'name': ingredient[1],
            'quantity': ingredient[2],
            'unit': ingredient[3],
            'category': ingredient[4],
            'expiry_date': expiry_date
        })
    
    return render_template('ingredients.html', ingredients=ingredients_list, today=datetime.now().date())

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
    try:
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
                'success': True,
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
            return jsonify({'success': False, 'error': f'Meal with ID {meal_id} not found'}), 404
            
    except Exception as e:
        print(f"Error in get_meal_details: {str(e)}")
        return jsonify({'success': False, 'error': 'Database error occurred'}), 500

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

@app.route('/delete_planned_meal', methods=['POST'])
@login_required
def delete_planned_meal():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Delete the specific planned meal
    cursor.execute('DELETE FROM meal_plan WHERE date = ? AND meal_type = ? AND user_id = ?', 
                   (data['date'], data['meal_type'], session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/toggle_favorite/<int:meal_id>', methods=['POST'])
@login_required
def toggle_favorite(meal_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Check if meal exists
    cursor.execute('SELECT id FROM meals WHERE id = ?', (meal_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Meal not found'})
    
    # Check if already favorited
    cursor.execute('SELECT id FROM favorites WHERE user_id = ? AND meal_id = ?', (session['user_id'], meal_id))
    existing_favorite = cursor.fetchone()
    
    if existing_favorite:
        # Remove from favorites
        cursor.execute('DELETE FROM favorites WHERE user_id = ? AND meal_id = ?', (session['user_id'], meal_id))
        message = 'Meal removed from favorites'
        message_type = 'error'
        is_favorited = False
    else:
        # Add to favorites
        cursor.execute('INSERT INTO favorites (user_id, meal_id) VALUES (?, ?)', (session['user_id'], meal_id))
        message = 'Meal added to favorites'
        message_type = 'success'
        is_favorited = True
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': message, 'message_type': message_type, 'is_favorited': is_favorited})

@app.route('/get_favorites')
@login_required
def get_favorites():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, COALESCE(u.username, 'System') as username 
        FROM favorites f
        JOIN meals m ON f.meal_id = m.id
        LEFT JOIN users u ON m.user_id = u.id
        WHERE f.user_id = ?
        ORDER BY m.name
    ''', (session['user_id'],))
    
    favorites = cursor.fetchall()
    conn.close()
    
    favorites_list = []
    for meal in favorites:
        favorites_list.append({
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
            'type': 'favorite'
        })
    
    return jsonify(favorites_list)

@app.route('/get_meal_details_by_name', methods=['POST'])
@login_required
def get_meal_details_by_name():
    data = request.get_json()
    meal_name = data.get('meal_name')
    user_id = data.get('user_id')
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, COALESCE(u.username, 'System') as username 
        FROM meals m 
        LEFT JOIN users u ON m.user_id = u.id 
        WHERE m.name = ? AND m.user_id = ?
        ORDER BY m.id DESC
        LIMIT 1
    ''', (meal_name, user_id))
    
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
            'is_community': meal[9],
            'username': meal[10]
        })
    else:
        return jsonify({'error': 'Meal not found'}), 404

@app.route('/shopping_list')
@login_required
def shopping_list():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shopping_list WHERE user_id = ? ORDER BY category, name', (session['user_id'],))
    shopping_data = cursor.fetchall()
    conn.close()
    
    shopping_items = []
    for item in shopping_data:
        shopping_items.append({
            'id': item[0],
            'name': item[1],
            'quantity': item[2],
            'unit': item[3],
            'category': item[4],
            'is_purchased': item[5]
        })
    
    return render_template('shopping_list.html', shopping_items=shopping_items)

@app.route('/generate_shopping_list', methods=['POST'])
@login_required
def generate_shopping_list():
    data = request.get_json()
    period = data.get('period', 'week')  # 'week' or 'month'
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Calculate date range
    today = datetime.now().date()
    if period == 'week':
        start_date = today
        end_date = today + timedelta(days=6)
    else:  # month
        start_date = today
        end_date = today + timedelta(days=29)
    
    # Get planned meals for the period
    cursor.execute('''
        SELECT mp.date, mp.meal_type, m.ingredients
        FROM meal_plan mp 
        JOIN meals m ON mp.meal_id = m.id 
        WHERE mp.date BETWEEN ? AND ? AND mp.user_id = ?
        ORDER BY mp.date
    ''', (start_date, end_date, session['user_id']))
    
    planned_meals = cursor.fetchall()
    
    # Parse ingredients and aggregate them
    ingredient_counts = {}
    
    for meal in planned_meals:
        ingredients_str = meal[2]
        if ingredients_str:
            # Parse ingredients (assuming format like "2 cups flour, 1 lb chicken, etc.")
            ingredients = [ing.strip() for ing in ingredients_str.split(',')]
            for ingredient in ingredients:
                if ingredient:
                    # Try to parse quantity and unit
                    parts = ingredient.split(' ', 2)
                    if len(parts) >= 2:
                        try:
                            quantity = float(parts[0])
                            unit = parts[1]
                            name = parts[2] if len(parts) > 2 else ''
                        except ValueError:
                            quantity = 1
                            unit = ''
                            name = ingredient
                    else:
                        quantity = 1
                        unit = ''
                        name = ingredient
                    
                    # Aggregate ingredients
                    key = f"{name} ({unit})".strip()
                    if key in ingredient_counts:
                        ingredient_counts[key]['quantity'] += quantity
                    else:
                        ingredient_counts[key] = {
                            'name': name,
                            'quantity': quantity,
                            'unit': unit,
                            'category': 'General'  # Default category
                        }
    
    # Clear existing shopping list
    cursor.execute('DELETE FROM shopping_list WHERE user_id = ?', (session['user_id'],))
    
    # Add items to shopping list
    for key, item in ingredient_counts.items():
        cursor.execute('''
            INSERT INTO shopping_list (name, quantity, unit, category, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (item['name'], item['quantity'], item['unit'], item['category'], session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'Shopping list generated for {period}'})

@app.route('/add_shopping_item', methods=['POST'])
@login_required
def add_shopping_item():
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO shopping_list (name, quantity, unit, category, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['quantity'], data['unit'], data['category'], session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/toggle_purchased/<int:item_id>', methods=['POST'])
@login_required
def toggle_purchased(item_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get current status
    cursor.execute('SELECT is_purchased FROM shopping_list WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
    result = cursor.fetchone()
    
    if result:
        new_status = not result[0]
        cursor.execute('UPDATE shopping_list SET is_purchased = ? WHERE id = ? AND user_id = ?', 
                      (new_status, item_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_purchased': new_status})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found'})

@app.route('/mark_as_purchased/<int:item_id>', methods=['POST'])
@login_required
def mark_as_purchased(item_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get shopping item details
    cursor.execute('SELECT name, quantity, unit, category FROM shopping_list WHERE id = ? AND user_id = ?', 
                  (item_id, session['user_id']))
    item = cursor.fetchone()
    
    if item:
        # Add to ingredients inventory
        cursor.execute('''
            INSERT INTO ingredients (name, quantity, unit, category, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (item[0], item[1], item[2], item[3], session['user_id']))
        
        # Remove from shopping list
        cursor.execute('DELETE FROM shopping_list WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Item added to ingredients inventory'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Item not found'})

@app.route('/delete_shopping_item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_shopping_item(item_id):
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shopping_list WHERE id = ? AND user_id = ?', (item_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/get_user_ingredients')
@login_required
def get_user_ingredients():
    """Get user's available ingredients for meal filtering"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, quantity, unit, category FROM ingredients WHERE user_id = ? ORDER BY name', (session['user_id'],))
    ingredients_data = cursor.fetchall()
    conn.close()
    
    ingredients_list = []
    for ingredient in ingredients_data:
        ingredients_list.append({
            'name': ingredient[0],
            'quantity': ingredient[1],
            'unit': ingredient[2],
            'category': ingredient[3]
        })
    
    return jsonify({'success': True, 'ingredients': ingredients_list})

@app.route('/bulk_mark_purchased', methods=['POST'])
@login_required
def bulk_mark_purchased():
    """Bulk mark shopping items as purchased"""
    data = request.get_json()
    item_ids = data.get('item_ids', [])
    
    if not item_ids:
        return jsonify({'success': False, 'message': 'No items selected'})
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Mark all selected items as purchased
    cursor.execute('UPDATE shopping_list SET is_purchased = TRUE WHERE id IN ({}) AND user_id = ?'.format(
        ','.join(['?' for _ in item_ids])), item_ids + [session['user_id']])
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'{len(item_ids)} items marked as purchased'})

@app.route('/bulk_delete_shopping_items', methods=['POST'])
@login_required
def bulk_delete_shopping_items():
    """Bulk delete shopping items"""
    data = request.get_json()
    item_ids = data.get('item_ids', [])
    
    if not item_ids:
        return jsonify({'success': False, 'message': 'No items selected'})
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Delete all selected items
    cursor.execute('DELETE FROM shopping_list WHERE id IN ({}) AND user_id = ?'.format(
        ','.join(['?' for _ in item_ids])), item_ids + [session['user_id']])
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'{len(item_ids)} items deleted'})

@app.route('/quick_add_ingredient', methods=['POST'])
@login_required
def quick_add_ingredient():
    """Quick add ingredient with minimal data"""
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Check if ingredient already exists
    cursor.execute('SELECT id FROM ingredients WHERE name = ? AND user_id = ?', 
                  (data['name'], session['user_id']))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Ingredient already exists'})
    
    # Add ingredient with default values
    cursor.execute('''
        INSERT INTO ingredients (name, quantity, unit, category, user_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data.get('quantity', 1), data.get('unit', 'pcs'), 
          data.get('category', 'other'), session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Ingredient added quickly'})

@app.route('/quick_add_meal', methods=['POST'])
@login_required
def quick_add_meal():
    """Quick add meal with minimal data"""
    data = request.get_json()
    
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Add meal with default values
    cursor.execute('''
        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE)
    ''', (data['name'], data.get('ingredients', ''), data.get('instructions', ''), 
          data.get('prep_time', 15), data.get('cook_time', 30), data.get('servings', 4), 
          data.get('category', 'dinner'), session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Meal added quickly'})

@app.route('/duplicate_meal/<int:meal_id>', methods=['POST'])
@login_required
def duplicate_meal(meal_id):
    """Duplicate an existing meal"""
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    # Get the original meal
    cursor.execute('''
        SELECT name, ingredients, instructions, prep_time, cook_time, servings, category
        FROM meals WHERE id = ?
    ''', (meal_id,))
    meal = cursor.fetchone()
    
    if not meal:
        conn.close()
        return jsonify({'success': False, 'message': 'Meal not found'})
    
    # Create a duplicate with "Copy" suffix
    new_name = f"{meal[0]} (Copy)"
    cursor.execute('''
        INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category, user_id, is_community)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE)
    ''', (new_name, meal[1], meal[2], meal[3], meal[4], meal[5], meal[6], session['user_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Meal duplicated successfully'})

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
