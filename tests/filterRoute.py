from typing import List, Tuple, Optional
import networkx as nx


class CandidateRoute:
    def __init__(
        self,
        coordinates: List[Tuple[float, float]],
        mode: str,
        total_time: float,
        running_time: float,
        running_distance_km: float,
        meta: Optional[dict] = None
    ):
        self.coordinates = coordinates
        self.mode = mode  # run / run+bus / run+subway
        self.total_time = total_time
        self.running_time = running_time
        self.running_distance_km = running_distance_km
        self.meta = meta or {}
        self.similarity_score = None
        self.recommended_pace = None

    def to_dict(self):
        return {
            "coordinates": self.coordinates,
            "mode": self.mode,
            "total_time": self.total_time,
            "running_time": self.running_time,
            "running_distance_km": self.running_distance_km,
            "similarity_score": self.similarity_score,
            "recommended_pace": self.recommended_pace,
            "meta": self.meta,
        }

    def __repr__(self):
        return f"<{self.mode} - total {self.total_time:.1f}min, run {self.running_distance_km:.2f}km>"

def estimate_distance(G: nx.MultiDiGraph, nodes: List[int]) -> float:
    dist = 0
    for u, v in zip(nodes[:-1], nodes[1:]):
        if G.has_edge(u, v, 0):
            dist += G.edges[u, v, 0].get("length", 0)
    return dist

from typing import List, Set, Dict, Tuple
import networkx as nx

def split_by_transit(
    route_nodes: List[int],
    G: nx.MultiDiGraph,
    bus_stops: Set[int],
    subway_stops: Set[int],
    node_to_coords: Dict[int, Tuple[float, float]],
    pace_min_per_km: float
) -> List[CandidateRoute]:
    candidates = []

    # 전체 러닝 경로 (교통 안 탐)
    full_coords = [node_to_coords[n] for n in route_nodes]
    total_dist_m = estimate_distance(G, route_nodes)
    running_time = (total_dist_m / 1000) * pace_min_per_km

    candidates.append(CandidateRoute(
        coordinates=full_coords,
        mode="run",
        total_time=running_time,
        running_time=running_time,
        running_distance_km=total_dist_m / 1000,
        meta={"split_node": None}
    ))

    # 정류장 기준 분기
    for i, node in enumerate(route_nodes[:-1]):
        if node in bus_stops or node in subway_stops:
            mode = "run+bus" if node in bus_stops else "run+subway"

            run_nodes = route_nodes[:i+1]
            transit_nodes = route_nodes[i+1:]

            run_dist_m = estimate_distance(G, run_nodes)
            run_time = (run_dist_m / 1000) * pace_min_per_km

            transit_dist_m = estimate_distance(G, transit_nodes)
            speed_kmh = 20 if mode == "run+bus" else 30
            transit_time = (transit_dist_m / 1000) / speed_kmh * 60  # 분

            total_time = run_time + transit_time
            coords = [node_to_coords[n] for n in route_nodes]

            candidates.append(CandidateRoute(
                coordinates=coords,
                mode=mode,
                total_time=total_time,
                running_time=run_time,
                running_distance_km=run_dist_m / 1000,
                meta={
                    "split_node": node,
                    "transit_time": transit_time,
                    "transit_distance_km": transit_dist_m / 1000
                }
            ))

    return candidates


def expand_all_candidate_routes(
    candidate_paths: List[List[int]],
    G: nx.MultiDiGraph,
    bus_stops: Set[int],
    subway_stops: Set[int],
    node_to_coords: Dict[int, Tuple[float, float]],
    pace_min_per_km: float
) -> List[CandidateRoute]:
    all_expanded = []

    for path in candidate_paths:
        expanded = split_by_transit(path, G, bus_stops, subway_stops, node_to_coords, pace_min_per_km)
        all_expanded.extend(expanded)

    return all_expanded
