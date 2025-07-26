import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(gid.strip()) for gid in os.getenv("GUILD_IDS", "").split(",") if gid.strip().isdigit()]

WHITELIST_EMBED_ROLES = os.getenv("WHITELIST_EMBED_ROLES", "").split(',')
WHITELIST_APP_RESULTS_ROLES = os.getenv("WHITELIST_APP_RESULTS_ROLES", "").split(',')
WHITELIST_EXPLOITER_LOG_ROLES = os.getenv("WHITELIST_EXPLOITER_LOG_ROLES", "").split(',')
WHITELIST_PROMOTE_ROLES = os.getenv("WHITELIST_PROMOTE_ROLES", "").split(',')
WHITELIST_FLIGHTLOG_ROLES = os.getenv("WHITELIST_FLIGHTLOG_ROLES", "").split(',')
WHITELIST_FLIGHTLOG_DELETE_ROLES = os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES", "").split(',')
WHITELIST_INFRACTION_ROLES = os.getenv("WHITELIST_INFRACTION_ROLES", "").split(',')
WHITELIST_INFRACTION_REMOVE_ROLES = os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES", "").split(',')
WHITELIST_INFRACTION_VIEW_ROLES = os.getenv("WHITELIST_INFRACTION_VIEW_ROLES", "").split(',')
WHITELIST_FLIGHTBRIEFING_ROLES = os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES", "").split(',')

APPRESULTS_CHANNEL_ID = int(os.getenv("APPRESULTS_CHANNEL_ID", 0))
EXPLOITLOG_CHANNEL_ID = int(os.getenv("EXPLOITLOG_CHANNEL_ID", 0))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", 0))
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID", 0))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def is_whitelisted(interaction: discord.Interaction, allowed_roles):
    return any(str(role.id) in allowed_roles for role in interaction.user.roles)

def embed_footer():
    return f"ID: {''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync(guild=None)
        print(f'Synced {len(synced)} command(s) globally')
    except Exception as e:
        print(f"Sync failed: {e}")

@bot.tree.command(name="embed", description="Send a custom embed (Discohook JSON)")
@app_commands.describe(json="Discohook JSON")
async def embed(interaction: discord.Interaction, json: str):
    if not is_whitelisted(interaction, WHITELIST_EMBED_ROLES):
        return await interaction.response.send_message("Unauthorized.", ephemeral=True)
    try:
        import json as js
        data = js.loads(json)
        embed = discord.Embed.from_dict(data['embeds'][0])
        embed.set_footer(text=embed_footer())
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error parsing JSON: {e}", ephemeral=True)

@bot.tree.command(name="app_results", description="Send application results")
@app_commands.describe(user="Applicant", result="Pass or Fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    if not is_whitelisted(interaction, WHITELIST_APP_RESULTS_ROLES):
        return await interaction.response.send_message("Unauthorized.", ephemeral=True)
    embed = discord.Embed(title="Application Results", color=discord.Color.green() if result.lower() == "pass" else discord.Color.red())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Result", value=result)
    embed.set_footer(text=embed_footer())
    channel = bot.get_channel(APPRESULTS_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Application result sent.", ephemeral=True)

@bot.tree.command(name="exploiter_log", description="Log an exploiter")
@app_commands.describe(user="Exploiter", reason="Reason")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, reason: str):
    if not is_whitelisted(interaction, WHITELIST_EXPLOITER_LOG_ROLES):
        return await interaction.response.send_message("Unauthorized.", ephemeral=True)
    embed = discord.Embed(title="Exploiter Logged", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=embed_footer())
    channel = bot.get_channel(EXPLOITLOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

@bot.tree.command(name="promote", description="Promote a member")
@app_commands.describe(user="User to promote", new_rank="New rank")
async def promote(interaction: discord.Interaction, user: discord.User, new_rank: str):
    if not is_whitelisted(interaction, WHITELIST_PROMOTE_ROLES):
        return await interaction.response.send_message("Unauthorized.", ephemeral=True)
    embed = discord.Embed(title="Promotion", color=discord.Color.blue())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="New Rank", value=new_rank)
    embed.set_footer(text=embed_footer())
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Promotion announced.", ephemeral=True)

# Additional commands (e.g. flight_log, infraction, etc.) can be added here following the same pattern

bot.run(TOKEN)
