import os
import discord
from discord.ext import commands
from discord import app_commands, Interaction, Embed, File
import random
import string
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = list(map(int, os.getenv("GUILD_IDS").split(",")))

# Channel IDs
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

# Whitelist Roles
WHITELIST_APP_RESULTS_ROLES = list(map(int, os.getenv("WHITELIST_APP_RESULTS_ROLES").split(",")))
WHITELIST_EMBED_ROLES = list(map(int, os.getenv("WHITELIST_EMBED_ROLES").split(",")))
WHITELIST_EXPLOITER_LOG_ROLES = list(map(int, os.getenv("WHITELIST_EXPLOITER_LOG_ROLES").split(",")))
WHITELIST_FLIGHTBRIEFING_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES").split(",")))
WHITELIST_FLIGHTLOG_DELETE_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES").split(",")))
WHITELIST_FLIGHTLOG_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_ROLES").split(",")))
WHITELIST_INFRACTION_REMOVE_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES").split(",")))
WHITELIST_INFRACTION_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_ROLES").split(",")))
WHITELIST_INFRACTION_VIEW_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_VIEW_ROLES").split(",")))
WHITELIST_PROMOTE_ROLES = list(map(int, os.getenv("WHITELIST_PROMOTE_ROLES").split(",")))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def has_whitelisted_role(interaction: Interaction, allowed_roles):
    return any(role.id in allowed_roles for role in interaction.user.roles)

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def make_footer():
    return f"ID: {generate_id()} • {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_IDS[0]))
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

# /app_results
@bot.tree.command(name="app_results", description="DM a user their application result")
@app_commands.describe(user="User to DM", result="Result message (Pass/Fail)", reason="Reason for the result")
async def app_results(interaction: Interaction, user: discord.Member, result: str, reason: str):
    if not has_whitelisted_role(interaction, WHITELIST_APP_RESULTS_ROLES):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    embed = Embed(title="Application Result", description=result, color=discord.Color.green() if "pass" in result.lower() else discord.Color.red())
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=make_footer())
    await user.send(embed=embed)
    await interaction.response.send_message(f"✅ Application result sent to {user.mention}.", ephemeral=True)

# /flight_briefing
@bot.tree.command(name="flight_briefing", description="Send a flight briefing embed")
@app_commands.describe(game_link="Link to the game", vc_link="Link to the VC", flight_code="Flight Code (e.g., LS8800)")
async def flight_briefing(interaction: Interaction, game_link: str, vc_link: str, flight_code: str):
    if not has_whitelisted_role(interaction, WHITELIST_FLIGHTBRIEFING_ROLES):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    embed = Embed(title="Flight Briefing", color=discord.Color.blue())
    embed.add_field(name="Game Link", value=f"[Click here]({game_link})")
    embed.add_field(name="VC Link", value=f"[Join VC]({vc_link})")
    embed.add_field(name="Flight Code", value=flight_code, inline=False)
    embed.set_footer(text=make_footer())

    await interaction.response.send_message(embed=embed)

# /flight_log
@bot.tree.command(name="flight_log", description="Log a completed flight")
@app_commands.describe(user="User to log", file="Attach the log file", flight_code="Flight code (e.g., LS8800)")
async def flight_log(interaction: Interaction, user: discord.Member, file: discord.Attachment, flight_code: str):
    if not has_whitelisted_role(interaction, WHITELIST_FLIGHTLOG_ROLES):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    embed = Embed(title="Flight Log", color=discord.Color.orange())
    embed.add_field(name="Logged User", value=user.mention)
    embed.add_field(name="Flight Code", value=flight_code)
    embed.set_footer(text=make_footer())

    channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
    await channel.send(embed=embed, file=await file.to_file())
    await interaction.response.send_message(f"✅ Flight log for {user.mention} sent.", ephemeral=True)

# /promote
@bot.tree.command(name="promote", description="Log a promotion")
@app_commands.describe(user="User promoted", reason="Reason for promotion", promoted_to="New role or rank")
async def promote(interaction: Interaction, user: discord.Member, reason: str, promoted_to: str):
    if not has_whitelisted_role(interaction, WHITELIST_PROMOTE_ROLES):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return

    embed = Embed(title="Promotion Log", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Promoted To", value=promoted_to)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=make_footer())

    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Promotion log for {user.mention} sent.", ephemeral=True)

bot.run(TOKEN)
