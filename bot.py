```python
import os
import random
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

TOKEN = os.getenv("TOKEN")

# =========================
# CHANNELS
# =========================

STATUS_CHANNEL_ID = 1536651130594009171
BANLIST_CHANNEL_ID = 1536615625219252345

# =========================
# SERVER STATUS
# =========================

BANNER_URL = (
    "https://cdn.discordapp.com/attachments/"
    "1536614823536885760/1536721269171556433/"
    "5896a8dd-4896-4512-a1a5-48bd6f6f83ea.png"
)

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


def get_players():
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

    embed.set_footer(
        text="Dark Legacy • Classic CS 1.6 Community"
    )

    return embed


async def send_status_message():
    channel = bot.get_channel(STATUS_CHANNEL_ID)

    if channel is None:
        print("❌ Status channel not found.")
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


# =========================
# BANLIST TEST GENERATOR
# =========================

COUNTRIES = [
    ("🇷🇴", "Romania", ["AndreiFPS", "MihaiX", "RaduGaming", "Ionut.exe", "VladFPS"]),
    ("🇧🇷", "Brazil", ["RafinhaBR", "LucasFPS", "JoaoX", "Pedrinho", "GabrielBR"]),
    ("🇺🇸", "United States", ["ShadowFPS", "GhostHunter", "DarkNova", "MikeGaming"]),
    ("🇬🇧", "United Kingdom", ["HarryFPS", "JackGaming", "GhostUK", "LewisX"]),
    ("🇩🇪", "Germany", ["LukasX", "KaiserFPS", "NikoWolf", "MaxGaming"]),
    ("🇫🇷", "France", ["LouisFPS", "AlexFR", "ShadowFR", "TheoGaming"]),
    ("🇪🇸", "Spain", ["CarlosFPS", "DaniGG", "AlejandroX", "DiegoGaming"]),
    ("🇮🇹", "Italy", ["MarcoFPS", "LucaGaming", "MatteoX", "DavideGG"]),
    ("🇵🇹", "Portugal", ["JoaoFPS", "TiagoX", "RuiGaming", "PedroPT"]),
    ("🇵🇱", "Poland", ["KubaFPS", "MateuszX", "KacperGG", "JakubGaming"]),
    ("🇹🇷", "Turkey", ["EmirX", "KaanFPS", "MertGG", "BurakGaming"]),
    ("🇷🇸", "Serbia", ["NikolaFPS", "MarkoX", "LukaGaming", "StefanGG"]),
    ("🇭🇷", "Croatia", ["IvanFPS", "LukaX", "MarkoGaming", "MateoGG"]),
    ("🇧🇬", "Bulgaria", ["GeorgiFPS", "IvanBG", "DimitarX", "NikolayGG"]),
    ("🇬🇷", "Greece", ["NikosFPS", "GiorgosX", "KostasGaming", "DimitrisGG"]),
    ("🇭🇺", "Hungary", ["MateFPS", "BenceX", "DanielHU", "MarkGaming"]),
    ("🇨🇿", "Czech Republic", ["JakubCZ", "PetrFPS", "MartinX", "DavidGaming"]),
    ("🇸🇰", "Slovakia", ["MarekFPS", "TomasX", "LukasSK", "PeterGaming"]),
    ("🇺🇦", "Ukraine", ["DimaFPS", "AndriyX", "MaksGaming", "SashaUA"]),
    ("🇲🇩", "Moldova", ["IonFPS", "AndreiMD", "SergiuX", "VladMD"]),
    ("🇳🇱", "Netherlands", ["DaanFPS", "LarsX", "FinnGaming", "SemGG"]),
    ("🇧🇪", "Belgium", ["LouisBE", "NoahFPS", "LucasX", "MilanGaming"]),
    ("🇨🇭", "Switzerland", ["LucaCH", "NoahFPS", "LeonX", "JanGaming"]),
    ("🇦🇹", "Austria", ["FelixFPS", "LukasAT", "MaxX", "DavidGaming"]),
    ("🇸🇪", "Sweden", ["ErikFPS", "LiamSE", "OscarX", "ViktorGaming"]),
    ("🇳🇴", "Norway", ["OskarNO", "LarsFPS", "MagnusX", "HenrikGaming"]),
    ("🇩🇰", "Denmark", ["MikkelFPS", "EmilDK", "NoahX", "LucasGaming"]),
    ("🇫🇮", "Finland", ["EliasFPS", "MikaX", "JoonasGaming", "AleksiGG"]),
    ("🇮🇪", "Ireland", ["SeanFPS", "LiamIRL", "ConnorX", "RyanGaming"]),
    ("🇨🇦", "Canada", ["RyanCA", "EthanFPS", "LoganX", "NoahGaming"]),
    ("🇲🇽", "Mexico", ["CarlosMX", "DiegoFPS", "LuisX", "MiguelGaming"]),
    ("🇦🇷", "Argentina", ["MateoAR", "TomasFPS", "SantiX", "NicoGaming"]),
    ("🇨🇱", "Chile", ["DiegoCL", "MatiasFPS", "NicolasX", "FelipeGaming"]),
    ("🇨🇴", "Colombia", ["JuanCO", "MateoFPS", "SantiagoX", "AndresGaming"]),
    ("🇯🇵", "Japan", ["KaitoFPS", "RenX", "HiroGaming", "YukiGG"]),
    ("🇰🇷", "South Korea", ["MinJaeFPS", "JoonX", "HyunGaming", "JihoGG"]),
    ("🇮🇳", "India", ["ArjunFPS", "RohanX", "AmanGaming", "RahulGG"]),
    ("🇦🇺", "Australia", ["JackAU", "LiamFPS", "CooperX", "MasonGaming"]),
    ("🇳🇿", "New Zealand", ["LiamNZ", "JackNZ", "MasonX", "OliverGaming"]),
    ("🇿🇦", "South Africa", ["LiamZA", "DylanFPS", "RyanX", "KyleGaming"]),
    ("🇪🇬", "Egypt", ["OmarFPS", "AhmedX", "KarimGaming", "YoussefGG"]),
    ("🇸🇦", "Saudi Arabia", ["FahadFPS", "OmarX", "SaadGaming", "KhalidGG"]),
    ("🇦🇪", "United Arab Emirates", ["ZayedFPS", "OmarAE", "HamdanX", "RashidGaming"]),
    ("🇮🇱", "Israel", ["NoamFPS", "DanielIL", "EliX", "YonatanGaming"]),
    ("🇮🇩", "Indonesia", ["RizkyFPS", "DimasX", "BimaGaming", "FajarGG"]),
    ("🇲🇾", "Malaysia", ["AmirMY", "HakimFPS", "DanialX", "FarisGaming"]),
    ("🇸🇬", "Singapore", ["RyanSG", "JayFPS", "EthanX", "KaiGaming"]),
    ("🇵🇭", "Philippines", ["MiguelPH", "JoshFPS", "CarloX", "PaoloGaming"]),
    ("🇹🇭", "Thailand", ["NarinFPS", "BeamX", "KritGaming", "NonGG"]),
    ("🇻🇳", "Vietnam", ["MinhFPS", "LongX", "KhanhGaming", "NamGG"]),
    ("🇵🇰", "Pakistan", ["AliFPS", "HamzaX", "UsmanGaming", "BilalGG"]),
    ("🇧🇩", "Bangladesh", ["ArifFPS", "RafiX", "NabilGaming", "SiamGG"]),
    ("🇰🇿", "Kazakhstan", ["ArmanFPS", "DiasX", "NursultanGaming", "AlikhanGG"]),
    ("🇬🇪", "Georgia", ["GiorgiFPS", "NikaX", "SabaGaming", "LukaGE"]),
    ("🇦🇲", "Armenia", ["ArmanAM", "TigranFPS", "LevonX", "HaykGaming"]),
    ("🇦🇿", "Azerbaijan", ["AliAZ", "MuradFPS", "EminX", "TuralGaming"]),
]


CHEAT_REASONS = [
    ("Aimbot", "Permanent"),
    ("Wallhack", "Permanent"),
    ("ESP", "Permanent"),
    ("Speed Hack", "Permanent"),
    ("Triggerbot", "Permanent"),
    ("No Recoil", "Permanent"),
    ("Cheat Software Detected", "Permanent"),
    ("Multiple Cheat Signatures", "Permanent"),
]

EXPLOIT_REASONS = [
    ("Bug Abuse", "7 Days"),
    ("Map Exploit", "3 Days"),
    ("Server Exploit", "7 Days"),
    ("Game Exploit", "14 Days"),
]

BEHAVIOR_REASONS = [
    ("Toxic Behavior", "2 Days"),
    ("Harassment", "3 Days"),
    ("Abusive Language", "1 Day"),
    ("Spam", "1 Day"),
    ("Disruptive Behavior", "3 Days"),
    ("Repeated Toxicity", "7 Days"),
]

OTHER_REASONS = [
    ("Ban Evasion", "14 Days"),
    ("Multiple Accounts", "7 Days"),
    ("Advertising", "3 Days"),
    ("Impersonation", "7 Days"),
    ("Unauthorized Modification", "14 Days"),
]

BAN_TITLES = [
    ("🔨", "PLAYER BANNED"),
    ("🚫", "BAN ISSUED"),
    ("⛔", "PLAYER REMOVED"),
]


def create_ban_embed():
    flag, country, names = random.choice(COUNTRIES)
    player = random.choice(names)

    category = random.choice(
        ["cheat", "exploit", "behavior", "other"]
    )

    if category == "cheat":
        reason, duration = random.choice(CHEAT_REASONS)
        source_name = "🤖 Anti-Cheat"
        source_value = "Dark Legacy Anti-Cheat"

    elif category == "exploit":
        reason, duration = random.choice(EXPLOIT_REASONS)
        source_name = "👑 Admin"
        source_value = "Dark Legacy Staff"

    elif category == "behavior":
        reason, duration = random.choice(BEHAVIOR_REASONS)
        source_name = "👑 Admin"
        source_value = "Dark Legacy Staff"

    else:
        reason, duration = random.choice(OTHER_REASONS)
        source_name = "👑 Admin"
        source_value = "Dark Legacy Staff"

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

    return embed


async def send_ban_message():
    channel = bot.get_channel(BANLIST_CHANNEL_ID)

    if channel is None:
        print("❌ Banlist channel not found.")
        return

    try:
        await channel.send(embed=create_ban_embed())
        print("✅ Banlist message sent.")

    except discord.HTTPException as error:
        print(f"❌ Banlist Discord error: {error}")

    except Exception as error:
        print(f"❌ Banlist error: {error}")


@tasks.loop(hours=2)
async def banlist_loop():
    # Random delay between 0 and 60 minutes.
    delay = random.randint(0, 60)

    if delay > 0:
        await discord.utils.sleep_until(
            datetime.now() + timedelta(minutes=delay)
        )

    await send_ban_message()


@banlist_loop.before_loop
async def before_banlist_loop():
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

    if not banlist_loop.is_running():
        banlist_loop.start()

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
```
