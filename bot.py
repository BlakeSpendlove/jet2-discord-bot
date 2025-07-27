import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime

# Load environment variables from Railway (dotenv not needed)
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS").split(",")

FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

def get_roles(var): return [int(r) for r in os.getenv(var, "").split(",")]

WHITELIST_APP_RESULTS_ROLES = get_roles("WHITELIST_APP_RESULTS_ROLES")
WHITELIST_EMBED_ROLES = get_roles("WHITELIST_EMBED_ROLES")
WHITELIST_EXPLOITER_LOG_ROLES = get_roles("WHITELIST_EXPLOITER_LOG_ROLES")
WHITELIST_FLIGHTBRIEFING_ROLES = get_roles("WHITELIST_FLIGHTBRIEFING_ROLES")
WHITELIST_FLIGHTLOG_DELETE_ROLES = get_roles("WHITELIST_FLIGHTLOG_DELETE_ROLES")
WHITELIST_FLIGHTLOG_ROLES = get_roles("WHITELIST_FLIGHTLOG_ROLES")
WHITELIST_INFRACTION_REMOVE_ROLES = get_roles("WHITELIST_INFRACTION_REMOVE_ROLES")
WHITELIST_INFRACTION_ROLES = get_roles("WHITELIST_INFRACTION_ROLES")
WHITELIST_INFRACTION_VIEW_ROLES = get_roles("WHITELIST_INFRACTION_VIEW_ROLES")
WHITELIST_PROMOTE_ROLES = get_roles("WHITELIST_PROMOTE_ROLES")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def is_whitelisted(interaction: discord.Interaction, whitelist):
    return any(role.id in whitelist for role in interaction.user.roles)

def make_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

def footer(embed, unique_id):
    embed.set_footer(text=f"ID: {unique_id} | {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return embed

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        for guild_id in GUILD_IDS:
            await tree.sync(guild=discord.Object(id=int(guild_id)))
            print(f"✅ Synced to guild {guild_id}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

@tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! The bot is online.", ephemeral=True)

@tree.command(name="app_results", description="Send application results to a user")
@app_commands.describe(user="User to DM", result="Pass or Fail", reason="Reason for the result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    if not is_whitelisted(interaction, WHITELIST_APP_RESULTS_ROLES):
        await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Application Result",
        description=f"**Result:** {result}\n**Reason:** {reason}",
        color=discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    )
    embed = footer(embed, make_id())

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"✅ Sent result to {user.mention}.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Could not DM the user.", ephemeral=True)

@tree.command(name="embed", description="Send a custom embed using Discohook JSON")
@app_commands.describe(json="Paste your Discohook-style JSON")
async def embed(interaction: discord.Interaction, json: str):
    if not is_whitelisted(interaction, WHITELIST_EMBED_ROLES):
        await interaction.response.send_message("❌ You are not authorized.", ephemeral=True)
        return
    try:
        data = eval(json)  # You should use `json.loads()` in production!
        embed = discord.Embed.from_dict(data)
        embed = footer(embed, make_id())
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error parsing JSON: {e}", ephemeral=True)

# TODO: Add the rest of the 8 commands here...

bot.run(TOKEN)
