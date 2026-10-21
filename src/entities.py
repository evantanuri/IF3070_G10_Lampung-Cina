import json

class Vehicle:
    def __init__(self, id, w, l, shipping_fee, weight, orientation="Horizontal", eta=0):
        self.id = id
        self.orientation = orientation
        self.shipping_fee = shipping_fee
        self.weight = weight
        self.eta = eta
        self.base_w = w
        self.base_l = l

        if orientation == "Horizontal":
            self.w = w
            self.l = l
        elif orientation == "Vertical":
            self.w = l
            self.l = w

    def get_dim(self, orientation):
        if orientation == "Vertical":
            return self.base_l, self.base_w
        return self.base_w, self.base_l

    def rotate(self):
        if self.orientation == "Horizontal":
            self.orientation = "Vertical"
            self.w, self.l = self.l, self.w
        else:
            self.orientation = "Horizontal"
            self.w, self.l = self.l, self.w

class Ship:
    def __init__(self, id, w, l, max_capacity):
        self.id = id
        self.w = w
        self.l = l
        self.max_capacity = max_capacity

def load_data(filepath):
    #Buka dan baca file JSON
    with open(filepath, "r") as f:
        data = json.load(f)

    #Parsing data ships
    ships = []
    raw_ships = data.get("ships", [data.get("ship")] if "ship" in data else [])

    for idx, s in enumerate(raw_ships):
        ship_id = s.get("id", f"Ship_{idx + 1}")
        ships.append(Ship(
            id=ship_id,
            w=s["dimensions"]["w"],
            l=s["dimensions"]["l"],
            max_capacity=s["max_capacity"]
        ))

    #Parsing data vehicles
    vehicles = []
    for v in data["vehicles"]:
        vehicles.append(Vehicle(
            id=v["id"],
            w=v["dimensions"]["w"],
            l=v["dimensions"]["l"],
            shipping_fee=v["shipping_fee"],
            weight=v["weight"],
            orientation=v.get("orientation", "Horizontal"),
            eta=v.get("eta", 0)
        ))

    return ships, vehicles

'''
Contoh format json yang bisa di import :
{
  "ships": [
    {
      "id": "S1",
      "dimensions": { "w": 10, "l": 20 },
      "max_capacity": 500
    },
    {
      "id": "S2",
      "dimensions": { "w": 8, "l": 15 },
      "max_capacity": 300
    }
  ],
  "vehicles": [
    {
      "id": "V01",
      "dimensions": { "w": 2, "l": 4 },
      "shipping_fee": 60,
      "weight": 25,
      "orientation": "Horizontal",
      "eta": 2
    },
    {
      "id": "V02",
      "dimensions": { "w": 3, "l": 5 },
      "shipping_fee": 80,
      "weight": 40,
      "orientation": "Vertical",
      "eta": 1
    },
    {
      "id": "V03",
      "dimensions": { "w": 2, "l": 3 },
      "shipping_fee": 45,
      "weight": 18,
      "orientation": "Horizontal",
      "eta": 3
    }
  ]
}
'''
