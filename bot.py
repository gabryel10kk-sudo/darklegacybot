import os
import random
import asyncio
from datetime import datetime, date

import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")

# =========================
# CHANNELS
# =========================

STATUS_CHANNEL_ID = 1536651130594009171
VIP_STATUS_CHANNEL_ID = 1536952688443658342
BANLIST_CHANNEL_ID = 1536615625219252345

# Existing status banner
BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

MAX_PLAYERS = 32
MAX_VIP_ONLINE = 16

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

# =========================
# PLAYER SIMULATION
# =========================

last_players = None


def smooth_players(low, high):
    global last_players

    if last_players is None:
        value = random.randint(low, high)
    else:
        # Keep changes natural instead of jumping around.
        minimum = max(low, last_players - 3)
        maximum = min(high, last_players + 3)

        if minimum > maximum:
            minimum = low
            maximum = high

        value = random.randint(minimum, maximum)

    last_players = value
    return value


def get_players():
    """
    Simulated server population.

    Morning:
        minimum 8

    Afternoon:
        more active

    Evening:
        peak activity

    Night:
        still active, but gradually lower
    """

    hour = datetime.now().hour

    # 00:00 - 02:59
    if 0 <= hour < 3:
        return smooth_players(14, 24)

    # 03:00 - 05:59
    if 3 <= hour < 6:
        return smooth_players(9, 14)

    # 06:00 - 08:59
    if 6 <= hour < 9:
        return smooth_players(8, 13)

    # 09:00 - 11:59
    if 9 <= hour < 12:
        return smooth_players(12, 18)

    # 12:00 - 14:59
    if 12 <= hour < 15:
        return smooth_players(16, 22)

    # 15:00 - 17:59
    if 15 <= hour < 18:
        return smooth_players(20, 27)

    # 18:00 - 19:59
    if 18 <= hour < 20:
        return smooth_players(24, 30)

    # 20:00 - 23:59
    return smooth_players(27, 32)


# =========================
# SERVER STATUS
# =========================

def create_status_embed():
    players = get_players()
    current_map = random.choice(MAPS)

    embed = discord.Embed(
        title="🎮 DARK LEGACY • SERVER STATUS",
        description="🟢 **SERVER ONLINE**",
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
    embed.set_footer(text="Dark Legacy • Classic CS 1.6 Community")

    return embed


async def find_existing_message(channel, title):
    """
    Finds an existing bot message with the requested embed title.
    This prevents duplicate status messages after bot restarts.
    """

    try:
        async for message in channel.history(limit=100):
            if message.author.id != bot.user.id:
                continue

            if not message.embeds:
                continue

            if message.embeds[0].title == title:
                return message

    except Exception as error:
        print(f"❌ Could not search existing messages: {error}")

    return None


async def update_server_status():
    channel = bot.get_channel(STATUS_CHANNEL_ID)

    if channel is None:
        print("❌ Server Status channel not found.")
        return

    try:
        message = await find_existing_message(
            channel,
            "🎮 DARK LEGACY • SERVER STATUS",
        )

        embed = create_status_embed()

        if message is not None:
            await message.edit(embed=embed)
            print("✅ Server Status updated.")
        else:
            await channel.send(embed=embed)
            print("✅ Server Status message created.")

    except Exception as error:
        print(f"❌ Server Status error: {error}")


@tasks.loop(minutes=30)
async def status_loop():
    await update_server_status()


@status_loop.before_loop
async def before_status_loop():
    await bot.wait_until_ready()


# =========================
# VIP STATUS
# =========================

VIP_START_TOTAL = 36
VIP_GROWTH_START = date(2026, 9, 10)
VIP_MAX_TOTAL = 100


def get_total_vips():
    """
    36 VIPs initially.

    Starting September 10, 2026,
    the total increases gradually by 2 per day
    until it reaches 100.
    """

    today = datetime.now().date()

    if today < VIP_GROWTH_START:
        return VIP_START_TOTAL

    days_since_growth = (today - VIP_GROWTH_START).days

    total = VIP_START_TOTAL + (days_since_growth * 2)

    return min(total, VIP_MAX_TOTAL)


last_vip_online = None


def get_vip_online():
    global last_vip_online

    total_vips = get_total_vips()

    # Never exceed 16 or total VIP count.
    maximum = min(MAX_VIP_ONLINE, total_vips)

    if last_vip_online is None:
        value = random.randint(5, maximum)
    else:
        minimum = max(1, last_vip_online - 2)
        maximum_value = min(maximum, last_vip_online + 2)

        if minimum > maximum_value:
            minimum = 1
            maximum_value = maximum

        value = random.randint(minimum, maximum_value)

    last_vip_online = value

    return value


def create_vip_status_embed():
    vip_online = get_vip_online()
    total_vips = get_total_vips()

    embed = discord.Embed(
        title="💎 DARK LEGACY VIP",
        description=(
            "# 💎 VIP ONLINE\n"
            f"## **{vip_online} / {MAX_VIP_ONLINE}**\n\n"
            "**TOTAL VIP PLAYERS**\n"
            f"`{total_vips}`\n\n"
            "✨ **BECOME A VIP**\n"
            "*MONTHLY SUBSCRIPTION*"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="💎 VIP ONLINE",
        value=f"**{vip_online} / {MAX_VIP_ONLINE}**",
        inline=False,
    )

    embed.add_field(
        name="👑 TOTAL VIP PLAYERS",
        value=f"`{total_vips}`",
        inline=True,
    )

    embed.add_field(
        name="💳 SUBSCRIPTION",
        value="**MONTHLY**",
        inline=True,
    )

    embed.set_footer(
        text="Dark Legacy • Exclusive VIP Membership"
    )

    return embed


async def update_vip_status():
    channel = bot.get_channel(VIP_STATUS_CHANNEL_ID)

    if channel is None:
        print("❌ VIP Status channel not found.")
        return

    try:
        message = await find_existing_message(
            channel,
            "💎 DARK LEGACY VIP",
        )

        embed = create_vip_status_embed()

        if message is not None:
            await message.edit(embed=embed)
            print("✅ VIP Status updated.")
        else:
            await channel.send(embed=embed)
            print("✅ VIP Status message created.")

    except Exception as error:
        print(f"❌ VIP Status error: {error}")


@tasks.loop(minutes=30)
async def vip_status_loop():
    await update_vip_status()


@vip_status_loop.before_loop
async def before_vip_status_loop():
    await bot.wait_until_ready()


# =========================
# ANNOUNCEMENT / BANLIST DATA
# =========================

COUNTRIES = [
    ("🇷🇴", "Romania"),
    ("🇧🇷", "Brazil"),
    ("🇺🇸", "United States"),
    ("🇬🇧", "United Kingdom"),
    ("🇩🇪", "Germany"),
    ("🇫🇷", "France"),
    ("🇪🇸", "Spain"),
    ("🇮🇹", "Italy"),
    ("🇵🇹", "Portugal"),
    ("🇵🇱", "Poland"),
    ("🇹🇷", "Turkey"),
    ("🇷🇸", "Serbia"),
    ("🇭🇷", "Croatia"),
    ("🇧🇬", "Bulgaria"),
    ("🇬🇷", "Greece"),
    ("🇭🇺", "Hungary"),
    ("🇨🇿", "Czech Republic"),
    ("🇸🇰", "Slovakia"),
    ("🇺🇦", "Ukraine"),
    ("🇲🇩", "Moldova"),
    ("🇳🇱", "Netherlands"),
    ("🇧🇪", "Belgium"),
    ("🇨🇭", "Switzerland"),
    ("🇦🇹", "Austria"),
    ("🇸🇪", "Sweden"),
    ("🇳🇴", "Norway"),
    ("🇩🇰", "Denmark"),
    ("🇫🇮", "Finland"),
    ("🇮🇪", "Ireland"),
    ("🇨🇦", "Canada"),
    ("🇲🇽", "Mexico"),
    ("🇦🇷", "Argentina"),
    ("🇨🇱", "Chile"),
    ("🇨🇴", "Colombia"),
    ("🇯🇵", "Japan"),
    ("🇰🇷", "South Korea"),
    ("🇮🇳", "India"),
    ("🇦🇺", "Australia"),
    ("🇳🇿", "New Zealand"),
    ("🇿🇦", "South Africa"),
    ("🇪🇬", "Egypt"),
    ("🇸🇦", "Saudi Arabia"),
    ("🇦🇪", "United Arab Emirates"),
    ("🇮🇩", "Indonesia"),
    ("🇲🇾", "Malaysia"),
    ("🇸🇬", "Singapore"),
    ("🇵🇭", "Philippines"),
    ("🇹🇭", "Thailand"),
    ("🇻🇳", "Vietnam"),
]

NAME_PARTS = [
    "Shadow",
    "Ghost",
    "Dark",
    "Nova",
    "Raven",
    "Viper",
    "Blaze",
    "Frost",
    "Storm",
    "Night",
    "Rapid",
    "Silent",
    "Phantom",
    "Zero",
    "Iron",
    "Wolf",
    "Venom",
    "Killer",
    "Hunter",
    "Sniper",
]

SUFFIXES = [
    "FPS",
    "GG",
    "X",
    "Gaming",
    "Strike",
    "Nox",
    "Rush",
    "Core",
    "Wave",
    "Zone",
]

USED_NAMES_FILE = "used_names.json"


def load_used_names():
    try:
        with open(USED_NAMES_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return set(data)

    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    return set()


USED_NAMES = load_used_names()


def save_used_names():
    try:
        with open(USED_NAMES_FILE, "w", encoding="utf-8") as file:
            import json

            json.dump(
                sorted(USED_NAMES),
                file,
                ensure_ascii=False,
                indent=2,
            )

    except OSError as error:
        print(f"⚠️ Could not save used names: {error}")


def generate_unique_name():
    for _ in range(100):
        name = (
            random.choice(NAME_PARTS)
            + random.choice(SUFFIXES)
            + str(random.randint(10, 9999))
        )

        if name not in USED_NAMES:
            USED_NAMES.add(name)
            save_used_names()
            return name

    name = f"Player{random.randint(100000, 999999)}"

    USED_NAMES.add(name)
    save_used_names()

    return name


REASONS = [
    ("Aimbot", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
    ("Wallhack", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
    ("ESP", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
    ("Speed Hack", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
    ("Triggerbot", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
    (
        "Cheat Software Detected",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    ("Bug Abuse", "7 Days", "👑 Admin", "Dark Legacy Staff"),
    ("Map Exploit", "3 Days", "👑 Admin", "Dark Legacy Staff"),
    ("Toxic Behavior", "2 Days", "👑 Admin", "Dark Legacy Staff"),
    ("Harassment", "3 Days", "👑 Admin", "Dark Legacy Staff"),
    ("Abusive Language", "1 Day", "👑 Admin", "Dark Legacy Staff"),
    ("Spam", "1 Day", "👑 Admin", "Dark Legacy Staff"),
    ("Ban Evasion", "14 Days", "👑 Admin", "Dark Legacy Staff"),
    ("Advertising", "3 Days", "👑 Admin", "Dark Legacy Staff"),
]


BAN_TITLES = [
    ("🔨", "PLAYER BANNED"),
    ("🚫", "BAN ISSUED"),
    ("⛔", "PLAYER REMOVED"),
]


def create_announcement_embed():
    flag, country = random.choice(COUNTRIES)
    player = generate_unique_name()

    reason, duration, source_name, source_value = random.choice(REASONS)

    icon, title = random.choice(BAN_TITLES)

    embed = discord.Embed(
        title=f"{icon} {title}",
        color=discord.Color.dark_red(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="👤 Player",
        value=f"`{player}`",
        inline=True,
    )

    embed.add_field(
        name="🌎 Country",
        value=f"{flag} **{country}**",
        inline=True,
    )

    embed.add_field(
        name="🛡️ Reason",
        value=f"`{reason}`",
        inline=True,
    )

    embed.add_field(
        name="⏱️ Duration",
        value=f"**{duration}**",
        inline=True,
    )

    embed.add_field(
        name=source_name,
        value=f"**{source_value}**",
        inline=True,
    )

    embed.set_footer(text="Dark Legacy • announce")

    return embed


async def send_announcement():
    channel = bot.get_channel(BANLIST_CHANNEL_ID)

    if channel is None:
        print("❌ Announcement channel not found.")
        return

    try:
        await channel.send(embed=create_announcement_embed())
        print("✅ Announcement sent.")

    except Exception as error:
        print(f"❌ Announcement error: {error}")


@tasks.loop(hours=2)
async def announcement_loop():
    await asyncio.sleep(random.randint(0, 3600))
    await send_announcement()


@announcement_loop.before_loop
async def before_announcement_loop():
    await bot.wait_until_ready()


# =========================
# BOT
# =========================

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

    if not vip_status_loop.is_running():
        vip_status_loop.start()

    if not announcement_loop.is_running():
        announcement_loop.start()

    # Initial updates
    await update_server_status()
    await update_vip_status()


@bot.event
async def on_disconnect():
    print("⚠️ Discord disconnected. Automatic reconnect enabled.")


@bot.event
async def on_resumed():
    print("🔄 Discord connection resumed.")


@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Discord event error: {event}")


if not TOKEN:
    raise RuntimeError("TOKEN environment variable is missing.")


bot.run(TOKEN)
