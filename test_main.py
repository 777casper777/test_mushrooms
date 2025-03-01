import pytest
from fastapi.testclient import TestClient
from main import app, mushrooms, baskets


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_create_mushroom(client):
    print("Testing mushroom creation...")
    response = client.post(
        "/mushrooms/",
        json={
            "name": "Champignon",
            "edible": True,
            "weight": 200,
            "fresh": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    print(f"Mushroom created: {data}")
    assert "id" in data
    assert data["name"] == "Champignon"
    assert data["weight"] == 200
    assert data["edible"] is True


def test_update_mushroom(client):
    print("Testing mushroom update...")
    # Сначала создаем гриб
    response = client.post(
        "/mushrooms/",
        json={
            "name": "Oyster Mushroom",
            "edible": True,
            "weight": 150,
            "fresh": True,
        },
    )
    mushroom_id = response.json()["id"]
    print(f"Created mushroom with ID: {mushroom_id}")

    # Теперь обновим его
    response = client.put(
        f"/mushrooms/{mushroom_id}",
        json={
            "name": "Oyster Mushroom Updated",
            "edible": False,
            "weight": 160,
            "fresh": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    print(f"Mushroom updated: {data}")
    assert data["name"] == "Oyster Mushroom Updated"
    assert data["weight"] == 160
    assert data["edible"] is False


def test_get_mushroom(client):
    print("Testing getting mushroom...")
    # Создадим гриб
    response = client.post(
        "/mushrooms/",
        json={
            "name": "Shiitake",
            "edible": True,
            "weight": 180,
            "fresh": True,
        },
    )
    mushroom_id = response.json()["id"]
    print(f"Created mushroom with ID: {mushroom_id}")

    # Получим его
    response = client.get(f"/mushrooms/{mushroom_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"Mushroom details: {data}")
    assert data["name"] == "Shiitake"
    assert data["weight"] == 180


def test_create_basket(client):
    print("Testing basket creation...")
    response = client.post(
        "/baskets/",
        json={
            "owner": "John Doe",
            "capacity": 1000,
        },
    )
    assert response.status_code == 200
    data = response.json()
    print(f"Basket created: {data}")
    assert "id" in data
    assert data["owner"] == "John Doe"
    assert data["capacity"] == 1000


def test_add_mushroom_to_basket(client):
    print("Testing adding mushroom to basket...")
    # Создадим корзину и гриб
    basket_response = client.post(
        "/baskets/",
        json={
            "owner": "John Doe",
            "capacity": 1000,
        },
    )
    basket_id = basket_response.json()["id"]
    print(f"Created basket with ID: {basket_id}")

    mushroom_response = client.post(
        "/mushrooms/",
        json={
            "name": "Portobello",
            "edible": True,
            "weight": 150,
            "fresh": True,
        },
    )
    mushroom_id = mushroom_response.json()["id"]
    print(f"Created mushroom with ID: {mushroom_id}")

    # Добавим гриб в корзину
    response = client.post(f"/baskets/{basket_id}/add_mushroom/{mushroom_id}")
    assert response.status_code == 200
    print("Mushroom added to basket successfully.")
    assert response.json() == {"message": "Mushroom added to basket"}

    # Проверим корзину
    basket_response = client.get(f"/baskets/{basket_id}")
    basket_data = basket_response.json()
    print(f"Basket details: {basket_data}")
    assert len(basket_data["mushrooms"]) == 1
    assert basket_data["mushrooms"][0]["name"] == "Portobello"


def test_add_mushroom_to_basket_capacity_exceeded(client):
    print("Testing adding mushroom to basket with exceeded capacity...")
    # Создадим корзину с малым объемом и гриб
    basket_response = client.post(
        "/baskets/",
        json={
            "owner": "John Doe",
            "capacity": 100,
        },
    )
    basket_id = basket_response.json()["id"]
    print(f"Created basket with ID: {basket_id}")

    mushroom_response = client.post(
        "/mushrooms/",
        json={
            "name": "Chanterelle",
            "edible": True,
            "weight": 150,
            "fresh": True,
        },
    )
    mushroom_id = mushroom_response.json()["id"]
    print(f"Created mushroom with ID: {mushroom_id}")

    # Попробуем добавить гриб в корзину
    response = client.post(f"/baskets/{basket_id}/add_mushroom/{mushroom_id}")
    assert response.status_code == 400
    print("Basket capacity exceeded!")
    assert response.json() == {"detail": "Basket capacity exceeded"}


def test_remove_mushroom_from_basket(client):
    print("Testing removing mushroom from basket...")
    # Создадим корзину и гриб
    basket_response = client.post(
        "/baskets/",
        json={
            "owner": "John Doe",
            "capacity": 1000,
        },
    )
    basket_id = basket_response.json()["id"]
    print(f"Created basket with ID: {basket_id}")

    mushroom_response = client.post(
        "/mushrooms/",
        json={
            "name": "Enoki",
            "edible": True,
            "weight": 100,
            "fresh": True,
        },
    )
    mushroom_id = mushroom_response.json()["id"]
    print(f"Created mushroom with ID: {mushroom_id}")

    # Добавим гриб в корзину
    client.post(f"/baskets/{basket_id}/add_mushroom/{mushroom_id}")

    # Удалим гриб из корзины
    response = client.delete(f"/baskets/{basket_id}/remove_mushroom/{mushroom_id}")
    assert response.status_code == 200
    print("Mushroom removed from basket successfully.")
    assert response.json() == {"message": "Mushroom removed from basket"}

    # Проверим, что гриб удален
    basket_response = client.get(f"/baskets/{basket_id}")
    basket_data = basket_response.json()
    print(f"Basket details: {basket_data}")
    assert len(basket_data["mushrooms"]) == 0


def test_get_basket(client):
    print("Testing getting basket...")
    # Создадим корзину
    response = client.post(
        "/baskets/",
        json={
            "owner": "John Doe",
            "capacity": 1000,
        },
    )
    basket_id = response.json()["id"]
    print(f"Created basket with ID: {basket_id}")

    # Получим корзину
    response = client.get(f"/baskets/{basket_id}")
    assert response.status_code == 200
    data = response.json()
    print(f"Basket details: {data}")
    assert data["owner"] == "John Doe"
    assert data["capacity"] == 1000
