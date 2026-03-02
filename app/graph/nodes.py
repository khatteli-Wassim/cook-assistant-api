from app.chains.prompts import meal_to_ingredients_chain, ingredients_to_meals_chain

# Node 1: classify what mode the user wants
def classify_intent(state: dict) -> dict:
    if state.get("meal"):
        state["intent"] = "meal_to_ingredients"
    elif state.get("ingredients"):
        state["intent"] = "ingredients_to_meals"
    else:
        state["intent"] = "unknown"
    return state

# Node 2: handle meal → ingredients
def handle_meal_to_ingredients(state: dict) -> dict:
    result = meal_to_ingredients_chain.invoke({"meal": state["meal"]})
    state["result"] = result
    return state

# Node 3: handle ingredients → meals
def handle_ingredients_to_meals(state: dict) -> dict:
    ingredients_str = ", ".join(state["ingredients"])
    result = ingredients_to_meals_chain.invoke({"ingredients": ingredients_str})
    state["result"] = result
    return state

# Node 4: format the final response
def format_response(state: dict) -> dict:
    state["response"] = {
        "intent": state["intent"],
        "data": state.get("result", {})
    }
    return state