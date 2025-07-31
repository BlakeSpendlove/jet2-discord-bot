import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random
import string
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Load environment variables (Railway)
TOKEN = os.environ.get("BOT_TOKEN")
WHITELIST_ROLE_ID = int(os.environ.get("WHITELIST_ROLE_ID"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
BANNER_URL = os.environ.get("BANNER_URL")
APPLICATION_RESULTS_CHANNEL_ID = int(os.environ.get("APPLICATION_RESULTS_CHANNEL_ID"))
FLIGHT_LOG_CHANNEL_ID = int(os.environ.get("FLIGHT_LOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.environ.get("INFRACTION_CHANNEL_ID"))
PROMOTION_CHANNEL_ID = int(os.environ.get("PROMOTION_CHANNEL_ID"))
EXPLOITER_LOG_CHANNEL_ID = int(os.environ.get("EXPLOITER_LOG_CHANNEL_ID"))

# Utility functions
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_footer():
    return {
        "text": f"ID: {generate_id()} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    }

# Register application commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connected as {bot.user}")

# 1. /embed
@tree.command(name="embed", description="Send a custom embed from Discohook JSON")
@app_commands.describe(json="Raw JSON (Discohook-style) embed")
async def embed(interaction: discord.Interaction, json: str):
    if ROLE_EMBED not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)
    try:
        data = json_loads(json)
        embed = discord.Embed.from_dict(data["embeds"][0])
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Invalid JSON: {e}", ephemeral=True)


# 2. /app_results
@tree.command(name="app_results", description="Send application result")
@app_commands.describe(user="User to DM", result="Pass or Fail", reason="Reason for the result")
async def app_results(interaction: discord.Interaction, user: discord.Member, result: str, reason: str):
    if ROLE_APPLICATION_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)
    
    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    color = discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    embed = discord.Embed(
        title=f"📨 Application Result: {result.upper()}",
        description=f"**Reason:** {reason}",
        color=color
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")
    
    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"Result sent to {user.mention}", ephemeral=True)
    except:
        await interaction.response.send_message("Failed to DM user.", ephemeral=True)



# 3. /exploiter_log
@tree.command(name="exploiter_log", description="Log an exploiter with evidence")
@app_commands.describe(user="User who exploited", reason="Reason for logging", evidence="Screenshot/video proof")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str, evidence: discord.Attachment):
    if ROLE_MODERATOR not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title="🚨 Exploiter Logged",
        description=f"**User:** `{user}`\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_image(url=evidence.url)
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")

    channel = bot.get_channel(EXPLOITER_LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Exploiter log submitted.", ephemeral=True)

@tree.command(name="flight_briefing", description="Send a flight briefing with buttons")
@app_commands.describe(flight_code="Flight code", game_link="Roblox game link", vc_link="VC link")
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    if ROLE_FLIGHT_BRIEFER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title=f"📋 Flight Briefing — {flight_code}",
        description="Please read the full briefing before joining.",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Join Game", url=game_link))
    view.add_item(discord.ui.Button(label="Join VC", url=vc_link))

    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Briefing posted.", ephemeral=True)

@tree.command(name="flight_log", description="Log a flight with attachment")
@app_commands.describe(user="User to log", flight_code="Flight code", log="Flight log file")
async def flight_log(interaction: discord.Interaction, user: discord.Member, flight_code: str, log: discord.Attachment):
    if ROLE_FLIGHT_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title="✅ Flight Logged",
        description=f"**User:** {user.mention}\n**Flight Code:** `{flight_code}`",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")
    embed.add_field(name="Log File", value=log.url, inline=False)

    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message(f"{user.mention}'s flight log has been recorded.", ephemeral=True)

@tree.command(name="flightlog_delete", description="Delete a flight log by ID")
@app_commands.describe(log_id="6-character ID of the flight log")
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    if ROLE_FLIGHT_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    # No actual delete logic implemented
    await interaction.response.send_message(f"Flight log `{log_id}` deletion simulated.", ephemeral=True)

@tree.command(name="flightlogs_view", description="View flight logs for a user")
@app_commands.describe(user="The user to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.Member):
    if ROLE_FLIGHT_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title=f"Flight Logs for {user.name}",
        description="No flight logs found.",  # Replace with DB if needed
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"ID: {uid} | {timestamp}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="infraction", description="Log an infraction, termination or demotion")
@app_commands.describe(user="User to log", action="infraction, termination, demotion", reason="Reason for log")
async def infraction(interaction: discord.Interaction, user: discord.Member, action: str, reason: str):
    if ROLE_INFRACTION_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title=f"🚫 {action.upper()}",
        description=f"**User:** {user.mention}\n**Action:** `{action}`\n**Reason:** {reason}\n**Logged by:** {interaction.user.mention}",
        color=discord.Color.red()
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

@tree.command(name="infraction_remove", description="Remove an infraction by ID")
@app_commands.describe(log_id="6-character ID of the infraction")
async def infraction_remove(interaction: discord.Interaction, log_id: str):
    if ROLE_INFRACTION_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    # No DB logic – placeholder
    await interaction.response.send_message(f"Infraction `{log_id}` removed (placeholder).", ephemeral=True)

@tree.command(name="infraction_view", description="View infractions for a user")
@app_commands.describe(user="The user to view")
async def infraction_view(interaction: discord.Interaction, user: discord.Member):
    if ROLE_INFRACTION_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title=f"Infractions for {user.name}",
        description="No infractions found.",  # Replace with actual DB logic
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"ID: {uid} | {timestamp}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="promote", description="Log a promotion")
@app_commands.describe(user="User promoted", rank="New rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.Member, rank: str, reason: str):
    if ROLE_PROMOTION_LOGGER not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("Unauthorized", ephemeral=True)

    uid = generate_uid()
    timestamp = datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')
    embed = discord.Embed(
        title="📈 Promotion",
        description=f"**User:** {user.mention}\n**New Rank:** `{rank}`\n**Reason:** {reason}\n**Promoted By:** {interaction.user.mention}",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"ID: {uid} | {timestamp}")

    channel = bot.get_channel(LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)


# Run the bot
bot.run(TOKEN)
