import discord
from discord.ext import commands
import logging
import os

# 봇의 설정
bot_token = os.getenv("discord_token")
bot_application_id = os.environ.get("discord_application_key")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None,
    application_id=bot_application_id
)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="?",
            intents = intents,
            help_command=None,
            application_id=bot_application_id  # 디스코드 봇의 application id를 입력하세요.
        )

# 봇이 준비될 때 실행되는 이벤트 핸들러
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

# 봇에 ?hello 명령어 추가
@bot.command()
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

# 봇 실행
bot.run(bot_token)  # 봇 토큰을 입력하세요.

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)