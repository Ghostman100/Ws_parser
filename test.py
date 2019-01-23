import requests
import re
import websocket
import json
import ssl
import time
import threading
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time

exitFlag = 0

class Parse (threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		#self.counter = counter
	def run(self):
	    websocket.enableTrace(True)
	    ws = websocket.WebSocketApp("wss://betting-async.gin.bet/sockjs/089/0h5wfxpj/websocket",
	                              on_message = on_message,
	                              on_error = on_error,
	                              on_close = on_close)
	    ws.on_open = on_open
	    ws.run_forever()
	def on_message(ws, message):
	    print(message)

	def on_error(ws, error):
	    print(error)

	def on_close(ws):
	    print("### closed ###")

	def on_open(ws):
	    print("run")
	    global live
	    while (live == []):
	    	sleep(5)


class Graphql (threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		#self.counter = counter
	def run(self):
		websocket.enableTrace(True)
	    ws = websocket.WebSocketApp("wss://betting-public-gql.gin.bet/graphql",
	                          on_message = on_message,
	                          on_error = on_error,
	                          on_close = on_close)
		ws.on_open = on_open
		ws.run_forever()
	def on_message(ws, message):
	    print(message)
	    message = json.loads(message)
    	live = []
		for mat in message['payload']['data']['matches']:
			live.append(mat['id'])

	def on_error(ws, error):
	    print(error)

	def on_close(ws):
	    print("### closed ###")

	def on_open(ws):
	    print("run")
	    payload = {'_username': 'runner12345', '_password': 'runner009900', '_target_path': '/ru/betting'}
		r = requests.post("https://gg11.bet/api/auth/login", data=payload)
		html = r.text
		token = re.search(r'token: "(.*?)"', html)
		token = token.group(1)
		message = {"type":"connection_init","payload":{"headers":{"X-Auth-Token":token},"X-Auth-Token":token}}
		ws.send(json.dumps(message))
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


x = 0
# Create new threads
thread2 = myThread2(2, "Thread-2")
thread1 = myThread(1, "Thread-1")

# Start new Threads
thread2.start()
thread1.start()
thread2.join()
thread1.join()
print ("Exiting Main Thread")