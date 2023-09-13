import discord
from discord.ext import commands
import logging
import os
import requests
import pymysql
import utils
from utils import DB_CONFIG

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

# DB 연결 설정
db = pymysql.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    database=DB_CONFIG['db'],
    charset='utf8'
)
cursor = db.cursor(pymysql.cursors.DictCursor)

@bot.event
async 
    await ctx.send(f"Team 2: {', '.join([s['name'] for s in team2])}")


# Command to delete a summoner from the DB
    else:
        await ctx.send(f"Failed to delete '{summoner_name}' from the database. Please check if the summoner name is correct.")

# Function to delete a summoner from the DB
    finally:
        connection.close()




        else:
            await ctx.send(f"Summoner '{summoner_name}' not found in the database.")



bot.run(bot_token)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.command()
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

@bot.command()
async def reg(ctx, *args):
    # args는 튜플이므로 join을 사용하여 하나의 문자열로 만듭니다.
    full_summoner_name = ' '.join(ctx.message.content.split(" ")[1:])
    summoner_id = utils.get_summoner_id(full_summoner_name)
    if not summoner_id:
        await ctx.send(f"{summoner_id}님은 존재하지 않습니다.")

@bot.command()
async def matchhistory(ctx, summoner_id: str):
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }

    # 소환사 ID 가져오기
    response = requests.get(API_URL + f"summoner/v4/summoners/by-name/{summoner_id}", headers=headers)
    data = response.json()

    if response.status_code != 200:
        await ctx.send(f"Error: {data.get('status', {}).get('message', 'Unknown error')}")

@bot.command()
async def summonerinfo(ctx, summoner_id: str):  # region의 기본값은 'kr'로 설정
    headers = {
        'X-Riot-Token': RIOT_API_KEY
    }

    response = requests.get(API_URL + f'summoner/v4/summoners/by-name/{summoner_id}', headers=headers)

    if response.status_code == 200:
        data = response.json()    
        summoner_id = data['puuid']
        print(summoner_id)
        await ctx.send(data)  # Discord 채널에 데이터 출력
