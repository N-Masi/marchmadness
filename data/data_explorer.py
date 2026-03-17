# https://github.com/henrygd/ncaa-api?tab=readme-ov-file#scoreboard

import http.client
import json
import pdb 

conn = http.client.HTTPSConnection("ncaa-api.henrygd.me")

# all scores on a given day, gives the next day if no game played that day
# first day of play this season was 2025/11/03
# conn.request("GET", "/scoreboard/basketball-men/d1/2025/12/01/all-conf")

# winning percentage of every team
# the 'PCT' field of the 'data' key gives the percentage
conn.request("GET", "/stats/basketball-men/d1/current/team/168")

# page two of winning percentages
# the 'pages' key denotes how many pages there are in total
# conn.request("GET", "/stats/basketball-men/d1/current/team/168/p2")

res = conn.getresponse()
data = res.read()
data = json.loads(data)
pdb.set_trace()

print(data.decode("utf-8"))