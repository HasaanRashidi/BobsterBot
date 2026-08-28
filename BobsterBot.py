# all the important import stuff (allows the bot to actually work)
import discord
from discord.ext import commands, tasks
import subprocess
import asyncio

# Load private configuration from the local .env file
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

#getting announcement channel ID
HC_ANNOUNCEMENT_CHANNEL_ID = int(
    os.getenv("HC_ANNOUNCEMENT_CHANNEL_ID", "0")
)

from hardcore.monitor import (
    ParsedDeath,
    parse_deaths_from_lines,
    read_new_log_lines,
)
from hardcore.service import (
    format_boss_announcement,
    format_death_announcement,
    prepare_next_run,
    record_boss_defeat,
    record_death,
    format_boss_progress,
    normalize_boss_name,
    format_death_totals,
    format_death_log,
    format_player_death_stats,
)

from hardcore.worlds import archive_worlds

from datetime import datetime, timezone
from pathlib import Path
from hardcore.state import load_state, save_state

import json

from hardcore.bosses import read_defeated_bosses





# loading RCON password
OLD_RCON_PASSWORD = os.getenv("OLD_RCON_PASSWORD")

# loading the authorized users
AUTHORIZED_USERS = [
    int(user_id.strip())
    for user_id in os.getenv("AUTHORIZED_USER_IDS", "").split(",")
    if user_id.strip()
]

#getting the executable and directories
OLD_JAVA_EXECUTABLE = os.getenv("OLD_JAVA_EXECUTABLE")
OLD_SERVER_DIRECTORY = os.getenv("OLD_SERVER_DIRECTORY")

# allows to check if server is online using this
import socket

# importing the RCON client to interact with the server over RCON
from mcrcon import MCRcon

from hardcore.config import HardcoreConfig
from hardcore.server import HardcoreServerManager

# Enable the Discord events required for text commands
intents = discord.Intents.default()
intents.message_content = True

# setting the prefix for the commands
bot = commands.Bot(command_prefix='-', intents=intents)


# Separate manager for the temporary vanilla Hardcore server.
hardcore_server = HardcoreServerManager(HardcoreConfig.from_environment())

HARDCORE_LOG_PATH = (
    hardcore_server.config.server_directory / "logs" / "latest.log"
)

PROJECT_ROOT = Path(__file__).resolve().parent
HARDCORE_STATE_PATH = PROJECT_ROOT / "data" / "hardcore_state.json"
hardcore_state = load_state(HARDCORE_STATE_PATH)

HARDCORE_STATS_PATH = (
    hardcore_server.config.server_directory
    / hardcore_state.world_folder
    / "stats"
)

HC_ARCHIVE_DIRECTORY_TEXT = os.getenv("HC_ARCHIVE_DIRECTORY")
HC_ARCHIVE_DIRECTORY = (
    Path(HC_ARCHIVE_DIRECTORY_TEXT)
    if HC_ARCHIVE_DIRECTORY_TEXT
    else None
)


hardcore_log_position = 0
hardcore_log_initialized = False

# bot starts as disarmed
global armed
armed = False

# keep track of server process
global server_process
server_process = None

# connecting to server and checking if its online
def is_server_online  (host="localhost", port=25565):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except:
        return False

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

    if not monitor_hardcore_log.is_running():
        monitor_hardcore_log.start()
        print(f"Watching Hardcore log: {HARDCORE_LOG_PATH}")

    if not monitor_hardcore_bosses.is_running():
        monitor_hardcore_bosses.start()
        print(f"Watching Hardcore stats: {HARDCORE_STATS_PATH}")

@tasks.loop(seconds=2)
async def monitor_hardcore_log():
    global hardcore_log_position, hardcore_log_initialized

    if not hardcore_log_initialized:
        if HARDCORE_LOG_PATH.exists():
            hardcore_log_position = HARDCORE_LOG_PATH.stat().st_size

        hardcore_log_initialized = True
        return
    lines, hardcore_log_position = await asyncio.to_thread(
        read_new_log_lines,
        HARDCORE_LOG_PATH,
        hardcore_log_position,
    )

    deaths = parse_deaths_from_lines(lines)

    if not deaths:
        return

    for death in deaths:
        timestamp = datetime.now(timezone.utc).isoformat()

        record = record_death(
            state=hardcore_state,
            death=death,
            timestamp=timestamp,
        )

        if record is None:
            continue

        save_state (HARDCORE_STATE_PATH, hardcore_state)

        channel = bot.get_channel(HC_ANNOUNCEMENT_CHANNEL_ID)

        if channel is None:
            print("Could not find the Hardcore announcement channel.")
            continue

        announcement = format_death_announcement(
            run_number=record.run_number,
            death=death,
        )

        try:
            await channel.send(announcement)
        except discord.DiscordException as error:
            print(
                "Could not announce the Hardcore death in Discord: "
                f"{error}"
            )

@tasks.loop(seconds=5)
async def monitor_hardcore_bosses():
    if hardcore_state.status != "RUNNING":
        return

    detected_bosses = await asyncio.to_thread(
        read_defeated_bosses,
        HARDCORE_STATS_PATH,
    )

    for boss_name in hardcore_state.bosses:
        if boss_name not in detected_bosses:
            continue

        recorded = record_boss_defeat(
            state=hardcore_state,
            boss_name=boss_name,
        )

        if not recorded:
            continue

        save_state(HARDCORE_STATE_PATH, hardcore_state)

        announcement = format_boss_announcement(
            state=hardcore_state,
            boss_name=boss_name,
        )

        print(f"Detected Hardcore boss: {announcement}")

        channel = bot.get_channel(HC_ANNOUNCEMENT_CHANNEL_ID)

        if channel is not None:
            try:
                await channel.send(announcement)
            except discord.DiscordException as error:
                print(
                    "Could not announce the Hardcore boss in Discord: "
                    f"{error}"
                )
        else:
            print("Could not find the Hardcore announcement channel.")

        minecraft_message = json.dumps(
            {
                "text": announcement,
                "color": "gold",
                "bold": True,
            }
        )

        try:
            await asyncio.to_thread(
                hardcore_server.send_command,
                f"tellraw @a {minecraft_message}",
            )
        except RuntimeError as error:
            print(
                "Could not announce the boss in Minecraft: "
                f"{error}"
            )

# COMMANDS

# Displays the bot's available commands.
@bot.command()
async def Bobster(ctx):
    await ctx.send(
        "Hello! I'm Bobster Bot! My commands are:\n"
        "```text\n"
        "GENERAL SERVER\n"
        "-status   Check whether the server is online\n"
        "-start    Start the server\n"
        "-stop     Stop the server\n"
        "-players  Show the online players\n"
        "\n"
        "HARDCORE SERVER\n"
        "-statusHC          Show run status and boss progress\n"
        "-startHC           Start or resume the Hardcore server\n"
        "-stopHC            Save and stop the Hardcore server\n"
        "-nextHC            Archive a dead run and prepare the next run\n"
        "-bossHC <boss>     Manually record a defeated boss\n"
        "-HCdeaths          Show death totals for every player\n"
        "-HCdeathlog        Show the five most recent deaths\n"
        "-HCstats <player>  Show detailed stats for one player\n"
        "\n"
        "AUTHORIZED CONTROL\n"
        "-arm      Allow others to start the original server\n"
        "-disarm   Prevent others from starting the original server\n"
        "```\n"
        "Questions, problems, or need help? "
        "Contact **krezn1k** on Discord."
    )


# checks status of server
@bot.command()
async def status(ctx):
    if is_server_online():
        await ctx.send ("Hi! The server is **online**! 🟢")
    else:
        await ctx.send ("Hi! The server is **offline**. 🔴")

# checks how many players are on the server and their usernames
@bot.command()
async def players(ctx):
    if not OLD_RCON_PASSWORD:
        await ctx.send ("❌ The old server's RCON password is not configured.")
        return

    try:
        with MCRcon ("127.0.0.1", OLD_RCON_PASSWORD, port=25575) as mcr:
            response = mcr.command("list")

        await ctx.send(f"🧑‍🤝‍🧑 {response}")

    except Exception as e:
        await ctx.send(f"❌ Im sorry, I couldnt fetch the payer list: {e}")

# allows authorized user to arm
@bot.command()
async def arm(ctx):
    global armed
    if ctx.author.id in AUTHORIZED_USERS:
        if armed:
            await ctx.send("Hello! I am already in armed mode!")
        else:
            armed = True
            await ctx.send("Hello! I am now in armed mode.")

# allows authorized user to disarm
@bot.command()
async def disarm(ctx):
    global armed
    if ctx.author.id in AUTHORIZED_USERS:
        if not armed:
            await ctx.send("Hello! I am already disarmed!")
        else:
            armed = False
            await ctx.send("Hello! I am now disarmed.")


# STARTING THE SERVER
@bot.command()
async def start(ctx):
    global armed, server_process
    if not armed:
        await ctx.send("I am currently disarmed! Ask hasaan to either turn on the server or arm me.")
        return
    if not OLD_JAVA_EXECUTABLE or not OLD_SERVER_DIRECTORY:
        await ctx.send("The original server paths are not configured.")
        return

    try:
        server_process = subprocess.Popen(
            [
                OLD_JAVA_EXECUTABLE,
                "@user_jvm_args.txt",
                "@libraries/net/neoforged/neoforge/21.1.194/win_args.txt"
            ],
            cwd=OLD_SERVER_DIRECTORY,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        await ctx.send("Great to see you again! I will start the official BBISS Minecraft server! Please try joining in 15 seconds.")
    except Exception as e:
        await ctx.send(f"Failed to start the server: {e}")

# STOPPING THE SERVER
@bot.command()
async def stop(ctx):
    global armed, server_process
    if not armed:
        await ctx.send("Hi! I'm disarmed, so I can't stop the server! Ask hasaan to either turn it off or arm me.")
        return

    if server_process is None or server_process.poll() is not None:
        await ctx.send("Hello! The server isn't running right now, so I cant turn it off! :steamhappy:")
        return

    try:
        server_process.stdin.write(b"stop\n")
        server_process.stdin.flush()
        await ctx.send("Hi! I will stop the Minecraft server. Thanks for playing! Hope to see you soon!")
    except Exception as e:
        await ctx.send(f"Something went wrong while stopping the server: {e}")





# NEW HARDCORE PORTION

# These commands deliberately stay small. Automatic death detection, run state,
# world archiving, and reset handling will be added later in hardcore/service.py.
@bot.command(name="startHC", aliases=["starthc"])
async def start_hardcore(ctx):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("❌ You are not authorized to start the Hardcore server.")
        return

    if hardcore_state.status == "DEAD":
        await ctx.send(
            f"💀 Run {hardcore_state.run_number} has already ended. "
            "Create the next run before restarting."
        )
        return

    try:
        await asyncio.to_thread(hardcore_server.start)
        await ctx.send("⏳ Starting the vanilla Hardcore server...")
        online = await asyncio.to_thread(hardcore_server.wait_until_online, 120)
        if online:
            hardcore_state.status = "RUNNING"
            save_state(HARDCORE_STATE_PATH, hardcore_state)
            await ctx.send("❤️ The Hardcore server is online. Good luck!")
        else:
            await ctx.send(
                "❌ The server did not finish starting. Check "
                "hardcore_server/logs/bobster-console.log."
            )
    except Exception as error:
        await ctx.send(f"❌ Could not start the Hardcore server: {error}")


@bot.command(name="stopHC", aliases=["stophc"])
async def stop_hardcore(ctx):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("❌ You are not authorized to stop the Hardcore server.")
        return

    try:
        await asyncio.to_thread(hardcore_server.stop, 60)

        if hardcore_state.status != "DEAD":
            hardcore_state.status = "STOPPED"
            save_state(HARDCORE_STATE_PATH, hardcore_state)

        await ctx.send("💾 The Hardcore world was saved and the server stopped.")
    except Exception as error:
        await ctx.send(f"❌ Could not stop the Hardcore server: {error}")


@bot.command(name="statusHC", aliases=["statushc"])
async def status_hardcore(ctx):
    online = await asyncio.to_thread(hardcore_server.is_online)
    if online:
        server_status = "🟢 ONLINE"
    else:
        server_status = "🔴 OFFLINE"

    boss_progress = format_boss_progress(hardcore_state)

    await ctx.send(
        f"🏰 Hardcore Run {hardcore_state.run_number}\n"
        f"Challenge status: {hardcore_state.status}\n"
        f"Server connection: {server_status}\n\n"
        f"{boss_progress}"
    )


@bot.command(name="HCdeaths", aliases=["hcdeaths"])
async def hardcore_death_totals(ctx):
    death_totals = format_death_totals(hardcore_state)

    await ctx.send(death_totals)


@bot.command(name="HCdeathlog", aliases=["hcdeathlog"])
async def hardcore_death_log(ctx):
    death_log = format_death_log(hardcore_state)

    await ctx.send(death_log)


@bot.command(name="HCstats", aliases=["hcstats"])
async def hardcore_player_stats(ctx, *, player_name: str = ""):
    if not player_name.strip():
        await ctx.send("❌ Usage: `-HCstats <player>`")
        return

    player_stats = format_player_death_stats(
        state=hardcore_state,
        player_name=player_name,
    )

    await ctx.send(player_stats)


@bot.command(name="bossHC", aliases=["bosshc"])
async def boss_hardcore(ctx, *, boss_name: str = ""):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send(
            "❌ You are not authorized to record a Hardcore boss."
        )
        return

    if not boss_name.strip():
        await ctx.send("❌ Usage: `-bossHC ender dragon`")
        return

    normalized_name = normalize_boss_name(boss_name)

    if normalized_name not in hardcore_state.bosses:
        valid_bosses = ", ".join(
            name.replace("_", " ").title()
            for name in hardcore_state.bosses
        )
        await ctx.send(
            f"❌ Unknown boss. Choose from: {valid_bosses}."
        )
        return
    if hardcore_state.status != "RUNNING":
        await ctx.send(
            "❌ Bosses can only be recorded during an active Hardcore run."
        )
        return

    if hardcore_state.bosses[normalized_name]:
        display_name = normalized_name.replace("_", " ").title()
        await ctx.send(f"❌ {display_name} has already been recorded.")
        return

    recorded = record_boss_defeat(
        state=hardcore_state,
        boss_name=normalized_name,
    )

    if not recorded:
        await ctx.send("❌ Could not record that boss.")
        return

    save_state(HARDCORE_STATE_PATH, hardcore_state)

    announcement = format_boss_announcement(
        state=hardcore_state,
        boss_name=normalized_name,
    )

    channel = bot.get_channel(HC_ANNOUNCEMENT_CHANNEL_ID)

    if channel is not None:
        await channel.send(announcement)
    else:
        await ctx.send(
            "⚠ Boss recorded, but the announcement channel was not found."
        )

    minecraft_message = json.dumps(
        {
            "text": announcement,
            "color": "gold",
            "bold": True,
        }
    )

    try:
        await asyncio.to_thread(
            hardcore_server.send_command,
            f"tellraw @a {minecraft_message}",
        )
    except RuntimeError as error:
        await ctx.send(
            "⚠ Boss recorded, but the Minecraft announcement failed: "
            f"{error}"
        )


@bot.command(name="nextHC", aliases=["nexthc"])
async def next_hardcore(ctx):
    global hardcore_log_position, hardcore_log_initialized

    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send("❌ You are not authorized to prepare the next run.")
        return

    if hardcore_state.status != "DEAD":
        await ctx.send(f"❌ Run {hardcore_state.run_number} has not ended yet.")
        return

    online = await asyncio.to_thread(hardcore_server.is_online)
    if online:
        await ctx.send("❌ Stop the Hardcore Server before preparing the next run.")
        return

    if HC_ARCHIVE_DIRECTORY is None:
        await ctx.send("❌ HC_ARCHIVE_DIRECTORY has not been configured.")
        return

    try:
        archive_path = await asyncio.to_thread(
            archive_worlds,
            server_directory=hardcore_server.config.server_directory,
            archive_directory=HC_ARCHIVE_DIRECTORY,
            run_number=hardcore_state.run_number,
        )

        prepare_next_run(hardcore_state)
        save_state(HARDCORE_STATE_PATH, hardcore_state)

        hardcore_log_position = 0
        hardcore_log_initialized = False

        await ctx.send(
            f"✅ Previous world archived to `{archive_path}`.\n"
            f"🌎 Hardcore Run {hardcore_state.run_number} is ready!"
        )

    except FileExistsError as error:
        await ctx.send(f"❌ Could not archive the world: {error}")

    except FileNotFoundError as error:
        await ctx.send(f"❌ A required world folder is missing: {error}")

    except Exception as error:
        await ctx.send(f"❌ Could not prepare the next run: {error}")


@bot.command(name="testHCdeath", aliases=["testhcdeath"])
async def test_hardcore_death(ctx):
    if ctx.author.id not in AUTHORIZED_USERS:
        await ctx.send ("Sorry! You're not authorized to use this command!")
        return

    death = ParsedDeath(
        player="TestPlayer",
        cause="creeper",
        message="TestPlayer was blown up by Creeper",
    )

    announcement = format_death_announcement(run_number=6, death=death)

    await ctx.send(announcement)









# bot run
bot.run(TOKEN)
