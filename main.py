import os
import time
from src.entities import load_data
from src.state import randomize_state, calculate_fitness
from src.algorithms import simple_hill_climbing
from src.simulated_annealing import simulated_annealing
from src.visualizer import visualize_state, plot_acceptance_probability, plot_objective_function

def main():
    print("PILIH ALGORITMA SEARCHING:")
    print("  [1] Simple Hill Climbing")
    print("  [2] Steepest Ascent Hill Climbing")
    print("  [3] Hill Climbing with Sideways Move")
    print("  [4] Random Restart Hill Climbing")
    print("  [5] Stochastic Hill Climbing")
    print("  [6] Simulated Annealing")
    print("  [7] Genetic Algorithm")

    choice = input("\nPilih nomor algoritma: ").strip()
    input_file = input("Masukkan nama file input (misal: input.json): ").strip()
    runs = 0
    while (runs <= 0):
        runs = int(input("Berapa kali algoritma dijalankan? ").strip())

    if (input_file == ""):
        input_file = "input.json"
    ships, vehicles = load_data(input_file)

    for r in range(1, runs + 1):
        history = {}
        initial_state = randomize_state(ships, vehicles)
        init_fitness = calculate_fitness(initial_state, vehicles)

        start_time = time.time()

        if choice == "1":
            final_state, final_fitness, total_iter = simple_hill_climbing(
                initial_state, ships, vehicles, max_iter=1000, max_tries=100)
        #Nanti masukin algoritma kalian disini ges, buat aja elif choice == "2" misal
        
        elif choice == "6":
            final_state, final_fitness, total_iter = simulated_annealing(
                initial_state, ships, vehicles, initial_temp=1000.0,
                cooling_rate=0.995, stopping_temp=0.1, max_iter=10000,
                max_stagnation=500, alpha=5, history=history)
            total_sa = len(history["iteration"])
            print(f"Stuck di Local Optima : {history['stuck_count']} kali "
                  f"dari {total_sa} iterasi")
            
            #ini outputnya sesuaikan sama path folder output kalian ya ges
            plot_acceptance_probability(
                history,
                title=f"Simulated Annealing - e^(ΔE/T) vs Iterasi (Run #{r})",
                save_path=os.path.join(r"C:\DAI Lampung China\IF3070_G10_Lampung-Cina\output", f"algo{choice}_run{r}_probability.png"),
                show=False)
        else: 
            print("otw dibuat")
            break

        duration = time.time() - start_time

        print(f"\n--- Ringkasan Run #{r} ---")
        print(f"Durasi Pencarian : {duration:.4f} detik")
        print(f"Total Iterasi    : {total_iter}")
        print(f"Initial Fitness  : {init_fitness}")
        print(f"Final Fitness    : {final_fitness}")

        #ini outputnya sesuaikan sama path folder output kalian ya ges
        visualize_state(initial_state, ships, vehicles,
                        title=f"Initial State - Run #{r}",
                        save_path=os.path.join(r"C:\DAI Lampung China\IF3070_G10_Lampung-Cina\output", f"algo{choice}_run{r}_initial.png"),
                        show=False)
        visualize_state(final_state, ships, vehicles,
                        title=f"Final State - Run #{r}",
                        save_path=os.path.join(r"C:\DAI Lampung China\IF3070_G10_Lampung-Cina\output", f"algo{choice}_run{r}_final.png"),
                        show=False)
        plot_objective_function(
            history,
            title=f"Objective Function vs Iterasi (Run #{r})",
            save_path=os.path.join(r"C:\DAI Lampung China\IF3070_G10_Lampung-Cina\output", f"algo{choice}_run{r}_objective.png"),
            show=False)

if __name__ == "__main__":
    main()

