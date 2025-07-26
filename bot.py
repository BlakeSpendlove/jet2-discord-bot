import discord
from discord.ext import commands
from discord import app_commands, File
import os
import random
import string
from datetime import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = list(map(int, os.getenv("GUILD_IDS", "").split(",")))

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

FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID", 0))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID", 0))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="/", intents=intents)


def generate_footer():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    return f"ID: {code} | {timestamp}"


def is_whitelisted(interaction: discord.Interaction, allowed_roles: list):
    return any(role.id in allowed_roles for role in interaction.user.roles)


@bot.event
async def on_ready():
    await bot.tree.sync(guild=None)
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="embed", description="Send a custom embed using Discohook JSON")
@app_commands.checks.has_any_role(*WHITELIST_EMBED_ROLES)
@app_commands.describe(json="Raw Discohook-style embed JSON")
async def embed(interaction: discord.Interaction, json: str):
    await interaction.response.send_message("Embed command received (functionality placeholder)", ephemeral=True)


@bot.tree.command(name="app_results", description="Send application result to user")
@app_commands.checks.has_any_role(*WHITELIST_APP_RESULTS_ROLES)
@app_commands.describe(user="User to DM", result="Result: Pass or Fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    embed = discord.Embed(
        title="Application Result",
        description=f"You have **{result.upper()}** your application.",
        color=discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    )
    embed.set_footer(text=generate_footer())
    await user.send(embed=embed)
    await interaction.response.send_message("Result sent.", ephemeral=True)


@bot.tree.command(name="exploiter_log", description="Log an exploiter")
@app_commands.checks.has_any_role(*WHITELIST_EXPLOITER_LOG_ROLES)
@app_commands.describe(user="User being reported", reason="Why they are being logged", evidence="Upload file")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str, evidence: discord.Attachment):
    embed = discord.Embed(title="🚨 Exploiter Logged", color=discord.Color.red())
    embed.add_field(name="User", value=user, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=evidence.url)
    embed.set_footer(text=generate_footer())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="promote", description="Log a promotion")
@app_commands.checks.has_any_role(*WHITELIST_PROMOTE_ROLES)
@app_commands.describe(user="User being promoted", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.Member, reason: str):
    embed = discord.Embed(title="📈 Promotion Logged", color=discord.Color.blue())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=generate_footer())
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)


@bot.tree.command(name="flight_log", description="Log a flight")
@app_commands.checks.has_any_role(*WHITELIST_FLIGHTLOG_ROLES)
@app_commands.describe(file="Flight log file")
async def flight_log(interaction: discord.Interaction, file: discord.Attachment):
    embed = discord.Embed(title="✈️ Flight Log Submitted", color=discord.Color.blue())
    embed.add_field(name="Submitted By", value=interaction.user.mention, inline=False)
    embed.set_footer(text=generate_footer())
    channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
    await channel.send(embed=embed, file=await file.to_file())
    await interaction.response.send_message("Flight log submitted.", ephemeral=True)


@bot.tree.command(name="flightlog_delete", description="Delete a flight log by ID")
@app_commands.checks.has_any_role(*WHITELIST_FLIGHTLOG_DELETE_ROLES)
@app_commands.describe(log_id="Log ID to delete")
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    await interaction.response.send_message(f"(Placeholder) Deleted log ID {log_id}", ephemeral=True)


@bot.tree.command(name="flightlogs_view", description="View a user's flight logs")
@app_commands.checks.has_any_role(*WHITELIST_FLIGHTLOG_ROLES)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"(Placeholder) Viewing logs for {user.mention}", ephemeral=True)


@bot.tree.command(name="infraction", description="Log an infraction")
@app_commands.checks.has_any_role(*WHITELIST_INFRACTION_ROLES)
@app_commands.describe(user="User being infracted", reason="Reason", type="Type (e.g. warning, termination)")
async def infraction(interaction: discord.Interaction, user: discord.Member, reason: str, type: str):
    embed = discord.Embed(title="⚠️ Infraction Logged", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention, inline=False)
    embed.add_field(name="Type", value=type, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=generate_footer())
    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)


@bot.tree.command(name="infraction_remove", description="Delete an infraction by ID")
@app_commands.checks.has_any_role(*WHITELIST_INFRACTION_REMOVE_ROLES)
@app_commands.describe(log_id="Log ID to delete")
async def infraction_remove(interaction: discord.Interaction, log_id: str):
    await interaction.response.send_message(f"(Placeholder) Deleted infraction ID {log_id}", ephemeral=True)


@bot.tree.command(name="infraction_view", description="View a user's infractions")
@app_commands.checks.has_any_role(*WHITELIST_INFRACTION_VIEW_ROLES)
@app_commands.describe(user="User to view infractions for")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"(Placeholder) Viewing infractions for {user.mention}", ephemeral=True)


@bot.tree.command(name="flight_briefing", description="Send a flight briefing")
@app_commands.checks.has_any_role(*WHITELIST_FLIGHTBRIEFING_ROLES)
@app_commands.describe(game_link="Flight game link", vc_link="VC link")
async def flight_briefing(interaction: discord.Interaction, game_link: str, vc_link: str):
    embed = discord.Embed(title="🛫 Flight Briefing", color=discord.Color.teal())
    embed.add_field(name="Game Link", value=game_link, inline=False)
    embed.add_field(name="VC Link", value=vc_link, inline=False)
    embed.set_footer(text=generate_footer())
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
