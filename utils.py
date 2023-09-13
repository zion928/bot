from collections import Counter
import pymysql
import requests
import os

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
API_URL = "https://kr.api.riotgames.com/lol/"
HEADERS = {"X-Riot-Token": RIOT_API_KEY}

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

def get_summoner_id(summoner_name):
    response = requests.get(f"{API_URL}summoner/v4/summoners/by-name/{summoner_name}", headers=HEADERS)
    data = response.json()
    return data.get("id", None)

def get_recent_lines(summoner_id):
    matches = requests.get(f"{API_URL}match/v4/matchlists/by-account/{summoner_id}?endIndex=20", headers=HEADERS).json()['matches']
    positions = [match['lane'] for match in matches]

    counter = Counter(positions)
    sorted_lines = sorted(counter, key=counter.get, reverse=True)

    return sorted_lines

def get_tier_score_from_db(tier, line):
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()

    query = "SELECT {} FROM TierScore WHERE tier = %s".format(line)
    cursor.execute(query, (tier,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]
    else:
        return None