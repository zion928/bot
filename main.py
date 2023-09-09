import discord  # 봇 토큰을 여기에 입력 
token = "MTE0OTk3MzM3NTg3MjE1OTc3NA.Gp1Eyu.Dq-WP2iG-Z44Xwtvajr5TK6ReB64Tpo4ZODfFg"  
# 봇 클라이언트 생성 
client = discord.Client()  

@client.event 
async def on_ready():     
    print(f'We have logged in as {client.user}')  

@client.event 
async def on_message(message):     
    if message.author == client.user:         
        return      
    if message.content.startswith('!hello'):         
        await message.channel.send('Hello!')  # 봇을 실행 
    client.run(token)