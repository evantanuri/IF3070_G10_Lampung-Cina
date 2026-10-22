import random
from src.state import randomize_state, is_valid_placement, calculate_fitness
from src.algorithms import get_random_neighbor


def _copy_state(state):             # membuat salinan state supaya state asli tidak berubah
    return {vid: dict(placement) if placement is not None else None for vid, placement in state.items()}


# memilih induk
def select_parent(population, fitnesses, tournament_size):     # mengambil individu secara acak dan yang nilainya tertinggi akan menjadi induk
    contestants = random.sample(range(len(population)), tournament_size)
    winner      = max(contestants, key=lambda i: fitnesses[i])
    return population[winner]


# crossover
def pick_by_cut_line(first, second, ships, vehicles):   # memotong kapal 
    inherited = []                                      # daftar kendaran & posisinya yang akan diwariskan
    for ship in ships:
        axis   = random.choice(["x", "y"])              # memotong secara vertikal atau horizontal
        length = ship.w if axis == "x" else ship.l
        if length < 2:                                  # geladak terlalu kecil untuk dipotong
            continue
        cut_line = random.randint(1, length - 1)

        for v in vehicles:
            placement = first[v.id]                     # induk pertama mengambil kendaraan yg ada di sebelum garis
            if placement is not None and placement["ship_id"] == ship.id:
                w, l    = v.get_dim(placement["orientation"])
                end_pos = placement["x"] + w if axis == "x" else placement["y"] + l
                if end_pos <= cut_line:
                    inherited.append((v, placement))
            placement = second[v.id]                    # induk kedua mengambil kendaraan yg ada setelah garis
            if placement is not None and placement["ship_id"] == ship.id:
                start_pos = placement["x"] if axis == "x" else placement["y"]
                if start_pos >= cut_line:
                    inherited.append((v, placement))
    return inherited

# menaruh kendaraan ke anak, dengan fee tertinggi dulu
def place_inherited(inherited, ship_by_id, vehicles):   
    random.shuffle(inherited)
    inherited.sort(key=lambda item: item[0].shipping_fee, reverse=True)

    child = {v.id: None for v in vehicles}              # semua kendaraan di luar kapal
    for v, placement in inherited:
        ship = ship_by_id[placement["ship_id"]]
        if child[v.id] is None and is_valid_placement(v, ship, placement["x"], placement["y"], placement["orientation"], child, vehicles):
            child[v.id] = dict(placement)
    return child

# bagi kendaraan yang belum mendapatkan tempat, coba di induk A / B
def fill_unplaced(child, parent_a, parent_b, ship_by_id, vehicles):    
    unplaced = [v for v in vehicles if child[v.id] is None]
    random.shuffle(unplaced)
    unplaced.sort(key=lambda v: v.shipping_fee, reverse=True)
    for v in unplaced:
        for parent in (parent_a, parent_b):
            placement = parent[v.id]
            if placement is None:
                continue
            ship = ship_by_id[placement["ship_id"]]
            if is_valid_placement(v, ship, placement["x"], placement["y"], placement["orientation"], child, vehicles):
                child[v.id] = dict(placement)
                break
    return child

# menggabungkan dua induk 
def crossover(parent_a, parent_b, ships, vehicles):     
    ship_by_id    = {s.id: s for s in ships}
    first, second = (parent_a, parent_b) if random.random() < 0.5 else (parent_b, parent_a)

    inherited = pick_by_cut_line(first, second, ships, vehicles)
    child     = place_inherited(inherited, ship_by_id, vehicles)
    return fill_unplaced(child, parent_a, parent_b, ship_by_id, vehicles)


# mengubah anak dengan satu pergerakkan acak
def mutate(child, ships, vehicles):         # satu pergerakan acak (relocate / rotate / swap)
    neighbor = get_random_neighbor(child, ships, vehicles)
    return neighbor if neighbor is not None else child


# genetic algorithm
def genetic_algorithm(ships, vehicles, population_size=30, generations=100, crossover_rate=0.9,
                      mutation_rate=0.5, tournament_size=3, elite_size=1, seed=None, verbose=False):
    if population_size < 2:
        raise ValueError("population_size minimal 2")
    if generations < 0:
        raise ValueError("generations tidak boleh negatif")
    if not (0 <= crossover_rate <= 1 and 0 <= mutation_rate <= 1):
        raise ValueError("crossover_rate dan mutation_rate harus di antara 0 dan 1")
    if not (0 <= elite_size < population_size):
        raise ValueError("elite_size harus lebih kecil dari population_size")
    if not (1 <= tournament_size <= population_size):
        raise ValueError("tournament_size harus antara 1 dan population_size")
    if seed is not None:
        random.seed(seed)                               # jika seed sama maka hasil bisa diulang

    # populasi awal: banyak state acak
    population = [randomize_state(ships, vehicles) for _ in range(population_size)]
    fitnesses  = [calculate_fitness(individual, vehicles) for individual in population]

    best_idx      = fitnesses.index(max(fitnesses))
    initial_best  = _copy_state(population[best_idx])       # state awal terbaik (untuk ditampilkan)
    best_state    = _copy_state(population[best_idx])       # solusi terbaik sejauh ini    
    best_fitness  = fitnesses[best_idx]

    history_max   = [max(fitnesses)]                        # nilai terbaik di setiap generasi
    history_avg   = [sum(fitnesses) / len(fitnesses)]       # rata-rata nilai populasi setiap generasi

    if verbose:
        print(f"Generasi 0 (Populasi Awal): Fitness Terbaik = {best_fitness} | Rata-rata = {history_avg[0]:.1f}")

    for generation in range(1, generations + 1):
        # individu terbaik langsung lolos ke generasi berikutnya
        ranking        = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        new_population = [_copy_state(population[i]) for i in ranking[:elite_size]]

        # sisa tempat diisi anak-anak baru
        while len(new_population) < population_size:
            parent_a = select_parent(population, fitnesses, tournament_size)
            parent_b = select_parent(population, fitnesses, tournament_size)
            if random.random() < crossover_rate:
                child = crossover(parent_a, parent_b, ships, vehicles)
            else:
                child = _copy_state(parent_a)           # tidak digabung -> anak = salinan induk
            if random.random() < mutation_rate:
                child = mutate(child, ships, vehicles)
            new_population.append(child)

        population = new_population
        fitnesses  = [calculate_fitness(individual, vehicles) for individual in population]

        best_idx = fitnesses.index(max(fitnesses))
        history_max.append(max(fitnesses))
        history_avg.append(sum(fitnesses) / len(fitnesses))

        if fitnesses[best_idx] > best_fitness:
            best_fitness = fitnesses[best_idx]
            best_state   = _copy_state(population[best_idx])
            if verbose:
                print(f"Generasi {generation}: terbaik {history_max[-1]} | rata-rata {history_avg[-1]:.1f}")

    return best_state, best_fitness, generations, history_max, history_avg, initial_best