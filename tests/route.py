from itertools import permutations
import networkx as nx
import osmnx as ox

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

import networkx as nx

def print_routes_summary(graph, routes, max_print=5):
    print("\n📌 생성된 경로 요약:")
    for i, path in enumerate(routes[:max_print]):
        # 엣지의 길이 합산
        distance = 0
        for u, v in zip(path[:-1], path[1:]):
            if graph.has_edge(u, v):
                data = graph.get_edge_data(u, v)
                # 여러 엣지가 있는 경우 가장 첫 번째 선택
                if isinstance(data, dict):
                    edge = list(data.values())[0]
                else:
                    edge = data
                distance += edge.get("length", 0)
        print(f"경로 {i+1}: 총 거리 약 {int(distance)}m, 노드 수: {len(path)}개")

    if len(routes) > max_print:
        print(f"...(생략) 총 {len(routes)}개 경로 생성됨")
        
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

def plot_routes_on_graph(G, routes, max_routes=10, title="Routes on Graph"):
    """
    G: networkx 그래프
    routes: 노드 리스트 경로들의 리스트
    max_routes: 한 번에 그릴 경로 개수 제한
    """
    coords = []
    for node, data in G.nodes(data=True):
        lat = float(data['y'])
        lon = float(data['x'])
        coords.append((lat, lon))
    coords = np.array(coords)

    plt.figure(figsize=(10, 8))
    plt.title(title)

    # 모든 노드 회색 점으로
    plt.scatter(coords[:,1], coords[:,0], c='lightgray', s=10, label='Nodes')

    # 경로별 색깔 지정 (최대 max_routes)
    cmap = plt.cm.get_cmap('tab20', max_routes)

    for i, path in enumerate(routes[:max_routes]):
        path_coords = np.array([(G.nodes[n]['y'], G.nodes[n]['x']) for n in path])
        plt.plot(path_coords[:,1], path_coords[:,0], color=cmap(i), linewidth=2, label=f'Route {i+1}')
        plt.scatter(path_coords[:,1], path_coords[:,0], color=cmap(i), s=20)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()


import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString

def coord_getLabel(coords):
    # 1. LineString 생성 (coords는 (위도, 경도) 순서라고 가정)
    line = LineString([(lng, lat) for lat, lng in coords])

    # 2. 약 100m 버퍼 생성 (단위: degree → m로 환산)
    buffer_polygon = line.buffer(100 / 111000)

    # 3. GeoSeries로 변환 + 좌표계 설정 (WGS84)
    buffer_gdf = gpd.GeoSeries([buffer_polygon], crs="EPSG:4326")
        # 4. OSM 데이터 가져오기 (공원, 카페 등 다양한 피처)
    tags = {
        'leisure': True,
        'amenity': True,
        'highway': True,
        'incline': True,
        'lit': True,
        'bicycle': True,
        'waterway':True,
        'shop': True,
        'railway' :True,
    }

    features = ox.features_from_polygon(buffer_gdf[0], tags=tags)
    
        # 5. 태그별 value 집계
    tag_columns = ['highway', 'leisure', 'amenity', 'incline', 
                   'lit', 'bicycle','waterway','shop','railway']
    dfs = []

    for tag in tag_columns:
        if tag in features.columns:
            counts = features[tag].value_counts(dropna=True)
            df = pd.DataFrame({
                'tag': tag,
                'value': counts.index,
                'count': counts.values
            })
            dfs.append(df)

    tag_summary = pd.concat(dfs, ignore_index=True)

    # print(tag_summary)



    # 2. GeoDataFrame으로 버퍼 폴리곤 변환 및 UTM 변환 (면적 계산용)
    buffer_area = buffer_gdf.area.values[0]

    # 3. 공원(park) 집계
    park_area = 0
    park_count = 0
    park_ratio = 0
    if 'leisure' in features.columns:
        parks = features[features['leisure'] == 'park']
        if not parks.empty:
            parks_utm = parks.to_crs(epsg=32652)
            intersection_areas = parks_utm.geometry.intersection(buffer_gdf[0])
            park_area = intersection_areas.area.sum()
            park_count = len(parks)
            park_ratio = park_area / buffer_area if buffer_area > 0 else 0

    # 4. 하천(river) 집계
    river_area = 0
    river_count = 0
    river_ratio = 0

    if 'waterway' in features.columns:
        rivers = features[features['waterway'] == 'river']
        if not rivers.empty:
            rivers_utm = rivers.to_crs(epsg=32652)
            river_area = rivers_utm.geometry.length.sum()
            river_count = len(rivers)
            river_ratio = river_area / buffer_area if buffer_area > 0 else 0

    # 5. 편의시설(amenity) 개수 집계
    amenity_count = 0
    if 'shop' in features.columns:
        amenity_count = features['shop'].notna().sum()


    # 6. 횡단보도(crossing) 개수 집계
    crossing_count = 0
    if 'highway' in features.columns:
        crossing_count = features['highway'].eq('crossing').sum()
        
    # features: ox.features_from_polygon 등으로 얻은 GeoDataFrame

    # 1. 버스정류장 추출
    if 'highway' in features.columns:
        bus_stops = features[features['highway'] == 'bus_stop']
        bus_stop_coords = [(geom.y, geom.x) for geom in bus_stops.geometry if geom.geom_type == 'Point']
    else:
        bus_stop_coords = []

    # 2. 지하철 출입구 추출
    if 'railway' in features.columns:
        subway_entrances = features[features['railway'] == 'subway_entrance']
        subway_coords = [(geom.y, geom.x) for geom in subway_entrances.geometry if geom.geom_type == 'Point']
    else:
        subway_coords = []

    # 3. 합쳐서 반환
    all_stops = bus_stop_coords + subway_coords



    # 7. 결과 출력
    summary = {
        "park": {
            "count": int(park_count),
            "area": float(park_area),
            "ratio": f"{park_ratio:.2%}",
        },
        "river": {
            "count": int(river_count),
            "area": float(river_area),
            "ratio": f"{river_ratio:.2%}",
        },
        "amenity": {
            "count": int(amenity_count),
        },
        "cross": {
            "count": int(crossing_count),
        }
    }

    
    return summary,all_stops
