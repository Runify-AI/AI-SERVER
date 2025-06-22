from flask import request
from flask_restx import Resource,reqparse
from app.utils.route.graph import build_walk_graph, generate_diverse_paths_from_coords,cluster_waypoints_kmeans
from app.utils.route.label import coord_getLabel

from tests.data.DummyData import data
from app.model.routeModel import route_ns,UserInput,request_model,response_model

parser = reqparse.RequestParser()
parser.add_argument('start_address',type=str,help='출발지 주소',default="영남대학교")
parser.add_argument('end_address',type=str,help='도착지 주소',default="반월당")

@route_ns.route('/')
class RouteResource(Resource):
    @route_ns.expect(parser,request_model)
    @route_ns.marshal_with(response_model)
    def post(self):
        args = parser.parse_args()
        value = request.get_json()
        
        results = getRoute(args,value)
        return {"paths":results}
    
    
def getRoute(args,value):
    user_input =  UserInput(
        start_address = args["start_address"],
        end_address = args["end_address"]
    )
    # 2. 그래프 생성 + 라벨링 + 선호도 가중치 적용
    G = build_walk_graph(user_input.start_location,user_input.end_location)
    
    all_nodes = G.nodes()
    print(len(all_nodes))
    
    kmeans_nodes = cluster_waypoints_kmeans(G)
    print(len(kmeans_nodes))
    
    all_nodes = G.nodes()
    print(len(all_nodes))

    print(len(kmeans_nodes))


    coords,nodes = generate_diverse_paths_from_coords(
        graph=G,
        start_coord=user_input.start_location,
        end_coord=user_input.end_location,
        waypoint_coords=kmeans_nodes,  # or cluster_nodes
        max_paths=20
    )

    print(f"🔀 생성된 경로 수: {len(nodes)}")

    print(len(coords))

    public_transparent = set()
    paths = []

    for idx,coord in enumerate(coords[:10]):
        summary,all_stop = coord_getLabel(coords[4])
        print(len(all_stop))
        public_transparent.update(all_stop)
        path = {}
        path['path-id'] = idx
        path['feture'] = summary
        path['recommend'] = data[idx]
        path['coord'] = [(float(lat), float(lon)) for lat, lon in coord]
        
        paths.append(path)
        
    print(len(public_transparent))

    return paths