from fastapi import FastAPI

app = FastAPI()

# Restaurant menu
menu = [
    {"id": 1, "name": "Pizza", "category": "main", "price": 12},
    {"id": 2, "name": "Burger", "category": "main", "price": 10},
    {"id": 3, "name": "Salad", "category": "starter", "price": 8},
    {"id": 4, "name": "Ice Cream", "category": "dessert", "price": 5},
]


# Get one item by ID
@app.get("/items/{item_id}")
def get_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return {"error": "Not found"}


# Get items with filters
@app.get("/items")
def get_items(category: str = None, name: str = None):
    result = []

    for item in menu:
        # Check if item matches filters
        category_match = True
        name_match = True

        # Check category filter
        if category:
            if item["category"] == category:
                category_match = True
            else:
                category_match = False

        # Check name filter
        if name:
            if item["name"] == name:
                name_match = True
            else:
                name_match = False

        # Add item if both filters match
        if category_match and name_match:
            result.append(item)
        print(result) # res[{'id': 1, 'name': 'Pizza', 'category': 'main', 'price': 12}, {'id': 2, 'name': 'Burger', 'category': 'main', 'price': 10}]

    return result
