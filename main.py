import discord
from discord.ext import commands

import os

# 봇의 설정
bot_token = os.environ.get("discord_token")
bot_application_id = os.environ.get("discord_application_key")

# 인텐트 설정
intents = discord.Intents.default()
intents.typing = False  # typing 이벤트 비활성화 (선택 사항)
intents.presences = False  # presence 이벤트 비활성화 (선택 사항)
intents.messages = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="?",
            intents=intents,
            help_command=None,
            application_id=bot_application_id  # 디스코드 봇의 application id를 입력하세요.
        )

    # 봇이 준비될 때 실행되는 이벤트 핸들러
        async def on_ready(self):
            print(f'We have logged in as {self.user}')

    # 봇에 ?hello 명령어 추가
    @commands.command(name='hello')
    async def hello(ctx):
        await ctx.send("Hello!")

# 봇 실행
bot = MyBot()
bot.run(bot_token)  # 봇 토큰을 입력하세요.