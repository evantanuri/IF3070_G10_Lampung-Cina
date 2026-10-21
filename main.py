from src.entities import load_data
from src.state import randomize_state


def main():
    print("PILIH ALGORITMA SEARCHING:")
    print("  [1] Simple Hill Climbing")
    print("  [2] Steepest Ascent Hill Climbing")
    print("  [3] Hill Climbing with Sideways Move")
    print("  [4] Random Restart Hill Climbing")
    print("  [5] Stochastic Hill Climbing")
    print("  [6] Simulated Annealing")
    print("  [7] Genetic Algorithm")

    #inputs
    choice = input("\nPilih nomor algoritma: ").strip()
    input_file = input("Masukkan nama file input (misal: input3.json): ").strip()
    runs = int(input("Berapa kali algoritma dijalankan?").strip())

    ships, vehicles = load_data(input_file)

    for i in range(runs):
        initial_state = randomize_state(ships, vehicles)
        if (choice == ""):
            pass
        elif (choice == "2") : 
            pass
        elif (choice == "3") : 
            pass
        elif (choice == "4") : 
            pass
        elif (choice == "5") : 
            pass
        elif (choice == "6") : 
            pass 
        elif (choice =="7") : 
            pass

if __name__ == "__main__":
    main()