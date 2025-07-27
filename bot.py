import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import random

# --- Setup Intents and Bot ---
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)

# --- Environment Variables ---
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
GUILD_IDS = [int(guild_id.strip()) for guild_id in os.getenv("GUILD_IDS").split(",")]
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

WHITELIST_APP_RESULTS_ROLES = [int(i) for i in os.getenv("WHITELIST_APP_RESULTS_ROLES").split(",")]
WHITELIST_EMBED_ROLES = [int(i) for i in os.getenv("WHITELIST_EMBED_ROLES").split(",")]
WHITELIST_EXPLOITER_LOG_ROLES = [int(i) for i in os.getenv("WHITELIST_EXPLOITER_LOG_ROLES").split(",")]
WHITELIST_FLIGHTBRIEFING_ROLES = [int(i) for i in os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES").split(",")]
WHITELIST_FLIGHTLOG_DELETE_ROLES = [int(i) for i in os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES").split(",")]
WHITELIST_FLIGHTLOG_ROLES = [int(i) for i in os.getenv("WHITELIST_FLIGHTLOG_ROLES").split(",")]
WHITELIST_INFRACTION_REMOVE_ROLES = [int(i) for i in os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES").split(",")]
WHITELIST_INFRACTION_ROLES = [int(i) for i in os.getenv("WHITELIST_INFRACTION_ROLES").split(",")]
WHITELIST_INFRACTION_VIEW_ROLES = [int(i) for i in os.getenv("WHITELIST_INFRACTION_VIEW_ROLES").split(",")]
WHITELIST_PROMOTE_ROLES = [int(i) for i in os.getenv("WHITELIST_PROMOTE_ROLES").split(",")]

# --- Helper Functions ---
def is_authorized(interaction: discord.Interaction, whitelist_roles):
    return any(role.id in whitelist_roles for role in interaction.user.roles)

def generate_id():
    return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))

# --- Ready Event ---
@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_IDS[0]))
        print(f"Synced {len(synced)} command(s) to {GUILD_IDS[0]}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# --- Add your commands below ---
# We'll continue building all 11 commands here in the next message.

# Temporary command to confirm working bot
@bot.tree.command(name="ping", description="Check if bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Bot is online.", ephemeral=True)

# --- Run Bot ---
bot.run(DISCORD_TOKEN)
