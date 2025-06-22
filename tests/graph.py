import osmnx as ox
import networkx as nx
from typing import Tuple
from input import UserInput

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

def label_nodes(G: nx.MultiDiGraph) -> None:
    """
    노드에 라벨 부여: 예시로 '공원' 또는 '강변' 여부만 간단 표시
    실제 구현에서는 더 많은 특성 가능
    """
    for node_id, data in G.nodes(data=True):
        # osmnx가 제공하는 주변 POI (point of interest) 또는 위치태그 활용
        if 'park' in str(data.get('name', '')).lower():
            G.nodes[node_id]['tag'] = 'park'
        elif 'river' in str(data.get('name', '')).lower():
            G.nodes[node_id]['tag'] = 'river'
        else:
            G.nodes[node_id]['tag'] = 'normal'
            
def apply_preference_weights(G: nx.MultiDiGraph, preferences: dict) -> None:
    """
    사용자 선호도에 따라 도보 경로(edge)의 가중치를 조정
    - 공원 등 선호 장소가 포함되면 가중치를 낮춤
    - 어두운 길, 경사 등 피하고 싶은 조건은 가중치를 높임
    """
    for u, v, k, data in G.edges(keys=True, data=True):
        base_weight = data.get('length', 1)  # m 기준
        
        # 예시: 태그가 있는 노드 포함 시
        tags = [
            G.nodes[u].get('tag', 'normal'),
            G.nodes[v].get('tag', 'normal')
        ]
        
        # 기본 가중치 보정
        if 'park' in tags and 'park' in preferences.get('preferred_places', []):
            base_weight *= 0.7  # 선호: 더 짧게
        if 'river' in tags and 'river' in preferences.get('preferred_places', []):
            base_weight *= 0.8

        if 'dark' in preferences.get('avoid_conditions', []):
            # 실제 조명 데이터 없다면 예시로 강변/골목 등 어둡다고 가정
            if 'river' in tags:
                base_weight *= 1.5

        G.edges[u, v, k]['weight'] = base_weight

def prepare_graph_for_user(user_input: UserInput) -> nx.MultiDiGraph:
    G = build_walk_graph(user_input.start_location, user_input.end_location)
    label_nodes(G)
    apply_preference_weights(G, user_input.preferences)
    return G