import discord
from discord.ext import commands
from discord import app_commands, Embed
import os
import json
import random
import string
from datetime import datetime

# --- Utilities ---
def generate_log_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_footer():
    return f"Logged at {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')} | ID: {generate_log_id()}"

def get_whitelist(env_name):
    return [int(role) for role in os.getenv(env_name, '').split(',') if role.isdigit()]

def is_allowed(interaction: discord.Interaction, env_name: str):
    allowed_roles = get_whitelist(env_name)
    return any(role.id in allowed_roles for role in interaction.user.roles)

def get_channel(bot, var_name):
    channel_id = os.getenv(var_name)
    return bot.get_channel(int(channel_id)) if channel_id and channel_id.isdigit() else None

# --- Setup ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

guild_ids = [int(gid) for gid in os.getenv("GUILD_IDS", "").split(',') if gid.isdigit()]

# --- Events ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# -------------------- /embed --------------------
@bot.tree.command(name="embed", description="Send a custom embed via Discohook JSON")
async def embed(interaction: discord.Interaction, json_data: str):
    if not is_allowed(interaction, 'WHITELIST_EMBED_ROLES'):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return
    try:
        data = json.loads(json_data)
        emb = Embed.from_dict(data)
        emb.set_footer(text=get_footer())
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# -------------------- /app_results --------------------
@bot.tree.command(name="app_results", description="Post application results")
async def app_results(interaction: discord.Interaction, user: discord.Member, result: str):
    if not is_allowed(interaction, 'WHITELIST_APP_RESULTS_ROLES'):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return
    emb = Embed(title="Application Result", description=f"User: {user.mention}\nResult: {result}", color=0x3498db)
    emb.set_footer(text=get_footer())
    await interaction.response.send_message(embed=emb)

# -------------------- /exploiter_log --------------------
@bot.tree.command(name="exploiter_log", description="Log an exploiter")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str):
    if not is_allowed(interaction, 'WHITELIST_EXPLOITER_LOG_ROLES'):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return
    emb = Embed(title="🚨 Exploiter Log", description=f"**Username:** {user}\n**Reason:** {reason}", color=0xe74c3c)
    emb.set_footer(text=get_footer())
    await interaction.response.send_message(embed=emb)

# -------------------- /promote --------------------
@bot.tree.command(name="promote", description="Log a promotion")
async def promote(interaction: discord.Interaction, user: discord.Member, new_role: str):
    if not is_allowed(interaction, 'WHITELIST_PROMOTE_ROLES'):
        await interaction.response.send_message("You do not have permission.", ephemeral=True)
        return
    emb = Embed(title="📈 Promotion Log", description=f"{user.mention} has been promoted to **{new_role}**!", color=0x2ecc71)
    emb.set_footer(text=get_footer())
    channel = get_channel(bot, 'PROMOTE_CHANNEL_ID') or interaction.channel
    await channel.send(embed=emb)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

# -------------------- Placeholder for remaining commands --------------------
# (Add /flight_briefing, /flight_log, /flightlog_delete, etc. here following the same pattern)

# --- Run ---
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
