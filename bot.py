import os
import requests
import pymysql
import discord
import pandas as pd
from discord.ext import commands

# 데이터베이스 설정
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

# 환경변수에서 토큰 가져오기
DISCORD_BOT_TOKEN = os.environ.get('discord_token')
RIOT_API_KEY = os.environ.get('RIOT_API_KEY')

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

# 테스트용 명령어
@bot.command()
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

# 이 부분에 '팀짜기', '등록', '삭제', '업데이트' 등의 명령어 로직이 추가될 예정입니다.

# 코드의 나머지 부분...

bot.run(DISCORD_BOT_TOKEN)
