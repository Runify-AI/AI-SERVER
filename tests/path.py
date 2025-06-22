import random
from typing import List, Tuple
import networkx as nx
import osmnx as ox

import cluster_waypoints

def get_nearest_node(G: nx.MultiDiGraph, coord: Tuple[float, float]) -> int:
    return ox.distance.nearest_nodes(G, coord[1], coord[0])  # lon, lat 순서!

def generate_candidate_routes(G, start_coord, end_coord,  num_routes=100):
    """
    다양한 경유지를 활용해 후보 경로를 생성한다.
    waypoints는 경유지 리스트 [(lat, lon), ...]
    """
    print("📌 후보 경로 생성 중...")

    all_routes = []

    # 1. OSM에서 좌표를 가장 가까운 노드로 변환
    start_node = nx.nearest_nodes(G, X=start_coord[1], Y=start_coord[0])
    end_node = nx.nearest_nodes(G, X=end_coord[1], Y=end_coord[0])
    clustered_waypoints = cluster_waypoints(G)


    # 3. 다양한 조합으로 경로 생성
    for _ in range(num_routes):
        # 경유지 랜덤 선택
        middle_nodes = []
        sampled_waypoints = random.sample(clustered_waypoints, k=min(2, len(clustered_waypoints)))

        for lat, lon in sampled_waypoints:
            try:
                node = nx.nearest_nodes(G, X=lon, Y=lat)
                middle_nodes.append(node)
            except:
                continue

        # 경로 생성: start → 경유지들 → end
        try:
            path = nx.shortest_path(G, start_node, end_node, weight='length')
            for node in middle_nodes:
                path = nx.shortest_path(G, path[-1], node, weight='length') + path[1:]
            all_routes.append(path)
        except:
            continue

    print(f"✅ 생성된 후보 경로 수: {len(all_routes)}")
    return all_routes