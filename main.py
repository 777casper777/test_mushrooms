from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Хранилище данных
mushrooms: Dict[int, dict] = {}
baskets: Dict[int, dict] = {}

# Счетчики ID
mushroom_id_counter = 1
basket_id_counter = 1


# Pydantic модели
class Mushroom(BaseModel):
    name: str
    edible: bool
    weight: int  # в граммах
    fresh: bool


class MushroomInDB(Mushroom):
    id: int


class Basket(BaseModel):
    owner: str
    capacity: int  # в граммах


class BasketInDB(Basket):
    id: int
    mushrooms: List[MushroomInDB] = []


# Маршруты для грибов
@app.post("/mushrooms/", response_model=MushroomInDB)
def create_mushroom(mushroom: Mushroom):
    global mushroom_id_counter
    mushroom_id = mushroom_id_counter
    mushroom_id_counter += 1
    mushrooms[mushroom_id] = mushroom.model_dump()
    mushrooms[mushroom_id]["id"] = mushroom_id
    return mushrooms[mushroom_id]


@app.put("/mushrooms/{mushroom_id}", response_model=MushroomInDB)
def update_mushroom(mushroom_id: int, mushroom: Mushroom):
    if mushroom_id not in mushrooms:
        raise HTTPException(status_code=404, detail="Mushroom not found")
    mushrooms[mushroom_id].update(mushroom.model_dump())
    return mushrooms[mushroom_id]


@app.get("/mushrooms/{mushroom_id}", response_model=MushroomInDB)
def get_mushroom(mushroom_id: int):
    if mushroom_id not in mushrooms:
        raise HTTPException(status_code=404, detail="Mushroom not found")
    return mushrooms[mushroom_id]


# Маршруты для корзинок
@app.post("/baskets/", response_model=BasketInDB)
def create_basket(basket: Basket):
    global basket_id_counter
    basket_id = basket_id_counter
    basket_id_counter += 1
    baskets[basket_id] = basket.model_dump()
    baskets[basket_id]["id"] = basket_id
    baskets[basket_id]["mushrooms"] = []
    return baskets[basket_id]


@app.post("/baskets/{basket_id}/add_mushroom/{mushroom_id}")
def add_mushroom_to_basket(basket_id: int, mushroom_id: int):
    if basket_id not in baskets:
        raise HTTPException(status_code=404, detail="Basket not found")
    if mushroom_id not in mushrooms:
        raise HTTPException(status_code=404, detail="Mushroom not found")

    basket = baskets[basket_id]
    mushroom = mushrooms[mushroom_id]

    total_weight = sum(m["weight"] for m in basket["mushrooms"])
    if total_weight + mushroom["weight"] > basket["capacity"]:
        raise HTTPException(status_code=400, detail="Basket capacity exceeded")

    basket["mushrooms"].append(mushroom)
    return {"message": "Mushroom added to basket"}


@app.delete("/baskets/{basket_id}/remove_mushroom/{mushroom_id}")
def remove_mushroom_from_basket(basket_id: int, mushroom_id: int):
    if basket_id not in baskets:
        raise HTTPException(status_code=404, detail="Basket not found")

    basket = baskets[basket_id]
    basket["mushrooms"] = [m for m in basket["mushrooms"] if m["id"] != mushroom_id]
    return {"message": "Mushroom removed from basket"}


@app.get("/baskets/{basket_id}", response_model=BasketInDB)
def get_basket(basket_id: int):
    if basket_id not in baskets:
        raise HTTPException(status_code=404, detail="Basket not found")
    return baskets[basket_id]


# Запуск приложения (для отладки)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
