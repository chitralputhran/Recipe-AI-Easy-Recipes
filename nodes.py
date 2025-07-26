"""
LangGraph nodes for the recipe generation workflow.
"""

import json

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from tavily import TavilyClient
from models import (
    RecipeState, FinalRecipe
)


class RecipeNodes:
    """Collection of all nodes for the Recipe AI LangGraph workflow."""
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4", tavily_api_key: str = None):
        self.llm = ChatOpenAI(model=model_name, temperature=0.1, openai_api_key=openai_api_key, max_tokens=4000, timeout=120.0, max_retries=3)
        self.creative_llm = ChatOpenAI(model=model_name, temperature=0.7, openai_api_key=openai_api_key, max_tokens=4000, timeout=120.0, max_retries=3)
        self.tavily_api_key = tavily_api_key
        self.tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None
    
    def cooking_tips_node(self, state: RecipeState) -> RecipeState:
        """Generate cooking tips based on appliance and skill level."""
        # Processing cooking tips node
        
        # Update processing step
        state["processing_step"] = "cooking_tips"
        
        try:
            prompt = ChatPromptTemplate.from_template(
                """Generate helpful cooking tips for:
                Recipe: {recipe}
                Available appliances: {appliance}
                Skill level: {skill_level}
                
                Focus on:
                - Technique tips specific to the available appliances
                - How to use multiple appliances effectively if applicable
                - Timing and temperature guidance
                - Common mistakes to avoid
                - Safety considerations
                - Tips for the user's skill level
                
                Provide 5-8 practical tips as a numbered list.
                """
            )
            
            chain = prompt | self.llm
            response = chain.invoke({
                "recipe": state["selected_recipe"],
                "appliance": f"{state['appliance']} (Available: {', '.join(state.get('available_appliances', [state['appliance']]))})",
                "skill_level": state["skill_level"]
            })
            
            # Parse tips into a list
            tips = [tip.strip() for tip in response.content.split('\n') if tip.strip()]
            state["cooking_tips"] = tips
            state["processing_step"] = "cooking_tips_complete"
            
        except Exception as e:
            # Error in cooking tips generator
            state["cooking_tips"] = [
                "Read through the entire recipe before starting",
                "Prep all ingredients before cooking",
                "Keep a clean workspace",
                "Taste as you go and adjust seasoning"
            ]
        
        return state
    
    def final_recipe_compiler_node(self, state: RecipeState) -> RecipeState:
        """Compile everything into final detailed recipe."""
        # Processing final recipe compiler node
        
        # Update processing step
        state["processing_step"] = "final_recipe_compilation"
        
        try:
            parser = PydanticOutputParser(pydantic_object=FinalRecipe)
            
            prompt = ChatPromptTemplate.from_template(
                """Create a complete, detailed recipe using:
                Selected recipe: {selected_recipe}
                Available ingredients: {ingredients}
                Nutrition info: {nutrition_info}
                Cooking tips: {cooking_tips}
                Available appliances: {appliance}
                
                Create a comprehensive recipe with:
                - Clear, step-by-step instructions
                - Precise ingredient measurements
                - Detailed cooking techniques using available appliances
                - Instructions for using multiple appliances if beneficial
                - Storage instructions
                - Fun emoji representation
                - Recipe variations
                
                IMPORTANT: For the 'appliance_used' field, provide ONLY the primary appliance as a single string (e.g., "Oven" or "Stovetop"), not a list.
                
                Make it engaging and easy to follow!
                
                {format_instructions}
                """
            )
            
            chain = prompt | self.creative_llm | parser
            final_recipe = chain.invoke({
                "selected_recipe": state["selected_recipe"],
                "ingredients": state["parsed_ingredients"],
                "nutrition_info": state["nutrition_info"],
                "cooking_tips": state["cooking_tips"],
                "appliance": f"{state['appliance']} (Available: {', '.join(state.get('available_appliances', [state['appliance']]))})",
                "format_instructions": parser.get_format_instructions()
            })
            
            # Convert to dict and fix appliance_used field if it's a list
            final_recipe_dict = final_recipe.dict()
            if isinstance(final_recipe_dict.get("appliance_used"), list):
                # Take the first appliance if it's a list
                final_recipe_dict["appliance_used"] = final_recipe_dict["appliance_used"][0]
            
            state["final_recipe"] = final_recipe_dict
            state["processing_step"] = "final_recipe_complete"
            
        except Exception as e:
            # Error in final recipe compiler
            # Create fallback recipe with proper appliance field
            primary_appliance = state.get('appliance', 'Stovetop')
            if isinstance(primary_appliance, list):
                primary_appliance = primary_appliance[0] if primary_appliance else 'Stovetop'
            
            state["final_recipe"] = {
                "name": state["selected_recipe"].get("name", "Custom Recipe"),
                "description": state["selected_recipe"].get("description", "A delicious homemade dish"),
                "ingredients": [f"• {ing['name']}" for ing in state["parsed_ingredients"]],
                "instructions": [
                    "1. Prepare all ingredients",
                    "2. Follow cooking method for your appliance",
                    "3. Cook until done",
                    "4. Serve and enjoy!"
                ],
                "prep_time": state["selected_recipe"].get("prep_time", 15),
                "cook_time": state["selected_recipe"].get("cook_time", 30),
                "total_time": state["selected_recipe"].get("prep_time", 15) + state["selected_recipe"].get("cook_time", 30),
                "servings": state["selected_recipe"].get("servings", 4),
                "difficulty": state["selected_recipe"].get("difficulty", "Medium"),
                "cuisine_type": state["selected_recipe"].get("cuisine_type", "International"),
                "appliance_used": primary_appliance,
                "nutrition": state["nutrition_info"],
                "tips": state["cooking_tips"],
                "variations": ["Try different seasonings", "Add more vegetables"],
                "storage_instructions": "Store in refrigerator for up to 3 days",
                "emoji_representation": "🍽️✨"
            }
        
        return state
    
    def online_search_node(self, state: RecipeState) -> RecipeState:
        """Search online for additional recipe information and cooking tips."""
        # Processing online search node
        
        # Update processing step
        state["processing_step"] = "online_search"
        
        if not self.tavily_client:
            # Tavily not available, skipping online search
            state["online_search_results"] = []
            state["search_enhanced"] = False
            return state
        
        try:
            # Create search queries based on the recipe context
            selected_recipe = state.get("selected_recipe", {})
            ingredients = state.get("ingredients", [])
            cuisine_preference = state.get("cuisine_preference", "Any")
            
            search_queries = []
            
            # Search for recipe-specific information
            if selected_recipe.get("name"):
                search_queries.append(f"{selected_recipe['name']} recipe cooking tips best practices")
            
            # Search for ingredient-specific techniques
            if ingredients:
                main_ingredients = ingredients[:3]  # Use first 3 ingredients
                ingredient_query = " ".join(main_ingredients)
                search_queries.append(f"cooking techniques {ingredient_query} {cuisine_preference} cuisine")
            
            # Search for appliance-specific tips
            appliances = state.get("available_appliances", [])
            if appliances:
                appliance_query = " ".join(appliances)
                search_queries.append(f"cooking tips {appliance_query} techniques professional chef")
            
            # Perform searches
            search_results = []
            for query in search_queries[:2]:  # Limit to 2 searches to avoid rate limits
                try:
                    # Searching for query
                    response = self.tavily_client.search(query, max_results=2)
                    
                    if response and "results" in response:
                        for result in response["results"]:
                            search_results.append({
                                "title": result.get("title", ""),
                                "content": result.get("content", ""),
                                "url": result.get("url", ""),
                                "query": query
                            })
                    
                except Exception as search_error:
                    error_str = str(search_error).lower()
                    if "unauthorized" in error_str or "api key" in error_str:
                        # Tavily API key issue - continuing without online search
                        # Stop trying more searches if API key is the issue
                        break
                    else:
                        # Error searching - continuing with next query
                        pass
                    continue
            
            state["online_search_results"] = search_results
            state["search_enhanced"] = len(search_results) > 0
            state["processing_step"] = "online_search_complete"
            
            # Online search completed
            
        except Exception as e:
            # Error in online search
            state["online_search_results"] = []
            state["search_enhanced"] = False
            state["error_message"] = f"Online search error: {str(e)}"
        
        return state
    
    def enhance_with_search_node(self, state: RecipeState) -> RecipeState:
        """Enhance recipe suggestions with online search results."""
        # Processing search enhancement node
        
        # Update processing step
        state["processing_step"] = "search_enhancement"
        
        # Check if enhancement has already been done
        if state.get("search_enhancement_complete", False):
            # Search enhancement already completed, skipping
            return state
        
        if not state.get("search_enhanced", False) or not state.get("online_search_results"):
            # No search results available for enhancement
            return state
        
        try:
            # Use search results to enhance cooking tips
            search_results = state.get("online_search_results", [])
            search_content = []
            
            for result in search_results:
                if result.get("content"):
                    search_content.append(f"Source: {result.get('title', 'Unknown')}\n{result['content']}")
            
            if search_content:
                # Create enhanced cooking tips using search results
                prompt = ChatPromptTemplate.from_template(
                    """Based on the following online search results about cooking techniques and tips:

{search_content}

And the current recipe context:
- Recipe: {recipe_name}
- Ingredients: {ingredients}
- Appliances: {appliances}
- Current tips: {current_tips}

Generate 3-5 enhanced cooking tips that incorporate insights from the search results.
Focus on:
1. Professional cooking techniques
2. Ingredient-specific handling tips
3. Appliance optimization
4. Common mistakes to avoid
5. Quality improvements

Format as a JSON list of strings, each tip should be concise and actionable.
"""
                )
                
                current_tips = state.get("cooking_tips", [])
                selected_recipe = state.get("selected_recipe", {})
                
                response = self.llm.invoke(prompt.format(
                    search_content="\n\n".join(search_content[:3]),  # Limit content to avoid token limits
                    recipe_name=selected_recipe.get("name", "Unknown Recipe"),
                    ingredients=", ".join(state.get("ingredients", [])),
                    appliances=", ".join(state.get("available_appliances", [])),
                    current_tips=", ".join(current_tips) if current_tips else "None yet"
                ))
                
                try:
                    # Get the content from the response properly
                    response_content = response.content if hasattr(response, 'content') else str(response)
                    enhanced_tips = json.loads(response_content)
                    if isinstance(enhanced_tips, list):
                        # Combine original tips with enhanced tips
                        all_tips = current_tips + enhanced_tips
                        # Remove duplicates while preserving order
                        unique_tips = []
                        seen = set()
                        for tip in all_tips:
                            if isinstance(tip, str) and tip not in seen:
                                unique_tips.append(tip)
                                seen.add(tip)
                        
                        state["cooking_tips"] = unique_tips[:8]  # Limit to 8 tips
                        state["processing_step"] = "search_enhancement_complete"
                        state["search_enhancement_complete"] = True  # Add completion flag
                        # Enhanced cooking tips with new tips
                    
                except json.JSONDecodeError as json_error:
                    # Failed to parse enhanced tips JSON
                    pass
                except Exception as parse_error:
                    # Error processing enhanced tips
                    pass
                
        except Exception as e:
            # Error in search enhancement - don't modify state
            pass
        
        return state
    
    def instruction_completion_node(self, state: RecipeState) -> RecipeState:
        """Ensure instructions are complete and detailed - fallback for incomplete instructions."""
        # Processing instruction completion node
        
        state["processing_step"] = "instruction_completion"
        
        try:
            recipe = state.get("final_recipe", {})
            if not recipe:
                # No recipe to complete instructions
                return state
            
            instructions = recipe.get("instructions", [])
            ingredients = recipe.get("ingredients", [])
            
            # Check if instructions seem incomplete (too few steps, very short instructions, etc.)
            if not instructions or len(instructions) < 3:
                needs_completion = True
                # Instructions seem incomplete: only few steps
            else:
                # Check if any instruction is too short (likely truncated)
                avg_length = sum(len(inst) for inst in instructions) / len(instructions)
                needs_completion = avg_length < 30  # If average instruction is very short
                if needs_completion:
                    # Instructions seem truncated: average length too short
                    pass
            
            if needs_completion:
                completion_prompt = f"""
                The following recipe has incomplete or truncated instructions. Please provide COMPLETE, detailed step-by-step instructions.
                
                Recipe: {recipe.get('name', 'Unknown')}
                Ingredients: {', '.join(ingredients)}
                Current Instructions: {instructions}
                
                Please provide complete, detailed cooking instructions in JSON format:
                {{
                    "complete_instructions": [
                        "Step 1: Detailed preparation step with timing",
                        "Step 2: Detailed cooking step with temperature and timing", 
                        "Step 3: Continue with ALL necessary steps",
                        "... include every step needed from start to finish"
                    ]
                }}
                
                Make sure to include:
                - All preparation steps (washing, chopping, seasoning)
                - Proper cooking steps with times and temperatures
                - Any resting, cooling, or finishing steps
                - Serving suggestions
                
                Focus especially on ensuring ingredients like lentils, grains, and proteins are properly cooked.
                """
                
                response = self.creative_llm.invoke([
                    {"role": "system", "content": "You are a professional chef. Provide complete, detailed cooking instructions. Never truncate or abbreviate steps."},
                    {"role": "user", "content": completion_prompt}
                ])
                
                try:
                    completion_result = json.loads(response.content)
                    complete_instructions = completion_result.get("complete_instructions", [])
                    
                    if complete_instructions and len(complete_instructions) > len(instructions):
                        # Update recipe with complete instructions
                        recipe["instructions"] = complete_instructions
                        state["final_recipe"] = recipe
                        state["selected_recipe"] = recipe
                        
                        # Instructions completed successfully
                    
                except json.JSONDecodeError:
                    # Failed to parse instruction completion response
                    pass
            
            state["processing_step"] = "instruction_completion_complete"
            
        except Exception as e:
            # Error in instruction completion
            pass
        
        return state
