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
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

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
        return
    
    lines_from_api = utils.get_recent_lines(summoner_id)
    main_line_api = lines_from_api[0] if lines_from_api else None
    sub_lines_api = lines_from_api[1:]

    # 티어 및 라인 정보 설정
    tier = args[0] if args else None
    main_line = args[1] if len(args) > 1 else main_line_api
    sub_lines = args[2:] if len(args) > 2 else sub_lines_api

    # Excel에서 메인 라인 점수 가져오기
    main_score = utils.get_tier_score_from_db(tier, main_line)
    sub_scores = [main_score * x for x in [0.85, 0.8, 0.75, 0.7]]

    data_to_save = {
        "SummonName": summoner_id,
        "tier": tier,
        "main_line": [main_line, main_score],
    }

    for i, line in enumerate(sub_lines, 1):
        if i > 4:  # 최대 4개의 부라인만 저장
            break
        sub_tier_score = main_score * (1 - 0.05 * i)
        data_to_save[f"sub_line{i}"] = [line, sub_tier_score]
    
    # 데이터베이스에 저장하기 (SQL Injection을 피하기 위한 안전한 방법으로 수정)
    query = """
    INSERT INTO your_table_name (SummonName, tier, main_line, main_tier_score, sub_line1, sub_tier_score1, ...)
    VALUES (%s, %s, %s, %s, %s, %s, ...)
    """
    cursor.execute(query, (summoner_id, tier, main_line, main_score, sub_lines[0] if sub_lines else None, sub_scores[0] if sub_scores else None))

    # 만약 이 연결이 전역적으로 초기화된 연결이라면, 커밋할 수 있습니다.
    db.commit()

    # 결과 메시지 전송
    if not tier or not main_line:
        await ctx.send(f"{summoner_id}님의 티어/라인이 존재하지 않습니다! 직접 입력하세요. ...")
    else:
        response = f"{summoner_id}님의 티어는 {tier}이며, 주라인 {main_line}, "
        for idx, line in enumerate(sub_lines, 1):
            response += f"부라인{idx} {line}, "
        response = response.rstrip(", ")
        await ctx.send(response)

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
        return

    summoner_id = data['id']

    # 최근 전적 가져오기
    response = requests.get(API_URL + f"match/v4/matchlists/by-account/{summoner_id}?endIndex=1", headers=headers)
    data = response.json()

    if response.status_code != 200:
        await ctx.send(f"Error: {data.get('status', {}).get('message', 'Unknown error')}")
        return

    if not data.get('matches'):
        await ctx.send(f"No recent matches found for {summoner_id}.")
        return

    recent_match = data['matches'][0]
    await ctx.send(f"Most recent match for {summoner_id}: Game ID {recent_match['gameId']}")

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
    else:
        await ctx.send(f"Error {response.status_code}: {response.text}")

@bot.event
async def on_close():
    cursor.close()
    db.close()

bot.run(bot_token)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)