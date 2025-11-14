from app.schemas.routeModel import UserInput
from app.utils.route.graph import *
from app.utils.route.label import *


def getRoute(start_location,end_location=None):
    # 2. 그래프 생성 + 라벨링 + 선호도 가중치 적용
    G = build_walk_graph(start_location,end_location)

    all_nodes = G.nodes()
    print(len(all_nodes))

    kmeans_nodes = cluster_waypoints_kmeans(G)
    print(len(kmeans_nodes))

    all_nodes = G.nodes()
    print(len(all_nodes))

    print(len(kmeans_nodes))


    coords,nodes = generate_diverse_paths_from_coords(
        graph=G,
        start_coord=start_location,
        end_coord=end_location,
        waypoint_coords=kmeans_nodes,  # or cluster_nodes
        max_paths=10
    )

    print(f"🔀 생성된 경로 수: {len(nodes)}")

    print(len(coords))
    paths = []

    for idx, (coord, node_path) in enumerate(zip(coords[:10], nodes[:10])):

        summary = coord_getLabel(coord)

        slope = compute_path_slope(G,node_path)

        path = {'pathId': idx, 'feature': summary,'slope' : slope,'distance': compute_path_distance(G, node_path),
                'coord': [(float(lat), float(lon)) for lat, lon in coord]}



        paths.append(path)


    return paths