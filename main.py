from datetime import datetime
from flask import Flask, jsonify, request
from marshmallow import ValidationError
import json
from minetest_log_parser.Parser.MinetestLogParser import MinetestLogParser

from schemas.RequestSchemas import LogsSchema, ClustersSchema, ActivityByPosSchema, AuthActivitySchema, \
    IpsHistoryByMaskSchema, IpsHistorySchema

from src.minetest_activity_analysis.ActivitySorter.ActivitySorter import ActivitySorter

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_apispec.extension import FlaskApiSpec


class Config:
    APISPEC_SPEC = APISpec(
        title="Minetest Activity Analysis",
        version="v0.0.1",
        plugins=[MarshmallowPlugin()],
        openapi_version="2.0.0",
    )
    APISPEC_SWAGGER_URL = "/swagger/"  # Corresponds to Documentation
    APISPEC_SWAGGER_UI_URL = "/swagger_ui/"  # Corresponds to MainSwagger UI


app = Flask(__name__)
docs = FlaskApiSpec(app)

# define path to your log-file
# logFilepath = "./debug.txt"
logFilepath = "./all-logs/log.txt"


def get_coordinates(item):
    coordinates = list(map(int, item[0].split()))
    return coordinates


def checkKeys(keysToCheck, targetDict):
    for key in keysToCheck:
        if key not in targetDict:
            return False
    return True


logParser = MinetestLogParser(logFilepath)
activitySorter = ActivitySorter(logParser)


def jsonErrorResponse(messages):
    return json.dumps({
        "result": 'error',
        "msgs": messages
    })


# players - arrays of players names
# actions - arrays of actions. Available: "places node", "digs", "takes", "moves"
@app.route('/api/logs', methods=['POST'])
@use_kwargs(LogsSchema, location="json")
def logs():
    json_data = request.get_json()
    if not json_data:
        return {"message": "Wrong JSON format"}, 400

    validateSchema = LogsSchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [players, actions, dateFrom, dateTo] = validated.values()

    logs = activitySorter.getActions(players, actions, dateFrom, dateTo)
    return jsonify({
        "result": 'success',
        "data": logs
    }), 200

@use_kwargs(ClustersSchema, location="json")
@app.route('/api/logs/clusters', methods=['POST'])
def clusters():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Wrong JSON format"}), 400

    validateSchema = ClustersSchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [players, actions, dateFrom, dateTo, mode, onlyCount] = validated.values()

    logs = activitySorter.getClusters(players, actions, mode, dateFrom, dateTo)

    cluster_points = {}

    if onlyCount:
        for key, val in logs.items():
            lencl = len(val)
            cluster_points[key] = lencl
        logs = cluster_points
        del cluster_points
    sorted_coordinates_dict = dict(sorted(logs.items(), key=get_coordinates))

    return jsonify({
        "result": 'success',
        "data": sorted_coordinates_dict
    })


#
#
@app.post('/api/logs/activity-by-pos')
@use_kwargs(ActivityByPosSchema, location="json")
def activity_pos():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Wrong JSON format"}), 400

    validateSchema = ActivityByPosSchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [players, actions, dateFrom, dateTo, mode, onlyCount, pos, radius] = validated.values()

    new_pos = []
    print(pos)
    for coord in pos:
        new_pos.append(float(coord))
    pos = new_pos
    del new_pos

    logs = activitySorter.getActionsByPos(players, actions, pos, radius, dateFrom=dateFrom, dateTo=dateTo)

    cluster_points = {}
    if onlyCount:
        for key, val in logs.items():
            cluster_points[key] = len(val)
        logs = cluster_points

    return jsonify({
        "result": 'success',
        # "data": logs
        "data": logs
    }), 200


#
#
@app.post('/api/logs/auths')
@use_kwargs(AuthActivitySchema, location="json")
def auths_list():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Wrong JSON format"}), 400

    validateSchema = AuthActivitySchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [players] = validated.values()

    logs = activitySorter.getAuths(players)

    return jsonify({
        "result": 'success',
        "data": logs
    })


@app.post('/api/logs/ips')
@use_kwargs(IpsHistorySchema, location="json")
def ips_list():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Wrong JSON format"}), 400

    validateSchema = AuthActivitySchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [players] = validated.values()

    logs = activitySorter.getAuths(players)

    ips = {}
    for log in logs:
        name = log['name']
        ip = log['ip']
        if name not in ips:
            ips[name] = []
        if ip not in ips[name]:
            ips[name].append(ip)
    del logs
    return jsonify({
        "result": 'success',
        "data": ips
    })


#
@app.post('/api/logs/players/find-by-ips')
@use_kwargs(IpsHistoryByMaskSchema, location="json")
def ips_by_masks_list():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Wrong JSON format"}), 400

    validateSchema = IpsHistoryByMaskSchema()
    try:
        validated = validateSchema.load(data=json_data)
    except ValidationError as err:
        # Return a nice message if validation fails
        return jsonify(err.messages), 400

    [ipMasks] = validated.values()
    print(ipMasks)
    logs = activitySorter.getAuths()

    ips = {}
    for log in logs:
        name = log['name']
        ip = log['ip']
        for ipMask in ipMasks:
            if ipMask in ip:
                if name not in ips:
                    ips[name] = []
                    ips[name].append(ip)

    del logs
    return jsonify({
        "result": 'success',
        "data": ips
    })


docs.register(logs)
docs.register(activity_pos)
docs.register(auths_list)
docs.register(ips_list)
docs.register(ips_by_masks_list)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
