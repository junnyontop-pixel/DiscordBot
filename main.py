import random
import discord
from discord.ext import commands
import config
import sqlite3

#노래 기능 관련 라이브러리 임포트
import asyncio

# [1] 데이터베이스 초기 설정
# 봇이 껐다 켜져도 유준이의 검 단계를 기억해주는 보물상자야.
conn = sqlite3.connect('bot_data.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS swords (
        user_id TEXT PRIMARY KEY,
        level INTEGER DEFAULT 0
    )
''')
conn.commit()

try:
    cursor.execute('ALTER TABLE swords ADD COLUMN win INTEGER DEFAULT 0')
    cursor.execute('ALTER TABLE swords ADD COLUMN loss INTEGER DEFAULT 0')
    conn.commit()
except:
    pass  # 이미 컬럼이 존재하면 무시

print(">> 데이터베이스 연결 및 테이블 준비 완료!")
print(">> 봇 실행 준비 중... 잠시만 기다려줘!")

# [2] 봇 기본 설정
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} 연결 완료! ---')
    print('이제 명령만 내려줘. 😎')

# [3] 메뉴 추천 기능
@bot.command()
async def 메뉴(ctx, *choices):
    """결정 시간을 줄여주는 도구! !메뉴 치킨 피자 우유"""
    if not choices:
        await ctx.send("고를 후보들을 뒤에 써줘! (예: !메뉴 치킨 피자)")
        return
        
    result = random.choice(choices)
    await ctx.send(f'음... 내 생각엔 **{result}**(이)가 좋겠어! 🥛😎')

# [4] 기본 명령어들
@bot.command()
async def 안녕(ctx):
    await ctx.send(f'반가워, {ctx.author.name}! 나는 봇이야. 🤖')

@bot.command()
async def 하하(ctx):
    await ctx.send('ㄹㅇ날ㅇ너머린머리위ㄹㅇㄴㄹㄴㅇㄹㅇㄴㅁㄹㅇㄴㅁ남렁ㄴㅁ')

# 유튜브 재생 설정
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'default_search': 'ytsearch',
    # [추가] 브라우저인 척해서 보안을 피하는 옵션이야!
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@bot.command()
async def 노래(ctx):
    if ctx.author.voice:
        try:
            # 1. 먼저 메시지를 보내서 봇이 반응하고 있다는 걸 보여줘!
            await ctx.send("🥛 웅장한 브금을 틀기 위해 채널에 입장 중이야...")
            
            # 2. 연결 시도 (시간 제한 30초로 늘림)
            await ctx.author.voice.channel.connect(timeout=30.0, reconnect=True)
            
            await ctx.send("✅ 입장 완료! 이제 `!재생 [제목]`을 입력해줘.")
            
        except Exception as e:
            # 에러가 나면 유준이한테 왜 안 되는지 알려줘
            await ctx.send(f"❌ 입장 실패... (이유: {e})")
    else:
        await ctx.send("노래 듣고 싶으면 먼저 음성 채널에 들어가줘!")

@bot.command()
async def 재생(ctx, *, search):
    import yt_dlp

    if not ctx.guild.voice_client:
        await ctx.invoke(노래)
    
    vc = ctx.guild.voice_client
    async with ctx.typing():
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(search, download=False)
            # 검색 결과 중 첫 번째 영상 가져오기
            url2 = info['entries'][0]['url'] if 'entries' in info else info['url']
            title = info['entries'][0]['title'] if 'entries' in info else info['title']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            vc.play(source)
    await ctx.send(f"🎵 **{title}** 재생 시작!")

@bot.command()
async def 퇴장(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("난 이미 밖에 있어!")

# [5] 검 강화 시스템 (핵심!)
@bot.command()
async def 강화(ctx):
    user_id = str(ctx.author.id)
    
    # 1. DB에서 현재 레벨 가져오기
    cursor.execute('SELECT level FROM swords WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        cursor.execute('INSERT INTO swords (user_id, level) VALUES (?, ?)', (user_id, 0))
        conn.commit()
        current_level = 0
    else:
        current_level = result[0]
    
    # 2. 확률 설계
    # 0~5강: 90% / 6~10강: 70% / 11~15강: 40% / 16강 이상: 15%
    if current_level < 5:
        success_chance = 90
    elif current_level < 10:
        success_chance = 70
    elif current_level < 15:
        success_chance = 40
    else:
        success_chance = 15
        
    roll = random.randint(1, 100)
    
    # 3. 강화 결과 처리
    if roll <= success_chance:
        new_level = current_level + 1
        cursor.execute('UPDATE swords SET level = ? WHERE user_id = ?', (new_level, user_id))
        
        # 검 목록 대폭 추가! (2단계마다 이름 변경)
        titles = [
            "부러진 이쑤시개", "길가다 주운 나뭇가지", "녹슨 식도", "단단한 돌검", 
            "날카로운 청동검", "제련된 철광검", "기사의 롱소드", "명품 카타나", 
            "빛나는 마법검", "불꽃의 에스토크", "빙결의 라피에르", "드래곤의 발톱", 
            "천사의 미카엘", "파괴의 데몬슬레이어", "운명의 엑스칼리버", "신을 죽이는 자"
        ]
        title_idx = min(new_level // 2, len(titles) - 1)
        sword_name = titles[title_idx]
        
        msg = f'✨ **강화 성공!** ✨\n{ctx.author.mention}님! **+{new_level} {sword_name}**(이)가 되었습니다! (성공확률: {success_chance}%)'
    else:
        # 실패 리스크 완화: 0강으로 가는 대신 1단계만 하락 (선택 사항)
        new_level = 0
        cursor.execute('UPDATE swords SET level = ? WHERE user_id = ?', (new_level, user_id))
        msg = f'💥 **강화 실패...** 💥\n...검이 손상되어 **+0강**으로 되었습니다!'
    
    conn.commit()
    await ctx.send(msg)

# [6] 내 검 확인하기 (DB 연동 완료)
@bot.command()
async def 내검(ctx):
    user_id = str(ctx.author.id)
    
    cursor.execute('SELECT level FROM swords WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    level = result[0] if result else 0
    await ctx.send(f'🗡️ {ctx.author.mention}님의 검은 현재 **+{level}강** 상태야!')

@bot.command()
async def 배틀(ctx, opponent: discord.Member = None):
    if opponent is None or ctx.author == opponent:
        await ctx.send("대결할 상대를 정확히 지목해줘! 🥛")
        return

    # 1. 각자의 강화 수치 가져오기
    cursor.execute('SELECT level FROM swords WHERE user_id = ?', (str(ctx.author.id),))
    my_level = (cursor.fetchone() or (0,))[0]

    cursor.execute('SELECT level FROM swords WHERE user_id = ?', (str(opponent.id),))
    op_level = (cursor.fetchone() or (0,))[0]

    my_id = str(ctx.author.id)
    op_id = str(opponent.id)

    my_base = my_level * 7
    op_base = op_level * 7

    # 2. 주사위 범위를 30으로 설정
    my_dice = random.randint(1, 30)
    op_dice = random.randint(1, 30)

    # 3. 치명타는 10%로 다시 복구 (스릴을 위해!)
    my_crit = 2 if random.random() < 0.1 else 1
    op_crit = 2 if random.random() < 0.1 else 1

    my_power = (my_base + my_dice) * my_crit
    op_power = (op_base + op_dice) * op_crit

    # 3. 배틀 연출 및 결과
    status = f"⚔️ **{ctx.author.name}**({my_level}강) vs **{opponent.name}**({op_level}강)\n"
    if my_crit > 1: status += "💥 **자신의 치명타가 터졌다!!**\n"
    if op_crit > 1: status += f"💥 **{opponent.name}의 치명타가 터졌다!!**\n"
    
    await ctx.send(status)

    if my_power > op_power:
        cursor.execute('UPDATE swords SET win = win + 1 WHERE user_id = ?', (my_id,))
        cursor.execute('UPDATE swords SET loss = loss + 1 WHERE user_id = ?', (op_id,))
        await ctx.send(f"🚩 **{ctx.author.mention} 승리!** (전투력: {my_power} vs {op_power})")
    elif my_power < op_power:
        cursor.execute('UPDATE swords SET win = win + 1 WHERE user_id = ?', (op_id,))
        cursor.execute('UPDATE swords SET loss = loss + 1 WHERE user_id = ?', (my_id,))
        await ctx.send(f"🚩 **{opponent.mention} 승리!** (전투력: {my_power} vs {op_power})")
    else:
        await ctx.send("🤝 무승부!")

    conn.commit()

# 내 전적 보기
@bot.command()
async def 전적(ctx):
    cursor.execute('SELECT level, win, loss FROM swords WHERE user_id = ?', (str(ctx.author.id),))
    res = cursor.fetchone()
    if not res:
        await ctx.send("기록이 없어! 강화나 배틀을 먼저 해봐. 🥛")
        return
    
    level, win, loss = res
    win_rate = (win / (win + loss) * 100) if (win + loss) > 0 else 0
    await ctx.send(f"📊 **{ctx.author.name}님의 데이터**\n검: +{level}강 | 승리: {win} | 패배: {loss} (승률: {win_rate:.1f}%)")

# 강화 랭킹 TOP 5
@bot.command()
async def 강화랭킹(ctx):
    cursor.execute('SELECT user_id, level FROM swords ORDER BY level DESC LIMIT 5')
    rows = cursor.fetchall()
    rank = "\n".join([f"{i+1}위: <@{row[0]}> (+{row[1]}강)" for i, row in enumerate(rows)])
    await ctx.send(f"🏆 **강화 랭킹 TOP 5** 🏆\n{rank}")

# 배틀 랭킹 TOP 5 (다승 순)
@bot.command()
async def 배틀랭킹(ctx):
    cursor.execute('SELECT user_id, win FROM swords ORDER BY win DESC LIMIT 5')
    rows = cursor.fetchall()
    rank = "\n".join([f"{i+1}위: <@{row[0]}> ({row[1]}승)" for i, row in enumerate(rows)])
    await ctx.send(f"⚔️ **배틀 랭킹 TOP 5** ⚔️\n{rank}")

print("봇 접속 시도 중...")

# [7] 봇 실행

bot.run(config.TOKEN)
