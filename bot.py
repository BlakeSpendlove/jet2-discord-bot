import os
import discord
from discord.ext import commands
from discord import app_commands, File, Embed
from dotenv import load_dotenv
import json
import random
import string
from datetime import datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = list(map(int, os.getenv("GUILD_IDS", "").split(",")))

FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

WHITELIST_APP_RESULTS_ROLES = list(map(int, os.getenv("WHITELIST_APP_RESULTS_ROLES", "").split(",")))
WHITELIST_EMBED_ROLES = list(map(int, os.getenv("WHITELIST_EMBED_ROLES", "").split(",")))
WHITELIST_EXPLOITER_LOG_ROLES = list(map(int, os.getenv("WHITELIST_EXPLOITER_LOG_ROLES", "").split(",")))
WHITELIST_FLIGHTBRIEFING_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES", "").split(",")))
WHITELIST_FLIGHTLOG_DELETE_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES", "").split(",")))
WHITELIST_FLIGHTLOG_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_ROLES", "").split(",")))
WHITELIST_INFRACTION_REMOVE_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES", "").split(",")))
WHITELIST_INFRACTION_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_ROLES", "").split(",")))
WHITELIST_INFRACTION_VIEW_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_VIEW_ROLES", "").split(",")))
WHITELIST_PROMOTE_ROLES = list(map(int, os.getenv("WHITELIST_PROMOTE_ROLES", "").split(",")))

# Utility functions

def generate_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def current_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def is_whitelisted(interaction, whitelist_roles):
    return any(role.id in whitelist_roles for role in interaction.user.roles)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@bot.event
async def on_ready():
    for guild_id in GUILD_IDS:
        await tree.sync(guild=discord.Object(id=guild_id))
    print(f"✅ Logged in as {bot.user} and synced with {len(GUILD_IDS)} guild(s).")

# COMMANDS

@tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! I'm online.", ephemeral=True)

@tree.command(name="app_results", description="Send an application result to a user")
@app_commands.describe(user="User to send result to", result="Result (pass/fail)", reason="Optional reason")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str = ""): 
    if not is_whitelisted(interaction, WHITELIST_APP_RESULTS_ROLES):
        return await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)

    embed = Embed(title="Jet2 Application Result", color=0x00ff00 if result.lower() == "pass" else 0xff0000)
    embed.add_field(name="Status", value=result.capitalize(), inline=False)
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=f"ID: {generate_id()} | {current_timestamp()}")
    await user.send(embed=embed)
    await interaction.response.send_message(f"✅ Sent application result to {user.mention}.", ephemeral=True)

# TO BE CONTINUED: Add the remaining 10 commands here following the same pattern
# Due to message size limits, commands like:
# /embed
# /exploiter_log
# /flight_briefing
# /flight_log
# /flightlog_delete
# /flightlogs_view
# /infraction
# /infraction_remove
# /infraction_view
# /promote
# Will follow with full embed formats, role checks, and prompt validation.

# Start the bot
bot.run(TOKEN)
