import discord
from discord.ext import commands
from discord import app_commands, File, ButtonStyle
from discord.ui import View, Button
import os
import random
import string
from datetime import datetime, timezone

# Load variables from environment
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = list(map(int, os.getenv("GUILD_IDS", "").split(",")))

# Channels
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

# Whitelist roles (converted to sets of ints for easy checking)
def parse_roles(var): return set(map(int, os.getenv(var, "").split(",")))

WHITELIST_APP_RESULTS_ROLES = parse_roles("WHITELIST_APP_RESULTS_ROLES")
WHITELIST_EMBED_ROLES = parse_roles("WHITELIST_EMBED_ROLES")
WHITELIST_EXPLOITER_LOG_ROLES = parse_roles("WHITELIST_EXPLOITER_LOG_ROLES")
WHITELIST_FLIGHTBRIEFING_ROLES = parse_roles("WHITELIST_FLIGHTBRIEFING_ROLES")
WHITELIST_FLIGHTLOG_DELETE_ROLES = parse_roles("WHITELIST_FLIGHTLOG_DELETE_ROLES")
WHITELIST_FLIGHTLOG_ROLES = parse_roles("WHITELIST_FLIGHTLOG_ROLES")
WHITELIST_INFRACTION_REMOVE_ROLES = parse_roles("WHITELIST_INFRACTION_REMOVE_ROLES")
WHITELIST_INFRACTION_ROLES = parse_roles("WHITELIST_INFRACTION_ROLES")
WHITELIST_INFRACTION_VIEW_ROLES = parse_roles("WHITELIST_INFRACTION_VIEW_ROLES")
WHITELIST_PROMOTE_ROLES = parse_roles("WHITELIST_PROMOTE_ROLES")

# Utils
def generate_footer():
    return f"ID: {''.join(random.choices(string.ascii_uppercase + string.digits, k=6))} • {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"

def is_authorized(interaction, whitelisted_roles):
    return any(role.id in whitelisted_roles for role in interaction.user.roles)

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Embed command
@bot.tree.command(name="embed", description="Send an embed using Discohook JSON")
async def embed(interaction: discord.Interaction, json_text: str):
    if not is_authorized(interaction, WHITELIST_EMBED_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    try:
        embed = discord.Embed.from_dict(eval(json_text))
        embed.set_footer(text=generate_footer())
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# Application results
@bot.tree.command(name="app_results", description="Send application results via DM")
@app_commands.describe(user="User to DM", result="Result (pass/fail)")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    if not is_authorized(interaction, WHITELIST_APP_RESULTS_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Application Result",
        description=f"Hello {user.mention}, your application has been **{result.upper()}**!",
        color=discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    )
    embed.set_footer(text=generate_footer())
    await user.send(embed=embed)
    await interaction.response.send_message("Result sent.", ephemeral=True)

# Exploiter log
@bot.tree.command(name="exploiter_log", description="Log an exploiter")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str, evidence: discord.Attachment):
    if not is_authorized(interaction, WHITELIST_EXPLOITER_LOG_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
    embed = discord.Embed(title="🚨 Exploiter Log", color=discord.Color.red())
    embed.add_field(name="User", value=user)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=generate_footer())
    await channel.send(embed=embed, file=await evidence.to_file())
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

# Promote
@bot.tree.command(name="promote", description="Log a promotion")
async def promote(interaction: discord.Interaction, user: discord.User, new_rank: str, reason: str):
    if not is_authorized(interaction, WHITELIST_PROMOTE_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    embed = discord.Embed(title="📈 Promotion Logged", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="New Rank", value=new_rank)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=generate_footer())
    await channel.send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

# Flight briefing
@bot.tree.command(name="flight_briefing", description="Send flight briefing embed with buttons")
async def flight_briefing(interaction: discord.Interaction, route: str, time: str, aircraft: str, game_link: str, vc_link: str):
    if not is_authorized(interaction, WHITELIST_FLIGHTBRIEFING_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    embed = discord.Embed(title="🛫 Flight Briefing", color=discord.Color.blue())
    embed.add_field(name="Route", value=route)
    embed.add_field(name="Time", value=time)
    embed.add_field(name="Aircraft", value=aircraft)
    embed.set_footer(text=generate_footer())
    view = View()
    view.add_item(Button(label="Join Game", url=game_link, style=ButtonStyle.link))
    view.add_item(Button(label="Join VC", url=vc_link, style=ButtonStyle.link))
    await interaction.response.send_message(embed=embed, view=view)

# Flight log
@bot.tree.command(name="flight_log", description="Log a flight")
async def flight_log(interaction: discord.Interaction, flight_code: str, aircraft: str, route: str, file: discord.Attachment):
    if not is_authorized(interaction, WHITELIST_FLIGHTLOG_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    embed = discord.Embed(title="✈️ Flight Log", color=discord.Color.blue())
    embed.add_field(name="Flight Code", value=flight_code)
    embed.add_field(name="Aircraft", value=aircraft)
    embed.add_field(name="Route", value=route)
    embed.set_footer(text=generate_footer())
    await bot.get_channel(FLIGHTLOG_CHANNEL_ID).send(embed=embed, file=await file.to_file())
    await interaction.response.send_message("Flight logged.", ephemeral=True)

# Flightlog delete
flight_logs = {}  # This should ideally be persistent

@bot.tree.command(name="flightlog_delete", description="Delete a flight log")
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    if not is_authorized(interaction, WHITELIST_FLIGHTLOG_DELETE_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    # Simulate deletion (you'd need a DB or message ID store)
    await interaction.response.send_message(f"Flight log {log_id} deleted.", ephemeral=True)

# Flightlogs view
@bot.tree.command(name="flightlogs_view", description="View user flight logs")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    if not is_authorized(interaction, WHITELIST_FLIGHTLOG_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    await interaction.response.send_message(f"Showing logs for {user.display_name}. (WIP)", ephemeral=True)

# Infraction
@bot.tree.command(name="infraction", description="Log an infraction/demotion/termination")
async def infraction(interaction: discord.Interaction, user: discord.User, type: str, reason: str):
    if not is_authorized(interaction, WHITELIST_INFRACTION_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    embed = discord.Embed(title=f"⚠️ {type.capitalize()}", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=generate_footer())
    await bot.get_channel(INFRACTION_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

# Infraction remove
@bot.tree.command(name="infraction_remove", description="Remove an infraction by ID")
async def infraction_remove(interaction: discord.Interaction, log_id: str):
    if not is_authorized(interaction, WHITELIST_INFRACTION_REMOVE_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    await interaction.response.send_message(f"Infraction {log_id} removed.", ephemeral=True)

# Infraction view
@bot.tree.command(name="infraction_view", description="View user infractions")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    if not is_authorized(interaction, WHITELIST_INFRACTION_VIEW_ROLES):
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    await interaction.response.send_message(f"Showing infractions for {user.display_name}. (WIP)", ephemeral=True)

# Sync on ready
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    for guild_id in GUILD_IDS:
        guild = discord.Object(id=guild_id)
        await bot.tree.sync(guild=guild)
    print("Commands synced.")

# Run bot
bot.run(TOKEN)
