import os
import requests
from collections import defaultdict
from database_manager_updated import *

RIOT_API_KEY = os.environ.get('RIOT_API_KEY')  # System environment variable
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
    "Accept-Language": "ko,en-US;q=0.9,en;q=0.8,es;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": RIOT_API_KEY
}

BASE_URL = "https://kr.api.riotgames.com/lol"

def fetch_summoner_data_from_riot(summoner_name):
    # Fetch summoner's basic data
    summoner_endpoint = f"{BASE_URL}/summoner/v4/summoners/by-name/{summoner_name}"
    response = requests.get(summoner_endpoint, headers=HEADERS)
    summoner_data = response.json()

    if response.status_code != 200:
        return None

    # Fetch summoner's tier and rank
    encrypted_summoner_id = summoner_data['id']
    league_endpoint = f"{BASE_URL}/league/v4/entries/by-summoner/{encrypted_summoner_id}"
    league_response = requests.get(league_endpoint, headers=HEADERS)
    league_data = league_response.json()

    if league_response.status_code == 200 and league_data:
        for entry in league_data:
            if entry['queueType'] == 'RANKED_SOLO_5x5':  # We focus on solo queue data
                summoner_data['tier'] = entry['tier']
                summoner_data['rank'] = entry['rank']
                break
    
    return summoner_data

def get_recent_matches(summoner_puuid, count=20):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?start=0&count={count}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching recent matches: {response.status_code}")
        return []
    
    return response.json()

def get_match_details(match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching match details: {response.status_code}")
        return None
    
    return response.json()

def analyze_match_history_from_riot(summoner_name):
    summoner_data = fetch_summoner_data_from_riot(summoner_name)
    
    if not summoner_data or 'puuid' not in summoner_data:
        return None, None

    puuid = summoner_data['puuid']
    match_ids = get_recent_matches(puuid)

    if not match_ids:
        return None, None

    lane_counts = defaultdict(int)
    
    for match_id in match_ids:
        match_details = get_match_details(match_id)
        
        # Checking if 'metadata' and 'participants' exist in match_details
        if not match_details or 'metadata' not in match_details or 'participants' not in match_details['metadata']:
            continue
        
        # Using match_details['metadata']['participants'] for participants
        for participant_puuid in match_details['metadata']['participants']:
            if participant_puuid == puuid:
                # Assuming each participant's data has 'timeline' which includes 'lane' information
                lane = match_details['info']['participants'][match_details['metadata']['participants'].index(participant_puuid)]['individualPosition']
                lane_counts[lane] += 1

    if not lane_counts:
        return None, None

    sorted_lanes = sorted(lane_counts.items(), key=lambda x: x[1], reverse=True)
    print(sorted_lanes)
    main_lane = sorted_lanes[0][0]
    secondary_lane = sorted_lanes[1][0] if len(sorted_lanes) > 1 else None
    
    return main_lane, secondary_lane

def insert_into_database(summoner_name):
    summoner_data = fetch_summoner_data_from_riot(summoner_name)
    print(summoner_data)

    if not summoner_data:
        return False

    main_lane, secondary_lane = analyze_match_history_from_riot(summoner_name)
    print(f'{main_lane}, {secondary_lane}')

    if not main_lane or not secondary_lane:
        return False
    
    tier = summoner_data['tier']
    rank = summoner_data['rank']
    summoner_id = summoner_data['id']

    # 데이터베이스 관리자를 사용하여 데이터 삽입
    dm = DatabaseManager(DB_CONFIG)
    success = dm.insert(summoner_id, summoner_name, tier, rank, main_lane, secondary_lane)
    dm.close()
    
    return success
