from datetime import datetime
from bottle import route, run, post, request, response
import json
from minetest_log_parser.Parser.MinetestLogParser import MinetestLogParser
from src.minetest_activity_analysis.src.ActivitySorter.ActivitySorter import ActivitySorter

# define path to your log-file
logFilepath = "./debug.txt"


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


def dateStrToTimestamp(date):
    date_format = "%d-%m-%Y %H:%M"
    try:
        date_obj = datetime.strptime(date, date_format)
        if date_obj:
            timestamp = date_obj.timestamp()
            return timestamp
        else:
            return None
    except ValueError:
        return None


# players - arrays of players names
# actions - arrays of actions. Available: "places node", "digs", "takes", "moves"
@post('/api/logs')
def logs():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    response.content_type = 'application/json'

    if not checkKeys(['players', 'actions'], postdata):
        return jsonErrorResponse(["Fields players and actions is required."])

    [players, actions] = [postdata['players'], postdata['actions']]

    dateFrom = None
    dateTo = None
    if "from" in postdata:
        dateFrom = dateStrToTimestamp(postdata['from'])
        if dateFrom is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])
    if "to" in postdata:
        dateTo = dateStrToTimestamp(postdata['to'])
        if dateTo is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])

    logs = activitySorter.getActions(players, actions, dateFrom, dateTo)
    return json.dumps({
        "result": 'success',
        "data": logs
    })


@post('/api/logs/clusters')
def logs2():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    [players, actions] = [postdata['players'], postdata['actions']]

    if not checkKeys(['players', 'actions'], postdata):
        return jsonErrorResponse(["Fields players and actions is required."])

    mode = '2d'
    if 'mode' in postdata and mode in ['2d', '3d']:
        mode = postdata['mode']

    onlyCount = False
    if 'onlyCount' in postdata and type(postdata['onlyCount'] == type(True)):
        onlyCount = bool(postdata['onlyCount'])

    dateFrom = None
    dateTo = None
    if "from" in postdata:
        dateFrom = dateStrToTimestamp(postdata['from'])
        if dateFrom is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])
    if "to" in postdata:
        dateTo = dateStrToTimestamp(postdata['to'])
        if dateTo is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])

    logs = activitySorter.getClusters(players, actions, mode, dateFrom, dateTo)

    response.content_type = 'application/json'
    cluster_points = {}
    for key, val in logs.items():
        lencl = len(val)
        cluster_points[key] = lencl
    logs = cluster_points
    del cluster_points
    sorted_coordinates_dict = dict(sorted(logs.items(), key=get_coordinates))
    return json.dumps({
        "result": 'success',
        # "data": logs
        "data": sorted_coordinates_dict
    })


@post('/api/logs/activity-by-pos')
def logs3():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    [players, actions, pos] = [postdata['players'], postdata['actions'], postdata['pos']]

    dateFrom = None
    dateTo = None
    if "from" in postdata:
        dateFrom = dateStrToTimestamp(postdata['from'])
        if dateFrom is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])
    if "to" in postdata:
        dateTo = dateStrToTimestamp(postdata['to'])
        if dateTo is None:
            return jsonErrorResponse(['Wrong date format. Try dd-mm-yyyy hh:ii'])



    raidus = 100
    if 'radius' in postdata:
        raidus = int(postdata['radius'])
    if 'onlyCount' in postdata and type(postdata['onlyCount'] == type(True)):
        onlyCount = bool(postdata['onlyCount'])
    new_pos = []
    print(pos)
    for coord in pos:
        new_pos.append(float(coord))
    pos = new_pos
    del new_pos

    logs = activitySorter.getActionsByPos(players, actions, pos, raidus, dateFrom=dateFrom, dateTo=dateTo)

    response.content_type = 'application/json'
    cluster_points = {}
    if onlyCount:
        for key, val in logs.items():
            cluster_points[key] = len(val)
        logs = cluster_points

    return json.dumps({
        "result": 'success',
        # "data": logs
        "data": logs
    })


@post('/api/logs/auths')
def logs2():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    [players] = [postdata['players']]

    logs = activitySorter.getAuths(players)
    response.content_type = 'application/json'

    return json.dumps({
        "result": 'success',
        "data": logs
    })


@post('/api/logs/ips')
def logs2():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    [players] = [postdata['players']]

    logs = activitySorter.getAuths(players)
    response.content_type = 'application/json'

    ips = {}
    for log in logs:
        name = log[1]
        ip = log[2]
        if name not in ips:
            ips[name] = []
        if ip not in ips[name]:
            ips[name].append(ip)
    del logs
    return json.dumps({
        "result": 'success',
        "data": ips
    })


@post('/api/logs/players/find-by-ips')
def logs2():
    postdata = json.loads(request.body.getvalue().decode('utf-8'))
    [ipMasks] = [postdata['ips']]

    logs = activitySorter.getAuths()
    response.content_type = 'application/json'

    ips = {}
    for log in logs:
        name = log[1]
        ip = log[2]
        for ipMask in ipMasks:
            if ipMask in ip:
                if name not in ips:
                    ips[name] = []
                    ips[name].append(ip)

    del logs
    return json.dumps({
        "result": 'success',
        "data": ips
    })


run(host='localhost', port=8080)
