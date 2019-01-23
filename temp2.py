import requests
import re
import websocket
import json
import ssl
import time
try:
    import thread
except ImportError:
    import _thread as thread
import time



def login():
	payload = {'_username': 'runner12345', '_password': 'runner009900', '_target_path': '/ru/betting'}
	r = requests.post("https://gg11.bet/api/auth/login", data=payload)
	cookie = r.headers.get('Set-Cookie')
	headers = {'cookie': cookie}
	url = "https://gg11.bet/ru/betting"
	r1 = requests.get(url, headers=headers)
	html = r1.text
	token = re.search(r'token: "(.*?)"', html)
	token = token.group(1)
	url2 = "https://async.gg11.bet/?message=%5B%7B%22channel%22%3A%22%2Fmeta%2Fhandshake%22%2C%22version%22%3A%221.0%22%2C%22supportedConnectionTypes%22%3A%5B%22websocket%22%2C%22eventsource%22%2C%22long-polling%22%2C%22cross-origin-long-polling%22%2C%22callback-polling%22%5D%2C%22id%22%3A%221%22%7D%5D&jsonp=__jsonp1__"
	r2 = requests.get(url2, headers=headers)
	response = r2.text
	if re.search(r'"successful":(.*?),', response).group(1):
		player_id = re.search(r'"clientId":"(.*?)"', response).group(1)
	print(token, player_id, cookie)
	return token, player_id, cookie

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("### closed ###")

def on_message(ws, message):
	result = json.loads(message)
	if result['type'] == 'data':
		stake = {  
		   "id":"2",
		   "type":"start",
		   "payload":{  
		      "variables":{  
		         "type":"SINGLE",
		         "stake":38,
		         "odds":[  
		            {  
		               "matchId":result['payload']['data']['matches'][0]['id'],
		               "marketId":"1",
		               "oddId":"1",
		               "ratio":result['payload']['data']['matches'][0]['markets'][0]['odds'][0]['value']
		            }
		         ],
		         "systemSize":[  
		            1
		         ],
		         "freebetId":""
		      },
		      "extensions":{  

		      },
		      "operationName":"PlaceBet",
		      "query":"mutation PlaceBet($type: BetType!, $odds: [PlaceBetOdd!]!, $stake: Float!, $systemSize: [Int!]!, $freebetId: String) {\n  bets: placeBet(type: $type, odds: $odds, stake: $stake, systemSize: $systemSize, freebetId: $freebetId) {\n    id\n    type\n    status\n    stake\n    systemSizes\n    odds {\n      ratio\n      oddId\n      marketId\n      matchId\n    }\n  }\n}\n"
		   }
		}
		ws.send(json.dumps(stake))
	print(message)

def on_open1(ws):
	print("start")


token, player_id, cookie = login()
message = {"type":"connection_init","payload":{"headers":{"X-Auth-Token":token},"X-Auth-Token":token}}
websocket.enableTrace(True)
ws = websocket.WebSocketApp("wss://betting-public-gql.gin.bet/graphql", on_message = on_message, on_error = on_error, on_close = on_close)
ws.on_open = on_open1
ws1 = websocket.WebSocketApp("wss://async.gg11.bet/", on_message = on_message, on_error = on_error, on_close = on_close, cookie = cookie)
ws1.on_open = on_open1
query = {  
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
            "LIVE",
            "NOT_STARTED"
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
ws.run_forever()
ws1.run_forever()
ws.send(json.dumps(message))
ws1.send(json.dumps([]))
ws.send(json.dumps(query))
verification = {"channel":"/meta/connect","clientId":player_id,"connectionType":"websocket","id":"2"}
ws1.send(json.dumps([json.dumps(verification)]))
#ws = websocket.create_connection("wss://betting-public-gql.gin.bet/graphql", ssl=True)



# print("Sent")
# print("Reeiving...")
# result =  ws.recv()
# print("Received '%s'" % result)
# res = []
# result =  ws.recv()
# print("Received '%s'" % result)
# result = json.loads(result)
# #print(result['payload']['data']['matches'][0]['markets'])
# #print(result['payload']['data']['matches'][0]['id'])
# #print(res)
# stake = {  
#    "id":"10",
#    "type":"start",
#    "payload":{  
#       "variables":{  
#          "type":"SINGLE",
#          "stake":38,
#          "odds":[  
#             {  
#                "matchId":result['payload']['data']['matches'][0]['id'],
#                "marketId":"1",
#                "oddId":"1",
#                "ratio":result['payload']['data']['matches'][0]['markets'][0]['odds'][0]['value']
#             }
#          ],
#          "systemSize":[  
#             1
#          ],
#          "freebetId":""
#       },
#       "extensions":{  

#       },
#       "operationName":"PlaceBet",
#       "query":"mutation PlaceBet($type: BetType!, $odds: [PlaceBetOdd!]!, $stake: Float!, $systemSize: [Int!]!, $freebetId: String) {\n  bets: placeBet(type: $type, odds: $odds, stake: $stake, systemSize: $systemSize, freebetId: $freebetId) {\n    id\n    type\n    status\n    stake\n    systemSizes\n    odds {\n      ratio\n      oddId\n      marketId\n      matchId\n    }\n  }\n}\n"
#    }
# }
# ws.send(json.dumps(stake))
# result =  ws.recv()
# print("Received '%s'" % result)
# time.sleep(20)
# result =  ws.recv()
# print("Received '%s'" % result)
# time.sleep(20)
# result =  ws.recv()
# print("Received '%s'" % result)
# ws.close()
