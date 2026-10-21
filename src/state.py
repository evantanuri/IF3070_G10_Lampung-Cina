import copy
from typing import Dict, List, Optional
from entities import Ship, Vehicle


class State:
    def __init__(
        self,
        ships: List[Ship],
        vehicles: List[Vehicle],
        placements: Optional[Dict[str, Optional[dict]]] = None,
    ):
        self.ships: Dict[str, Ship] = {s.id: s for s in ships}
        self.vehicles: Dict[str, Vehicle] = {v.id: v for v in vehicles}

        if placements is None:
            self.placements: Dict[str, Optional[dict]] = {
                v.id: None for v in vehicles
            }
        else:
            self.placements = placements

    def get_dim(self, v_id: str, orientation: str):
        v = self.vehicles[v_id]
        if orientation == "Vertical":
            return v.l, v.w
        return v.w, v.l

    def is_valid(self) -> bool:
        ship_weights = {s_id: 0 for s_id in self.ships}
        ship_rectangles = {s_id: [] for s_id in self.ships}

        for v_id, place in self.placements.items():
            if place is None:
                continue

            s_id = place["ship_id"]
            if s_id not in self.ships:
                return False

            v = self.vehicles[v_id]
            ship = self.ships[s_id]

            ship_weights[s_id] += v.weight
            if ship_weights[s_id] > ship.max_capacity:
                return False

            w_act, l_act = self.get_dim(v_id, place["orientation"])
            x, y = place["x"], place["y"]

            if x < 0 or y < 0 or (x + w_act > ship.w) or (y + l_act > ship.l):
                return False

            ship_rectangles[s_id].append((x, y, w_act, l_act))

        for s_id, rects in ship_rectangles.items():
            n = len(rects)
            for i in range(n):
                x1, y1, w1, l1 = rects[i]
                for j in range(i + 1, n):
                    x2, y2, w2, l2 = rects[j]
                    overlap_x = max(x1, x2) < min(x1 + w1, x2 + w2)
                    overlap_y = max(y1, y2) < min(y1 + l1, y2 + l2)
                    if overlap_x and overlap_y:
                        return False

        return True

    def calculate_eta_penalty(self) -> int:
        penalty = 0
        placed_items = [
            (v_id, p) for v_id, p in self.placements.items() if p is not None
        ]

        by_ship = {s_id: [] for s_id in self.ships}
        for v_id, place in placed_items:
            by_ship[place["ship_id"]].append((v_id, place))

        for s_id, items in by_ship.items():
            n = len(items)
            for i in range(n):
                v1_id, p1 = items[i]
                v1 = self.vehicles[v1_id]
                w1, l1 = self.get_dim(v1_id, p1["orientation"])
                x1, y1 = p1["x"], p1["y"]

                for j in range(i + 1, n):
                    v2_id, p2 = items[j]
                    v2 = self.vehicles[v2_id]
                    w2, l2 = self.get_dim(v2_id, p2["orientation"])
                    x2, y2 = p2["x"], p2["y"]

                    horizontal_overlap = max(x1, x2) < min(x1 + w1, x2 + w2)
                    if horizontal_overlap:
                        if y1 < y2 and v1.eta > v2.eta:
                            penalty += 50 * (v1.eta - v2.eta)
                        elif y2 < y1 and v2.eta > v1.eta:
                            penalty += 50 * (v2.eta - v1.eta)

        return penalty

    def calculate_objective(self) -> float:
        if not self.is_valid():
            return -1.0

        total_fee = sum(
            self.vehicles[v_id].shipping_fee
            for v_id, place in self.placements.items()
            if place is not None
        )

        eta_penalty = self.calculate_eta_penalty()
        return float(max(0, total_fee - eta_penalty))

    def copy(self):
        new_placements = {
            v_id: dict(place) if place is not None else None
            for v_id, place in self.placements.items()
        }
        return State(
            ships=list(self.ships.values()),
            vehicles=list(self.vehicles.values()),
            placements=new_placements,
        )