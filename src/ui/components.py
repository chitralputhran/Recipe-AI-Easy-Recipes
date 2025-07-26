"""
UI Components for Recipe AI - Smart Recipe Generation.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
import re


class RecipeUI:
    """UI components for recipe generation."""
    
    # Output formatting and display methods (moved from OutputHandler)
    def display_recipe_header(self, recipe: Dict[str, Any]) -> None:
        """Display recipe header with name and emoji."""
        if not recipe:
            return
        
        recipe_name = recipe.get("name", "Your Recipe")
        emoji = recipe.get("emoji_representation", "🍽️")
        description = recipe.get("description", "")
        
        st.divider()
        st.subheader(f"{emoji} {recipe_name}")
        
        # Display description as simple text
        if description:
            st.write(description)
    
    def display_recipe_details(self, recipe: Dict[str, Any]) -> None:
        """Display recipe timing and basic details in table format."""
        if not recipe:
            return
        
        # Create recipe details table
        details_data = []
        
        if recipe.get("prep_time"):
            details_data.append({"Detail": "⏱️ Prep Time", "Value": f"{recipe.get('prep_time', 0)} min"})
        if recipe.get("cook_time"):
            details_data.append({"Detail": "🔥 Cook Time", "Value": f"{recipe.get('cook_time', 0)} min"})
        if recipe.get("servings"):
            details_data.append({"Detail": "👥 Servings", "Value": str(recipe.get('servings', 4))})
        if recipe.get("difficulty"):
            details_data.append({"Detail": "📊 Difficulty", "Value": recipe.get('difficulty', 'Medium')})
        
        if details_data:
            details_df = pd.DataFrame(details_data)
            st.dataframe(
                details_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Detail": st.column_config.TextColumn("Detail", width="medium"),
                    "Value": st.column_config.TextColumn("Value", width="small")
                }
            )
    
    def display_ingredients_list(self, recipe: Dict[str, Any]) -> None:
        """Display ingredients in a formatted table."""
        if not recipe or "ingredients" not in recipe:
            return
        
        st.subheader("📋 Ingredients")
        ingredients = recipe["ingredients"]
        
        if isinstance(ingredients, list) and ingredients:
            # Create ingredients table
            ingredients_data = []
            for ingredient in ingredients:
                # Clean up ingredient text (remove bullet points if present)
                clean_ingredient = ingredient.replace("• ", "").strip()
                ingredients_data.append({"Ingredient": clean_ingredient})
            
            if ingredients_data:
                ingredients_df = pd.DataFrame(ingredients_data)
                st.dataframe(
                    ingredients_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "Ingredient": st.column_config.TextColumn("Ingredient", width="large")
                    }
                )
        else:
            st.write("No ingredients listed")
    
    def display_instructions(self, recipe: Dict[str, Any]) -> None:
        """Display cooking instructions as a simple numbered list."""
        if not recipe or "instructions" not in recipe:
            return
        
        st.subheader("👨‍🍳 Instructions")
        instructions = recipe["instructions"]
        
        if isinstance(instructions, list) and instructions:
            for i, instruction in enumerate(instructions, 1):
                # Clean instruction text by removing "Step X:" prefix if present
                clean_instruction = instruction
                if clean_instruction.lower().startswith(f"step {i}:"):
                    clean_instruction = clean_instruction[len(f"step {i}:"):].strip()
                elif clean_instruction.lower().startswith("step"):
                    # Handle various step formats like "Step 1:", "Step1:", etc.
                    clean_instruction = re.sub(r'^step\s*\d+\s*:\s*', '', clean_instruction, flags=re.IGNORECASE)
                
                st.write(f"{i}. {clean_instruction}")
        else:
            st.write("No instructions provided")
    
    def display_tips_and_variations(self, recipe: Dict[str, Any]) -> None:
        """Display cooking tips and variations in expandable sections."""
        if not recipe:
            return
        
        # Cooking Tips in expandable section
        if "tips" in recipe and recipe["tips"]:
            with st.expander("💡 Cooking Tips"):
                for tip in recipe["tips"]:
                    st.write(f"• {tip}")
        
        # Variations in expandable section
        if "variations" in recipe and recipe["variations"]:
            with st.expander("🔄 Variations"):
                for variation in recipe["variations"]:
                    st.write(f"• {variation}")
    
    def display_storage_info(self, recipe: Dict[str, Any]) -> None:
        """Display storage instructions in an expandable section."""
        if not recipe or "storage_instructions" not in recipe:
            return
        
        storage = recipe["storage_instructions"]
        if storage:
            with st.expander("📦 Storage"):
                st.info(storage)
    
    def display_nutrition_info(self, nutrition: Dict[str, Any]) -> None:
        """Display nutrition information in a formatted table."""
        if not nutrition:
            return
        
        st.subheader("🥗 Nutrition Information (per serving)")
        
        # Create nutrition table data
        nutrition_data = []
        
        # Add main nutrition values
        if nutrition.get('calories_per_serving'):
            nutrition_data.append({"Nutrient": "🔥 Calories", "Amount": f"{nutrition.get('calories_per_serving', 0)}"})
        if nutrition.get('protein_g'):
            nutrition_data.append({"Nutrient": "🥩 Protein", "Amount": f"{nutrition.get('protein_g', 0):.1f}g"})
        if nutrition.get('carbs_g'):
            nutrition_data.append({"Nutrient": "🌾 Carbs", "Amount": f"{nutrition.get('carbs_g', 0):.1f}g"})
        if nutrition.get('fat_g'):
            nutrition_data.append({"Nutrient": "🥑 Fat", "Amount": f"{nutrition.get('fat_g', 0):.1f}g"})
        if nutrition.get('fiber_g'):
            nutrition_data.append({"Nutrient": "Fiber", "Amount": f"{nutrition.get('fiber_g', 0):.1f}g"})
        if nutrition.get('sodium_mg'):
            nutrition_data.append({"Nutrient": "Sodium", "Amount": f"{nutrition.get('sodium_mg', 0):.0f}mg"})
        if nutrition.get('sugar_g'):
            nutrition_data.append({"Nutrient": "Sugar", "Amount": f"{nutrition.get('sugar_g', 0):.1f}g"})
        
        # Display nutrition table
        if nutrition_data:
            nutrition_df = pd.DataFrame(nutrition_data)
            st.dataframe(
                nutrition_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Nutrient": st.column_config.TextColumn("Nutrient", width="medium"),
                    "Amount": st.column_config.TextColumn("Amount", width="small")
                }
            )
        
        # Key nutrients and health benefits in expandable sections
        col1, col2 = st.columns(2)
        
        with col1:
            key_nutrients = nutrition.get('key_nutrients', [])
            if key_nutrients:
                with st.expander("🌟 Key Nutrients"):
                    for nutrient in key_nutrients:
                        st.write(f"• {nutrient}")
        
        with col2:
            health_benefits = nutrition.get('health_benefits', [])
            if health_benefits:
                with st.expander("🌟 Health Benefits"):
                    for benefit in health_benefits:
                        st.write(f"• {benefit}")
    
    def display_shopping_list(self, shopping_list: List[str]) -> None:
        """Display shopping list in a formatted table."""
        if not shopping_list:
            return
        
        st.subheader("🛒 Shopping List")
        
        # Create DataFrame for better display
        shopping_df = pd.DataFrame({
            "Items to Buy": shopping_list
        })
        
        st.dataframe(
            shopping_df, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "Items to Buy": st.column_config.TextColumn(width="large")
            }
        )
        
        st.caption(f"📝 Total items needed: {len(shopping_list)}")
    
    def display_complete_recipe(self, result: Dict[str, Any]) -> None:
        """Display the complete recipe with all sections."""
        if not result:
            st.error("No recipe data to display")
            return
        
        final_recipe = result.get("final_recipe", {})
        nutrition_info = result.get("nutrition_info", {})
        shopping_list = result.get("shopping_list", [])
        
        # Recipe header
        self.display_recipe_header(final_recipe)
        
        # Recipe details
        self.display_recipe_details(final_recipe)
        
        # Shopping list (moved to top after recipe details)
        if shopping_list:
            self.display_shopping_list(shopping_list)
        
        # Nutrition information (moved to top)
        if nutrition_info:
            self.display_nutrition_info(nutrition_info)
        
        # Main recipe content
        self.display_ingredients_list(final_recipe)
        self.display_instructions(final_recipe)
        
        # Additional information
        self.display_tips_and_variations(final_recipe)
        self.display_storage_info(final_recipe)
    
    def display_error_message(self, error: str) -> None:
        """Display error message with consistent formatting."""
        st.error(f"❌ {error}")
    
    def display_success_message(self, message: str) -> None:
        """Display success message with consistent formatting."""
        st.success(f"✅ {message}")
    
    def display_info_message(self, message: str) -> None:
        """Display info message with consistent formatting."""
        st.info(f"ℹ️ {message}")
    
    def display_warning_message(self, message: str) -> None:
        """Display warning message with consistent formatting."""
        st.warning(f"⚠️ {message}")
