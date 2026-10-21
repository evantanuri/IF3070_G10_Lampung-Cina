import time
from src.entities import load_data
from src.state import randomize_state, calculate_fitness
from src.algorithms import simple_hill_climbing

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
        initial_state = randomize_state(ships, vehicles)
        init_fitness = calculate_fitness(initial_state, vehicles)

        start_time = time.time()

        if choice == "1":
            final_state, final_fitness, total_iter = simple_hill_climbing(
                initial_state, ships, vehicles, max_iter=1000, max_tries=100)
        #Nanti masukin algoritma kalian disini ges, buat aja elif choice == "2" misal    
        else: 
            print("otw dibuat")
            break

        duration = time.time() - start_time

        print(f"\n--- Ringkasan Run #{r} ---")
        print(f"Durasi Pencarian : {duration:.4f} detik")
        print(f"Total Iterasi    : {total_iter}")
        print(f"Initial Fitness  : {init_fitness}")
        print(f"Final Fitness    : {final_fitness}")

if __name__ == "__main__":
    main()

