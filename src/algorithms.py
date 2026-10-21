import random
from src.state import is_valid_placement, calculate_fitness

# Generate 1 neighbor, ntah dengan relocate, rotate, ataupun swap (di randomize)
def get_random_neighbor(posisi, ships, vehicles):
    # buat copy
    posisi_baru = {}
    for vid, p in posisi.items():
        posisi_baru[vid] = dict(p) if p is not None else None

    move_type = random.choice(["relocate", "rotate", "swap"])

    # ROTATE
    if move_type == "rotate":
        di_kapal = [v for v in vehicles if posisi_baru[v.id] is not None]
        if di_kapal:
            v = random.choice(di_kapal)
            p = posisi_baru[v.id]
            ship = next(s for s in ships if s.id == p["ship_id"])

            new_ori = "Vertical" if p["orientation"] == "Horizontal" else "Horizontal"

            posisi_baru[v.id] = None

            if is_valid_placement(v, ship, p["x"], p["y"], new_ori, posisi_baru, vehicles):
                posisi_baru[v.id] = {"ship_id": ship.id, "x": p["x"], "y": p["y"], "orientation": new_ori}
                return posisi_baru

    # SWAP
    elif move_type == "swap" and len(vehicles) >= 2:
        v1, v2 = random.sample(vehicles, 2)
        p1, p2 = posisi_baru[v1.id], posisi_baru[v2.id]

        if p1 is None and p2 is None:
            return None

        posisi_baru[v1.id] = None
        posisi_baru[v2.id] = None

        # Kasus A: Keduanya di dalam kapal (saling tukar koordinat)
        if p1 is not None and p2 is not None:
            ship1 = next(s for s in ships if s.id == p1["ship_id"])
            ship2 = next(s for s in ships if s.id == p2["ship_id"])

            if is_valid_placement(v1, ship2, p2["x"], p2["y"], p2["orientation"], posisi_baru, vehicles):
                posisi_baru[v1.id] = {"ship_id": ship2.id, "x": p2["x"], "y": p2["y"], "orientation": p2["orientation"]}

                if is_valid_placement(v2, ship1, p1["x"], p1["y"], p1["orientation"], posisi_baru, vehicles):
                    posisi_baru[v2.id] = {"ship_id": ship1.id, "x": p1["x"], "y": p1["y"], "orientation": p1["orientation"]}
                    return posisi_baru

        # Kasus B: Ada yg tidak masuk kapal
        elif p1 is not None and p2 is None:
            ship1 = next(s for s in ships if s.id == p1["ship_id"])
            if is_valid_placement(v2, ship1, p1["x"], p1["y"], p1["orientation"], posisi_baru, vehicles):
                posisi_baru[v2.id] = {"ship_id": ship1.id, "x": p1["x"], "y": p1["y"], "orientation": p1["orientation"]}
                return posisi_baru

        elif p1 is None and p2 is not None:
            ship2 = next(s for s in ships if s.id == p2["ship_id"])
            if is_valid_placement(v1, ship2, p2["x"], p2["y"], p2["orientation"], posisi_baru, vehicles):
                posisi_baru[v1.id] = {"ship_id": ship2.id, "x": p2["x"], "y": p2["y"], "orientation": p2["orientation"]}
                return posisi_baru

    # RELOCATE
    else:
        v = random.choice(vehicles)
        spaces = list(ships) + ["diluar"]
        target_space = random.choice(spaces)

        posisi_baru[v.id] = None

        if target_space == "diluar":
            return posisi_baru
        else:
            ship = target_space
            ori = random.choice(["Horizontal", "Vertical"])
            w, l = v.get_dim(ori)
            max_x = ship.w - w
            max_y = ship.l - l

            if max_x >= 0 and max_y >= 0:
                # Cari koordinat random yang aman
                for _ in range(25):
                    rx = random.randint(0, max_x)
                    ry = random.randint(0, max_y)
                    if is_valid_placement(v, ship, rx, ry, ori, posisi_baru, vehicles):
                        posisi_baru[v.id] = {"ship_id": ship.id, "x": rx, "y": ry, "orientation": ori}
                        return posisi_baru

    return None


def simple_hill_climbing(initial_state, ships, vehicles, max_iter=1000, max_tries=100):
    current_state = {vid: dict(p) if p is not None else None for vid, p in initial_state.items()}
    current_fitness = calculate_fitness(current_state, vehicles)

    iteration = 0

    while iteration < max_iter:
        iteration += 1
        improved = False

        for _ in range(max_tries):
            neighbor = get_random_neighbor(current_state, ships, vehicles)
            if neighbor is not None:
                neighbor_fitness = calculate_fitness(neighbor, vehicles)
                if neighbor_fitness > current_fitness:
                    current_state = neighbor
                    current_fitness = neighbor_fitness
                    improved = True
                    break

        if not improved:
            break

    return current_state, current_fitness, iteration