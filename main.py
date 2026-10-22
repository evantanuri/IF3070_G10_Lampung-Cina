import os
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

    # Input User
    choice = input("\nPilih nomor algoritma: ").strip()
    input_file = input("Masukkan nama file input (default: input.json): ").strip()
    runs = 0
    while (runs <= 0):
        runs = int(input("Berapa kali algoritma dijalankan? : ").strip())
    if choice == "3":
        max_sideways = int(input("Masukkan jumlah maximum sideways move (default: 30): ").strip() or 30)
    if choice == "4":
        max_restarts = int(input("Masukkan jumlah maximum restart (default: 30): ").strip() or 30)


    # Buat folder untuk menyimpan visualisasi
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = f"output/Run_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n[INFO] Seluruh visualisasi disimpan di: {output_dir}")

    # Run algoritma
    if (input_file == ""):
        input_file = "input.json"
    ships, vehicles = load_data(input_file)

    for r in range(1, runs + 1):
        print (f"\n------ Run #{r} ------")
        initial_state = randomize_state(ships, vehicles)
        init_fitness = calculate_fitness(initial_state, vehicles)

         # Visualize state awal
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
            final_state, final_fitness, total_iter, history = stochastic_hill_climbing(initial_state, ships, vehicles, max_iter=1000)

        # Simulated Annealing
        elif choice == "6":
            history = {}
            final_state, final_fitness, total_iter = simulated_annealing(initial_state, ships, vehicles, history=history)

        elif choice == "7":
            print("otw kika")
            break

        else:
            print("Pilihan nomor algoritma tidak valid.")
            break

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

        # Ringkasan per run
        duration = time.time() - start_time

        print(f"\nRingkasan Run #{r}:")
        print(f"Durasi Pencarian : {duration:.4f} detik")
        print(f"Total Iterasi    : {total_iter}")
        print(f"Initial Fitness  : {init_fitness}")
        print(f"Final Fitness    : {final_fitness}")

if __name__ == "__main__":
    main()

