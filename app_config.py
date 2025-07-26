"""
Application Configuration Management.
Consolidated configuration for Recipe AI application.
"""

# App Configuration Constants
APP_NAME = "Recipe AI - Smart Recipe Generation"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "AI-powered recipe generation using advanced workflows"

# UI Configuration
UI_PAGE_TITLE = APP_NAME
UI_PAGE_ICON = "🍲"
UI_LAYOUT = "wide"
UI_THEME = "light"

# LLM Configuration
LLM_MODEL_NAME = "gpt-4"
LLM_TIMEOUT = 120.0
LLM_MAX_RETRIES = 3
LLM_DEFAULT_TEMPERATURE = 0.3
LLM_PRECISE_TEMPERATURE = 0.1
LLM_CREATIVE_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 4000

# Workflow Configuration
WORKFLOW_ENABLE_TAVILY_SEARCH = False
WORKFLOW_ENABLE_ENHANCED_TIPS = True
WORKFLOW_ENABLE_FALLBACK_RECIPES = True

# Recipe Generation Settings
MAX_RECIPE_SUGGESTIONS = 5
MIN_RECIPE_SUGGESTIONS = 3
DEFAULT_SERVINGS = 4
MAX_COOKING_TIME = 180  # minutes
MAX_PREP_TIME = 120  # minutes

# Supported Options
SUPPORTED_APPLIANCES = [
    "Oven",
    "Stovetop", 
    "Microwave",
    "Air Fryer",
    "Slow Cooker",
    "Pressure Cooker",
    "Grill",
    "Toaster",
    "Food Processor",
    "Blender"
]

SUPPORTED_SKILL_LEVELS = [
    "Beginner",
    "Intermediate", 
    "Advanced"
]

SUPPORTED_DIETARY_RESTRICTIONS = [
    "Vegetarian",
    "Vegan",
    "Gluten-Free",
    "Dairy-Free",
    "Keto",
    "Low-Carb",
    "Low-Sodium",
    "Nut-Free",
    "Egg-Free",
    "Soy-Free"
]

SUPPORTED_CUISINES = [
    "Any",
    "Italian",
    "Mexican",
    "Asian",
    "American",
    "Mediterranean",
    "Indian",
    "Thai",
    "French",
    "Middle Eastern",
    "Japanese",
    "Chinese",
    "Korean",
    "Greek",
    "Spanish"
]

# Common Kitchen Ingredients by Category
COMMON_INGREDIENTS = {
    'proteins': [
        'Chicken', 'Eggs', 'Salmon', 'Tuna', 'Tofu', 
        'Beans', 'Lentils', 'Chickpeas', 'Cheese', 'Greek yogurt', 
        'Shrimp', 'Turkey', 'Pork', 'Cottage cheese'
    ],
    'vegetables': [
        'Tomatoes', 'Onions', 'Garlic', 'Bell peppers', 'Spinach', 'Broccoli', 
        'Carrots', 'Mushrooms', 'Zucchini', 'Potatoes', 'Sweet potatoes', 
        'Avocado', 'Cucumber', 'Lettuce', 'Celery', 'Corn', 'Green beans', 'Limes'
    ],
    'grains_starches': [
        'Rice', 'Pasta', 'Bread', 'Quinoa', 'Oats', 'Flour', 'Noodles', 
        'Barley'
    ],
    'dairy': [
        'Milk', 'Heavy cream', 'Butter', 'Cream cheese', 'Mozzarella', 
        'Parmesan', 'Cheddar', 'Almond milk', 'Coconut milk', 'Sour cream', 
        'Ricotta', 'Feta', 'Goat cheese'
    ],
    'herbs_spices': [
        'Basil', 'Oregano', 'Thyme', 'Rosemary', 'Parsley', 'Cilantro', 
        'Garlic powder', 'Paprika', 'Cumin', 'Black pepper',
        'Chili powder', 'Cinnamon', 'Ginger', 'Turmeric', 'Bay leaves',
        'Coriander seeds', 'Cardamom', 'Cloves', 'Fennel seeds', 'Mustard seeds',
        'Fenugreek', 'Star anise', 'Curry leaves', 'Red chili powder',
        'Green cardamom', 'Black cardamom', 'Nutmeg', 'Mace', 'Saffron'
    ],
    'pantry': [
        'Salt', 'Olive oil', 'Vegetable oil', 'Soy sauce', 'Vinegar', 'Honey', 
        'Sugar', 'Canned tomatoes', 'Coconut oil', 'Vanilla extract', 
        'Baking powder', 'Stock/Broth', 'Mustard', 'Ketchup', 'Hot sauce'
    ],
    'fruits': [
        'Apples', 'Bananas', 'Lemons', 'Oranges', 'Berries', 
        'Grapes', 'Pineapple', 'Mango', 'Strawberries', 'Blueberries', 
        'Peaches', 'Pears', 'Cherries', 'Watermelon'
    ]
}

# Ingredient Categories (legacy - for backward compatibility)
INGREDIENT_CATEGORIES = {
    'proteins': COMMON_INGREDIENTS['proteins'],
    'vegetables': COMMON_INGREDIENTS['vegetables'],
    'grains': COMMON_INGREDIENTS['grains_starches'],
    'dairy': COMMON_INGREDIENTS['dairy'],
    'herbs_spices': COMMON_INGREDIENTS['herbs_spices'],
    'pantry': COMMON_INGREDIENTS['pantry'],
    'fruits': COMMON_INGREDIENTS['fruits']
}
