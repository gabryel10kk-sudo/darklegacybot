import os
import json
import random
import asyncio
from datetime import datetime, date, timedelta

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

STATUS_UPDATE_MINUTES = 30
VIP_UPDATE_MINUTES = 30

MAP_COOLDOWN_HOURS = 5

USED_NAMES_FILE = "used_names.json"
LAST_MAPS_FILE = "map_history.json"


# ============================================================
# BANNER
# ============================================================

BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

VIP_BANNER_URL = (
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
    "de_ancient",
    "de_vertigo",
    "de_anubis",
    "de_cobblestone",
    "de_season",
    "de_santorini",
    "de_zoo",
    "de_breach",
    "de_subzero",
    "de_iris",
    "de_chlorine",
    "de_abbey",
    "de_agency",
    "de_assault",
    "de_italy",
    "de_militia",
    "de_office",
    "de_cache",
    "awp_lego",
    "awp_india",
    "aim_map",
]


# ============================================================
# JSON HELPERS
# ============================================================

def load_json_file(path, default):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
    ):
        return default


def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )
        return True

    except OSError as error:
        print(f"⚠️ Could not save {path}: {error}")
        return False


# ============================================================
# USED PLAYER NAMES
# ============================================================

USED_NAMES = set(
    load_json_file(
        USED_NAMES_FILE,
        [],
    )
)


def save_used_names():
    save_json_file(
        USED_NAMES_FILE,
        sorted(USED_NAMES),
    )


# Optional generator for demo/testing only.
# Real ban events should use the actual player's name.
FIRST_NAMES = [
    "Alex",
    "Andrei",
    "Mihai",
    "David",
    "Vlad",
    "Radu",
    "Cristian",
    "Daniel",
    "Robert",
    "Adrian",
    "Matei",
    "Darius",
    "Lucas",
    "Marco",
    "Kevin",
    "Victor",
]

NICKNAMES = [
    "Shadow",
    "Ghost",
    "Raven",
    "Viper",
    "Nexus",
    "Reaper",
    "Maverick",
    "Hunter",
    "Phantom",
    "Storm",
    "Zero",
    "Silent",
    "Blaze",
    "Frost",
    "Venom",
]


def generate_unique_demo_name():
    for _ in range(500):

        style = random.randint(1, 4)

        if style == 1:
            name = (
                random.choice(FIRST_NAMES)
                + random.choice(
                    ["", "X", "_", "7", "13", "99"]
                )
            )

        elif style == 2:
            name = (
                random.choice(FIRST_NAMES)
                + "_"
                + random.choice(NICKNAMES)
            )

        elif style == 3:
            name = random.choice(NICKNAMES)

        else:
            name = (
                random.choice(NICKNAMES)
                + str(random.randint(1, 999))
            )

        if name not in USED_NAMES:
            USED_NAMES.add(name)
            save_used_names()
            return name

    # Extremely unlikely fallback.
    while True:
        name = f"Player_{random.randint(100000, 999999)}"

        if name not in USED_NAMES:
            USED_NAMES.add(name)
            save_used_names()
            return name


# ============================================================
# MAP ROTATION
# ============================================================

map_history = load_json_file(
    LAST_MAPS_FILE,
    [],
)


def get_random_map():
    now = datetime.now()

    available = []

    for map_name in MAPS:

        allowed = True

        for item in map_history:

            if item.get("map") != map_name:
                continue

            try:
                used_at = datetime.fromisoformat(
                    item["time"]
                )

                if now - used_at < timedelta(
                    hours=MAP_COOLDOWN_HOURS
                ):
                    allowed = False

            except (
                KeyError,
                ValueError,
                TypeError,
            ):
                pass

        if allowed:
            available.append(map_name)

    if not available:
        available = MAPS.copy()

    selected = random.choice(available)

    map_history.append(
        {
            "map": selected,
            "time": now.isoformat(),
        }
    )

    # Keep history small.
    cutoff = now - timedelta(hours=24)

    cleaned_history = []

    for item in map_history:

        try:
            item_time = datetime.fromisoformat(
                item["time"]
            )

            if item_time >= cutoff:
                cleaned_history.append(item)

        except (
            KeyError,
            ValueError,
            TypeError,
        ):
            pass

    map_history.clear()
    map_history.extend(cleaned_history)

    save_json_file(
        LAST_MAPS_FILE,
        map_history,
    )

    return selected


# ============================================================
# SERVER ACTIVITY
# ============================================================

last_players = None


def smooth_players(low, high):
    global last_players

    if last_players is None:
        value = random.randint(low, high)

    else:

        minimum = max(
            low,
            last_players - 2,
        )

        maximum = min(
            high,
            last_players + 4,
        )

        if minimum > maximum:
            minimum = low
            maximum = high

        value = random.randint(
            minimum,
            maximum,
        )

    last_players = value

    return value


def get_players():

    hour = datetime.now().hour

    # 00:00 - 03:00
    if 0 <= hour < 3:
        return smooth_players(18, 27)

    # 03:00 - 06:00
    if 3 <= hour < 6:
        return smooth_players(13, 20)

    # 06:00 - 09:00
    if 6 <= hour < 9:
        return smooth_players(15, 22)

    # 09:00 - 12:00
    if 9 <= hour < 12:
        return smooth_players(19, 27)

    # 12:00 - 15:00
    if 12 <= hour < 15:
        return smooth_players(23, 31)

    # 15:00 - 17:00
    if 15 <= hour < 17:
        return smooth_players(25, 32)

    # 17:00 - 20:00
    if 17 <= hour < 20:
        return smooth_players(28, 32)

    # 20:00 - midnight
    return smooth_players(27, 32)


# ============================================================
# SERVER STATUS
# ============================================================

def create_status_embed():

    players = get_players()
    current_map = get_random_map()

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

    embed.set_image(
        url=BANNER_URL
    )

    embed.set_footer(
        text="Dark Legacy • Classic CS 1.6 Community"
    )

    return embed


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
# FIND EXISTING MESSAGE
# ============================================================

async def find_existing_message(
    channel,
    title,
):

    try:

        async for message in channel.history(
            limit=100
        ):

            if message.author.id != bot.user.id:
                continue

            if not message.embeds:
                continue

            if message.embeds[0].title == title:
                return message

    except Exception as error:

        print(
            "❌ Could not search channel: "
            f"{error}"
        )

    return None


# ============================================================
# SERVER STATUS UPDATE
# ============================================================

async def update_server_status():

    channel = bot.get_channel(
        STATUS_CHANNEL_ID
    )

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

        if message:

            await message.edit(
                embed=embed
            )

            print(
                "✅ Server Status updated."
            )

        else:

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


@tasks.loop(
    minutes=STATUS_UPDATE_MINUTES
)
async def status_loop():

    await update_server_status()


@status_loop.before_loop
async def before_status_loop():

    await bot.wait_until_ready()


# ============================================================
# VIP STATUS
# ============================================================

VIP_START_TOTAL = 36
VIP_GROWTH_START = date(
    2026,
    9,
    10,
)
VIP_MAX_TOTAL = 100


def get_total_vips():

    today = datetime.now().date()

    if today < VIP_GROWTH_START:
        return VIP_START_TOTAL

    days_since = (
        today - VIP_GROWTH_START
    ).days

    total = (
        VIP_START_TOTAL
        + days_since * 2
    )

    return min(
        total,
        VIP_MAX_TOTAL,
    )


def get_vip_online():

    players = (
        last_players
        if last_players is not None
        else get_players()
    )

    total_vips = get_total_vips()

    # VIP can NEVER exceed:
    # 1. maximum VIP slots
    # 2. total VIP members
    # 3. players currently online
    maximum = min(
        MAX_VIP_ONLINE,
        total_vips,
        max(1, players - 1),
    )

    # Keep VIP reasonably below normal server population.
    minimum = min(
        maximum,
        max(
            1,
            int(players * 0.25),
        ),
    )

    return random.randint(
        minimum,
        maximum,
    )


def create_vip_status_embed():

    vip_online = get_vip_online()
    total_vips = get_total_vips()

    embed = discord.Embed(
        title="💎 DARK LEGACY VIP",
        description=(
            "**VIP MEMBERSHIP STATUS**\n\n"
            "💎 **VIP ONLINE**\n"
            f"**{vip_online}**\n\n"
            "👑 **TOTAL VIP PLAYERS**\n"
            f"`{total_vips}`\n\n"
            "💳 **SUBSCRIPTION**\n"
            "**MONTHLY**\n\n"
            "✨ **VIP PERKS**\n"
            "`+200$ / Kill` • `2 Jump` • `102 HP`\n"
            "`Priority Join`"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now(),
    )

    embed.set_image(
        url=VIP_BANNER_URL
    )

    embed.set_footer(
        text="Dark Legacy • Premium Membership"
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

        if message:

            await message.edit(
                embed=embed
            )

            print(
                "✅ VIP Status updated."
            )

        else:

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


@tasks.loop(
    minutes=VIP_UPDATE_MINUTES
)
async def vip_status_loop():

    await update_vip_status()


@vip_status_loop.before_loop
async def before_vip_status_loop():

    await bot.wait_until_ready()


# ============================================================
# REAL BANLIST EVENTS
# ============================================================

BAN_REASONS = {
    "Aimbot": "Permanent",
    "Wallhack": "Permanent",
    "ESP": "Permanent",
    "Speed Hack": "Permanent",
    "Triggerbot": "Permanent",
    "Cheat Software": "Permanent",
    "Bug Abuse": "7 Days",
    "Map Exploit": "3 Days",
    "Toxic Behavior": "2 Days",
    "Harassment": "3 Days",
    "Abusive Language": "1 Day",
    "Spam": "1 Day",
    "Ban Evasion": "14 Days",
    "Advertising": "3 Days",
}


def create_real_ban_embed(
    player_name,
    country,
    reason,
    duration,
    source,
):

    embed = discord.Embed(
        title="🔨 PLAYER BANNED",
        color=discord.Color.dark_red(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="👤 PLAYER",
        value=f"`{player_name}`",
        inline=True,
    )

    embed.add_field(
        name="🌎 COUNTRY",
        value=f"**{country}**",
        inline=True,
    )

    embed.add_field(
        name="🛡️ REASON",
        value=f"`{reason}`",
        inline=True,
    )

    embed.add_field(
        name="⏱️ DURATION",
        value=f"**{duration}**",
        inline=True,
    )

    embed.add_field(
        name="⚔️ SOURCE",
        value=f"**{source}**",
        inline=True,
    )

    embed.set_footer(
        text="Dark Legacy • Banlist"
    )

    return embed


# ============================================================
# EXAMPLE COMMAND FOR REAL STAFF BANS
# ============================================================

@bot.command(
    name="banlog"
)
@commands.has_permissions(
    ban_members=True
)
async def banlog(
    ctx,
    member: discord.Member,
    reason: str = "Rule violation",
):

    duration = BAN_REASONS.get(
        reason,
        "Staff decision",
    )

    embed = create_real_ban_embed(
        player_name=member.display_name,
        country="Unknown",
        reason=reason,
        duration=duration,
        source="👑 Dark Legacy Staff",
    )

    channel = bot.get_channel(
        BANLIST_CHANNEL_ID
    )

    if channel is None:
        return

    await channel.send(
        embed=embed
    )


# ============================================================
# ANTI-CHEAT BAN LOG
# ============================================================

async def post_anticheat_ban(
    player_name,
    country,
    reason,
):

    channel = bot.get_channel(
        BANLIST_CHANNEL_ID
    )

    if channel is None:
        return

    embed = create_real_ban_embed(
        player_name=player_name,
        country=country,
        reason=reason,
        duration="Permanent",
        source="🤖 Dark Legacy Anti-Cheat",
    )

    await channel.send(
        embed=embed
    )


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():

    print(
        f"✅ Dark Legacy connected as "
        f"{bot.user}"
    )

    if not status_loop.is_running():
        status_loop.start()

    if not vip_status_loop.is_running():
        vip_status_loop.start()

    # Initial messages.
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
