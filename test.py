import requests
import re
import json
import datetime
# import ssl
from time import sleep
import threading
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
SITE = "wss://gg11.bet/ru/betting/match/"


def bet(ws, id, marketId, oddId, ratio, amount):
    global graphCount
    stake = {
        "id": str(graphCount),
        "type": "start",
        "payload": {
            "variables": {
                "type": "SINGLE",
                "stake": float(amount),
                "odds": [
                    {
                        "matchId": id,
                        "marketId": marketId,
                        "oddId": oddId,
                        "ratio": float(ratio)
                    }
                ],
                "systemSize": [
                    1
                ],
                "freebetId": ""
            },
            "extensions": {

            },
            "operationName": "PlaceBet",
            "query": "mutation PlaceBet($type: BetType!, $odds: [PlaceBetOdd!]!, $stake: Float!, $systemSize: [Int!]!, $freebetId: String) {\n  bets: placeBet(type: $type, odds: $odds, stake: $stake, systemSize: $systemSize, freebetId: $freebetId) {\n    id\n    type\n    status\n    stake\n    systemSizes\n    odds {\n      ratio\n      oddId\n      marketId\n      matchId\n    }\n  }\n}\n"
        }
    }
    graphCount += 1
    f = open('bets.txt', 'a')
    f.write("потсавил Json" + json.dumps(stake))
    print("потсавил Json" + json.dumps(stake))
    print(json.dumps(stake))
    ws.send(json.dumps(stake))
    f.write("Поставил " + str(amount) + "\n")
    f.write(datetime.datetime.now())
    f.close()


def on_messageP(ws, message):
    print("Parse:")
    # print(message)
    if message[0] == 'a':
        a = message[1:]
        a = json.loads(a)[0]
        if type(a) == type:
            a = a[0]
        a = json.loads(a)
        # print(a)
        if a['method'] == "match":
            score = a['body']['fixture']['score']
            round = int(score[0]) + int(score[-1]) + 1
            league_name = a['body']['meta']["tournament/name"]
            start_time = a['body']['fixture']["start_time"]
            mapsNum = []
            global maps
            global bets
            for mapp in a["body"]['markets']:
                if mapp['id'] in maps:
                    mapsNum.append(a["body"]["markets"].index(mapp))
            print(a['body']['meta']["home_team/name"] + " vs " + a['body']['meta']["away_team/name"])
            for i in mapsNum:
                if a['body']['markets'][i]['odds'][0]['is_active']:
                    print(a['body']['markets'][i]["specifiers"]["mapnr"] + " match " + a['body']['markets'][i]['odds'][0]['value'] + "-" + a['body']['markets'][i]['odds'][1]['value'])
                    if int(a['body']['markets'][i]["specifiers"]["mapnr"]) == round:
                        data = {
                              "live_games":[
                                 {
                                    "date": "",
                                    "is_live": "true",
                                    "league_name": league_name,
                                    "details":[
                                       [
                                          [
                                             a['body']['markets'][i]['odds'][0]['value'],
                                             a['body']['markets'][i]['odds'][1]['value']
                                          ],
                                          "ПОБЕДИТЕЛЬ. КАРТА " + str(round)
                                       ]
                                    ],
                                    "teams":[
                                       a['body']['meta']["home_team/name"],
                                       a['body']['meta']["away_team/name"]
                                    ],
                                    "url": SITE + a['body']['id']
                                 }
                              ]
                           }
                        data = {"data": json.dumps(data), "betting_site": "ws_gg11_bet"}
                        response = requests.post("http://dotapicker.pro/betting_games/feed_data", data=data)
                        print(response)
                        res = requests.get("http://dotapicker.pro/betting_games/predictions?bankroll=2000&betting_site=ws_gg11_bet")
                        res = json.loads(res.text)
                        if res:
                            id = a['body']["id"]
                            for match in res:
                                if match['url'][32:] == id:
                                    marketId = "50m" + str(round)
                                    if a['body']['meta']["home_team/name"] == match['team']:
                                        oddId = "1"
                                    else:
                                        oddId = "2"
                                    ratio = a['body']['markets'][i]['odds'][int(oddId) - 1]['value']
                                    bets[match['id']] = {"matchId": id, "marketId": marketId, "oddId": oddId, "ratio": ratio, "map": match['map'], "team": match['team'], "model": match["prediction_model"], "amount": match['amount']}
    global live
    global subscribed
    global parseCount
    if message[0] == 'h':
        print(message)
        if live:
            matches = []
            for match in live:
                if match not in subscribed:
                    matches.append(match)
                    subscribed.append(match)
            query = []
            if matches:
                for match in matches:
                    query.append({"uid": str(parseCount), "method": "match_subscribe", "params": {"match": match}})
                    parseCount += 1
                ws.send(json.dumps([json.dumps(query)]))
                print(json.dumps([json.dumps(query)]))
                print(2)

        matches = []
        for match in subscribed:
            if match not in live:
                matches.append(match)
                subscribed.remove(match)
        query = []
        if matches:
            for match in matches:
                query.append({"uid": str(parseCount), "method": "match_unsubscribe", "params": {"match": match}})
                parseCount += 1
            ws.send(json.dumps([json.dumps(query)]))
            print(json.dumps([json.dumps(query)]))
            print(3)


def on_error(ws, error):
    print(error)


def on_closeP(ws):
    print("### Parser closed ###")
    global parser_start
    parser_start = False


def on_closeG(ws):
    print("### Graphql closed ###")
    global graph_start
    graph_start = False


def on_openP(ws):
    print("run")
    global token
    global live
    global subscribed
    global parseCount
    while (not live):
        sleep(5)
    query = []
    message = {"uid": "1", "method": "auth", "params": {"token": token}}
    for match in live:
        query.append({"uid": str(parseCount), "method": "match_subscribe", "params": {"match": match}})
        parseCount += 1
        subscribed.append(match)
    print(json.dumps([json.dumps(message)]))
    print(0)
    ws.send(json.dumps([json.dumps(message)]))
    print(json.dumps([json.dumps(query)]))
    print(1)
    ws.send(json.dumps([json.dumps(query)]))


def on_messageG(ws, message):
    print("graphql:")
    print(message)
    f = open('graphql.txt', 'a')
    f.write(message + "\n")
    f.close()
    message = json.loads(message)
    global live
    global graphCount
    global bets
    if "errors" in message['payload']:
        return
    if "bets" in message['payload']["data"]:
        id = message['payload']["data"]['bets']['odds'][0]['matchId']
        for key, match in bets.items():
            if match['matchId'] == id:
                data = {
                    "map": match['map'],
                    "amount": match['amount'],
                    "team": match['team'],
                    "bet": float(match['ratio']),
                    "prediction_model": match["model"]
                }
                url = 'http://dotapicker.pro/betting_games/' + str(key) +'/update_bet_details'
                response = requests.post(url, data)
                print(response.text)
                print("send отчет")
                del bets[key]
        return
    if message["type"] == 'data':
        live = []
        for mat in message['payload']['data']['matches']:
            live.append(mat['id'])
        live_games = []
        for match in message["payload"]["data"]["matches"]:
            league_name = match["fixture"]['tournament']['name']
            live_games.append({
                                    "date": "",
                                    "is_live": "true",
                                    "league_name": league_name,
                                    "details": [],
                                    "teams": [
                                        match["fixture"]["competitors"][0]["name"],
                                        match["fixture"]["competitors"][1]["name"]
                                    ],
                                    "url": SITE + match['id']
                                 })
        d = {"betting_games": live_games}
        data = {"data": json.dumps(d), "betting_site": "ws_gg11_bet"}
        print(json.dumps(data))
        response = requests.post("http://dotapicker.pro/betting_games/feed_data", data=data)
        print(response)
        count = 0
        while(count < 5):
            f = open('text.txt', 'a')
            sleep(12)
            count += 1
            f.write(str(bets) + "\n")
            if bets:
                print(str(bets))
                for key, match in bets.items():
                    bet(ws, match['matchId'], match['marketId'], match["oddId"], match["ratio"], match["amount"])
            f.close()
        query = {
            "id": str(graphCount),
            "type": "start",
            "payload": {
                "variables": {
                    "offset": 0,
                    "limit": 20,
                    "marketStatuses": [
                        "ACTIVE",
                        "SUSPENDED"
                    ],
                    "matchStatuses": [
                        "LIVE"
                    ],
                    "sportEventTypes": [
                        "MATCH"
                    ],
                    "sportIds": [
                        "esports_dota_2"
                    ],
                    "providerIds": [
                    ]
                },
                "extensions": {

                },
                "operationName": "GetMatchesByFilters",
                "query": "query GetMatchesByFilters($offset: Int!, $limit: Int!, $search: String, $dateFrom: String, $dateTo: String, $providerIds: [Int!], $matchStatuses: [SportEventStatus!], $sportIds: [String!], $tournamentIds: [String!], $competitorIds: [String!], $marketStatuses: [MarketStatus!], $marketLimit: Int = 1, $dateSortAscending: Boolean, $sportEventTypes: [SportEventType!], $withMarketsCount: Boolean = true, $marketTypes: [Int!]) {\n  matches: sportEventsByFilters(offset: $offset, limit: $limit, searchString: $search, dateFrom: $dateFrom, dateTo: $dateTo, providerIds: $providerIds, matchStatuses: $matchStatuses, sportIds: $sportIds, tournamentIds: $tournamentIds, competitorIds: $competitorIds, marketStatuses: $marketStatuses, sportEventTypes: $sportEventTypes, dateSortAscending: $dateSortAscending, marketLimit: $marketLimit, marketTypes: $marketTypes) {\n    ...Match\n    marketsCount @include(if: $withMarketsCount)\n  }\n}\n\nfragment Match on SportEvent {\n  id\n  disabled\n  providerId\n  hasMatchLog\n  fixture {\n    ...MatchFixture\n  }\n  markets {\n    id\n    name\n    status\n    typeId\n    priority\n    specifiers {\n      name\n      value\n    }\n    odds {\n      id\n      name\n      value\n      isActive\n      status\n      competitorId\n    }\n  }\n}\n\nfragment MatchFixture on SportEventFixture {\n  score\n  title\n  status\n  type\n  startTime\n  sportId\n  liveCoverage\n  streams {\n    id\n    locale\n    url\n  }\n  tournament {\n    id\n    name\n    masterId\n    countryCode\n    logo\n    description\n    showTournamentInfo\n    prizePool\n    dateStart\n    dateEnd\n    isLocalizationOverridden\n  }\n  competitors {\n    id: masterId\n    name\n    type\n    homeAway\n    logo\n    templatePosition\n  }\n}\n"
            }
        }
        ws.send(json.dumps(query))
        graphCount += 1


def on_openG(ws):
    print("run")
    global token
    payload = {'_username': 'runner12345', '_password': 'runner009900', '_target_path': '/ru/betting'}
    response = requests.post("https://gg11.bet/api/auth/login", data=payload)
    html = response.text
    token = re.search(r'token: "(.*?)"', html)
    token = token.group(1)
    message = {"type": "connection_init",
               "payload": {"headers": {"X-Auth-Token": token}, "X-Auth-Token": token}}
    ws.send(json.dumps(message))
    query = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {
                "offset": 0,
                "limit": 20,
                "marketStatuses": [
                    "ACTIVE",
                    "SUSPENDED"
                ],
                "matchStatuses": [
                    "LIVE"
                ],
                "sportEventTypes": [
                    "MATCH"
                ],
                "sportIds": [
                    "esports_dota_2"
                ],
                "providerIds": [
                ]
            },
            "extensions": {

            },
            "operationName": "GetMatchesByFilters",
            "query": "query GetMatchesByFilters($offset: Int!, $limit: Int!, $search: String, $dateFrom: String, $dateTo: String, $providerIds: [Int!], $matchStatuses: [SportEventStatus!], $sportIds: [String!], $tournamentIds: [String!], $competitorIds: [String!], $marketStatuses: [MarketStatus!], $marketLimit: Int = 1, $dateSortAscending: Boolean, $sportEventTypes: [SportEventType!], $withMarketsCount: Boolean = true, $marketTypes: [Int!]) {\n  matches: sportEventsByFilters(offset: $offset, limit: $limit, searchString: $search, dateFrom: $dateFrom, dateTo: $dateTo, providerIds: $providerIds, matchStatuses: $matchStatuses, sportIds: $sportIds, tournamentIds: $tournamentIds, competitorIds: $competitorIds, marketStatuses: $marketStatuses, sportEventTypes: $sportEventTypes, dateSortAscending: $dateSortAscending, marketLimit: $marketLimit, marketTypes: $marketTypes) {\n    ...Match\n    marketsCount @include(if: $withMarketsCount)\n  }\n}\n\nfragment Match on SportEvent {\n  id\n  disabled\n  providerId\n  hasMatchLog\n  fixture {\n    ...MatchFixture\n  }\n  markets {\n    id\n    name\n    status\n    typeId\n    priority\n    specifiers {\n      name\n      value\n    }\n    odds {\n      id\n      name\n      value\n      isActive\n      status\n      competitorId\n    }\n  }\n}\n\nfragment MatchFixture on SportEventFixture {\n  score\n  title\n  status\n  type\n  startTime\n  sportId\n  liveCoverage\n  streams {\n    id\n    locale\n    url\n  }\n  tournament {\n    id\n    name\n    masterId\n    countryCode\n    logo\n    description\n    showTournamentInfo\n    prizePool\n    dateStart\n    dateEnd\n    isLocalizationOverridden\n  }\n  competitors {\n    id: masterId\n    name\n    type\n    homeAway\n    logo\n    templatePosition\n  }\n}\n"
        }
    }
    ws.send(json.dumps(query))


class Parse (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        # self.counter = counter

    def run(self):

        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://betting-async.gin.bet/sockjs/089/0h5wfxpj/websocket",
                                    on_message=on_messageP,
                                    on_error=on_error,
                                    on_close=on_closeP)
        ws.on_open = on_openP
        print("run parse")
        ws.run_forever()


class Graphql (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        # self.counter = counter

    def run(self):
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp("wss://betting-public-gql.gin.bet/graphql",
                                on_message=on_messageG,
                                on_error=on_error,
                                on_close=on_closeG)
        ws.on_open = on_openG
        print("run graphql")
        ws.run_forever()


x = 0
# Create new threads

parser_start = False
graph_start = False

maps = ["50m1", "50m2", "50m3"]
thread2 = Graphql(2, "Graphql")
thread1 = Parse(1, "Websocket")
parseCount = 2
graphCount = 2
subscribed = []
live = []
bets = {}
# Start new Threads
c = 0
while (c < 10):
    if graph_start:
        thread2.start()
        graph_start = True
    if parser_start:
        thread1.start()
        parser_start = True
    sleep(30)
thread2.join()
thread1.join()
print("Exiting Main Thread")
