
import os
import random
import asyncio
import json
from datetime import datetime

import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")

STATUS_CHANNEL_ID = 1536651130594009171
BANLIST_CHANNEL_ID = 1536615625219252345

BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

MAX_PLAYERS = 32

MAPS = [
    "de_mirage", "de_inferno", "de_dust2", "de_nuke",
    "de_train", "de_cache", "de_overpass", "de_cbble",
    "de_tuscan", "de_aztec", "de_lego", "awp_lego",
    "awp_india", "aim_map", "cs_assault", "cs_italy",
    "cs_office", "cs_militia",
]


def get_players():
    hour = datetime.now().hour

    if 7 <= hour < 9:
        return random.randint(5, 6)
    if 9 <= hour < 12:
        return random.randint(12, 14)
    if 12 <= hour < 14:
        return random.randint(16, 19)
    if 14 <= hour < 17:
        return random.randint(18, 22)
    if 17 <= hour < 19:
        return random.randint(23, 28)
    if 19 <= hour < 20:
        return random.randint(27, 31)
    if 20 <= hour < 23:
        return random.randint(29, 32)
    if 23 <= hour:
        return random.randint(24, 29)
    if hour == 0:
        return random.randint(20, 24)
    if hour == 1:
        return random.randint(14, 18)
    if hour == 2:
        return random.randint(10, 14)
    if 3 <= hour < 5:
        return random.randint(7, 9)

    return random.randint(4, 7)


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


async def send_status_message():
    channel = bot.get_channel(STATUS_CHANNEL_ID)

    if channel is None:
        print("❌ Status channel not found.")
        return

    try:
        await channel.send(embed=create_status_embed())
        print("✅ Status message sent.")
    except Exception as error:
        print(f"❌ Status error: {error}")


@tasks.loop(minutes=30)
async def status_loop():
    await send_status_message()


@status_loop.before_loop
async def before_status_loop():
    await bot.wait_until_ready()


# =========================
# ANNOUNCEMENT DATA
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
    "Shadow", "Ghost", "Dark", "Nova", "Raven",
    "Viper", "Blaze", "Frost", "Storm", "Night",
    "Rapid", "Silent", "Phantom", "Zero", "Iron",
    "Wolf", "Venom", "Killer", "Hunter", "Sniper",
]


SUFFIXES = [
    "FPS", "GG", "X", "Gaming", "Strike",
    "Nox", "Rush", "Core", "Wave", "Zone",
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
    ("Cheat Software Detected", "Permanent", "🤖 Anti-Cheat", "Dark Legacy Anti-Cheat"),
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

    reason, duration, source_name, source_value = random.choice(
        REASONS
    )

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

    if not announcement_loop.is_running():
        announcement_loop.start()

    if not getattr(bot, "initial_message_sent", False):
        bot.initial_message_sent = True
        await send_status_message()


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
