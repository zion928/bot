
import os
import requests
import pymysql
import discord
from discord.ext import commands

# Riot API and Database Configuration
RIOT_API_KEY = os.environ.get('RIOT_API_KEY')
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None
)

class RiotAPIHandler:
    BASE_URL = "https://kr.api.riotgames.com/lol"

    @staticmethod
    def fetch_summoner_data(summoner_name):
        # Fetch summoner data from Riot API
        # Return: Dictionary containing summoner data or None if error
        try:
            url = f"{RiotAPIHandler.BASE_URL}/summoner/v4/summoners/by-name/{summoner_name}?api_key={RIOT_API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching summoner info: {e}")
            return None

    @staticmethod
    def analyze_match_history(summoner_name):
        # Analyze match history from Riot API to determine main and secondary lane
        # This is just a mock function for now.
        # Return: Tuple containing main_lane and secondary_lane or (None, None) if error
        return ("JUNGLE", "MID")

class DatabaseManager:
    @staticmethod
    def execute_query(query, data):
        # Execute given query with provided data using pymysql
        # Return: Query result or None if error
        try:
            connection = pymysql.connect(**DB_CONFIG)
            with connection.cursor() as cursor:
                cursor.execute(query, data)
                result = cursor.fetchall()
            connection.commit()
            return result
        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def insert_into_database(summoner_name):
        # Insert or update summoner data into the database
        # Return: True if successful, False otherwise
        summoner_data = RiotAPIHandler.fetch_summoner_data(summoner_name)
        main_lane, secondary_lane = RiotAPIHandler.analyze_match_history(summoner_name)
        
        if not summoner_data or not main_lane or not secondary_lane:
            return False
        
        query = """
        INSERT INTO summoners (id, name, tier, rank, main_lane, secondary_lane) 
        VALUES (%s, %s, %s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE name=%s, tier=%s, rank=%s, main_lane=%s, secondary_lane=%s
        """
        
        data = (summoner_data['id'], summoner_name, summoner_data['tier'], summoner_data['rank'], main_lane, secondary_lane,
                summoner_name, summoner_data['tier'], summoner_data['rank'], main_lane, secondary_lane)
        
        try:
            DatabaseManager.execute_query(query, data)
            return True
        except Exception as e:
            print(f"Error inserting into database: {e}")
            return False

class BotCommands:
    def __init__(self, bot):
        self.bot = bot

    @bot.command(name='등록')
    async def register_summoner(self, ctx, summoner_name, *args):
        # Handle summoner registration
        if len(args) == 4:
            # Custom registration
            tier, rank, main_lane, secondary_lane = args
            # Insert these details directly into the database (pseudo-code)
            # Insert into DB
            await ctx.send(f"{summoner_name}의 정보가 커스텀 등록되었습니다.")
        else:
            success = DatabaseManager.insert_into_database(summoner_name)
            if success:
                await ctx.send(f"{summoner_name}이(가) 성공적으로 등록되었습니다.")
            else:
                await ctx.send(f"{summoner_name}의 등록에 실패하였습니다. 다시 시도해주세요.")


BotCommands(bot)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

bot.run(os.environ.get('DISCORD_BOT_TOKEN'))
