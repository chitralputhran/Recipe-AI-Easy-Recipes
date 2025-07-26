"""
Data models for the Recipe AI LangGraph implementation.
"""

from typing import Dict, List, Any, TypedDict, Optional
from pydantic import BaseModel, Field


class RecipeState(TypedDict):
    """State object that flows through the LangGraph workflow."""
    # User inputs
    ingredients: List[str]
    appliance: str
    available_appliances: List[str]
    dietary_restrictions: List[str]
    cuisine_preference: str
    skill_level: str
    
    # Processed data
    parsed_ingredients: List[Dict[str, Any]]
    recipe_suggestions: List[Dict[str, Any]]
    selected_recipe: Dict[str, Any]
    alternative_recipes: List[Dict[str, Any]]  # Other recipe options
    user_selected_alternative: Optional[str]  # User's choice of alternative
    nutrition_info: Dict[str, Any]
    shopping_list: List[str]
    cooking_tips: List[str]
    final_recipe: Dict[str, Any]
    
    # Online search data
    online_search_results: List[Dict[str, Any]]
    search_enhanced: bool
    search_enhancement_complete: bool
    
    # Recipe verification data
    verification_result: Optional[Dict[str, Any]]
    
    # Metadata
    processing_step: str
    error_message: Optional[str]


class NutritionInfo(BaseModel):
    """Model for nutritional information."""
    calories_per_serving: int = Field(description="Calories per serving")
    protein_g: float = Field(description="Protein in grams")
    carbs_g: float = Field(description="Carbohydrates in grams")
    fat_g: float = Field(description="Fat in grams")
    fiber_g: float = Field(description="Fiber in grams")
    sodium_mg: float = Field(description="Sodium in milligrams")
    sugar_g: float = Field(description="Sugar in grams")
    key_nutrients: List[str] = Field(description="Key nutrients and vitamins")
    health_benefits: List[str] = Field(description="Health benefits of this recipe")


class FinalRecipe(BaseModel):
    """Model for the complete final recipe."""
    name: str = Field(description="Recipe name")
    description: str = Field(description="Recipe description")
    ingredients: List[str] = Field(description="List of ingredients with quantities")
    instructions: List[str] = Field(description="Step-by-step instructions")
    prep_time: int = Field(description="Preparation time in minutes")
    cook_time: int = Field(description="Cooking time in minutes")
    total_time: int = Field(description="Total time in minutes")
    servings: int = Field(description="Number of servings")
    difficulty: str = Field(description="Difficulty level")
    cuisine_type: str = Field(description="Type of cuisine")
    appliance_used: str = Field(description="Primary appliance used")
    nutrition: NutritionInfo = Field(description="Nutritional information")
    tips: List[str] = Field(description="Cooking tips")
    variations: List[str] = Field(description="Recipe variations")
    storage_instructions: str = Field(description="How to store leftovers")
    emoji_representation: str = Field(description="Fun emoji representation of the recipe")
