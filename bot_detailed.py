import os
import requests
import pymysql
import discord
from discord.ext import commands
import pandas as pd

# 환경변수에서 토큰 가져오기
DISCORD_BOT_TOKEN = os.environ.get('discord_token')
RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

# 데이터베이스 설정
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

# 티어 점수 불러오기
tier_score_df = pd.read_excel("/path/to/TierScore.xlsx")

# 디스코드 봇 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None
)

# 봇 로그인 정보 출력
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

# 소환사 등록 명령어
@bot.command(name='등록')
async def register_summoner(ctx, summoner_name, *args):
    # 이 명령어는 소환사의 정보를 등록합니다.
    if len(args) == 4:
        # 커스텀 등록
        tier, rank, main_lane, secondary_lane = args
        # 데이터베이스에 직접 입력
        # TODO: 데이터베이스 입력 코드 작성
        await ctx.send(f"{summoner_name}의 정보가 커스텀 등록되었습니다.")
    else:
        success = insert_into_database(summoner_name)
        if success:
            await ctx.send(f"{summoner_name}이(가) 성공적으로 등록되었습니다.")
        else:
            await ctx.send(f"{summoner_name}의 등록에 실패하였습니다. 다시 시도해주세요.")

# TODO: 다른 명령어 및 로직 추가

bot.run(DISCORD_BOT_TOKEN)
