import math
 
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
 
from src.state import calculate_fitness
 
 
def visualize_state(
    posisi,
    ships,
    vehicles,
    title="Visualisasi Penempatan Kendaraan",
    alpha=5,
    save_path=None,
    show=True,
):
    # Visualisasi penempatan kendaraan pada kapal.
    if not ships:
        print("Tidak ada kapal untuk divisualisasikan.")
        return
 
    vehicle_by_id = {v.id: v for v in vehicles}
 
    n_ships = len(ships)
    n_cols = min(2, n_ships)
    n_rows = math.ceil(n_ships / n_cols)
 
    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(7 * n_cols, 6 * n_rows),
        squeeze=False,
    )
    axes = axes.flatten()
 
    colors = plt.get_cmap("tab20")
    color_of = {v.id: colors(i % 20) for i, v in enumerate(vehicles)}
 
    for index, ship in enumerate(ships):
        ax = axes[index]
 
        ax.add_patch(
            Rectangle(
                (0, 0),
                ship.w,
                ship.l,
                facecolor="whitesmoke",
                edgecolor="black",
                linewidth=2,
            )
        )
 
        ax.set_xlim(0, ship.w)
        ax.set_ylim(0, ship.l)
        ax.set_aspect("equal", adjustable="box")
 
        ax.set_xlabel("Koordinat X (lebar)")
        ax.set_ylabel("Koordinat Y (panjang)")
 
        ax.set_xticks(range(0, ship.w + 1, max(1, ship.w // 20)))
        ax.set_yticks(range(0, ship.l + 1, max(1, ship.l // 20)))
        ax.grid(True, linestyle="--", alpha=0.3)
 
        placed_count = 0
        used_weight = 0
 
        for vid, p in posisi.items():
            if p is None or p["ship_id"] != ship.id:
                continue
 
            v = vehicle_by_id[vid]
            x, y = p["x"], p["y"]
            width, length = v.get_dim(p["orientation"])
 
            ax.add_patch(
                Rectangle(
                    (x, y),
                    width,
                    length,
                    facecolor=color_of[vid],
                    edgecolor="black",
                    linewidth=1.5,
                    alpha=0.85,
                )
            )
 
            ori = "H" if p["orientation"] == "Horizontal" else "V"
            ax.text(
                x + width / 2,
                y + length / 2,
                f"{vid}\n{ori}",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
            )
            ax.annotate(
                f"({x},{y})",
                (x, y),
                xytext=(3, 3),
                textcoords="offset points",
                fontsize=7,
            )
 
            placed_count += 1
            used_weight += v.weight
 
        ax.set_title(
            f"{ship.id} ({ship.w} x {ship.l})  |  "
            f"Muatan {used_weight}/{ship.max_capacity}",
            fontsize=12,
            fontweight="bold",
        )
        ax.text(
            0.02,
            0.98,
            f"Kendaraan: {placed_count}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9,
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray"),
        )
 
    for index in range(n_ships, len(axes)):
        axes[index].set_visible(False)
 
    fitness = calculate_fitness(posisi, vehicles, alpha)
    unplaced = [vid for vid, p in posisi.items() if p is None]
 
    fig.suptitle(f"{title}  (Fitness: {fitness})", fontsize=15, fontweight="bold")
 
    if unplaced:
        fig.text(
            0.5,
            0.015,
            "Di luar kapal: " + ", ".join(unplaced),
            ha="center",
            fontsize=10,
        )
 
    plt.tight_layout(rect=(0, 0.04, 1, 0.94))
 
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
 
def plot_acceptance_probability(
    history,
    title="Simulated Annealing: e^(ΔE/T) terhadap Iterasi",
    save_path=None,
    show=True,
):
    
    xs_acc, ys_acc, xs_rej, ys_rej = [], [], [], []
    for it, delta, prob, acc in zip(
        history["iteration"],
        history["delta"],
        history["probability"],
        history["accepted"],
    ):
        if delta is None or delta >= 0:
            continue
        if acc:
            xs_acc.append(it)
            ys_acc.append(prob)
        else:
            xs_rej.append(it)
            ys_rej.append(prob)
 
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(xs_rej, ys_rej, s=8, color="tab:red", alpha=0.5,
               label=f"Ditolak ({len(xs_rej)})")
    ax.scatter(xs_acc, ys_acc, s=14, color="tab:green", alpha=0.9,
               label=f"Diterima ({len(xs_acc)})")
 
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("e^(ΔE/T)")
    ax.set_ylim(-0.02, 1.02)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="upper right")
 
    total = len(history["iteration"])
    stuck = history["stuck_count"]
    pct = (stuck / total * 100) if total else 0
    ax.text(
        0.02, 0.02,
        f"Frekuensi stuck di local optima: {stuck} dari {total} iterasi ({pct:.1f}%)",
        transform=ax.transAxes, ha="left", va="bottom", fontsize=9,
        bbox=dict(facecolor="white", alpha=0.85, edgecolor="gray"),
    )
 
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)

def plot_objective_function(
    history,
    title="Objective Function terhadap Iterasi",
    save_path=None,
    show=True,
):
    
    objective = history["objective"]
    xs = range(len(objective))
 
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(xs, objective, color="tab:blue", linewidth=1.2, label="Fitness state saat ini")
 
    best = history.get("best_objective")
    if best:
        ax.plot(range(len(best)), best, color="tab:orange", linewidth=1.5,
                linestyle="--", label="Fitness terbaik")
 
    ax.set_xlabel("Iterasi")
    ax.set_ylabel("Objective function (fitness)")
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="lower right")
 
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)