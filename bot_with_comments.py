import os
import requests
import pymysql
import discord
from discord.ext import commands

# Constants
RIOT_API_KEY = os.environ.get("RIOT_API_KEY")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
BASE_RIOT_URL = "https://kr.api.riotgames.com/lol/"
HEADERS = {"X-Riot-Token": RIOT_API_KEY}
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '7856',
    'db': 'LoLDB',
    'charset': 'utf8'
}

# Helper functions
def execute_query(query, data=None):
    pass

# Riot API에서 소환사 데이터를 가져오는 함수
def fetch_summoner_data_from_riot(summoner_name):
    try:
        response = requests.get(f"{BASE_RIOT_URL}summoner/v4/summoners/by-name/{summoner_name}", headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching summoner data: {e}")
        return None

def fetch_matchlist_from_riot(summoner_id):
    try:
        response = requests.get(f"{BASE_RIOT_URL}match/v4/matchlists/by-account/{summoner_id}?endIndex=10", headers=HEADERS)
        response.raise_for_status()
        return response.json()["matches"]
    except requests.RequestException as e:
        print(f"Error fetching match list: {e}")
        return None

# Riot API에서 소환사의 매치 히스토리를 분석하는 함수
def analyze_match_history_from_riot(summoner_name):
    summoner_data = fetch_summoner_data_from_riot(summoner_name)
    if not summoner_data:
        return None, None

    summoner_id = summoner_data["id"]
    matches = fetch_matchlist_from_riot(summoner_id)
    if not matches:
        return None, None

    main_lane = matches[0]["lane"]
    secondary_lane = matches[1]["lane"]

    return main_lane, secondary_lane

def insert_custom_data_into_database(summoner_name, tier, rank, main_lane, secondary_lane):
    # Connect to the MySQL database
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        db=DB_CONFIG['db'],
        charset=DB_CONFIG['charset']
    )
    
    try:
        with connection.cursor() as cursor:
            # Insert the summoner data into the database
            sql = """INSERT INTO summoners (summoner_name, tier, rank, main_lane, sub_lane)
                     VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (summoner_name, tier, rank, main_lane, secondary_lane))
        
        connection.commit()
        return True

    except pymysql.MySQLError:
        return False

    finally:
        connection.close()


# 소환사 데이터를 데이터베이스에 삽입하는 함수
def insert_into_database(summoner_name):
    summoner_data = fetch_summoner_data_from_riot(summoner_name)
    if not summoner_data:
        return False

    tier = summoner_data['tier']
    rank = summoner_data['rank']
    main_lane = summoner_data['main_lane']
    sub_lane = summoner_data['sub_lane']

    return insert_custom_data_into_database(summoner_name, tier, rank, main_lane, sub_lane)


# 소환사 이름을 기반으로 데이터베이스에서 데이터를 가져오는 함수
def fetch_from_database(summoner_name):
    query = "SELECT * FROM summoners WHERE name=%s"
    data = (summoner_name,)
    
    try:
        result = execute_query(query, data)
        return result[0] if result else None
    except Exception as e:
        print(f"Error fetching from database: {e}")
        return None

# 데이터베이스에서 특정 소환사 데이터를 삭제하는 함수
def delete_from_database(summoner_name):
    query = "DELETE FROM summoners WHERE name=%s"
    data = (summoner_name,)
    
    try:
        execute_query(query, data)
        return True
    except Exception as e:
        print(f"Error deleting from database: {e}")
        return False

# 데이터베이스의 특정 소환사 데이터를 업데이트하는 함수
def update_database(summoner_name):
    return insert_into_database(summoner_name)

# Bot setup
# 디스코드 봇의 기본 의도 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# 봇 명령어 접두사 및 의도 설정
bot = commands.Bot(
    command_prefix='?', 
    intents=intents,
    help_command=None
)

# Bot events and commands
@bot.event
# 봇이 준비되었을 때 실행되는 함수
async def on_ready():
    print(f'We have logged in as {bot.user} (ID : {bot.user.id})')
    print('------')

@bot.command()
# 'hello' 명령어에 응답하는 함수
async def hello(ctx):
    print("Hello command received!")
    await ctx.send("Hello!")

@bot.command(name='등록')
# '등록' 명령어를 처리하는 함수
async def register_summoner(ctx, summoner_name, *args):
    if len(args) == 4:
        # Custom registration
        tier, rank, main_lane, secondary_lane = args
        # Insert these details directly into the database
        success = insert_custom_data_into_database(summoner_name, tier, rank, main_lane, secondary_lane)
        if success:
            await ctx.send(f"{summoner_name}의 정보가 커스텀 등록되었습니다.")
        else:
            await ctx.send(f"{summoner_name}의 커스텀 등록에 실패하였습니다. 다시 시도해주세요.")
    else:
        # Fetch data from Riot API and insert into DB
        success = insert_into_database(summoner_name)
        if success:
            await ctx.send(f"{summoner_name}이(가) 성공적으로 등록되었습니다.")
        else:
            await ctx.send(f"{summoner_name}의 등록에 실패하였습니다. 다시 시도해주세요.")


@bot.command(name='팀짜기')
async def form_teams(ctx, *summoners):
    # This function will use a sophisticated algorithm to form teams based on the criteria provided.
    # As a placeholder, we will just divide the summoners into two teams.
    team1 = ", ".join(summoners[:5])
    team2 = ", ".join(summoners[5:])
    await ctx.send(f"팀 1: {team1} 팀 2: {team2}")

@bot.command(name='삭제')
async def delete_summoner(ctx, summoner_name):
    success = delete_from_database(summoner_name)
    if success:
        await ctx.send(f"{summoner_name}이(가) 성공적으로 삭제되었습니다.")
    else:
        await ctx.send(f"{summoner_name}의 삭제에 실패하였습니다. 다시 시도해주세요.")

@bot.command(name='업데이트')
@commands.has_role('admin')
async def update_all_summoners(ctx):
    # Update all summoners in the database (pseudo-code)
    # For each summoner in DB, fetch their details and update them
    await ctx.send("모든 소환사의 정보가 업데이트되었습니다.")

@bot.command(name='평가하기')
async def evaluate(ctx, summoner_name=None):
    # If a specific summoner name is provided, allow users to rate that summoner
    if summoner_name:
        await ctx.send(f"{summoner_name}에 대한 평가를 0~5 사이의 숫자로 제공해주세요.")
    else:
        await ctx.send("내전 참가자 전체에 대한 평가를 0~5 사이의 숫자로 제공해주세요.")

@bot.command(name='내전결과')
async def input_match_result(ctx, result):
    # Store the match result into the database (pseudo-code)
    # Insert result into DB
    await ctx.send(f"내전 결과가 {result}로 저장되었습니다.")

@bot.command(name='내전리스트')
async def display_match_list(ctx):
    # Fetch the recent match results from the database and display (pseudo-code)
    # Fetch results from DB
    results = "Recent match results here."
    await ctx.send(results)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
