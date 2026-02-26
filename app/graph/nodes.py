from app.chains.prompts import meal_to_ingredients_chain, ingredients_to_meals_chain, meals_and_ingredients_chain

def classify_intent(state: dict) -> dict:
    state["intent"] = state.get("mode", "propose_meal")
    return state

def handle_meal_to_ingredients(state: dict) -> dict:
    result = meal_to_ingredients_chain.invoke({"meal": state["meal"]})
    state["result"] = result
    return state

def handle_ingredients_to_meals(state: dict) -> dict:
    ingredients_str = ", ".join(state["ingredients"])
    result = ingredients_to_meals_chain.invoke({"ingredients": ingredients_str})
    state["result"] = result
    return state

def propose_meal(state: dict) -> dict:
    result = meals_and_ingredients_chain.invoke({})
    state["result"] = result
    return state

def format_response(state: dict) -> dict:
    state["response"] = {
        "intent": state["intent"],
        "data": state.get("result", {})
    }
    return state