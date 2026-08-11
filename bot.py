import os
import random
from datetime import datetime

import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1536651130594009171

BANNER_URL = "https://cdn.discordapp.com/attachments/1536614823536885760/1536721269171556433/5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png?ex=6a7c6eb5&is=6a7b1d35&hm=5cb4ff683a0abe333b0fd847af604b7ff21f8508478fca7999da4eb77a743b6f&"

MAX_PLAYERS = 32

MAPS = [
    "de_mirage",
    "de_inferno",
    "de_dust2",
    "de_nuke",
    "de_train",
    "de_cache",
    "de_overpass",
    "de_cbble",
    "de_tuscan",
    "de_aztec",
    "de_lego",
    "awp_lego",
    "awp_india",
    "aim_map",
    "cs_assault",
    "cs_italy",
    "cs_office",
    "cs_militia",
]


def get_demo_players():
    hour = datetime.now().hour

    if 7 <= hour < 9:
        return random.randint(5, 6)
    elif 9 <= hour < 12:
        return random.randint(12, 14)
    elif 12 <= hour < 14:
        return random.randint(16, 19)
    elif 14 <= hour < 17:
        return random.randint(18, 22)
    elif 17 <= hour < 19:
        return random.randint(23, 28)
    elif 19 <= hour < 20:
        return random.randint(27, 31)
    elif 20 <= hour < 23:
        return random.randint(29, 32)
    elif 23 <= hour:
        return random.randint(24, 29)
    elif hour == 0:
        return random.randint(20, 24)
    elif hour == 1:
        return random.randint(14, 18)
    elif hour == 2:
        return random.randint(10, 14)
    elif 3 <= hour < 5:
        return random.randint(7, 9)
    else:
        return random.randint(4, 7)


def create_status_embed():
    players = get_demo_players()
    current_map = random.choice(MAPS)

    embed = discord.Embed(
        title="🎮 DARK LEGACY • SERVER STATUS",
        description="🟢 **SERVER ONLINE**\n━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.dark_red(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="🗺️ CURRENT MAP",
        value=f"`{current_map}`",
        inline=True,
    )

    embed.add_field(
        name="👥 PLAYERS",
        value=f"`{players}/{MAX_PLAYERS}`",
        inline=True,
    )

    embed.add_field(
        name="🌍 REGION",
        value="**INTERNATIONAL**",
        inline=True,
    )

    embed.add_field(
        name="⚡ PERFORMANCE",
        value="**OPTIMIZED**",
        inline=True,
    )

    embed.add_field(
        name="🌐 SERVER ACTIVITY",
        value="`24/7 ACTIVITY`",
        inline=True,
    )

    embed.add_field(
        name="🔄 STATUS",
        value="**LIVE • AUTO UPDATE**",
        inline=True,
    )

    embed.set_image(url=BANNER_URL)

    embed.set_footer(
        text="Dark Legacy • Classic CS 1.6 Community"
    )

    return embed


async def send_status_message():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Channel not found.")
        return

    try:
        await channel.send(embed=create_status_embed())
        print("✅ Status message sent.")

    except discord.HTTPException as error:
        print(f"❌ Discord HTTP error: {error}")

    except Exception as error:
        print(f"❌ Status error: {error}")


@tasks.loop(minutes=30)
async def status_loop():
    try:
        await send_status_message()

    except Exception as error:
        print(f"❌ Status loop error: {error}")


@status_loop.before_loop
async def before_status_loop():
    await bot.wait_until_ready()


intents = discord.Intents.default()


bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    reconnect=True,
)


@bot.event
async def on_ready():
    print(f"✅ Dark Legacy connected as {bot.user}")

    if not status_loop.is_running():
        status_loop.start()

    if not getattr(bot, "_initial_status_sent", False):
        bot._initial_status_sent = True
        await send_status_message()


@bot.event
async def on_disconnect():
    print("⚠️ Discord disconnected. Waiting for automatic reconnect...")


@bot.event
async def on_resumed():
    print("🔄 Discord connection resumed.")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Discord event error: {event}")


if not TOKEN:
    raise RuntimeError("TOKEN environment variable is missing.")


bot.run(TOKEN)
