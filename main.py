import requests
from bs4 import BeautifulSoup
import pandas as pd

# gets a dataframe from each of the stat pages
statType = ["mostRuns","highestScore","highestAvg","highestSr","mostHundreds","mostFifties","mostFours","mostSixes","mostNineties","mostWickets","lowestAvg","bestBowlingInnings","mostFiveWickets","LowestEcon","lowestSr"]
teams = {
    "Chennai Super Kings": 58,
    "Royal Challengers Bengaluru": 59,
    "Delhi Capitals": 61,
    "Mumbai Indians": 62,
    "Kolkata Knight Riders": 63,
    "Rajasthan Royals": 64,
    "Punjab Kings": 65,
    "Sunrisers Hyderabad": 255,
    "Lucknow Super Giants": 966,
    "Gujarat Titans": 971
}

def datascraper(statType, teamName, teamId):
    url = f"https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/stats?statsType={statType}&teamId={teamId}&seasonSeriesId=9237&matchFormat=3"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,"html.parser")
    title = soup.find("title")

    table = soup.find_all("table")
    rows = soup.find_all("tr")

    headers = []
    header_cells = rows[0].find_all("th")
    for th in header_cells:
        headers.append(th.get_text(strip = True))
    all_players = []
    for row in rows:
        player = []
        data = row.find_all("td")
        if len(data) == 0:
            continue
        for x in data:
            player.append(x.get_text(strip = True))

        all_players.append(player)

    if len(all_players) == 0:
        print("No data rows for", statType)
        return None


    df = pd.DataFrame(all_players,columns = headers)

    #rename first col to Player
    df = df.rename(columns = {headers[0]: "player"})

 
    clean_names = []
    for name in df.columns:
        clean_names.append(name.strip().lower())
    df.columns = clean_names
    df["team"] = teamName

    return df

#batting
batting_list = []
for teamName in teams:
    teamId = teams[teamName]
    df = datascraper("mostRuns", teamName, teamId)
    if df is not None:
         batting_list.append(df)


bowling_list = []
for teamName in teams:
    teamId = teams[teamName]
    df = datascraper("mostWickets", teamName, teamId)
    if df is not None:
        bowling_list.append(df)

batting_df = pd.concat(batting_list, ignore_index = True)
bowling_df = pd.concat(bowling_list, ignore_index = True)


batting_df = batting_df.drop_duplicates(subset = ["player", "team"])
bowling_df = bowling_df.drop_duplicates(subset = ["player", "team"])


#renaming the columns
batting_df = batting_df.rename(columns = {
    "matches": "matches_played",
    "inns": "innings",
    "runs": "runs_scored",
    "avg": "batting_avg",
    "sr": "batting_sr",
    "4s": "fours",
    "6s": "sixes"
})

bowling_df = bowling_df.rename(columns = {
    "matches": "bowling_matches",
    "overs": "overs_bowled",
    "balls": "balls_bowled",
    "runs": "runs_conceded",
    "wkts": "wickets",
    "avg": "bowling_avg",
    "4-fers": "four_wicket_hauls",
    "5-fers": "five_wicket_hauls"
})


final_df = pd.merge(batting_df, bowling_df, on = ["player", "team"], how = "outer", suffixes = ("_bat", "_bowl"))

first_columns = ["player", "team"]
new_order = []
for col in first_columns:
    new_order.append(col)
for col in final_df.columns:
    if col not in first_columns:
        new_order.append(col)

final_df = final_df[new_order]

final_df.to_csv("ipl_2025_players.csv", index = False)
print("Saved CSV")