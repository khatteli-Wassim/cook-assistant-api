from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Literal
from app.graph.workflow import recommendation_graph

router = APIRouter()

class RecommendationRequest(BaseModel):
    mode: Literal["meal_to_ingredients", "ingredients_to_meals", "propose_meal"] = "propose_meal"
    meal: Optional[str] = None
    ingredients: Optional[List[str]] = None

@router.post("/recommend")
async def recommend(request: RecommendationRequest):
    if request.mode == "meal_to_ingredients" and not request.meal:
        raise HTTPException(status_code=400, detail="Provide a meal name for this mode")
    if request.mode == "ingredients_to_meals" and not request.ingredients:
        raise HTTPException(status_code=400, detail="Provide ingredients for this mode")

    initial_state = {
        "mode": request.mode,
        "meal": request.meal,
        "ingredients": request.ingredients,
    }

    result = recommendation_graph.invoke(initial_state)
    return result["response"]