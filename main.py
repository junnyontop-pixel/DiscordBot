import random
import discord
from discord.ext import commands
import config

# 유준아, 이 줄을 맨 위에 추가해봐! 프로그램이 돌아가는지 바로 알 수 있어.
print(">> 봇 실행 준비 중... 잠시만 기다려줘!")
    
intents = discord.Intents.all() # 권한을 '전체'로 넓혔어!
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} 연결 완료! ---')
    print('이제 명령만 내려줘. 😎')

@bot.command()
async def 메뉴(ctx, *choices):
    """결정 시간을 줄여주는 도구! !메뉴 치킨 피자 우유"""
    if not choices:
        await ctx.send("고를 후보들을 뒤에 써줘! (예: !메뉴 치킨 피자)")
        return
        
    result = random.choice(choices)
    await ctx.send(f'음... 내 생각엔 **{result}**(이)가 좋겠어! 🥛😎')

@bot.command()
async def 안녕(ctx):
    await ctx.send(f'반가워, {ctx.author.name}! 나는 봇이야. 🤖')

@bot.command()
async def 하하(ctx):
    await ctx.send('ㄹㅇ날ㅇ너머린머리위ㄹㅇㄴㄹㄴㅇㄹㅇㄴㅁㄹㅇㄴㅁ남렁ㄴㅁ')

# 여기에 토큰 넣고 실행!
bot.run(config.TOKEN)