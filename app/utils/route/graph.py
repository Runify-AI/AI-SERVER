
from itertools import permutations
from typing import Tuple
import numpy as np
import  osmnx as ox
import networkx as nx
from sklearn.cluster import KMeans


def build_walk_graph(start: Tuple[float, float], end: Tuple[float, float], dist_buffer_m=1000) -> nx.MultiDiGraph:
    """
    출발지-도착지를 중심으로 일정 거리 내 OSM 도보 그래프 생성
    """
    # 중심점과 거리 계산
    center_lat = (start[0] + end[0]) / 2
    center_lon = (start[1] + end[1]) / 2

    # OSM에서 도보 네트워크 다운로드
    G = ox.graph_from_point(
        (center_lat, center_lon),
        dist=dist_buffer_m,
        network_type='walk',
        retain_all=True
    )
    
    # 엣지 길이 추가 (m 단위)
    G = ox.distance.add_edge_lengths(G)
    
    return G


def route_via_multiple_points(graph, points, weight="length"):
    """
    여러 포인트를 거쳐가는 경로를 반환한다.
    points: [start, wp1, wp2, ..., end]
    """
    full_path = []
    for i in range(len(points) - 1):
        try:
            segment = nx.shortest_path(graph, source=points[i], target=points[i + 1], weight=weight)
            if i > 0:
                segment = segment[1:]  # 중복 제거
            full_path += segment
        except nx.NetworkXNoPath:
            return None  # 경로 구성 실패 시 None 반환
    return full_path

def nodes_to_coords(G,nodes):
        return [(G.nodes[node]['y'], G.nodes[node]['x']) for node in nodes]


def generate_diverse_paths_from_coords(graph, start_coord, end_coord, waypoint_coords, max_paths=20):
    """
    start_coord, end_coord, waypoint_coords: (lat, lon) 형식
    내부에서 자동으로 node로 매핑하여 diverse path 생성
    """
    start_node = ox.nearest_nodes(graph, start_coord[1], start_coord[0])
    end_node = ox.nearest_nodes(graph, end_coord[1], end_coord[0])
    waypoint_nodes = [ox.nearest_nodes(graph, lon, lat) for lat, lon in waypoint_coords]

    coords = []
    nodes = []

    # 최단 경로 추가
    path = route_via_multiple_points(graph, [start_node, end_node])
    if path and is_acceptable(graph, path):
        coords.append(nodes_to_coords(graph,path))
        nodes.append(path)

    # 1개 경유지 경로
    for wp in waypoint_nodes:
        path = route_via_multiple_points(graph, [start_node, wp, end_node])
        if path and is_acceptable(graph, path):
            coords.append(nodes_to_coords(graph,path))
            nodes.append(path)
        if len(coords) >= max_paths:
            return coords,nodes
        

    # 2개 경유지 경로
    for wp1, wp2 in permutations(waypoint_nodes, 2):
        path = route_via_multiple_points(graph, [start_node, wp1, wp2, end_node])
        if path and is_acceptable(graph, path):
            coords.append(nodes_to_coords(graph,path))
            nodes.append(path)
        if len(coords) >= max_paths:
            return coords,nodes

    return coords,nodes

def cluster_waypoints_kmeans(G, n_clusters=10):
    """
    그래프 G의 노드 좌표를 kmeans로 클러스터링하고,
    각 클러스터의 대표 지점(중심점)을 반환한다.
    """
    
    coords = []
    for node, data in G.nodes(data=True):
        lat = float(data['y'])
        lon = float(data['x'])
        coords.append((lat, lon))

    coords = np.array(coords)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(coords)

    clustered_centers = []
    for i in range(n_clusters):
        cluster_points = coords[labels == i]
        # kmeans.cluster_centers_가 바로 중심점임
        centroid = tuple(kmeans.cluster_centers_[i])
        clustered_centers.append(centroid)

    return clustered_centers

def is_acceptable(graph, path, max_length=7000):
    if not path:
        return False
    total_length = calc_path_length(graph, path)
    return total_length < max_length

def calc_path_length(graph, path):
    if not path or len(path) < 2:
        return 0
    edges = list(zip(path[:-1], path[1:]))
    total_length = 0
    for u, v in edges:
        data = graph.get_edge_data(u, v)
        if isinstance(data, dict):
            edge_data = list(data.values())[0]
        else:
            edge_data = data
        total_length += edge_data.get('length', 0)
    return total_length