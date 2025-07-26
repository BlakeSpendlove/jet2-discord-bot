import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import string
from datetime import datetime

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS", "").split(",")

# Role-based permissions
EMBED_ROLE_IDS = [int(r) for r in os.getenv("EMBED_ROLE_IDS", "").split(",") if r.isdigit()]
APPRESULTS_ROLE_IDS = [int(r) for r in os.getenv("APPRESULTS_ROLE_IDS", "").split(",") if r.isdigit()]
EXPLOITLOG_ROLE_IDS = [int(r) for r in os.getenv("EXPLOITLOG_ROLE_IDS", "").split(",") if r.isdigit()]
PROMOTE_ROLE_IDS = [int(r) for r in os.getenv("PROMOTE_ROLE_IDS", "").split(",") if r.isdigit()]

# Channel IDs
APPRESULTS_CHANNEL_ID = int(os.getenv("APPRESULTS_CHANNEL_ID", "0"))
EXPLOITLOG_CHANNEL_ID = int(os.getenv("EXPLOITLOG_CHANNEL_ID", "0"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", "0"))

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Generate a unique 6-character ID
def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Check authorization
def is_authorized(interaction: discord.Interaction, allowed_roles: list) -> bool:
    if not interaction.user or not hasattr(interaction.user, 'roles'):
        return False
    user_roles = [role.id for role in interaction.user.roles]
    return any(role in user_roles for role in allowed_roles)

# /embed
@app_commands.command(name="embed", description="Send a custom embed")
@app_commands.describe(title="Title of the embed", description="Main body of the embed")
async def embed(interaction: discord.Interaction, title: str, description: str):
    if not is_authorized(interaction, EMBED_ROLE_IDS):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return
    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    await interaction.response.send_message(embed=embed)

# /app_results
@app_commands.command(name="app_results", description="Post application results")
@app_commands.describe(user="User to mention", result="Pass or Fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    if not is_authorized(interaction, APPRESULTS_ROLE_IDS):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return
    channel = bot.get_channel(APPRESULTS_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
        return
    embed = discord.Embed(title="Application Result", description=f"{user.mention} has **{result.upper()}** their application!", color=discord.Color.green() if result.lower() == "pass" else discord.Color.red())
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Result posted!", ephemeral=True)

# /exploiter_log
@app_commands.command(name="exploiter_log", description="Log an exploiter")
@app_commands.describe(user="User to log", reason="Reason for logging")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, reason: str):
    if not is_authorized(interaction, EXPLOITLOG_ROLE_IDS):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return
    channel = bot.get_channel(EXPLOITLOG_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
        return
    embed = discord.Embed(title="Exploiter Log", description=f"User: {user.mention}\nReason: {reason}", color=discord.Color.red())
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Exploiter logged.", ephemeral=True)

# /promote
@app_commands.command(name="promote", description="Announce a promotion")
@app_commands.describe(user="User being promoted", new_rank="New rank title")
async def promote(interaction: discord.Interaction, user: discord.User, new_rank: str):
    if not is_authorized(interaction, PROMOTE_ROLE_IDS):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
        return
    embed = discord.Embed(title="Promotion", description=f"{user.mention} has been promoted to **{new_rank}**!", color=discord.Color.blue())
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Promotion announced!", ephemeral=True)

# Sync commands
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        for guild_id in GUILD_IDS:
            guild = discord.Object(id=int(guild_id.strip()))
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

bot.run(TOKEN)
