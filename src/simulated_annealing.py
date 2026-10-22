
import math
import random
import copy

from src.state import calculate_fitness, is_valid_placement


def copy_state(posisi):
    return {
        vehicle_id: dict(placement) if placement is not None else None
        for vehicle_id, placement in posisi.items()
    }


def get_random_neighbor(posisi, ships, vehicles, max_attempts=30):

    if not vehicles or not ships:
        return None

    ship_by_id = {ship.id: ship for ship in ships}

    for _ in range(max_attempts):
        neighbor = copy_state(posisi)

        action = random.choice(["relocate", "rotate", "swap"])

        # RELOCATE
        if action == "relocate":
            vehicle = random.choice(vehicles)

            # Hapus sementara penempatan kendaraan.
            neighbor[vehicle.id] = None

            # Kendaraan dapat dikeluarkan dari kapal.
            if random.random() < 0.15:
                return neighbor

            ship = random.choice(ships)
            orientation = random.choice(
                ["Horizontal", "Vertical"]
            )

            w, l = vehicle.get_dim(orientation)

            if w > ship.w or l > ship.l:
                continue

            x = random.randint(0, ship.w - w)
            y = random.randint(0, ship.l - l)

            if is_valid_placement(
                vehicle, ship, x, y,
                orientation, neighbor, vehicles
            ):
                neighbor[vehicle.id] = {
                    "ship_id": ship.id,
                    "x": x,
                    "y": y,
                    "orientation": orientation
                }
                return neighbor

        # ROTATE
        elif action == "rotate":
            loaded_vehicles = [
                v for v in vehicles
                if neighbor[v.id] is not None
            ]

            if not loaded_vehicles:
                continue

            vehicle = random.choice(loaded_vehicles)
            old_position = dict(neighbor[vehicle.id])

            ship = ship_by_id.get(old_position["ship_id"])
            if ship is None:
                continue

            old_orientation = old_position["orientation"]
            new_orientation = (
                "Vertical"
                if old_orientation == "Horizontal"
                else "Horizontal"
            )

            x = old_position["x"]
            y = old_position["y"]

            # Hapus sementara agar tidak dianggap overlap dengan dirinya sendiri
            neighbor[vehicle.id] = None

            w, l = vehicle.get_dim(new_orientation)

            if (
                w <= ship.w
                and l <= ship.l
                and is_valid_placement(
                    vehicle, ship, x, y,
                    new_orientation, neighbor, vehicles
                )
            ):
                neighbor[vehicle.id] = {
                    "ship_id": ship.id,
                    "x": x,
                    "y": y,
                    "orientation": new_orientation
                }
                return neighbor

        # SWAP
        else:
            if len(vehicles) < 2:
                continue

            v1, v2 = random.sample(vehicles, 2)

            p1 = neighbor[v1.id]
            p2 = neighbor[v2.id]

            if p1 is None and p2 is None:
                continue

            # Simpan kedua posisi, lalu kosongkan.
            p1 = dict(p1) if p1 is not None else None
            p2 = dict(p2) if p2 is not None else None

            neighbor[v1.id] = None
            neighbor[v2.id] = None

            # Posisi v2 dicoba untuk v1.
            if p2 is not None:
                ship2 = ship_by_id.get(p2["ship_id"])

                if ship2 is None:
                    continue

                if not is_valid_placement(
                    v1, ship2, p2["x"], p2["y"],
                    p2["orientation"], neighbor, vehicles
                ):
                    continue

                neighbor[v1.id] = dict(p2)

            # Posisi v1 dicoba untuk v2.
            if p1 is not None:
                ship1 = ship_by_id.get(p1["ship_id"])

                if ship1 is None:
                    continue

                if not is_valid_placement(
                    v2, ship1, p1["x"], p1["y"],
                    p1["orientation"], neighbor, vehicles
                ):
                    continue

                neighbor[v2.id] = dict(p1)

            return neighbor

    return None


def simulated_annealing(
    initial_state,
    ships,
    vehicles,
    initial_temp=1000.0,
    cooling_rate=0.995,
    stopping_temp=0.1,
    max_iter=10000,
    max_stagnation=500,
    alpha=5,
    history=None
):
    
    if initial_temp <= 0:
        raise ValueError("initial_temp harus lebih besar dari 0.")

    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate harus di antara 0 dan 1.")

    if not 0 <= stopping_temp < initial_temp:
        raise ValueError(
            "stopping_temp harus >= 0 dan lebih kecil dari initial_temp."
        )

    if max_iter < 0:
        raise ValueError("max_iter tidak boleh negatif.")

    if max_stagnation < 1:
        raise ValueError("max_stagnation harus minimal 1.")

    current_state = copy_state(initial_state)
    best_state = copy_state(initial_state)

    current_fitness = calculate_fitness(
        current_state, vehicles, alpha
    )
    best_fitness = current_fitness

    temperature = initial_temp
    iterations = 0
    stagnation_counter = 0
    stuck_count = 0

    if history is not None:
        history.clear()
        history.update({
            "iteration": [],
            "temperature": [],
            "delta": [],
            "probability": [],
            "accepted": [],
            "stuck_count": 0,
            "objective": [current_fitness],
            "best_objective": [best_fitness],
        })

    def record_objective():
        if history is not None:
            history["objective"].append(current_fitness)
            history["best_objective"].append(best_fitness)
            
    def record(delta, probability, accepted):
        if history is not None:
            history["iteration"].append(iterations)
            history["temperature"].append(temperature)
            history["delta"].append(delta)
            history["probability"].append(probability)
            history["accepted"].append(accepted)

    while (
        temperature > stopping_temp
        and iterations < max_iter
        and stagnation_counter < max_stagnation
    ):
        neighbor = get_random_neighbor(
            current_state, ships, vehicles
        )

        iterations += 1

        if neighbor is None:
            stuck_count += 1
            record(None, None, False)
            record_objective()
            stagnation_counter += 1
            temperature *= cooling_rate
            continue

        neighbor_fitness = calculate_fitness(
            neighbor, vehicles, alpha
        )

        delta = neighbor_fitness - current_fitness

        if delta >= 0:
            probability = 1.0
            accept = True
        else:
            probability = math.exp(delta / temperature)
            accept = random.random() < probability
            if not accept:
                stuck_count += 1

        record(delta, probability, accept)

        if accept:
            current_state = neighbor
            current_fitness = neighbor_fitness

        if current_fitness > best_fitness:
            best_state = copy_state(current_state)
            best_fitness = current_fitness
            stagnation_counter = 0
        else:
            stagnation_counter += 1

        record_objective()
        temperature *= cooling_rate

        if history is not None:
            history["stuck_count"] = stuck_count

    return best_state, best_fitness, iterations
