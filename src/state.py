import random

# Cek apakah memenuhi constraints atau ngga
def is_valid_placement(v, ship, x, y, orientation, posisi, vehicles):
    w, l = v.get_dim(orientation)

    # Cek apakah vehicle dalam ship
    if x < 0 or y < 0:
        return False
    if (x + w) > ship.w or (y + l) > ship.l:
        return False

    # Cek total berat dalam ship
    current_weight = 0
    for other in vehicles:
        pos = posisi[other.id]
        if pos is not None and pos["ship_id"] == ship.id and other.id != v.id:
            current_weight += other.weight

    if current_weight + v.weight > ship.max_capacity:
        return False

    # 3. Cek apakah overlap dengan vehicle lain
    for other in vehicles:
        if other.id == v.id:
            continue

        pos = posisi[other.id]
        if pos is not None and pos["ship_id"] == ship.id:
            ow, ol = other.get_dim(pos["orientation"])
            ox = pos["x"]
            oy = pos["y"]

            overlap_x = max(x, ox) < min(x + w, ox + ow)
            overlap_y = max(y, oy) < min(y + l, oy + ol)

            if overlap_x and overlap_y:
                return False

    return True


def randomize_state(ships, vehicles):
    posisi = {}
    for v in vehicles:
        posisi[v.id] = None

    # Pilihan domain: ship yang ada + diluar ship
    spaces = list(ships) + ["diluar"]

    shuffled_vehicles = list(vehicles)
    random.shuffle(shuffled_vehicles)

    for v in shuffled_vehicles:
        target_space = random.choice(spaces)

        if target_space == "diluar":
            posisi[v.id] = None
        else:
            ship = target_space
            orientation = random.choice(["Horizontal", "Vertical"])
            w, l = v.get_dim(orientation)

            max_x = ship.w - w
            max_y = ship.l - l

            if max_x < 0 or max_y < 0:
                posisi[v.id] = None
                continue

            dapat_tempat = False
            for _ in range(10):
                rx = random.randint(0, max_x)
                ry = random.randint(0, max_y)

                if is_valid_placement(v, ship, rx, ry, orientation, posisi, vehicles):
                    posisi[v.id] = {
                        "ship_id": ship.id,
                        "x": rx,
                        "y": ry,
                        "orientation": orientation
                    }
                    dapat_tempat = True
                    break

            if not dapat_tempat:
                posisi[v.id] = None

    return posisi


# Hitung skor fitness. Rumus nya : Total Fee - (alpha * total ETA). 
# alpha di hard-code 5
def calculate_fitness(posisi, vehicles, alpha=5):
    total_fee = 0
    total_eta = 0

    for v in vehicles:
        if posisi[v.id] is not None:
            total_fee += v.shipping_fee
            total_eta += v.eta

    return total_fee - (alpha * total_eta)
