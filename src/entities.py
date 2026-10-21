import json

class Vehicle:
    def __init__(self, id, w, l, shipping_fee, weight, orientation="Horizontal", eta=0):
        self.id = id
        self.orientation = orientation
        self.shipping_fee = shipping_fee
        self.weight = weight
        self.eta = eta

        if orientation == "Horizontal":
            self.w = w
            self.l = l
        elif orientation == "Vertical":
            self.w = l
            self.l = w

    def rotate(self):
        if self.orientation == "Horizontal":
            self.orientation = "Vertical"
            self.w, self.l = self.l, self.w
        elif self.orientation == "Vertical":
            self.orientation = "Horizontal"
            self.w, self.l = self.l, self.w

class Ship:
    def __init__(self, id, w, l, max_capacity):
        self.id = id
        self.w = w
        self.l = l
        self.max_capacity = max_capacity

def load_data(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
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

if __name__ == "__main__":
    ships, vehicles = load_data("input.json")

    print(f"Total kapal: {len(ships)}")
    for s in ships:
        print(f"-> Kapal {s.id}: Dimensi={s.w}x{s.l}, Kapasitas={s.max_capacity}")

    print(f"\nTotal kendaraan: {len(vehicles)}")
    for v in vehicles:
        print(f"-> {v.id}: Dimensi saat ini={v.w}x{v.l}, Fee={v.shipping_fee}, Berat={v.weight}, ETA={v.eta}, Orientasi={v.orientation}")

    # Tes rotasi singkat
    print("\n--- Tes Rotasi V01 ---")
    v_test = vehicles[0]
    print(f"Sebelum rotate: {v_test.w}x{v_test.l} ({v_test.orientation})")
    v_test.rotate()
    print(f"Setelah rotate: {v_test.w}x{v_test.l} ({v_test.orientation})")