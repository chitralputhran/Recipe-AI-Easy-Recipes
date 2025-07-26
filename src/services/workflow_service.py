"""
Workflow Service for managing LangGraph workflows.
"""

from typing import Any
from langgraph.graph import StateGraph, END
from models import RecipeState
from nodes import RecipeNodes
from .llm_service import LLMService
from .recipe_service import RecipeService


class WorkflowService:
    """Service for managing workflow execution."""
    
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4", tavily_api_key: str = None):
        """Initialize workflow service."""
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.tavily_api_key = tavily_api_key
        self.tavily_enabled = tavily_api_key is not None
        
        # Initialize services
        self.llm_service = LLMService(openai_api_key, model_name)
        self.recipe_service = RecipeService(self.llm_service)
        self.nodes = RecipeNodes(openai_api_key, model_name, tavily_api_key)
        
        self.graph = None
    
    def combined_recipe_generation_node(self, state: RecipeState) -> RecipeState:
        """Combined node that generates recipe, nutrition info, and shopping list."""
        try:
            # Processing combined recipe generation
            
            # Parse ingredients
            ingredients_list = state.get('ingredients', [])
            state["parsed_ingredients"] = self.recipe_service.parse_ingredients(ingredients_list)
            # Parsed ingredients
            
            # Generate combined recipe data
            try:
                response_data = self.recipe_service.generate_combined_recipe(state)
                
                # Validate and update state
                if self.recipe_service.validate_recipe_data(response_data):
                    state["selected_recipe"] = response_data["recipe"]
                    state["nutrition_info"] = response_data["nutrition"]
                    state["shopping_list"] = response_data["shopping_list"]
                    state["final_recipe"] = response_data["recipe"]
                else:
                    raise ValueError("Invalid recipe data structure")
                    
            except Exception as e:
                # Combined generation failed, using fallback
                # Use fallback recipe generation
                fallback_data = self.recipe_service.create_fallback_recipe(
                    ingredients_list, 
                    state.get('appliance', 'oven')
                )
                state["selected_recipe"] = fallback_data["recipe"]
                state["nutrition_info"] = fallback_data["nutrition"]
                state["shopping_list"] = fallback_data["shopping_list"]
                state["final_recipe"] = fallback_data["recipe"]
                
        except Exception as e:
            raise Exception(f"Error in combined recipe generation: {e}")
            
        return state
    
    def enhanced_cooking_tips_node(self, state: RecipeState) -> RecipeState:
        """Enhanced cooking tips with optional search and final compilation."""
        try:
            # Processing enhanced cooking tips
            
            # Online search if available
            if self.tavily_enabled:
                state = self.nodes.online_search_node(state)
                if state.get("online_search_results"):
                    state = self.nodes.enhance_with_search_node(state)
            
            # Generate cooking tips
            state = self.nodes.cooking_tips_node(state)
            
            # Final recipe compilation
            state = self.nodes.final_recipe_compiler_node(state)
            
            # Enhanced cooking tips completed
            
        except Exception as e:
            raise Exception(f"Error in enhanced cooking tips: {e}")
            # Fallback - use selected recipe as final recipe
            state["final_recipe"] = state.get("selected_recipe", {})
            
        return state
    
    def create_workflow_graph(self) -> StateGraph:
        """Create the workflow graph."""
        workflow = StateGraph(RecipeState)
        
        # Add nodes
        workflow.add_node("combined_recipe_generation", self.combined_recipe_generation_node)
        
        if self.tavily_enabled:
            workflow.add_node("enhanced_cooking_tips", self.enhanced_cooking_tips_node)
            workflow.add_node("instruction_completion", self.nodes.instruction_completion_node)
            
            # Enhanced workflow
            workflow.add_edge("combined_recipe_generation", "enhanced_cooking_tips")
            workflow.add_edge("enhanced_cooking_tips", "instruction_completion")
            workflow.add_edge("instruction_completion", END)
        else:
            workflow.add_node("instruction_completion", self.nodes.instruction_completion_node)
            
            # Simple workflow
            workflow.add_edge("combined_recipe_generation", "instruction_completion")
            workflow.add_edge("instruction_completion", END)
        
        workflow.set_entry_point("combined_recipe_generation")
        return workflow
    
    def compile_workflow(self) -> Any:
        """Compile the workflow graph."""
        workflow = self.create_workflow_graph()
        self.graph = workflow.compile()
        return self.graph
    
    def execute_workflow(self, initial_state: RecipeState) -> RecipeState:
        """Execute the complete workflow."""
        try:
            workflow_type = "enhanced" if self.tavily_enabled else "simplified"
            # Starting workflow
            
            graph = self.compile_workflow()
            result = graph.invoke(initial_state)
            
            # Workflow completed successfully
            return result
            
        except Exception as e:
            initial_state["error_message"] = f"Workflow failed: {str(e)}"
            return initial_state
