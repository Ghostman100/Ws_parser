import requests
import re
import websocket
import json
import ssl
try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    print(message)
    if message[0] == 'a':
        a = message[1:]
        a = json.loads(a)[0]
        a = json.loads(a)
        # print(a)
        if a['method'] == "match":
            print(a['body']['meta']["home_team/name"] + " vs " + a['body']['meta']["away_team/name"])
            if a['body']['markets'][2]['odds'][0]['is_active']:
                print("1st match " + a['body']['markets'][2]['odds'][0]['value'] + "-" + a['body']['markets'][2]['odds'][1]['value'])
            else:
                print("1st match not active")
            if a['body']['markets'][1]['odds'][0]['is_active']:
                print("2st match " + a['body']['markets'][1]['odds'][0]['value'] + "-" + a['body']['markets'][1]['odds'][1]['value'])
            else:
                print("2st match not active")
        print()

    else:
        print(message)

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("### closed ###")

def on_open(ws):
    url = "https://gg11.bet/ru/betting"
    r1 = requests.get(url)
    html = r1.text
    token = re.search(r'token: "(.*?)"', html)
    token = token.group(1)
    ws1 = websocket.create_connection("wss://betting-public-gql.gin.bet/graphql", ssl=True)
    message = {"type":"connection_init","payload":{"headers":{"X-Auth-Token":token},"X-Auth-Token":token}}
    q1 = {  
       "id":"1",
       "type":"start",
       "payload":{  
          "variables":{  
             "offset":0,
             "limit":20,
             "marketStatuses":[  
                "ACTIVE",
                "SUSPENDED"
             ],
             "matchStatuses":[  
                "LIVE"
             ],
             "sportEventTypes":[  
                "MATCH"
             ],
             "sportIds":[ 
                "esports_dota_2"
             ],
             "providerIds":[  

             ]
          },
          "extensions":{  

          },
          "operationName":"GetMatchesByFilters",
          "query":"query GetMatchesByFilters($offset: Int!, $limit: Int!, $search: String, $dateFrom: String, $dateTo: String, $providerIds: [Int!], $matchStatuses: [SportEventStatus!], $sportIds: [String!], $tournamentIds: [String!], $competitorIds: [String!], $marketStatuses: [MarketStatus!], $marketLimit: Int = 1, $dateSortAscending: Boolean, $sportEventTypes: [SportEventType!], $withMarketsCount: Boolean = true, $marketTypes: [Int!]) {\n  matches: sportEventsByFilters(offset: $offset, limit: $limit, searchString: $search, dateFrom: $dateFrom, dateTo: $dateTo, providerIds: $providerIds, matchStatuses: $matchStatuses, sportIds: $sportIds, tournamentIds: $tournamentIds, competitorIds: $competitorIds, marketStatuses: $marketStatuses, sportEventTypes: $sportEventTypes, dateSortAscending: $dateSortAscending, marketLimit: $marketLimit, marketTypes: $marketTypes) {\n    ...Match\n    marketsCount @include(if: $withMarketsCount)\n  }\n}\n\nfragment Match on SportEvent {\n  id\n  disabled\n  providerId\n  hasMatchLog\n  fixture {\n    ...MatchFixture\n  }\n  markets {\n    id\n    name\n    status\n    typeId\n    priority\n    specifiers {\n      name\n      value\n    }\n    odds {\n      id\n      name\n      value\n      isActive\n      status\n      competitorId\n    }\n  }\n}\n\nfragment MatchFixture on SportEventFixture {\n  score\n  title\n  status\n  type\n  startTime\n  sportId\n  liveCoverage\n  streams {\n    id\n    locale\n    url\n  }\n  tournament {\n    id\n    name\n    masterId\n    countryCode\n    logo\n    description\n    showTournamentInfo\n    prizePool\n    dateStart\n    dateEnd\n    isLocalizationOverridden\n  }\n  competitors {\n    id: masterId\n    name\n    type\n    homeAway\n    logo\n    templatePosition\n  }\n}\n"
       }
    }
    ws1.send(json.dumps(message))
    ws1.send(json.dumps(q1))
    print("Sent")
    print("Reeiving...")
    result =  ws1.recv()
    print("Received '%s'" % result)
    res = []
    result =  ws1.recv()
    result = json.loads(result)
    for mat in result['payload']['data']['matches']:
        res.append(mat['id'])
    #print(result['payload']['data']['matches'][0]['id'])
    ws1.close()
    #message = [{"uid":"1","method":"auth","params":{"token": token}}]
    message = {"uid": "1","method": "auth","params": {"token": token}}
    #message = {"type":"connection_init","payload":{"headers":{"X-Auth-Token":token},"X-Auth-Token":token}}
    #match = input()
    q = []
    for match in res:
        q.append({"uid":"2","method":"match_subscribe","params":{"match": match}})
    #q = [{"uid":"2","method":"match_subscribe","params":{"match": "4:165867"}}, {"uid":"2","method":"match_subscribe","params":{"match": "4:165862"}}]
    print(q)
    ws.send(json.dumps([json.dumps(message)]))
    ws.send(json.dumps([json.dumps(q)]))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://betting-async.gin.bet/sockjs/089/0h5wfxpj/websocket",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
