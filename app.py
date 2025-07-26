"""
Recipe AI - Smart Recipe Generation Application - Refactored Architecture.
"""

import streamlit as st
from typing import List, Dict, Any

# Core imports
from app_config import (
    COMMON_INGREDIENTS, UI_PAGE_TITLE, UI_PAGE_ICON, UI_LAYOUT, 
    SUPPORTED_SKILL_LEVELS, SUPPORTED_APPLIANCES, SUPPORTED_DIETARY_RESTRICTIONS, SUPPORTED_CUISINES,
    LLM_MODEL_NAME
)
from models import RecipeState
from src.services import WorkflowService
from src.ui.components import RecipeUI


class RecipeAIApp:
    """Main application class with modular architecture."""
    
    def __init__(self):
        """Initialize the application."""
        self.initialize_session_state()
        self.recipe_ui = RecipeUI()
    
    def initialize_session_state(self):
        """Initialize all session state variables."""
        default_states = {
            "workflow_result": None,
            "processing": False,
            "openai_api_key": None,
            "tavily_api_key": None,
            "current_recipe": None,
            "recipe_history": [],
            "user_preferences": {},
            "error_messages": [],
            "last_ingredients": []
        }
        
        for key, default_value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def setup_page_config(self) -> None:
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title=UI_PAGE_TITLE,
            page_icon=UI_PAGE_ICON,
            layout=UI_LAYOUT
        )
    
    def render_header(self) -> None:
        """Render application header."""
        st.title(f"{UI_PAGE_ICON} {UI_PAGE_TITLE}")
        st.caption("Transform your available ingredients into delicious recipes with AI-powered cooking assistance!")
    
    def render_api_configuration(self) -> None:
        """Render API key configuration sidebar."""
        with st.sidebar:
            st.header("🔑 API Configuration")
            
            # OpenAI API Key
            with st.form("openai_key_form"):
                openai_api_key = st.text_input("OpenAI API Key", type="password", key="openai_input")
                openai_submitted = st.form_submit_button("🔑 Set OpenAI Key", type="primary")
                
                if openai_submitted:
                    if openai_api_key and openai_api_key.startswith('sk-'):
                        st.session_state.openai_api_key = openai_api_key
                        self.recipe_ui.display_success_message("OpenAI API key validated and saved!")
                    else:
                        self.recipe_ui.display_error_message("Please provide a valid OpenAI API key (starts with 'sk-')")
            
            st.divider()
            
            # Tavily API Key (Optional)
            with st.form("tavily_key_form"):
                tavily_api_key = st.text_input(
                    "Tavily API Key", 
                    type="password", 
                    key="tavily_input",
                    help="Optional: For enhanced recipe research and cooking tips"
                )
                tavily_submitted = st.form_submit_button("🔍 Set Tavily Key", type="secondary")
                
                if tavily_submitted:
                    if tavily_api_key and len(tavily_api_key) > 10:
                        st.session_state.tavily_api_key = tavily_api_key
                        self.recipe_ui.display_success_message("Tavily API key validated and saved!")
                    else:
                        self.recipe_ui.display_error_message("Please provide a valid Tavily API key")
            
            # API Key Status
            openai_set = bool(st.session_state.get("openai_api_key"))
            tavily_set = bool(st.session_state.get("tavily_api_key"))
            
            if openai_set and tavily_set:
                self.recipe_ui.display_success_message("All API keys configured")
            elif openai_set and not tavily_set:
                self.recipe_ui.display_success_message("OpenAI key set")
                self.recipe_ui.display_info_message("Tavily key optional for enhanced features")
            elif not openai_set and tavily_set:
                self.recipe_ui.display_warning_message("OpenAI key required")
            else:
                self.recipe_ui.display_warning_message("OpenAI API key required to start")
            
            # Clear API keys button
            if openai_set or tavily_set:
                if st.button("🗑️ Clear All API Keys", type="secondary"):
                    st.session_state.openai_api_key = None
                    st.session_state.tavily_api_key = None
                    st.rerun()
    
    def render_ingredient_selection(self) -> Dict[str, List[str]]:
        """Render ingredient selection interface."""
        st.header("🍽️ What's in Your Kitchen?")
        st.caption("Select the ingredients you have available and let our AI create amazing recipes!")
        
        st.subheader("📋 Available Ingredients")
        
        # Create 3 columns for better organization
        col1, col2, col3 = st.columns(3)
        
        ingredients = {}
        
        with col1:
            st.markdown("#### 🥩 **Proteins & Meats**")
            ingredients['proteins'] = st.multiselect(
                "Select proteins:",
                COMMON_INGREDIENTS['proteins'],
                help="Choose proteins you have available",
                key="proteins_select"
            )
            
            st.markdown("#### 🥕 **Fresh Vegetables**")
            ingredients['vegetables'] = st.multiselect(
                "Select vegetables:",
                COMMON_INGREDIENTS['vegetables'],
                help="Choose vegetables you have available",
                key="vegetables_select"
            )
            
            st.markdown("#### 🌾 **Grains & Starches**")
            ingredients['grains'] = st.multiselect(
                "Select grains & starches:",
                COMMON_INGREDIENTS['grains_starches'],
                help="Choose grains and starches you have",
                key="grains_select"
            )
        
        with col2:
            st.markdown("#### 🥛 **Dairy & Alternatives**")
            ingredients['dairy'] = st.multiselect(
                "Select dairy products:",
                COMMON_INGREDIENTS['dairy'],
                help="Choose dairy products you have",
                key="dairy_select"
            )
            
            st.markdown("#### 🌿 **Herbs & Spices**")
            ingredients['herbs_spices'] = st.multiselect(
                "Select herbs & spices:",
                COMMON_INGREDIENTS['herbs_spices'],
                help="Choose herbs and spices you have",
                key="herbs_select"
            )
            
            st.markdown("#### 🥫 **Pantry Essentials**")
            ingredients['pantry'] = st.multiselect(
                "Select pantry items:",
                COMMON_INGREDIENTS['pantry'],
                help="Choose pantry staples you have",
                key="pantry_select"
            )
        
        with col3:
            st.markdown("#### 🍎 **Fresh Fruits**")
            ingredients['fruits'] = st.multiselect(
                "Select fruits:",
                COMMON_INGREDIENTS['fruits'],
                help="Choose fruits you have available",
                key="fruits_select"
            )
            
            st.markdown("#### ➕ **Additional Items**")
            additional_ingredients = st.text_area(
                "Other ingredients:",
                placeholder="Enter any other ingredients you have (comma-separated)",
                help="Add ingredients not listed in the categories above",
                key="additional_ingredients"
            )
            
            # Process additional ingredients
            if additional_ingredients:
                additional_list = [ing.strip() for ing in additional_ingredients.split(',') if ing.strip()]
                ingredients['additional'] = additional_list
            else:
                ingredients['additional'] = []
        
        return ingredients
    
    def render_cooking_preferences(self) -> Dict[str, Any]:
        """Render cooking preferences selection."""
        st.divider()
        st.subheader("👨‍🍳 Your Cooking Setup")
        
        pref_col1, pref_col2 = st.columns(2)
        
        preferences = {}
        
        with pref_col1:
            preferences['appliances'] = st.multiselect(
                "🔥 **Available Cooking Appliances**",
                ["Oven", "Stovetop", "Microwave", "Air Fryer", "Slow Cooker", "Pressure Cooker", "Grill", "Toaster"],
                default=["Oven", "Stovetop"],
                help="Select all cooking appliances you have available"
            )
            
            preferences['skill_level'] = st.selectbox(
                "🎯 **Your Cooking Skill Level**",
                ["Beginner", "Intermediate", "Advanced"],
                help="This helps us suggest appropriate recipes"
            )
        
        with pref_col2:
            preferences['dietary_restrictions'] = st.multiselect(
                "🚫 **Dietary Restrictions**",
                ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Low-Carb", "Low-Sodium", "Nut-Free"],
                help="Select any dietary restrictions we should consider"
            )
            
            preferences['cuisine_preference'] = st.selectbox(
                "🌍 **Cuisine Preference**",
                ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean", "Indian", "Thai", "French", "Middle Eastern"],
                help="Choose your preferred cuisine style"
            )
        
        return preferences
    
    def render_recipe_summary(self, all_ingredients: List[str], preferences: Dict[str, Any]) -> None:
        """Render recipe generation summary."""
        if not all_ingredients and not preferences['appliances']:
            return
        
        st.divider()
        st.subheader("📊 Recipe Generation Summary")
        
        import pandas as pd
        
        # Create summary data
        summary_data = {
            " ": [
                f"🥘 Total Ingredients: {len(all_ingredients)} selected",
                f"🔥 Appliances: {', '.join(preferences['appliances'])}" if preferences['appliances'] else "🔥 Appliances: None selected",
                f"🚫 Dietary: {', '.join(preferences['dietary_restrictions'])}" if preferences['dietary_restrictions'] else "🚫 Dietary: None",
                f"🌍 Cuisine: {preferences['cuisine_preference']}",
                f"🎯 Skill Level: {preferences['skill_level']}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        st.dataframe(
            summary_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                " ": st.column_config.TextColumn(width="large")
            }
        )
    
    def process_recipe_generation(self, ingredients: List[str], preferences: Dict[str, Any]) -> None:
        """Process recipe generation with the new modular workflow."""
        try:
            # Get API keys
            api_keys = {
                "openai": st.session_state.get("openai_api_key"),
                "tavily": st.session_state.get("tavily_api_key")
            }
            
            # Simple inline validation
            errors = []
            
            # Validate API keys
            if not api_keys["openai"] or not api_keys["openai"].startswith('sk-'):
                errors.append("Please provide a valid OpenAI API key (starts with 'sk-').")
            
            # Validate ingredients
            if not ingredients or len(ingredients) < 1:
                errors.append("Please select at least one ingredient.")
            elif len(ingredients) > 50:
                errors.append("Too many ingredients selected (maximum 50).")
            
            # Validate appliances
            if not preferences['appliances'] or len(preferences['appliances']) < 1:
                errors.append("Please select at least one cooking appliance.")
            else:
                for appliance in preferences['appliances']:
                    if appliance not in SUPPORTED_APPLIANCES:
                        errors.append(f"Invalid appliance: {appliance}")
            
            # Validate preferences
            if preferences['skill_level'] not in SUPPORTED_SKILL_LEVELS:
                errors.append(f"Invalid skill level. Must be one of: {', '.join(SUPPORTED_SKILL_LEVELS)}")
            
            if preferences['dietary_restrictions'] and not all(restriction in SUPPORTED_DIETARY_RESTRICTIONS for restriction in preferences['dietary_restrictions']):
                invalid_restrictions = [r for r in preferences['dietary_restrictions'] if r not in SUPPORTED_DIETARY_RESTRICTIONS]
                errors.append(f"Invalid dietary restrictions: {', '.join(invalid_restrictions)}")
            
            if preferences['cuisine_preference'] and preferences['cuisine_preference'] not in SUPPORTED_CUISINES:
                errors.append(f"Invalid cuisine preference: {preferences['cuisine_preference']}")
            
            # Clean ingredients
            processed_ingredients = [ing.strip() for ing in ingredients if ing and ing.strip()]
            
            if errors:
                st.error("Please fix the following issues:")
                for error in errors:
                    st.write(f"• {error}")
                return

            # Create initial state
            initial_state = RecipeState(
                ingredients=processed_ingredients,
                appliance=preferences['appliances'][0] if preferences['appliances'] else "Oven",
                available_appliances=preferences['appliances'],
                dietary_restrictions=preferences['dietary_restrictions'] or [],
                cuisine_preference=preferences['cuisine_preference'],
                skill_level=preferences['skill_level'],
                parsed_ingredients=[],
                recipe_suggestions=[],
                selected_recipe={},
                alternative_recipes=[],
                user_selected_alternative=None,
                nutrition_info={},
                shopping_list=[],
                cooking_tips=[],
                final_recipe={},
                online_search_results=[],
                search_enhanced=False,
                search_enhancement_complete=False,
                verification_result=None,
                processing_step="",
                error_message=""
            )
            
            # Log user action - removed for simplicity
            
            # Initialize workflow service
            workflow_service = WorkflowService(
                openai_api_key=api_keys["openai"],
                model_name=LLM_MODEL_NAME,
                tavily_api_key=api_keys["tavily"]
            )
            
            # Execute workflow with progress indicator
            with st.spinner("🍳 Creating your personalized recipe..."):
                result = workflow_service.execute_workflow(initial_state)
            
            # Handle results
            if result.get("error_message"):
                self.recipe_ui.display_error_message(result["error_message"])
                # Show basic fallback message instead of fallback recipe
                st.warning("⚠️ Recipe generation encountered an issue. Please try again with different ingredients.")
            else:
                # Store result in session state
                st.session_state.workflow_result = result
                # Add to recipe history
                if "recipe_history" not in st.session_state:
                    st.session_state.recipe_history = []
                st.session_state.recipe_history.append(result.get("final_recipe", {}))
                if len(st.session_state.recipe_history) > 10:
                    st.session_state.recipe_history.pop(0)
                
                # Display complete recipe
                self.recipe_ui.display_complete_recipe(result)
                
                # Log completion - removed for simplicity
                
        except Exception as e:
            self.recipe_ui.display_error_message(f"An unexpected error occurred: {str(e)}")
            
            # Show simple fallback message
            st.warning("⚠️ Something went wrong. Please try again with different ingredients.")
    
    def run(self) -> None:
        """Run the main application."""
        try:
            # Setup page
            self.setup_page_config()
            
            # Render header
            self.render_header()
            
            # Render API configuration
            self.render_api_configuration()
            
            # Main form
            with st.form("recipe_form"):
                # Ingredient selection
                ingredient_categories = self.render_ingredient_selection()
                
                # Cooking preferences
                preferences = self.render_cooking_preferences()
                
                # Combine all ingredients
                all_ingredients = []
                for category_ingredients in ingredient_categories.values():
                    all_ingredients.extend(category_ingredients)
                
                # Display summary
                self.render_recipe_summary(all_ingredients, preferences)
                
                # Submit button
                submitted = st.form_submit_button(
                    "Generate Recipes", 
                    type="primary", 
                    use_container_width=True,
                    disabled=not st.session_state.get("openai_api_key"),
                    help="OpenAI API key required" if not st.session_state.get("openai_api_key") else None
                )
            
            # Process form submission
            if submitted:
                # Combine ingredients for processing
                all_ingredients = []
                for category_ingredients in ingredient_categories.values():
                    all_ingredients.extend(category_ingredients)
                self.process_recipe_generation(all_ingredients, preferences)
                
        except Exception as e:
            st.error(f"""
            🚨 **Critical Error Occurred**
            
            An unexpected error prevented the application from working properly: {str(e)}
            
            Please try refreshing the page.
            """)
            st.stop()


def main():
    """Main application entry point."""
    app = RecipeAIApp()
    app.run()


if __name__ == "__main__":
    main()
