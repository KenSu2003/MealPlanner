import sqlite3

def add_meals():
    conn = sqlite3.connect('meal_planner.db')
    cursor = conn.cursor()
    
    meals_data = [
        {
            'name': 'Meatball Spaghetti',
            'ingredients': 'Spaghetti, ground beef, breadcrumbs, egg, parmesan cheese, garlic, onion, tomato sauce, olive oil, salt, pepper, basil',
            'instructions': '1. Mix ground beef, breadcrumbs, egg, parmesan, garlic, salt, and pepper to form meatballs\n2. Cook meatballs in olive oil until browned\n3. Add tomato sauce and simmer for 20 minutes\n4. Cook spaghetti according to package directions\n5. Serve meatballs over spaghetti with sauce and fresh basil',
            'prep_time': 15,
            'cook_time': 30,
            'servings': 4,
            'category': 'Italian'
        },
        {
            'name': 'Parmesan Cheese Bacon Spaghetti',
            'ingredients': 'Spaghetti, bacon, parmesan cheese, garlic, olive oil, black pepper, salt, parsley',
            'instructions': '1. Cook bacon until crispy, then crumble\n2. Cook spaghetti according to package directions\n3. In a pan, sauté garlic in olive oil\n4. Add cooked spaghetti, bacon, parmesan cheese, salt, and pepper\n5. Toss until well combined and serve with parsley',
            'prep_time': 10,
            'cook_time': 20,
            'servings': 4,
            'category': 'Italian'
        },
        {
            'name': 'Mac n Cheese',
            'ingredients': 'Macaroni, cheddar cheese, milk, butter, flour, breadcrumbs, salt, pepper',
            'instructions': '1. Cook macaroni according to package directions\n2. Make roux with butter and flour\n3. Add milk and stir until thickened\n4. Add cheese and stir until melted\n5. Mix with cooked macaroni\n6. Top with breadcrumbs and bake at 350°F for 20 minutes',
            'prep_time': 10,
            'cook_time': 25,
            'servings': 6,
            'category': 'American'
        },
        {
            'name': '滷肉飯 (Braised Pork Rice)',
            'ingredients': 'Pork belly, soy sauce, dark soy sauce, rice wine, sugar, garlic, shallots, star anise, cinnamon, white rice, hard-boiled eggs',
            'instructions': '1. Cut pork belly into small pieces\n2. Sauté garlic and shallots\n3. Add pork and brown\n4. Add soy sauces, rice wine, sugar, and spices\n5. Simmer for 1-2 hours until tender\n6. Serve over rice with hard-boiled eggs',
            'prep_time': 20,
            'cook_time': 120,
            'servings': 4,
            'category': 'Taiwanese'
        },
        {
            'name': 'Rabokki',
            'ingredients': 'Rice cakes, fish cakes, ramen noodles, gochujang, gochugaru, soy sauce, sugar, garlic, green onions, hard-boiled eggs',
            'instructions': '1. Soak rice cakes in water for 30 minutes\n2. Make sauce with gochujang, gochugaru, soy sauce, sugar, and garlic\n3. Boil rice cakes and fish cakes\n4. Add ramen noodles and sauce\n5. Simmer until thickened\n6. Garnish with green onions and eggs',
            'prep_time': 30,
            'cook_time': 20,
            'servings': 4,
            'category': 'Korean'
        },
        {
            'name': 'Chicken Noodle Soup',
            'ingredients': 'Chicken breast, egg noodles, carrots, celery, onion, chicken broth, garlic, thyme, bay leaves, salt, pepper, parsley',
            'instructions': '1. Sauté onion, celery, and carrots\n2. Add chicken broth and bring to boil\n3. Add chicken and simmer for 20 minutes\n4. Remove chicken, shred, and return to pot\n5. Add noodles and cook until tender\n6. Season with salt, pepper, and parsley',
            'prep_time': 15,
            'cook_time': 30,
            'servings': 6,
            'category': 'American'
        },
        {
            'name': '火腿蛋炒飯 (Ham and Egg Fried Rice)',
            'ingredients': 'Cooked rice, ham, eggs, green onions, soy sauce, sesame oil, vegetable oil, salt, pepper',
            'instructions': '1. Scramble eggs and set aside\n2. Sauté ham in oil\n3. Add rice and stir-fry\n4. Add eggs back to pan\n5. Season with soy sauce, salt, and pepper\n6. Garnish with green onions and drizzle with sesame oil',
            'prep_time': 10,
            'cook_time': 15,
            'servings': 4,
            'category': 'Chinese'
        },
        {
            'name': 'Parmesan Chicken',
            'ingredients': 'Chicken breasts, parmesan cheese, breadcrumbs, eggs, flour, olive oil, salt, pepper, Italian seasoning',
            'instructions': '1. Mix breadcrumbs, parmesan, and seasonings\n2. Dredge chicken in flour, then egg, then breadcrumb mixture\n3. Pan-fry in olive oil until golden and cooked through\n4. Serve with lemon wedges and pasta',
            'prep_time': 15,
            'cook_time': 20,
            'servings': 4,
            'category': 'Italian'
        },
        {
            'name': '乾麵 (Dry Noodles)',
            'ingredients': 'Noodles, soy sauce, sesame oil, green onions, garlic, chili oil, vinegar, sugar, ground pork (optional)',
            'instructions': '1. Cook noodles according to package directions\n2. Mix sauce with soy sauce, sesame oil, garlic, vinegar, and sugar\n3. Toss noodles with sauce\n4. Top with green onions and chili oil\n5. Add ground pork if desired',
            'prep_time': 10,
            'cook_time': 10,
            'servings': 2,
            'category': 'Chinese'
        },
        {
            'name': 'Dumplings',
            'ingredients': 'Ground pork, cabbage, green onions, ginger, garlic, soy sauce, sesame oil, dumpling wrappers, salt, pepper',
            'instructions': '1. Mix pork, cabbage, green onions, ginger, garlic, and seasonings\n2. Place filling in dumpling wrappers\n3. Fold and seal edges\n4. Steam or pan-fry until cooked\n5. Serve with soy sauce and vinegar dipping sauce',
            'prep_time': 30,
            'cook_time': 15,
            'servings': 6,
            'category': 'Chinese'
        },
        {
            'name': 'Risotto',
            'ingredients': 'Arborio rice, chicken broth, white wine, parmesan cheese, butter, onion, garlic, mushrooms, salt, pepper, parsley',
            'instructions': '1. Sauté onion and garlic in butter\n2. Add rice and toast for 2 minutes\n3. Add wine and stir until absorbed\n4. Gradually add hot broth, stirring constantly\n5. Add mushrooms and continue cooking\n6. Stir in parmesan and season to taste',
            'prep_time': 15,
            'cook_time': 25,
            'servings': 4,
            'category': 'Italian'
        },
        {
            'name': '飯糰 (Onigiri)',
            'ingredients': 'Cooked rice, nori sheets, salmon, pickled plum, salt, sesame seeds',
            'instructions': '1. Wet hands with salt water\n2. Take rice and form into triangle shape\n3. Make indentation and add filling\n4. Wrap with nori sheet\n5. Sprinkle with sesame seeds\n6. Serve immediately or wrap for later',
            'prep_time': 20,
            'cook_time': 0,
            'servings': 4,
            'category': 'Japanese'
        },
        {
            'name': 'Beef Noodle',
            'ingredients': 'Beef shank, noodles, soy sauce, dark soy sauce, star anise, cinnamon, garlic, ginger, green onions, bok choy, chili oil',
            'instructions': '1. Brown beef shank in oil\n2. Add soy sauces, spices, garlic, and ginger\n3. Simmer for 2-3 hours until tender\n4. Cook noodles according to package directions\n5. Blanch bok choy\n6. Serve beef over noodles with broth and vegetables',
            'prep_time': 20,
            'cook_time': 180,
            'servings': 4,
            'category': 'Chinese'
        },
        {
            'name': '蔥燒牛肉 (Scallion Beef)',
            'ingredients': 'Beef slices, green onions, soy sauce, oyster sauce, garlic, ginger, cornstarch, vegetable oil, salt, pepper',
            'instructions': '1. Marinate beef with soy sauce, cornstarch, and seasonings\n2. Sauté beef until browned\n3. Add garlic and ginger\n4. Add green onions and stir-fry\n5. Add oyster sauce and toss\n6. Serve over rice',
            'prep_time': 15,
            'cook_time': 10,
            'servings': 4,
            'category': 'Chinese'
        },
        {
            'name': '三杯雞 (Three Cup Chicken)',
            'ingredients': 'Chicken, soy sauce, rice wine, sesame oil, garlic, ginger, basil, sugar, vegetable oil',
            'instructions': '1. Cut chicken into pieces\n2. Heat oil and brown chicken\n3. Add garlic and ginger\n4. Add equal parts soy sauce, rice wine, and sesame oil\n5. Simmer until sauce thickens\n6. Add basil and serve',
            'prep_time': 15,
            'cook_time': 25,
            'servings': 4,
            'category': 'Taiwanese'
        }
    ]
    
    for meal in meals_data:
        cursor.execute('''
            INSERT INTO meals (name, ingredients, instructions, prep_time, cook_time, servings, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (meal['name'], meal['ingredients'], meal['instructions'], 
              meal['prep_time'], meal['cook_time'], meal['servings'], meal['category']))
    
    conn.commit()
    conn.close()
    print("All meals have been added successfully!")

if __name__ == "__main__":
    add_meals() 