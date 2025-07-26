import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import string
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(g) for g in os.getenv("GUILD_IDS", "").split(",") if g.isdigit()]

# Channel variables
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", 0))
APP_RESULTS_CHANNEL_ID = int(os.getenv("APP_RESULTS_CHANNEL_ID", 0))
EXPLOITER_LOG_CHANNEL_ID = int(os.getenv("EXPLOITER_LOG_CHANNEL_ID", 0))
EMBED_CHANNEL_ID = int(os.getenv("EMBED_CHANNEL_ID", 0))

# Role ID whitelists (as comma-separated env vars)
PROMOTE_ROLE_IDS = [int(r) for r in os.getenv("PROMOTE_ROLE_IDS", "").split(",") if r.isdigit()]
APP_RESULTS_ROLE_IDS = [int(r) for r in os.getenv("APP_RESULTS_ROLE_IDS", "").split(",") if r.isdigit()]
EXPLOITER_LOG_ROLE_IDS = [int(r) for r in os.getenv("EXPLOITER_LOG_ROLE_IDS", "").split(",") if r.isdigit()]
EMBED_ROLE_IDS = [int(r) for r in os.getenv("EMBED_ROLE_IDS", "").split(",") if r.isdigit()]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def is_authorized(interaction: discord.Interaction, allowed_roles):
    author_roles = [role.id for role in interaction.user.roles]
    return any(role in author_roles for role in allowed_roles)

def send_embed(title: str, description: str, color: discord.Color):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    for guild_id in GUILD_IDS:
        try:
            await bot.tree.sync(guild=discord.Object(id=guild_id))
            print(f"Synced commands for guild {guild_id}")
        except Exception as e:
            print(f"Failed to sync for guild {guild_id}: {e}")

@app_commands.command(name="embed", description="Send a custom embed")
@app_commands.describe(title="Embed title", description="Embed description")
async def embed_cmd(interaction: discord.Interaction, title: str, description: str):
    if not is_authorized(interaction, EMBED_ROLE_IDS):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    embed = send_embed(title, description, discord.Color.red())
    channel = bot.get_channel(EMBED_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    else:
        await interaction.response.send_message("Embed channel not found.", ephemeral=True)

@app_commands.command(name="promote", description="Log a promotion")
@app_commands.describe(user="User being promoted", new_rank="New rank")
async def promote(interaction: discord.Interaction, user: discord.Member, new_rank: str):
    if not is_authorized(interaction, PROMOTE_ROLE_IDS):
        await interaction.response.send_message("Unauthorized.", ephemeral=True)
        return
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    if channel:
        embed = send_embed("Promotion Logged", f"{user.mention} has been promoted to **{new_rank}** by {interaction.user.mention}", discord.Color.green())
        await channel.send(embed=embed)
        await interaction.response.send_message("Promotion logged.", ephemeral=True)
    else:
        await interaction.response.send_message("Promotion channel not found.", ephemeral=True)

@app_commands.command(name="app_results", description="Post application results")
@app_commands.describe(user="Applicant", result="Accepted or Rejected", notes="Optional notes")
async def app_results(interaction: discord.Interaction, user: discord.Member, result: str, notes: str = "N/A"):
    if not is_authorized(interaction, APP_RESULTS_ROLE_IDS):
        await interaction.response.send_message("Unauthorized.", ephemeral=True)
        return
    channel = bot.get_channel(APP_RESULTS_CHANNEL_ID)
    if channel:
        res_text = "✅ **Accepted**" if result.lower() == "accepted" else "❌ **Rejected**"
        embed = send_embed("Application Result", f"{user.mention} has been {res_text}\n**Notes:** {notes}", discord.Color.blue())
        await channel.send(embed=embed)
        await interaction.response.send_message("Result posted.", ephemeral=True)
    else:
        await interaction.response.send_message("Application results channel not found.", ephemeral=True)

@app_commands.command(name="exploiter_log", description="Log an exploiter")
@app_commands.describe(user="Exploiter", reason="Reason")
async def exploiter_log(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_authorized(interaction, EXPLOITER_LOG_ROLE_IDS):
        await interaction.response.send_message("Unauthorized.", ephemeral=True)
        return
    channel = bot.get_channel(EXPLOITER_LOG_CHANNEL_ID)
    if channel:
        embed = send_embed("Exploiter Logged", f"{user.mention} was logged for: {reason}", discord.Color.dark_red())
        await channel.send(embed=embed)
        await interaction.response.send_message("Exploiter logged.", ephemeral=True)
    else:
        await interaction.response.send_message("Exploiter log channel not found.", ephemeral=True)

# Register commands
bot.tree.add_command(embed_cmd)
bot.tree.add_command(promote)
bot.tree.add_command(app_results)
bot.tree.add_command(exploiter_log)

bot.run(TOKEN)
