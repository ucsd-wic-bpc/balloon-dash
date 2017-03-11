import sys
sys.path.append('gen-py')

import click
import json
from flask import Flask, render_template, request, redirect

from thrift import Thrift
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol

from competition_server_service import CompetitionServer
from competition_server_service.ttypes import (
    CompetitionSettings, LeaderboardServerNotReadyException, NotWatchingCompetitionException
)

app = Flask(__name__)

competition_server_transport = None
competition_server_client = None

def isStubRegistered(stub):
    try:
        competition_server_transport.open()
        return competition_server_client.isWatching(stub)
    finally:
        competition_server_transport.close()

@app.route('/', methods=['GET'])
def root():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def root_post():
    return redirect("/contest/{}".format(request.form['stub']))

@app.route('/register', methods=['GET'])
def register_get():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    stub = request.form['stub']
    if isStubRegistered(stub):
        return "Success!"

    alert_threshold = json.loads(request.form['alerts'])
    username = request.form['username']
    password = request.form['password']
    if request.form['categories']:
        categories = json.loads(request.form['categories'])
    else:
        categories = {}

    if request.form['tags']:
        tags = json.loads(request.form['tags'])
        for key, value in tags.items():
            if not isinstance(value, list):
                tags[key] = [value]
    else:
        tags = {}

    settings = CompetitionSettings(
        alert_thresholds=alert_threshold,
        stub=stub,
        username=username,
        password=password,
        categories=categories,
        tags=tags
    )

    try:
        competition_server_transport.open()
        competition_server_client.watchCompetition(settings)
    finally:
        competition_server_transport.close()

    return "Success!"


@app.route('/update/<stub>')
def update_get(stub):

    try:
        competition_server_transport.open()
        users = competition_server_client.getUpdatedUserList(stub)
        tags = {}
        categories = {}
        for user in users:
            tags.setdefault(user.username, []).extend(user.tags)
            categories[user.username] = user.category

        return render_template('update.html', stub=stub, categories=json.dumps(categories),
                               tags=json.dumps(tags))

    except LeaderboardServerNotReadyException as e:
        return "ERROR: {}".format(e.message)
    except NotWatchingCompetitionException:
        return "ERROR: Competition server not watching {}".format(stub)
    finally:
        competition_server_transport.close()


@app.route('/update/<stub>', methods=['POST'])
def update_post(stub):

    categories = json.loads(request.form['categories'])
    tags = json.loads(request.form['tags'])
    for username in tags:
        if not isinstance(tags[username], list):
            tags[username] = [tags[username]]


    try:
        competition_server_transport.open()
        competition_server_client.updateCategories(stub, categories)
        competition_server_client.updateTags(stub, tags)

        return "Success!"

    except NotWatchingCompetitionException:
        return "ERROR: Competition server not watching {}".format(stub)
    finally:
        competition_server_transport.close()

@app.route('/contest/<stub>')
def contests_access(stub):
    return render_template('contest.html', stub=stub)

@app.route('/api/<stub>', methods=['GET'])
def contests(stub):
    response = {"error": 0}
    try:
        competition_server_transport.open()
        users = competition_server_client.getUpdatedUserList(stub)
        categories = {}
        for user in users:
            categories.setdefault(user.category, {})[user.username] = {
                "username": user.username,
                "completed_problems": user.completed_problems,
                "acked_alerts": user.acked_alerts,
                "pending_alerts": user.pending_alerts,
                "category": user.category,
                "tags": user.tags
            }
        response["users"] = categories
        return json.dumps(response)
    except LeaderboardServerNotReadyException as e:
        return json.dumps({"error": 1, "message": e.message})
    except NotWatchingCompetitionException as e:
        return json.dumps({"error": 1, "message": "Competition server not watching {}".format(stub)})
    finally:
        competition_server_transport.close()


@app.route('/api/<stub>', methods=['POST'])
def ack_balloons(stub):
    try:
        competition_server_transport.open()
        acked_alerts = json.loads(request.data)
        competition_server_client.ackAlerts(stub, acked_alerts)
        return json.dumps({"error": 0})
    except Exception as e:
        return json.dumps({"error": 1, "message": str(e)})
    finally:
        competition_server_transport.close()

@click.command()
@click.option('--port', default=8080)
@click.option('--competitionserverurl', type=str, required=True)
@click.option('--competitionserverport', type=int, required=True)
def main(port, competitionserverurl, competitionserverport):
    transport = TSocket.TSocket(competitionserverurl, competitionserverport)

    global competition_server_transport
    competition_server_transport = TTransport.TBufferedTransport(transport)

    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    global competition_server_client
    competition_server_client = CompetitionServer.Client(protocol)

    app.run('0.0.0.0', port)

if __name__ == '__main__':
    main()
