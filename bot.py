import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import random

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1536651130594009171
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import random

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1536651130594009171

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

maps = [
    "de_dust2",
    "de_mirage",
    "de_inferno",
    "de_nuke",
    "de_train",
    "de_cbble",
    "de_cache",
    "de_overpass",
    "de_aztec",
    "de_tuscan",
    "cs_assault",
    "cs_italy",
    "cs_office",
    "cs_militia",
    "awp_india",
    "awp_lego",
    "aim_map"
]


def get_activity():
    hour = datetime.now().hour

    if 20 <= hour < 23:
        return random.choice([29, 30, 31, 32, 32, 31, 30])
    elif hour >= 23 or hour < 1:
        return random.randint(20, 28)
    elif 1 <= hour < 3:
        return random.randint(12, 16)
    elif 3 <= hour < 5:
        return random.randint(6, 10)
    elif 5 <= hour < 7:
        return random.randint(3, 6)
    elif 7 <= hour < 9:
        return random.randint(5, 8)
    elif 9 <= hour < 12:
        return random.randint(8, 12)
    elif 12 <= hour < 15:
        return random.randint(12, 18)
    elif 15 <= hour < 18:
        return random.randint(18, 24)
    else:
        return random.randint(24, 30)


async def send_status():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print("❌ Nu gasesc canalul!")
        return

    activity = get_activity()
    current_map = random.choice(maps)

    embed = discord.Embed(
        title="🎮 DARK LEGACY • SERVER STATUS",
        description=(
            "🟢 **SERVER ONLINE**\n\n"
            "🔥 Classic Gameplay • Free VIP • International"
        )
    )

    embed.add_field(
        name="🗺️ CURRENT MAP",
        value=f"```{current_map}```",
        inline=False
    )

    embed.add_field(
        name="📊 SERVER ACTIVITY",
        value=f"👥 `{activity}/32`",
        inline=True
    )

    embed.add_field(
        name="💎 VIP",
        value="🟢 FREE",
        inline=True
    )

    embed.add_field(
        name="🌍 REGION",
        value="🌐 INTERNATIONAL",
        inline=True
    )

    embed.add_field(
        name="⚡ PERFORMANCE",
        value="🚀 OPTIMIZED",
        inline=True
    )

    embed.add_field(
        name="🎯 MODE",
        value="🔫 CLASSIC",
        inline=True
    )

    embed.add_field(
        name="🔄 STATUS",
        value="AUTO UPDATE",
        inline=True
    )

    embed.set_footer(
        text="Dark Legacy • Classic CS 1.6 Community • Demo Activity"
    )

    await channel.send(embed=embed)


@tasks.loop(minutes=15)
async def status_loop():
    await send_status()


@bot.event
async def on_ready():
    print(f"✅ Dark Legacy este online ca {bot.user}")

    if not status_loop.is_running():
        status_loop.start()


bot.run(TOKEN)
