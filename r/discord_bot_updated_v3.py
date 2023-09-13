import os
import discord
from discord.ext import commands
import riot_api_updated as RiotAPI
from database_manager_updated import *

DISCORD_BOT_TOKEN = os.environ.get('discord_token')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None
)

db_manager = DatabaseManager(DB_CONFIG)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

@bot.command(name='등록')
async def register_summoner(ctx, summoner_name: str, *args):
    if len(args) == 4:
        # Custom registration
        tier, rank, main_lane, secondary_lane = args
        success = db_manager.insert(summoner_name, tier, rank, main_lane, secondary_lane)
        if success:
            await ctx.send(f"{summoner_name}의 정보가 커스텀 등록되었습니다.")
        else:
            await ctx.send(f"{summoner_name}의 커스텀 등록에 실패하였습니다. 다시 시도해주세요.")
    else:
        success = RiotAPI.insert_into_database(summoner_name)
        if success:
            await ctx.send(f"{summoner_name}이(가) 성공적으로 등록되었습니다.")
        else:
            await ctx.send(f"{summoner_name}의 등록에 실패하였습니다. 다시 시도해주세요.")

@bot.command(name='보기')
async def view_summoner(ctx, summoner_name):
    summoner_info = db_manager.get_summoner_info(summoner_name)
    
    if summoner_info:
        await ctx.send(
            f"소환사명: {summoner_info['name']}\n"
            f"티어: {summoner_info['tier']} {summoner_info['rank']}\n"
            f"주 라인: {summoner_info['main_lane']}\n"
            f"부 라인: {summoner_info['secondary_lane']}"
        )
    else:
        await ctx.send(f"{summoner_name}에 대한 정보를 찾을 수 없습니다.")

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)