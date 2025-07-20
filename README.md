# My Meal Planner

A comprehensive meal planning application built with Flask and modern web technologies. Organize your meals, track ingredients, and create monthly meal plans with automatic generation.

## Features

### 🍽️ Meals Management
- Add, edit, and delete meals with detailed information
- Include ingredients, cooking instructions, prep time, cook time, and servings
- Categorize meals (breakfast, lunch, dinner, snack, dessert)
- Beautiful card-based layout for easy browsing

### 🥕 Ingredients Tracking
- Track ingredients in your pantry with quantities and units
- Set expiry dates to avoid food waste
- Categorize ingredients (produce, dairy, meat, pantry, frozen, spices)
- View expiring items and category breakdowns

### 📅 Monthly Calendar
- Interactive monthly calendar view
- Plan breakfast, lunch, and dinner for each day
- Auto-generate meal plans for the entire month
- Visual indicators for planned meals
- Statistics and meal plan overview

## Installation

1. **Clone or download the project**
   ```bash
   cd MealPlanner
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python planner.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## Usage

### Getting Started
1. **Add Meals**: Start by adding your favorite recipes in the Meals tab
2. **Add Ingredients**: Track what you have in your pantry in the Ingredients tab
3. **Plan Your Month**: Use the Calendar tab to create your monthly meal plan

### Adding a Meal
1. Click the "Add New Meal" button in the Meals tab
2. Fill in the meal details:
   - Name and category
   - Prep time, cook time, and servings
   - Ingredients (one per line)
   - Cooking instructions
3. Click "Save Meal"

### Adding Ingredients
1. Click the "Add New Ingredient" button in the Ingredients tab
2. Fill in the ingredient details:
   - Name and category
   - Quantity and unit
   - Expiry date (optional)
3. Click "Save Ingredient"

### Creating a Meal Plan
1. Go to the Calendar tab
2. Click the "+" button on any day to plan meals
3. Select breakfast, lunch, and dinner from your saved meals
4. Click "Save Plan"

### Auto-Generating a Meal Plan
1. In the Calendar tab, click "Auto Generate"
2. The system will randomly assign meals to each day of the month
3. You can then manually adjust any days as needed

## Database

The application uses SQLite for data storage. The database file (`meal_planner.db`) will be created automatically when you first run the application.

### Database Schema
- **meals**: Stores meal information (name, ingredients, instructions, etc.)
- **ingredients**: Stores ingredient inventory (name, quantity, expiry date, etc.)
- **meal_plan**: Stores planned meals for specific dates

## Customization

### Adding New Meal Categories
Edit the meal category options in `templates/index.html`:
```html
<option value="your-category">Your Category</option>
```

### Adding New Ingredient Categories
Edit the ingredient category options in `templates/index.html`:
```html
<option value="your-category">Your Category</option>
```

### Adding New Units
Edit the unit options in `templates/index.html`:
```html
<option value="your-unit">Your Unit</option>
```

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6

## File Structure

```
MealPlanner/
├── planner.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── index.html         # Main application template
│   ├── meals.html         # Meals tab template
│   ├── ingredients.html   # Ingredients tab template
│   └── calendar.html      # Calendar tab template
└── meal_planner.db        # SQLite database (created automatically)
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in `planner.py` line: `app.run(debug=True, port=5001)`

2. **Database errors**
   - Delete `meal_planner.db` and restart the application

3. **Template not found**
   - Ensure the `templates` folder exists and contains all template files

### Getting Help

If you encounter any issues:
1. Check that all dependencies are installed correctly
2. Ensure you're running the application from the correct directory
3. Check the console output for error messages

## Future Enhancements

- [ ] Recipe import from popular cooking websites
- [ ] Shopping list generation based on meal plans
- [ ] Nutritional information tracking
- [ ] Meal plan sharing and collaboration
- [ ] Mobile-responsive design improvements
- [ ] Recipe scaling functionality
- [ ] Meal plan templates and themes

## License

This project is open source and available under the MIT License.
