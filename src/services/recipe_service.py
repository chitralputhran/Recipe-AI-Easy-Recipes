"""
Recipe Service for handling recipe generation logic.
"""

from typing import Dict, List, Any
from models import RecipeState
from .llm_service import LLMService


class RecipeService:
    """Service for recipe generation and processing."""
    
    def __init__(self, llm_service: LLMService):
        """Initialize recipe service with LLM service."""
        self.llm_service = llm_service
    
    def generate_combined_recipe(self, state: RecipeState) -> Dict[str, Any]:
        """Generate recipe, nutrition, and shopping list in one call."""
        try:
            ingredients_list = state.get('ingredients', [])
            
            system_prompt = """You are a professional chef and nutritionist. 
            Provide detailed, accurate recipe information in the requested JSON format. 
            Always include COMPLETE step-by-step instructions - never truncate or abbreviate them."""
            
            user_prompt = f"""
            Create a complete recipe analysis for the following ingredients and preferences:
            
            Ingredients: {ingredients_list}
            Appliances: {state['available_appliances']}
            Skill Level: {state['skill_level']}
            Dietary Restrictions: {state['dietary_restrictions']}
            Cuisine Preference: {state['cuisine_preference']}
            
            Please provide a comprehensive response in JSON format with the following structure:
            {{
                "recipe": {{
                    "name": "Recipe Name",
                    "description": "Brief description",
                    "emoji_representation": "🍽️",
                    "prep_time": 15,
                    "cook_time": 30,
                    "total_time": 45,
                    "servings": 4,
                    "difficulty": "Medium",
                    "cuisine_type": "Italian",
                    "appliance_used": "Oven",
                    "ingredients": ["ingredient with measurement", "..."],
                    "instructions": ["step 1 - be very detailed", "step 2 - include timing", "step 3 - include temperatures", "... continue with ALL steps needed"],
                    "tips": ["cooking tip 1", "tip 2", "..."],
                    "variations": ["variation 1", "variation 2"],
                    "storage_instructions": "How to store leftovers"
                }},
                "nutrition": {{
                    "calories_per_serving": 350,
                    "protein_g": 25.5,
                    "carbs_g": 30.2,
                    "fat_g": 12.8,
                    "fiber_g": 5.2,
                    "sodium_mg": 450,
                    "sugar_g": 8.1,
                    "key_nutrients": ["High in protein", "Good source of fiber"],
                    "health_benefits": ["benefit 1", "benefit 2"]
                }},
                "shopping_list": ["item 1", "item 2", "..."]
            }}
            
            Make sure the recipe:
            1. Uses primarily the provided ingredients
            2. Is appropriate for the specified skill level
            3. Respects dietary restrictions
            4. Uses the available cooking appliances
            5. Follows the cuisine preference when possible
            6. Includes accurate nutritional estimates
            7. Provides a practical shopping list for missing ingredients
            8. CRITICAL: Ensures ALL ingredients are properly cooked - especially:
               - Lentils, beans, and legumes (need 20-45 min cooking time)
               - Rice, quinoa, and grains (need proper cooking/boiling)
               - Raw meats and poultry (must reach safe internal temperatures)
               - Root vegetables (need adequate cooking time)
            9. CRITICAL: Instructions must be COMPLETE and include:
               - Every step from start to finish
               - Specific cooking times and methods for each ingredient
               - Temperatures where applicable
               - Preparation details (chopping, seasoning, etc.)
               - Do NOT truncate or abbreviate the instructions
            10. Verify that no ingredient is left uncooked when it should be cooked
            
            IMPORTANT: Provide COMPLETE step-by-step instructions. Do not abbreviate or summarize. Each step should be detailed enough for someone to follow exactly.
            """
            
            response_data = self.llm_service.generate_json_response(
                system_prompt, 
                user_prompt, 
                "default"
            )
            
            return response_data
            
        except Exception as e:
            raise
    
    def parse_ingredients(self, ingredients: List[str]) -> List[str]:
        """Simple ingredient parsing."""
        return [ingredient.strip() for ingredient in ingredients if ingredient.strip()]
    
    def validate_recipe_data(self, recipe_data: Dict[str, Any]) -> bool:
        """Validate recipe data structure."""
        required_keys = ["recipe", "nutrition", "shopping_list"]
        return all(key in recipe_data for key in required_keys)
    
    def create_fallback_recipe(self, ingredients: List[str], appliance: str = "oven") -> Dict[str, Any]:
        """Create a basic fallback recipe when generation fails."""
        return {
            "recipe": {
                "name": "Simple Mixed Dish",
                "description": f"A simple dish using available ingredients with {appliance}",
                "emoji_representation": "🍽️✨",
                "prep_time": 15,
                "cook_time": 30,
                "total_time": 45,
                "servings": 4,
                "difficulty": "Easy",
                "cuisine_type": "International",
                "appliance_used": appliance,
                "ingredients": [f"• {ingredient}" for ingredient in ingredients],
                "instructions": [
                    "1. Prepare all ingredients by washing and chopping as needed",
                    f"2. Use your {appliance} to cook the ingredients",
                    "3. Season to taste with salt and pepper",
                    "4. Cook until ingredients are tender and flavors are combined",
                    "5. Serve hot and enjoy!"
                ],
                "tips": [
                    "Taste and adjust seasoning as needed",
                    "Don't overcook the vegetables",
                    "Add herbs or spices to enhance flavor"
                ],
                "variations": [
                    "Add different seasonings",
                    "Include additional vegetables",
                    "Try different cooking methods"
                ],
                "storage_instructions": "Store in refrigerator for up to 3 days"
            },
            "nutrition": {
                "calories_per_serving": 300,
                "protein_g": 12.0,
                "carbs_g": 40.0,
                "fat_g": 10.0,
                "fiber_g": 5.0,
                "sodium_mg": 500.0,
                "sugar_g": 6.0,
                "key_nutrients": ["Vitamin C", "Iron", "Calcium"],
                "health_benefits": ["Provides balanced nutrition", "Contains essential vitamins"]
            },
            "shopping_list": ["Basic seasonings if needed"]
        }
