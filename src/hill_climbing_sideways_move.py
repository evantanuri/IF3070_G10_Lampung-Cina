import random
from src.state import is_valid_placement, calculate_fitness

def _copy_state(posisi):
    return {vid: dict(p) if p is not None else None for vid, p in posisi.items()}


def _state_key(posisi):
    return tuple(
        (vid, None if p is None else (p["ship_id"], p["x"], p["y"], p["orientation"]))
        for vid, p in sorted(posisi.items())
    )


def get_all_neighbors(posisi, ships, vehicles):
    ship_by_id = {s.id: s for s in ships}
    current_key = _state_key(posisi)
    seen = {current_key}
    neighbors = []

    def add(candidate):
        key = _state_key(candidate)
        if key not in seen:
            seen.add(key)
            neighbors.append(candidate)

    for i in range(len(vehicles)):
        for j in range(i + 1, len(vehicles)):
            v1, v2 = vehicles[i], vehicles[j]
            p1, p2 = posisi[v1.id], posisi[v2.id]
            if p1 is None and p2 is None:
                continue 

            baru = _copy_state(posisi)
            baru[v1.id] = None
            baru[v2.id] = None

            if p2 is not None:
                s2 = ship_by_id[p2["ship_id"]]
                if not is_valid_placement(v1, s2, p2["x"], p2["y"], p2["orientation"], baru, vehicles):
                    continue
                baru[v1.id] = dict(p2)

            if p1 is not None:
                s1 = ship_by_id[p1["ship_id"]]
                if not is_valid_placement(v2, s1, p1["x"], p1["y"], p1["orientation"], baru, vehicles):
                    continue
                baru[v2.id] = dict(p1)
            add(baru)

    for v in vehicles:
        base = _copy_state(posisi)
        base[v.id] = None 

        add(_copy_state(base))

        for ship in ships:
            for ori in ("Horizontal", "Vertical"):
                w, l = v.get_dim(ori)
                for x in range(ship.w - w + 1):
                    for y in range(ship.l - l + 1):
                        if is_valid_placement(v, ship, x, y, ori, base, vehicles):
                            baru = _copy_state(base)
                            baru[v.id] = {"ship_id": ship.id, "x": x, "y": y, "orientation": ori}
                            add(baru)

    for v in vehicles:
        p = posisi[v.id]
        if p is None:
            continue
        ship = ship_by_id[p["ship_id"]]
        ori = "Vertical" if p["orientation"] == "Horizontal" else "Horizontal"
        baru = _copy_state(posisi)
        baru[v.id] = None
        if is_valid_placement(v, ship, p["x"], p["y"], ori, baru, vehicles):
            baru[v.id] = {"ship_id": ship.id, "x": p["x"], "y": p["y"], "orientation": ori}
            add(baru)

    return neighbors


def hill_climbing_sideways_move(initial_state, ships, vehicles, max_sideways=100, max_iter=10000):
    current = _copy_state(initial_state)
    current_fitness = calculate_fitness(current, vehicles)
    history = [current_fitness]

    iteration = 0
    sideways_count = 0
    total_sideways = 0
    
    while iteration < max_iter:
        neighbors = get_all_neighbors(current, ships, vehicles)
        if not neighbors:
            break

        scored = [(calculate_fitness(n, vehicles), n) for n in neighbors]
        best_fitness = max(f for f, _ in scored)
        best_candidates = [n for f, n in scored if f == best_fitness]

        if best_fitness < current_fitness:
            break

        if best_fitness == current_fitness:
            if sideways_count >= max_sideways:
                break
            sideways_count += 1
            total_sideways += 1
        else:
            sideways_count = 0

        current = random.choice(best_candidates)
        current_fitness = best_fitness
        iteration += 1
        history.append(current_fitness)

    return current, current_fitness, iteration, history, total_sideways
