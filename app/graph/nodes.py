from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, streaming=True)
search_tool = TavilySearchResults(max_results=5)

# ─── Router Node ────────────────────────────────────────────────────────────

def route_message(state: dict) -> dict:
    """Decide which agent(s) to invoke based on the user message."""
    message = state["message"].lower()

    agents = []

    nutrition_keywords = [
        "calorie", "calories", "protein", "carb", "fiber", "fat", "macro",
        "nutrition", "nutritional", "healthy", "diet", "vitamin", "mineral",
        "weight", "lose weight", "gain muscle", "keto", "vegan", "health"
    ]

    grocery_keywords = [
        "buy", "shop", "store", "market", "price", "cheap", "cost", "where to find",
        "grocery", "groceries", "supermarket", "purchase", "ingredient list", "shopping list"
    ]

    if any(k in message for k in nutrition_keywords):
        agents.append("nutritionist")

    if any(k in message for k in grocery_keywords):
        agents.append("groceries")

    if not agents:
        agents.append("chef")

    state["agents"] = agents
    return state


# ─── Chef Agent ──────────────────────────────────────────────────────────────

def chef_agent(state: dict) -> dict:
    """Handles cooking questions, recipes, meal suggestions."""
    system = SystemMessage(content="""IMPORTANT: Always respond in English only, no matter what language the user writes in.

You are Chef AI, a world-class cooking assistant.
You help with:
- Recipes and step-by-step cooking instructions
- Meal suggestions based on available ingredients
- Random meal proposals when asked
- General cooking advice, techniques, and tips
- Food culture and cuisine knowledge

Be warm, conversational, and encouraging. Format recipes clearly with ingredients and steps.
Always respond in English only.
If the user just says hello or starts a conversation, introduce yourself briefly and ask how you can help.""")

    messages = [system] + state["history"] + [HumanMessage(content=state["message"])]
    response = llm.invoke(messages)
    state["chef_response"] = response.content
    return state


# ─── Nutritionist Agent ──────────────────────────────────────────────────────

def nutritionist_agent(state: dict) -> dict:
    """Handles nutrition, calories, macros, healthy eating."""
    system = SystemMessage(content="""IMPORTANT: Always respond in English only, no matter what language the user writes in.

You are a certified nutritionist AI assistant.
You provide detailed nutritional information including:
- Calories per serving
- Macronutrients: protein, carbohydrates, fats, fiber
- Micronutrients: vitamins and minerals when relevant
- Healthiness assessment and dietary notes
- Suggestions for healthier alternatives or modifications
- Dietary compatibility (keto, vegan, gluten-free, etc.)

Always be accurate, clear, and helpful. Format nutritional data in a readable way.
Always respond in English only.""")

    messages = [system] + state["history"] + [HumanMessage(content=state["message"])]
    response = llm.invoke(messages)
    state["nutrition_response"] = response.content
    return state


# ─── Groceries Agent ─────────────────────────────────────────────────────────

def groceries_agent(state: dict) -> dict:
    """Extracts ingredients, searches for prices and where to buy them."""

    # Step 1: Extract ingredients from conversation
    extract_system = SystemMessage(content="""IMPORTANT: Always respond in English only, no matter what language the user writes in.
Extract all food ingredients mentioned in the user message.
Return ONLY a plain comma-separated list of ingredients, nothing else.
Example: chicken breast, olive oil, garlic, tomatoes""")

    extract_messages = [extract_system, HumanMessage(content=state["message"])]
    extracted = llm.invoke(extract_messages)
    ingredients = [i.strip() for i in extracted.content.split(",") if i.strip()]

    if not ingredients:
        state["grocery_response"] = "I couldn't find any specific ingredients to search for. Could you list what you need?"
        return state

    # Step 2: Get location from state (user provided it)
    location = state.get("location", "")
    if not location:
        state["grocery_response"] = "📍 To find the best grocery prices near you, could you tell me your city or location?"
        state["needs_location"] = True
        return state

    # Step 3: Search for each ingredient
    search_results = []
    for ingredient in ingredients[:5]:  # limit to 5 to avoid rate limiting
        try:
            results = search_tool.invoke(
                f"where to buy {ingredient} cheapest price best quality {location} supermarket grocery store"
            )
            if results:
                search_results.append({
                    "ingredient": ingredient,
                    "results": results[:2]
                })
        except Exception:
            pass

    # Step 4: Synthesize results with LLM
    synthesis_system = SystemMessage(content=f"""You are a smart grocery shopping assistant.
Based on the search results below, give the user practical advice on:
- Where to find each ingredient in or near {location}
- Which stores offer the best price/quality ratio
- Any shopping tips

Be concise and practical. Format as a clear shopping guide.
Always respond in English only.

Search results:
{search_results}""")

    synthesis_messages = [synthesis_system, HumanMessage(content=f"Help me find these ingredients: {', '.join(ingredients)}")]
    response = llm.invoke(synthesis_messages)
    state["grocery_response"] = f"🛒 **Shopping Guide for {location}**\n\n" + response.content
    state["extracted_ingredients"] = ingredients
    return state


# ─── Response Merger ─────────────────────────────────────────────────────────

def merge_responses(state: dict) -> dict:
    """Combine all agent responses into one final response."""
    parts = []

    if "chef_response" in state:
        parts.append(state["chef_response"])

    if "nutrition_response" in state:
        if parts:
            parts.append("\n---\n🥗 **Nutritional Information:**\n" + state["nutrition_response"])
        else:
            parts.append(state["nutrition_response"])

    if "grocery_response" in state:
        if parts:
            parts.append("\n---\n" + state["grocery_response"])
        else:
            parts.append(state["grocery_response"])

    state["final_response"] = "\n".join(parts) if parts else "I'm not sure how to help with that. Could you rephrase?"
    return state