import http.client
import pandas as pd
import pickle
import json
import tqdm
import pdb
from datetime import date, timedelta

# instantiate empty arrays
team_names_arr = []
pct_arr = []
opp_pct_arr = []
opp_opp_pct_arr = []

# instantiate empty hash of str->float for pct
pct = {}

# get all winning percentages
conn = http.client.HTTPSConnection("ncaa-api.henrygd.me")
conn.request("GET", "/stats/basketball-men/d1/current/team/168")
res = conn.getresponse()
data = res.read()
data = json.loads(data)

# get number of pages, page length
num_pages = data['pages']
page_length = len(data['data'])

# for each page (i)
for i in range(1, num_pages+1):

    # get new page if needed
    if i > 1:
        conn = http.client.HTTPSConnection("ncaa-api.henrygd.me")
        conn.request("GET", f"/stats/basketball-men/d1/current/team/168/p{i}")
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data)

    # for each team (j)
    for j in range(len(data['data'])):

        # store team_name in ((i)*page_length+(j), 0)
        name = data['data'][j]['Team']
        team_names_arr.append(name)

        # get percent
        percent = float(data['data'][j]['Pct'])

        # store pct in ((i)*page_length+(j), 1)
        pct_arr.append(percent)

        # store team_name->pct in hash
        pct[name] = percent

# instantiate empty hash of str->float for average opp_pct
opp_pct = {}

# for each date 2025/11/03 to 2026/03/15
start = date(2025, 11, 3)
end = date(2026, 3, 15)
num_days = (end - start).days + 1
skip_dates = {
    date(2025, 12, 24),
    date(2025, 12, 25),
    date(2025, 12, 26)
}
for i in tqdm.tqdm(range(num_days)):

    # get date
    current = start + timedelta(days=i)

    # skip no-game dates
    if current in skip_dates:
        continue

    # get all the games on that day
    conn = http.client.HTTPSConnection("ncaa-api.henrygd.me")
    conn.request("GET", f"/scoreboard/basketball-men/d1/{current.strftime("%Y/%m/%d")}/all-conf")
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    games = data['games']

    # for each game
    for game in games:
        game = game['game']

        home_team = game['home']['names']['short']
        away_team = game['away']['names']['short']

        if home_team in pct:
            if not home_team in opp_pct:
                opp_pct[home_team] = []
            if away_team in pct:
                opp_pct[home_team].append(pct[away_team])
            else:
                opp_pct[home_team].append(0)

        if away_team in pct:
            if not away_team in opp_pct:
                opp_pct[away_team] = []
            if home_team in pct:
                opp_pct[away_team].append(pct[home_team])
            else:
                opp_pct[away_team].append(0)

    # increament date
    current += timedelta(days=1)

# average each value in opp_pct and conver to array
for team in team_names_arr:
    opp_pct[team] = sum(opp_pct[team])/len(opp_pct[team])
    opp_pct_arr.append(opp_pct[team])

# instantiate empty hash for opponents' opponents percent
opp_opp_pct = {}

for i in tqdm.tqdm(range(num_days)):

    # get date
    current = start + timedelta(days=i)

    # skip no-game dates
    if current in skip_dates:
        continue

    # get all the games on that day
    conn = http.client.HTTPSConnection("ncaa-api.henrygd.me")
    conn.request("GET", f"/scoreboard/basketball-men/d1/{current.strftime("%Y/%m/%d")}/all-conf")
    res = conn.getresponse()
    data = res.read()
    data = json.loads(data)
    games = data['games']

    # for each game
    for game in games:
        game = game['game']

        home_team = game['home']['names']['short']
        away_team = game['away']['names']['short']

        if home_team in opp_pct:
            if not home_team in opp_opp_pct:
                opp_opp_pct[home_team] = []
            if away_team in opp_pct:
                opp_opp_pct[home_team].append(opp_pct[away_team])
            else:
                opp_opp_pct[home_team].append(0)

        if away_team in opp_pct:
            if not away_team in opp_opp_pct:
                opp_opp_pct[away_team] = []
            if home_team in opp_pct:
                opp_opp_pct[away_team].append(opp_pct[home_team])
            else:
                opp_opp_pct[away_team].append(0)

    # increament date
    current += timedelta(days=1)

# average each value in opp_opp_pct and conver to array
for team in team_names_arr:
    opp_opp_pct[team] = sum(opp_opp_pct[team])/len(opp_opp_pct[team])
    opp_opp_pct_arr.append(opp_opp_pct[team])

# save all four arrays into a dataframe
df = pd.DataFrame({
    'team': team_names_arr,
    'pct': pct_arr,
    'opp_pct': opp_pct_arr,
    'opp_opp_pct': opp_opp_pct_arr
    })

# serialize dataframe as pickle
with open('rpi.pkl', 'wb') as f:
    pickle.dump(df, f)
