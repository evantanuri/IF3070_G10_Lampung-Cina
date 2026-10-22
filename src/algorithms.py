import random
from src.state import is_valid_placement, calculate_fitness, randomize_state

# Get neighbor (Stochastic)
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


# Get neighbor (Deterministic)
# Urutan algoritmanya dia cek semua move rotate dulu, baru swap, baru relocate.
# Urutan prioritas berdasarkan move mana yg kemungkinan besar membangkitkan neighbor lebih baik dengan perubahan terkecil. 
def get_deterministic_neighbors(posisi, ships, vehicles):
    def copy_state(state):
        return {vid: dict(p) if p is not None else None for vid, p in state.items()}

    # Urutan 1 yg di cek : ROTATE
    for v in vehicles:
        p = posisi[v.id]
        if p is not None:
            ship = next(s for s in ships if s.id == p["ship_id"])
            new_ori = "Vertical" if p["orientation"] == "Horizontal" else "Horizontal"

            temp_state = copy_state(posisi)
            temp_state[v.id] = None  # Angkat dulu mobilnya

            if is_valid_placement(v, ship, p["x"], p["y"], new_ori, temp_state, vehicles):
                temp_state[v.id] = {"ship_id": ship.id, "x": p["x"], "y": p["y"], "orientation": new_ori}
                yield temp_state

    # Urutan 2 yang di cek :SWAP
    n_v = len(vehicles)
    for i in range(n_v):
        for j in range(i + 1, n_v):
            v1, v2 = vehicles[i], vehicles[j]
            p1, p2 = posisi[v1.id], posisi[v2.id]

            # Skip kalo keduanya sama-sama di luar kapal
            if p1 is None and p2 is None:
                continue

            temp_state = copy_state(posisi)
            temp_state[v1.id] = None
            temp_state[v2.id] = None

            # Kasus A: Keduanya di kapal
            if p1 is not None and p2 is not None:
                ship1 = next(s for s in ships if s.id == p1["ship_id"])
                ship2 = next(s for s in ships if s.id == p2["ship_id"])

                if is_valid_placement(v1, ship2, p2["x"], p2["y"], p2["orientation"], temp_state, vehicles):
                    temp_state[v1.id] = {"ship_id": ship2.id, "x": p2["x"], "y": p2["y"], "orientation": p2["orientation"]}
                    if is_valid_placement(v2, ship1, p1["x"], p1["y"], p1["orientation"], temp_state, vehicles):
                        temp_state[v2.id] = {"ship_id": ship1.id, "x": p1["x"], "y": p1["y"], "orientation": p1["orientation"]}
                        yield temp_state

            # Kasus B: v1 di kapal, v2 di luar
            elif p1 is not None and p2 is None:
                ship1 = next(s for s in ships if s.id == p1["ship_id"])
                if is_valid_placement(v2, ship1, p1["x"], p1["y"], p1["orientation"], temp_state, vehicles):
                    temp_state[v2.id] = {"ship_id": ship1.id, "x": p1["x"], "y": p1["y"], "orientation": p1["orientation"]}
                    yield temp_state

            # Kasus C: v1 di luar, v2 di kapal
            elif p1 is None and p2 is not None:
                ship2 = next(s for s in ships if s.id == p2["ship_id"])
                if is_valid_placement(v1, ship2, p2["x"], p2["y"], p2["orientation"], temp_state, vehicles):
                    temp_state[v1.id] = {"ship_id": ship2.id, "x": p2["x"], "y": p2["y"], "orientation": p2["orientation"]}
                    yield temp_state

    # 3. Urutan 3 yang di cek : RELOCATE
    for v in vehicles:
        current_p = posisi[v.id]

        # 3a. Relocate ke domain 'diluar'
        if current_p is not None:
            temp_state = copy_state(posisi)
            temp_state[v.id] = None
            yield temp_state

        # 3b. Relocate ke kapal dan koordinat grid
        temp_state = copy_state(posisi)
        temp_state[v.id] = None

        for ship in ships:
            for ori in ["Horizontal", "Vertical"]:
                w, l = v.get_dim(ori)
                max_x = ship.w - w
                max_y = ship.l - l

                if max_x < 0 or max_y < 0:
                    continue

                for x in range(max_x + 1):
                    for y in range(max_y + 1):
                        # Lewati jika persis di posisi awalnya
                        if (current_p is not None and
                            current_p["ship_id"] == ship.id and
                            current_p["x"] == x and
                            current_p["y"] == y and
                            current_p["orientation"] == ori):
                            continue

                        if is_valid_placement(v, ship, x, y, ori, temp_state, vehicles):
                            candidate_state = copy_state(temp_state)
                            candidate_state[v.id] = {"ship_id": ship.id, "x": x, "y": y, "orientation": ori}
                            yield candidate_state


# Simple Hill Climbing Algorithm
def simple_hill_climbing(initial_state, ships, vehicles, max_iter=1000):
    current_state = {vid: dict(p) if p is not None else None for vid, p in initial_state.items()}
    current_fitness = calculate_fitness(current_state, vehicles)

    iteration = 0
    history = [current_fitness]
    print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")

    while iteration < max_iter:
        iteration += 1
        improved = False

        # Telusuri tetangga terstruktur, langsung lompat saat menemukan tetangga pertama yang lebih baik (cut)
        for neighbor in get_deterministic_neighbors(current_state, ships, vehicles):
            f = calculate_fitness(neighbor, vehicles)
            if f > current_fitness:
                current_state = neighbor
                current_fitness = f
                improved = True
                break

        history.append(current_fitness)

        if improved:
            print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")
        else:
            print(f"Iterasi {iteration}: Mencapai Local Optimum (berhenti).")
            break

    return current_state, current_fitness, iteration, history

# Steepest Ascent Hill Climbing Algorithm
def steepest_ascent_hill_climbing(initial_state, ships, vehicles, max_iter=1000, verbose=True):
    current_state = {vid: dict(p) if p is not None else None for vid, p in initial_state.items()}
    current_fitness = calculate_fitness(current_state, vehicles)

    iteration = 0
    history = [current_fitness]
    if verbose:
        print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")

    while iteration < max_iter:
        iteration += 1
        best_neighbor = None
        best_fitness = current_fitness

        # Evaluasi SEMUA neighbor
        for neighbor in get_deterministic_neighbors(current_state, ships, vehicles):
            f = calculate_fitness(neighbor, vehicles)
            if f > best_fitness:
                best_fitness = f
                best_neighbor = neighbor

        if best_neighbor is not None:
            current_state = best_neighbor
            current_fitness = best_fitness
            history.append(current_fitness)
            if verbose:
                print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")
        else:
            # Tidak ada tetangga yang lebih baik -> Local Optimum
            history.append(current_fitness)
            if verbose:
                print(f"Iterasi {iteration}: Mencapai Local Optimum (berhenti).")
            break

    return current_state, current_fitness, iteration, history

# Stochastic Hill Climbing Algorithm
def stochastic_hill_climbing(initial_state, ships, vehicles, max_iter=1000):
    current_state = {vid: dict(p) if p is not None else None for vid, p in initial_state.items()}
    current_fitness = calculate_fitness(current_state, vehicles)

    iteration = 0
    history = [current_fitness]
    print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")

    for _ in range(max_iter):
        iteration += 1
        neighbor = get_random_neighbor(current_state, ships, vehicles)

        if neighbor is not None:
            f = calculate_fitness(neighbor, vehicles)
            if f > current_fitness:
                current_state = neighbor
                current_fitness = f
                print(f"Iterasi {iteration}: Fitness Score = {current_fitness}")

        history.append(current_fitness)

    return current_state, current_fitness, iteration, history

# Random Restart Hill Climbing Algorithm
def random_restart_hill_climbing(initial_state, ships, vehicles, max_restarts=30, max_iter=1000):
    best_state = None
    best_fitness = float("-inf")
    total_iterations = 0

    all_history = []
    best_so_far_history = []

    current_init = initial_state

    for i in range(1, max_restarts + 1):
        if i > 1:
            current_init = randomize_state(ships, vehicles)

        local_state, local_fitness, local_iter, local_hist = steepest_ascent_hill_climbing(
            current_init, ships, vehicles, max_iter=max_iter, verbose=False
        )
        total_iterations += local_iter

        # Catat history tiap iterasi untuk plot grafik (dan running best)
        for h in local_hist:
            all_history.append(h)
            best_candidate = max(best_fitness, h) if best_fitness != float("-inf") else h
            best_so_far_history.append(best_candidate)

        is_new_best = False
        if local_fitness > best_fitness:
            best_fitness = local_fitness
            best_state = local_state
            is_new_best = True

        status = f" -> Global Best Baru = {best_fitness}" if is_new_best else ""
        print(f"Restart #{i}/{max_restarts}: Local Optimum = {local_fitness} (Iterasi: {local_iter}){status}")

    history_dict = {"objective": all_history, "best_objective": best_so_far_history}
    return best_state, best_fitness, total_iterations, history_dict 