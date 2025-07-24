# 🗄️ Meal Planner Database System

This document provides comprehensive information about the Meal Planner database system, including setup, management, and maintenance procedures.

## 📋 Overview

The Meal Planner uses SQLite as its database engine, providing a lightweight, serverless database solution that's perfect for both development and production use. The database system includes:

- **Automatic table creation** when the app starts
- **Database setup and management scripts**
- **Migration system** for schema updates
- **Backup and maintenance tools**
- **Sample data generation**

## 🏗️ Database Schema

### Tables

1. **users** - User accounts and authentication
2. **meals** - Recipe storage (personal and community)
3. **ingredients** - Pantry inventory management
4. **meal_plan** - Daily meal scheduling
5. **favorites** - User's favorite meals
6. **shopping_list** - Grocery shopping management

### Relationships

- Users can have multiple meals, ingredients, and meal plans
- Meals can be favorited by multiple users
- Shopping list items are linked to users
- Meal plans reference specific meals and users

## 🚀 Quick Start

### 1. Automatic Setup (Recommended)

The database is automatically created when you run the Flask application:

```bash
python3 app.py
```

This will:
- Create `meal_planner.db` if it doesn't exist
- Set up all required tables
- Initialize the database schema

### 2. Manual Setup

For more control over the database setup, use the database setup script:

```bash
python3 database_setup.py
```

This interactive script provides options for:
- Initializing the database
- Adding sample data
- Viewing database information
- Creating backups
- Resetting the database

## 📊 Database Management Scripts

### 1. Database Setup (`database_setup.py`)

**Purpose**: Initialize and configure the database

**Usage**:
```bash
python3 database_setup.py
```

**Features**:
- Create all database tables
- Add performance indexes
- Insert sample data
- Show database statistics
- Create backups
- Reset database

**Sample Data Included**:
- 3 test users (admin, demo_user, test_user)
- 5 community meals (Spaghetti Carbonara, Chicken Stir Fry, etc.)
- 8 sample ingredients

### 2. Database Migrations (`database_migrations.py`)

**Purpose**: Handle database schema updates and versioning

**Usage**:
```bash
python3 database_migrations.py
```

**Features**:
- Run pending migrations
- View migration status
- Rollback migrations (with warnings)
- Version tracking

**Available Migrations**:
- `001_initial_schema` - Initial database structure
- `002_add_indexes` - Performance optimization
- `003_add_meal_notes` - Add notes field to meals
- `004_add_ingredient_notes` - Add notes field to ingredients
- `005_add_shopping_list_notes` - Add notes field to shopping list

### 3. Database Maintenance (`database_maintenance.py`)

**Purpose**: Backup, optimize, and maintain the database

**Usage**:
```bash
python3 database_maintenance.py
```

**Features**:
- Create compressed/uncompressed backups
- List and manage backup files
- Restore from backups
- Database optimization (VACUUM, ANALYZE)
- Integrity checks
- Export data to JSON
- Clean up old backups

## 🔧 Database Operations

### Creating Backups

```bash
# Using the maintenance script
python3 database_maintenance.py
# Choose option 1: Create backup

# Or using the setup script
python3 database_setup.py
# Choose option 4: Backup database
```

### Restoring Backups

```bash
python3 database_maintenance.py
# Choose option 2: List backups
# Choose option 3: Restore from backup
```

### Optimizing Performance

```bash
python3 database_maintenance.py
# Choose option 4: Optimize database
```

This runs:
- `VACUUM` - Reclaims space and optimizes storage
- `ANALYZE` - Updates query statistics
- `PRAGMA optimize` - Optimizes database settings

### Checking Database Health

```bash
python3 database_maintenance.py
# Choose option 5: Check database integrity
```

## 📈 Performance Optimization

### Indexes

The database includes indexes on frequently queried columns:

- `users`: username, email
- `meals`: user_id, category
- `ingredients`: user_id, category
- `meal_plan`: date, user_id
- `shopping_list`: user_id, category
- `favorites`: user_id

### Database Settings

Recommended SQLite settings for optimal performance:

```sql
PRAGMA journal_mode = WAL;        -- Write-Ahead Logging
PRAGMA synchronous = NORMAL;      -- Balanced durability/performance
PRAGMA cache_size = -64000;       -- 64MB cache
PRAGMA temp_store = MEMORY;       -- Store temp tables in memory
```

## 🔒 Security Considerations

### Password Storage

- Passwords are hashed using Werkzeug's `generate_password_hash()`
- Uses secure hashing algorithms (bcrypt by default)
- Salt is automatically generated for each password

### Data Protection

- User data is isolated by `user_id` foreign keys
- Community meals are shared but user-specific data is protected
- Database file should have appropriate file permissions

### Backup Security

- Backups are stored in `database_backups/` directory
- Compressed backups use gzip compression
- Backup files include timestamps for versioning

## 📁 File Structure

```
MealPlanner/
├── meal_planner.db              # Main database file
├── database_setup.py            # Setup and initialization
├── database_migrations.py       # Schema migration system
├── database_maintenance.py      # Backup and maintenance
├── database_backups/            # Backup directory
│   ├── meal_planner_backup_20241224_143022.db.gz
│   └── ...
└── DATABASE_README.md           # This file
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Locked**
   ```bash
   # Check if another process is using the database
   lsof meal_planner.db
   # Restart the application
   ```

2. **Corrupted Database**
   ```bash
   # Check integrity
   python3 database_maintenance.py
   # Choose option 5: Check database integrity
   
   # If corrupted, restore from backup
   python3 database_maintenance.py
   # Choose option 3: Restore from backup
   ```

3. **Performance Issues**
   ```bash
   # Optimize database
   python3 database_maintenance.py
   # Choose option 4: Optimize database
   
   # Check statistics
   python3 database_maintenance.py
   # Choose option 6: Show database statistics
   ```

### Database Size Management

- Regular optimization helps maintain performance
- Clean up old backups periodically
- Monitor database size growth
- Consider archiving old data if needed

## 🔄 Migration Workflow

When making schema changes:

1. **Create a new migration** in `database_migrations.py`
2. **Test the migration** on a copy of the database
3. **Backup the production database**
4. **Run the migration** using `database_migrations.py`
5. **Verify the changes** work correctly

Example migration:
```python
{
    'name': '006_add_new_feature',
    'version': '1.3.0',
    'description': 'Add new feature table',
    'sql': [
        "CREATE TABLE IF NOT EXISTS new_feature (id INTEGER PRIMARY KEY, name TEXT)"
    ]
}
```

## 📞 Support

For database-related issues:

1. Check this README for common solutions
2. Use the maintenance scripts to diagnose issues
3. Create backups before making changes
4. Test migrations on sample data first

## 🔮 Future Enhancements

Potential database improvements:

- **PostgreSQL support** for larger deployments
- **Database connection pooling** for better performance
- **Automated backup scheduling**
- **Data archiving** for old records
- **Advanced analytics** and reporting
- **Multi-tenant support** for hosted versions

---

*Last updated: December 2024* 