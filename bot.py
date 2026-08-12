import os
import json
import random
import asyncio
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


# ============================================================
# IMAGES
# ============================================================

SERVER_STATUS_IMAGE = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

VIP_IMAGE = (
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
    """
    Simulated server population based on the time of day.
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
# SERVER STATUS
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


async def find_existing_message(channel, title):
    """
    Finds the existing bot message with the requested title.
    This prevents duplicate status messages.
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
        print(
            f"❌ Could not search existing messages: {error}"
        )

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

        # Existing message = EDIT IT
        if message is not None:

            await message.edit(
                embed=embed
            )

            print(
                "✅ Server Status updated."
            )

            return

        # No existing message = CREATE ONE
        await channel.send(
            embed=embed
        )

        print(
            "✅ Server Status message created."
        )

    except Exception as error:
        print(
            f"❌ Server Status error: {error}"
        )


@tasks.loop(minutes=30)
async def status_loop():
    await update_server_status()


@status_loop.before_loop
async def before_status_loop():
    await bot.wait_until_ready()


# ============================================================
# VIP STATUS
# ============================================================

VIP_START_TOTAL = 36
VIP_GROWTH_START = date(2026, 9, 10)
VIP_MAX_TOTAL = 100

last_vip_online = None


def get_total_vips():
    """
    Starts with 36 VIP players.

    From September 10, 2026:
    +2 VIP players per day
    until reaching 100.
    """

    today = datetime.now().date()

    if today < VIP_GROWTH_START:
        return VIP_START_TOTAL

    days_since_growth = (
        today - VIP_GROWTH_START
    ).days

    total = (
        VIP_START_TOTAL
        + (days_since_growth * 2)
    )

    return min(
        total,
        VIP_MAX_TOTAL,
    )


def get_vip_online():
    """
    VIP online count is completely independent
    from the normal Server Status player count.

    This means VIP online can be higher than
    normal server players.
    """

    global last_vip_online

    total_vips = get_total_vips()

    # Keep it realistic but independent.
    maximum = min(
        total_vips,
        18,
    )

    minimum_allowed = 4

    if maximum < minimum_allowed:
        minimum_allowed = maximum

    if last_vip_online is None:

        value = random.randint(
            minimum_allowed,
            maximum,
        )

    else:

        minimum = max(
            minimum_allowed,
            last_vip_online - 2,
        )

        maximum_value = min(
            maximum,
            last_vip_online + 2,
        )

        if minimum > maximum_value:
            minimum = minimum_allowed
            maximum_value = maximum

        value = random.randint(
            minimum,
            maximum_value,
        )

    last_vip_online = value

    return value


def create_vip_status_embed():
    vip_online = get_vip_online()
    total_vips = get_total_vips()

    embed = discord.Embed(
        title="💎 DARK LEGACY VIP",
        description=(
            "**VIP > PREMIUM SUBSCRIPTION**"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="💎 VIP ONLINE",
        value=f"`{vip_online} players online`",
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

    embed.add_field(
        name="⚡ VIP PERKS",
        value="**UNLOCKED**",
        inline=True,
    )

    embed.add_field(
        name="🟢 VIP STATUS",
        value="**LIVE • AUTO UPDATE**",
        inline=False,
    )

    embed.set_image(
        url=VIP_IMAGE
    )

    embed.set_footer(
        text="Dark Legacy • Exclusive VIP Membership"
    )

    return embed


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

        # Existing VIP message = EDIT IT
        if message is not None:

            await message.edit(
                embed=embed
            )

            print(
                "✅ VIP Status updated."
            )

            return

        # No existing VIP message = CREATE ONE
        await channel.send(
            embed=embed
        )

        print(
            "✅ VIP Status message created."
        )

    except Exception as error:
        print(
            f"❌ VIP Status error: {error}"
        )


@tasks.loop(minutes=30)
async def vip_status_loop():
    await update_vip_status()


@vip_status_loop.before_loop
async def before_vip_status_loop():
    await bot.wait_until_ready()


# ============================================================
# BANLIST / ANNOUNCEMENTS
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


# Different style from the old names.
# This makes the banlist players look less repetitive.

NAME_FIRST = [
    "Apex",
    "Crimson",
    "Obsidian",
    "Rogue",
    "Mercury",
    "Titan",
    "Infernal",
    "Reaper",
    "Wraith",
    "Specter",
    "Drift",
    "Onyx",
    "Volt",
    "Cipher",
    "Grim",
    "Havoc",
    "Arctic",
    "Phantom",
    "Dagger",
    "Riot",
    "Eclipse",
    "Vandal",
    "Striker",
    "Fury",
    "Nomad",
    "Vector",
    "Talon",
    "Maverick",
    "Raptor",
    "Chaos",
]


NAME_SECOND = [
    "Zero",
    "Seven",
    "Prime",
    "Rush",
    "Core",
    "Byte",
    "Edge",
    "One",
    "Six",
    "X",
    "FX",
    "Wave",
    "Unit",
    "Mode",
    "Force",
    "Pulse",
    "Lock",
    "Grid",
    "Peak",
    "Zone",
]


USED_NAMES_FILE = "used_names.json"


def load_used_names():
    """
    Safely loads used names.

    If used_names.json does not exist,
    the bot simply starts with an empty set.
    """

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
        return set()

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
    """
    Generates a different-looking player name
    and remembers it in used_names.json.
    """

    for _ in range(200):

        style = random.randint(1, 4)

        if style == 1:

            name = (
                random.choice(NAME_FIRST)
                + random.choice(NAME_SECOND)
                + str(random.randint(10, 999))
            )

        elif style == 2:

            name = (
                random.choice(NAME_FIRST)
                + "_"
                + random.choice(NAME_SECOND)
                + str(random.randint(1, 99))
            )

        elif style == 3:

            name = (
                random.choice(NAME_FIRST)
                + random.choice(NAME_SECOND)
                + str(random.randint(1000, 9999))
            )

        else:

            name = (
                random.choice(NAME_FIRST)
                + str(random.randint(100, 9999))
            )

        if name not in USED_NAMES:

            USED_NAMES.add(name)
            save_used_names()

            return name

    # Emergency fallback
    name = f"Player{random.randint(100000, 999999)}"

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
            "❌ Announcement channel not found."
        )
        return

    try:
        await channel.send(
            embed=create_announcement_embed()
        )

        print(
            "✅ Announcement sent."
        )

    except Exception as error:
        print(
            f"❌ Announcement error: {error}"
        )


@tasks.loop(hours=2)
async def announcement_loop():
    await asyncio.sleep(
        random.randint(0, 3600)
    )

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

    # Start loops only once.
    if not status_loop.is_running():
        status_loop.start()

    if not vip_status_loop.is_running():
        vip_status_loop.start()

    if not announcement_loop.is_running():
        announcement_loop.start()

    # Update the existing messages immediately.
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
# START
# ============================================================

if not TOKEN:
    raise RuntimeError(
        "TOKEN environment variable is missing."
    )


bot.run(TOKEN)
