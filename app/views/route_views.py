from flask import request
from flask_restx import Resource,reqparse

from app.schemas.routeModel import route_ns, request_model,response_model
from app.service.route import *

parser = reqparse.RequestParser()

@route_ns.route('/')
class RouteResource(Resource):
    @route_ns.expect(parser,request_model)
    @route_ns.marshal_with(response_model)
    def post(self):
        value = request.get_json()
        
        paths = getRoute(value["startAddr"],value.get("endAddr"))

        print(paths[0])
        paths = recommend_paths(paths,value)
        print(paths[0])
        return {"paths":paths}
    
    
