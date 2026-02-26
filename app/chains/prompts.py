from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# Chain 1: meal → ingredients
meal_to_ingredients_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful cooking assistant. Return only valid JSON."),
    ("human", "Give me the ingredients and step-by-step instructions to make: {meal}. "
              "Return JSON with keys: meal, ingredients (list), instructions (list).")
])
meal_to_ingredients_chain = meal_to_ingredients_prompt | llm | JsonOutputParser()

# Chain 2: ingredients → meals
ingredients_to_meals_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful cooking assistant. Return only valid JSON."),
    ("human", "I have these ingredients: {ingredients}. "
              "What meals can I make? Return JSON with keys: meals (list), descriptions (list).")
])
ingredients_to_meals_chain = ingredients_to_meals_prompt | llm | JsonOutputParser()

# Chain 3: propose a random meal 
meals_and_ingredients_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a creative cooking assistant. Return only valid JSON."),
    ("human", "Surprise me! Propose one random meal I can make today. "
              "Return JSON with keys: name (string), ingredients (list), instructions (list).")
])
meals_and_ingredients_chain = meals_and_ingredients_prompt | llm | JsonOutputParser()