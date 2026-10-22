import os
from pathlib import Path
import shutil
import time
from datetime import datetime
from src.entities import load_data
from src.state import randomize_state, calculate_fitness
from src.algorithms import (
    simple_hill_climbing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
    random_restart_hill_climbing,
)
from src.visualizer import (
    visualize_state,
    plot_objective_function,
    plot_acceptance_probability,
)
from src.hill_climbing_sideways_move import hill_climbing_sideways_move
from src.simulated_annealing import simulated_annealing
from src.genetic_algorithm import genetic_algorithm

def main():
    # Maiin Menu
    print("PILIH ALGORITMA SEARCHING:")
    print("  [1] Simple Hill Climbing")
    print("  [2] Steepest Ascent Hill Climbing")
    print("  [3] Hill Climbing with Sideways Move")
    print("  [4] Random Restart Hill Climbing")
    print("  [5] Stochastic Hill Climbing")
    print("  [6] Simulated Annealing")
    print("  [7] Genetic Algorithm")
    print("  [8] Clean output folder (hapus semua isinya)")

    # Input User
    choice = "0"
    while choice not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        choice = input("\nPilih nomor algoritma: ").strip()

    # Fungsi tambahan untuk membersihkan folder output (sangat membantu agar junk hasil pengetesan ga numpuk)
    if choice == "8":
        folder_path = Path("output")
        if folder_path.exists():
            for item in folder_path.iterdir():
                if item.name == ".gitkeep":
                    continue
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
        print("Output folder cleaned!")
        return

    input_file = input("Masukkan nama file input (default: input.json): ").strip()
    if input_file == "":
        input_file = "input.json"
    runs = 0
    while (runs <= 0):
        runs = int(input("Berapa kali algoritma dijalankan? : ").strip())
    if choice == "3":
        max_sideways = int(input("Masukkan jumlah maximum sideways move (default: 30): ").strip() or 30)
    if choice == "4":
        max_restarts = int(input("Masukkan jumlah maximum restart (default: 30): ").strip() or 30)
    if choice == "5":
        max_iter_user = int(input("Masukkan jumlah maximum iterasi (default: 100): ").strip() or 100)
    if choice == "7":
        ga_pop_size = int(input("Masukkan ukuran populasi GA (default: 30): ").strip() or 30)
        ga_generations = int(input("Masukkan jumlah generasi GA (default: 100): ").strip() or 100)


    # Buat folder untuk menyimpan visualisasi
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = f"output/Run_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n[INFO] Seluruh visualisasi untuk sesi ini disimpan di folder : {output_dir}")

    # Run algoritma
    ships, vehicles = load_data(input_file)

    for r in range(1, runs + 1):
        print (f"\n------ Run #{r} ------")
        initial_state = randomize_state(ships, vehicles)
        init_fitness = calculate_fitness(initial_state, vehicles)

         # Visualize state awal
        if choice != "7":
            visualize_state(
                initial_state, ships, vehicles,
                title=f"State Awal Run #{r}",
                save_path=f"{output_dir}/state_awal_run_{r}.png",
                show=False
            )

        start_time = time.time()

        # Simple Hill Climbing
        if choice == "1":
            final_state, final_fitness, total_iter, history = simple_hill_climbing(initial_state, ships, vehicles, max_iter=1000)

        # Steepest Ascent Hill Climbing
        elif choice == "2":
            final_state, final_fitness, total_iter, history = steepest_ascent_hill_climbing(initial_state, ships, vehicles, max_iter=1000)

        # Hill Climbing with Sideways Move
        elif choice == "3":
            final_state, final_fitness, total_iter, history, total_sideways, stop_reason = hill_climbing_sideways_move(initial_state, ships, vehicles, max_sideways=max_sideways, max_iter=10000)
            print(f"Alasan Berhenti : {stop_reason}")
            print(f"Total Gerakan Sideways  : {total_sideways}")

        # Random Restart Hill Climbing
        elif choice == "4":
            final_state, final_fitness, total_iter, history = random_restart_hill_climbing(initial_state, ships, vehicles, max_restarts=max_restarts, max_iter=1000)

        # Stochastic Hill Climbing
        elif choice == "5":
            final_state, final_fitness, total_iter, history = stochastic_hill_climbing(initial_state, ships, vehicles, max_iter=max_iter_user)

        # Simulated Annealing
        elif choice == "6":
            history = {}
            final_state, final_fitness, total_iter = simulated_annealing(initial_state, ships, vehicles, history=history)

        # Genetic Algorithm
        elif choice == "7":
            final_state, final_fitness, total_iter, history_max, history_avg, initial_best = genetic_algorithm(
                ships, vehicles, population_size=ga_pop_size, generations=ga_generations, verbose=True
            )
            initial_state = initial_best
            init_fitness = calculate_fitness(initial_best, vehicles)
            history = {"objective": history_avg, "best_objective": history_max}
            visualize_state(
                initial_best, ships, vehicles,
                title=f"State Awal (Best Gen 0) Run #{r}",
                save_path=f"{output_dir}/state_awal_run_{r}.png",
                show=False
            )

        else:
            print("Pilihan nomor algoritma tidak valid.")
            break

        duration = time.time() - start_time
        
         # Visualize state akhir
        visualize_state(
            final_state, ships, vehicles,
            title=f"State Akhir Run #{r}",
            save_path=f"{output_dir}/state_akhir_run_{r}.png",
            show=False
        )
        hist_data = history if isinstance(history, dict) else {"objective": history}
        plot_objective_function(
            hist_data,
            title=f"Grafik Fitness Run #{r}",
            save_path=f"{output_dir}/grafik_fitness_run_{r}.png",
            show=False
        )
        if choice == "6":
            plot_acceptance_probability(
                history,
                title=f"Probabilitas Penerimaan SA Run #{r}",
                save_path=f"{output_dir}/grafik_probabilitas_sa_run_{r}.png",
                show=False,
            )

        print(f"\nRingkasan Run #{r}:")
        print(f"Durasi Pencarian : {duration:.4f} detik")
        if choice == "7":
            print(f"Jumlah Populasi  : {ga_pop_size}")
            print(f"Total Iterasi    : {total_iter}")
        else:
            print(f"Total Iterasi    : {total_iter}")
        print(f"Initial Fitness  : {init_fitness}")
        print(f"Final Fitness    : {final_fitness}")

if __name__ == "__main__":
    main()

