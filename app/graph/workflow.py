from langgraph.graph import StateGraph, END
from app.graph.nodes import (
    classify_intent,
    handle_meal_to_ingredients,
    handle_ingredients_to_meals,
    propose_meal,
    format_response
)

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("classify", classify_intent)
    graph.add_node("meal_to_ingredients", handle_meal_to_ingredients)
    graph.add_node("ingredients_to_meals", handle_ingredients_to_meals)
    graph.add_node("propose_meal", propose_meal)
    graph.add_node("format", format_response)

    graph.set_entry_point("classify")

    def route_intent(state: dict) -> str:
        return state["intent"]

    graph.add_conditional_edges(
        "classify",
        route_intent,
        {
            "meal_to_ingredients": "meal_to_ingredients",
            "ingredients_to_meals": "ingredients_to_meals",
            "propose_meal": "propose_meal"
        }
    )

    graph.add_edge("meal_to_ingredients", "format")
    graph.add_edge("ingredients_to_meals", "format")
    graph.add_edge("propose_meal", "format")
    graph.add_edge("format", END)

    return graph.compile()

recommendation_graph = build_graph()