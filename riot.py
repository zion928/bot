import discord
from discord.ext import commands
import logging
import os
import requests
import pymysql

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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

@bot.command()
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

bot.run(bot_token)

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)