import discord
from discord.ext import commands
import logging
import os
import requests
import pymysql
from riotwatcher import LolWatcher
import pandas as pd

# 봇과 Riot API의 설정
bot_token = os.getenv("discord_token")
bot_application_id = os.environ.get("discord_application_key")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
API_URL = "https://kr.api.riotgames.com/lol/"
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None,
    application_id=bot_application_id
)

lol_watcher = LolWatcher(RIOT_API_KEY)
my_region = 'kr'

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

@bot.command()
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

@bot.command()
async def matchhistory(ctx, summoner_name: str):
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    # 소환사 ID 가져오기
    response = requests.get(API_URL + f"summoner/v4/summoners/by-name/{summoner_name}", headers=headers)
    data = response.json()

    if response.status_code != 200:
        await ctx.send(f"Error: {data.get('status', {}).get('message', 'Unknown error')}")
        return

    summoner_id = data['id']

    # 최근 전적 가져오기
    response = requests.get(API_URL + f"match/v4/matchlists/by-account/{summoner_id}?endIndex=1", headers=headers)
    data = response.json()

    if response.status_code != 200:
        await ctx.send(f"Error: {data.get('status', {}).get('message', 'Unknown error')}")
        return

    if not data.get('matches'):
        await ctx.send(f"No recent matches found for {summoner_name}.")
        return

    recent_match = data['matches'][0]
    await ctx.send(f"Most recent match for {summoner_name}: Game ID {recent_match['gameId']}")

@bot.command()
async def summonerinfo(ctx, summoner_name: str):  # region의 기본값은 'kr'로 설정
    headers = {
        'X-Riot-Token': RIOT_API_KEY
    }

    response = requests.get(API_URL + f'summoner/v4/summoners/by-name/{summoner_name}', headers=headers)

    if response.status_code == 200:
        data = response.json()    
        summoner_id = data['puuid']
        print(summoner_id)
        await ctx.send(data)  # Discord 채널에 데이터 출력
    else:
        await ctx.send(f"Error {response.status_code}: {response.text}")

bot.run(bot_token)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)