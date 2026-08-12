import os
import json
import random
from datetime import datetime, date

import discord
from discord.ext import commands, tasks


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("TOKEN")

STATUS_CHANNEL_ID = 1536651130594009171
VIP_STATUS_CHANNEL_ID = 1536952688443658342
BANLIST_CHANNEL_ID = 1536615625219252345

MAX_PLAYERS = 32
MAX_VIP_ONLINE = 16


# ============================================================
# IMAGES
# ============================================================

SERVER_STATUS_IMAGE = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

VIP_STATUS_IMAGE = (
    "https://raw.githubusercontent.com/"
    "gabryel10kk-sudo/darklegacybot/main/"
    "csgo-counter-terrorist-vs-terrorist-4k.jpg"
)


# ============================================================
# MAPS
# ============================================================

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


# ============================================================
# PLAYER SIMULATION
# ============================================================

last_players = None


def smooth_players(low, high):
    global last_players

    if last_players is None:
        value = random.randint(low, high)
    else:
        minimum = max(low, last_players - 3)
        maximum = min(high, last_players + 3)

        if minimum > maximum:
            minimum = low
            maximum = high

        value = random.randint(minimum, maximum)

    last_players = value
    return value


def get_players():
    hour = datetime.now().hour

    if 0 <= hour < 3:
        return smooth_players(14, 24)

    if 3 <= hour < 6:
        return smooth_players(9, 14)

    if 6 <= hour < 9:
        return smooth_players(8, 13)

    if 9 <= hour < 12:
        return smooth_players(12, 18)

    if 12 <= hour < 15:
        return smooth_players(16, 22)

    if 15 <= hour < 18:
        return smooth_players(20, 27)

    if 18 <= hour < 20:
        return smooth_players(24, 30)

    return smooth_players(27, 32)


# ============================================================
# BOT
# ============================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    reconnect=True,
)


# ============================================================
# SERVER STATUS EMBED
# ============================================================

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

    embed.set_image(url=SERVER_STATUS_IMAGE)

    embed.set_footer(
        text="Dark Legacy • Classic CS 1.6 Community"
    )

    return embed


# ============================================================
# VIP SYSTEM
# ============================================================

VIP_START_TOTAL = 36
VIP_GROWTH_START = date(2026, 9, 10)
VIP_MAX_TOTAL = 100

last_vip_online = None


def get_total_vips():
    today = datetime.now().date()

    if today < VIP_GROWTH_START:
        return VIP_START_TOTAL

    days_since_growth = (
        today - VIP_GROWTH_START
    ).days

    total = (
        VIP_START_TOTAL
        + days_since_growth * 2
    )

    return min(total, VIP_MAX_TOTAL)


def get_vip_online():
    global last_vip_online

    total_vips = get_total_vips()
    maximum = min(MAX_VIP_ONLINE, total_vips)

    if last_vip_online is None:
        value = random.randint(5, maximum)
    else:
        minimum = max(1, last_vip_online - 2)
        maximum_value = min(
            maximum,
            last_vip_online + 2
        )

        if minimum > maximum_value:
            minimum = 1
            maximum_value = maximum

        value = random.randint(
            minimum,
            maximum_value
        )

    last_vip_online = value

    return value


def create_vip_status_embed():
    vip_online = get_vip_online()
    total_vips = get_total_vips()

    embed = discord.Embed(
        title="💎 DARK LEGACY VIP",
        description="💎 **VIP MEMBERSHIP STATUS**",
        color=discord.Color.purple(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="💎 VIP ONLINE",
        value=f"**{vip_online} / {MAX_VIP_ONLINE}**",
        inline=True,
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

    embed.add_field(
        name="✨ VIP STATUS",
        value="**ACTIVE • EXCLUSIVE**",
        inline=True,
    )

    embed.add_field(
        name="⚡ VIP ACCESS",
        value="**AVAILABLE**",
        inline=True,
    )

    embed.add_field(
        name="🔄 STATUS",
        value="**LIVE • AUTO UPDATE**",
        inline=True,
    )

    embed.set_image(url=VIP_STATUS_IMAGE)

    embed.set_footer(
        text="Dark Legacy • Exclusive VIP Membership"
    )

    return embed


# ============================================================
# FIND EXISTING BOT MESSAGE
# ============================================================

async def find_existing_message(channel, title):
    try:
        async for message in channel.history(limit=100):

            if message.author.id != bot.user.id:
                continue

            if not message.embeds:
                continue

            if message.embeds[0].title == title:
                return message

    except Exception as error:
        print(
            f"❌ Could not search messages: {error}"
        )

    return None


# ============================================================
# SERVER STATUS UPDATE
# ============================================================

async def update_server_status():
    channel = bot.get_channel(STATUS_CHANNEL_ID)

    if channel is None:
        print(
            "❌ Server Status channel not found."
        )
        return

    try:
        message = await find_existing_message(
            channel,
            "🎮 DARK LEGACY • SERVER STATUS",
        )

        embed = create_status_embed()

        if message is not None:
            await message.edit(embed=embed)

            print(
                "✅ Server Status edited "
                "(same message)."
            )

        else:
            await channel.send(embed=embed)

            print(
                "✅ Server Status message created."
            )

    except Exception as error:
        print(
            f"❌ Server Status error: {error}"
        )


# ============================================================
# SERVER STATUS LOOP
# ============================================================

@tasks.loop(minutes=30)
async def status_loop():
    await update_server_status()


@status_loop.before_loop
async def before_status_loop():
    await bot.wait_until_ready()


# ============================================================
# VIP STATUS UPDATE
# ============================================================

async def update_vip_status():
    channel = bot.get_channel(
        VIP_STATUS_CHANNEL_ID
    )

    if channel is None:
        print(
            "❌ VIP Status channel not found."
        )
        return

    try:
        message = await find_existing_message(
            channel,
            "💎 DARK LEGACY VIP",
        )

        embed = create_vip_status_embed()

        if message is not None:
            await message.edit(embed=embed)

            print(
                "✅ VIP Status edited "
                "(same message)."
            )

        else:
            await channel.send(embed=embed)

            print(
                "✅ VIP Status message created."
            )

    except Exception as error:
        print(
            f"❌ VIP Status error: {error}"
        )


# ============================================================
# VIP LOOP
# ============================================================

@tasks.loop(minutes=30)
async def vip_status_loop():
    await update_vip_status()


@vip_status_loop.before_loop
async def before_vip_status_loop():
    await bot.wait_until_ready()


# ============================================================
# BANLIST COUNTRIES
# ============================================================

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


# ============================================================
# VARIED PLAYER NAMES
# ============================================================

NAME_POOL = [
    "xKryp7",
    "M4rko",
    "Zer0Aim",
    "NexuS",
    "iVortex",
    "K1ngR",
    "R3aper",
    "Mihai.exe",
    "D3v1l",
    "Stryke",
    "NoScopeR",
    "Aqua",
    "Ragnar",
    "Kronix",
    "Vexor",
    "Drako",
    "Nyx",
    "F1re",
    "Kairo",
    "Ryxen",
    "Sonic",
    "Fenix",
    "Axion",
    "Toxic",
    "Wraith",
    "Spectre",
    "Raptor",
    "Inferno",
    "Cryptex",
    "Volt",
    "ZeroX",
    "ShadowZ",
    "Revo",
    "Nero",
    "Karma",
    "Flux",
    "Havoc",
    "Titan",
    "Echo",
    "Rogue",
    "Blitz",
    "Onyx",
    "VenomX",
    "Frosty",
    "GhostR",
    "Striker",
    "ViperX",
    "Pulse",
    "NovaX",
    "DarkR",
    "Riven",
    "Krypt",
    "Aero",
    "Drax",
    "Zenith",
    "Maverick",
    "Saber",
    "Riot",
    "Orbit",
]


USED_NAMES_FILE = "used_names.json"


# ============================================================
# USED NAMES
# ============================================================

def load_used_names():
    try:
        with open(
            USED_NAMES_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return set(data)

            if isinstance(data, dict):
                return set(data.keys())

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
    ):
        pass

    return set()


USED_NAMES = load_used_names()


def save_used_names():
    try:
        with open(
            USED_NAMES_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                sorted(USED_NAMES),
                file,
                ensure_ascii=False,
                indent=2,
            )

    except OSError as error:
        print(
            f"⚠️ Could not save used names: {error}"
        )


def generate_unique_name():
    available = [
        name
        for name in NAME_POOL
        if name not in USED_NAMES
    ]

    if available:
        name = random.choice(available)

    else:
        # Once the main pool is exhausted,
        # create a less repetitive fallback.
        prefixes = [
            "x",
            "i",
            "Mr",
            "Dr",
            "Its",
            "The",
            "Real",
        ]

        bases = [
            "Kryp",
            "Rex",
            "Vex",
            "Nox",
            "Zyn",
            "Kairo",
            "Riven",
            "Axel",
            "Drax",
            "Nero",
            "Stryke",
            "Fenix",
        ]

        while True:
            name = (
                random.choice(prefixes)
                + random.choice(bases)
                + str(random.randint(10, 999))
            )

            if name not in USED_NAMES:
                break

    USED_NAMES.add(name)
    save_used_names()

    return name


# ============================================================
# BAN REASONS
# ============================================================

REASONS = [
    (
        "Aimbot",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "Wallhack",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "ESP",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "Speed Hack",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "Triggerbot",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "Cheat Software Detected",
        "Permanent",
        "🤖 Anti-Cheat",
        "Dark Legacy Anti-Cheat",
    ),
    (
        "Bug Abuse",
        "7 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Map Exploit",
        "3 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Toxic Behavior",
        "2 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Harassment",
        "3 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Abusive Language",
        "1 Day",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Spam",
        "1 Day",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Ban Evasion",
        "14 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
    (
        "Advertising",
        "3 Days",
        "👑 Admin",
        "Dark Legacy Staff",
    ),
]


# ============================================================
# BANLIST MESSAGE
# ============================================================

def create_announcement_embed():
    flag, country = random.choice(COUNTRIES)

    player = generate_unique_name()

    (
        reason,
        duration,
        source_name,
        source_value,
    ) = random.choice(REASONS)

    embed = discord.Embed(
        title="🔨 PLAYER BANNED",
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

    embed.set_footer(
        text="Dark Legacy • announce"
    )

    return embed


async def send_announcement():
    channel = bot.get_channel(
        BANLIST_CHANNEL_ID
    )

    if channel is None:
        print(
            "❌ Banlist channel not found."
        )
        return

    try:
        await channel.send(
            embed=create_announcement_embed()
        )

        print(
            "✅ Ban announcement sent."
        )

    except Exception as error:
        print(
            f"❌ Ban announcement error: {error}"
        )


# ============================================================
# BANLIST LOOP
# ============================================================

@tasks.loop(hours=2)
async def announcement_loop():
    await send_announcement()


@announcement_loop.before_loop
async def before_announcement_loop():
    await bot.wait_until_ready()


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():
    print(
        f"✅ Dark Legacy connected as {bot.user}"
    )

    if not status_loop.is_running():
        status_loop.start()

    if not vip_status_loop.is_running():
        vip_status_loop.start()

    if not announcement_loop.is_running():
        announcement_loop.start()

    # These update the existing messages.
    # They DO NOT create a new message if one already exists.
    await update_server_status()
    await update_vip_status()


# ============================================================
# CONNECTION EVENTS
# ============================================================

@bot.event
async def on_disconnect():
    print(
        "⚠️ Discord disconnected. "
        "Automatic reconnect enabled."
    )


@bot.event
async def on_resumed():
    print(
        "🔄 Discord connection resumed."
    )


@bot.event
async def on_error(
    event,
    *args,
    **kwargs,
):
    print(
        f"❌ Discord event error: {event}"
    )


# ============================================================
# START BOT
# ============================================================

if not TOKEN:
    raise RuntimeError(
        "TOKEN environment variable is missing."
    )


bot.run(TOKEN)
