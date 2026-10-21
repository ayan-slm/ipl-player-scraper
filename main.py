import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/stats"
response = requests.get(url)
soup = BeautifulSoup(response.text,"html.parser")
title = soup.find("title")
print(title.get_text())
print("status code:", response.status_code)

table = soup.find_all("table")
rows = soup.find_all("tr")

all_players = []
for row in rows:
    player = []
    data = row.find_all("td")
    if len(data) == 0:
        continue
    for x in data:
        player.append(x.get_text(strip = True))

    all_players.append(player)


df = pd.DataFrame(all_players, columns =["PLAYER","MATCHES","INNS","RUNS","AVG","SR","4S","6S"])
print(df)
        