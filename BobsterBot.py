# all the important import stuff (allows the bot to actually work)
import discord
from discord.ext import commands
import subprocess
import asyncio

# Load private configuration from the local .env file
from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

from hardcore.monitor import ParsedDeath
from hardcore.service import format_death_announcement

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



# COMMANDS

# simple greeting command that displays commands
@bot.command()
async def Bobster(ctx):
    await ctx.send ("Hello! I'm Bobster Bot! My commands are as follows:" \
    "\n```-status --> Returns the status of the server (Online/Offline)"
    "\n-start --> Turns on the server"
    "\n-stop --> Stops the server" \
    "\n-players --> Shows the number of players online and their usernames"
    "\n~~~~~~~~~~~~"
    "\nThe following are commands for authorized users"
    "\n-arm --> Arms the bot and allows others to turn on the server"
    "\n-disarm --> Disarms me and bars others from turning the server on```")

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
                "@libraries/net/neoforged/neoforge/21.1.194\win_args.txt"
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

    try:
        await asyncio.to_thread(hardcore_server.start)
        await ctx.send("⏳ Starting the vanilla Hardcore server...")
        online = await asyncio.to_thread(hardcore_server.wait_until_online, 120)
        if online:
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
        await ctx.send("💾 The Hardcore world was saved and the server stopped.")
    except Exception as error:
        await ctx.send(f"❌ Could not stop the Hardcore server: {error}")


@bot.command(name="statusHC", aliases=["statushc"])
async def status_hardcore(ctx):
    online = await asyncio.to_thread(hardcore_server.is_online)
    if online:
        await ctx.send("🟢 The Hardcore server is online.")
    else:
        await ctx.send("🔴 The Hardcore server is offline.")


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
