import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import datetime

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = [int(gid) for gid in os.getenv("GUILD_IDS", "").split(",") if gid]

WHITELIST_PROMOTE_ROLES = [int(rid) for rid in os.getenv("WHITELIST_PROMOTE_ROLES", "").split(",") if rid]
WHITELIST_INFRACTION_ROLES = [int(rid) for rid in os.getenv("WHITELIST_INFRACTION_ROLES", "").split(",") if rid]
WHITELIST_INFRACTION_REMOVE_ROLES = [int(rid) for rid in os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES", "").split(",") if rid]
WHITELIST_INFRACTION_VIEW_ROLES = [int(rid) for rid in os.getenv("WHITELIST_INFRACTION_VIEW_ROLES", "").split(",") if rid]
WHITELIST_EMBED_ROLES = [int(rid) for rid in os.getenv("WHITELIST_EMBED_ROLES", "").split(",") if rid]
WHITELIST_APP_RESULTS_ROLES = [int(rid) for rid in os.getenv("WHITELIST_APP_RESULTS_ROLES", "").split(",") if rid]
WHITELIST_EXPLOITER_LOG_ROLES = [int(rid) for rid in os.getenv("WHITELIST_EXPLOITER_LOG_ROLES", "").split(",") if rid]
WHITELIST_FLIGHTBRIEFING_ROLES = [int(rid) for rid in os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES", "").split(",") if rid]
WHITELIST_FLIGHTLOG_ROLES = [int(rid) for rid in os.getenv("WHITELIST_FLIGHTLOG_ROLES", "").split(",") if rid]
WHITELIST_FLIGHTLOG_DELETE_ROLES = [int(rid) for rid in os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES", "").split(",") if rid]

PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", 0))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID", 0))
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID", 0))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

def generate_footer():
    footer_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    timestamp = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
    return f"ID: {footer_id} • {timestamp}"

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_IDS[0]))
        print(f"Synced {len(synced)} command(s) to {GUILD_IDS[0]}")
    except Exception as e:
        print(e)

# Promote command
@bot.tree.command(name="promote", description="Log a user promotion")
@app_commands.describe(user="User promoted", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not any(role.id in WHITELIST_PROMOTE_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    embed = discord.Embed(title="Promotion Logged", color=discord.Color.green())
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Promoted by", value=interaction.user.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_footer(text=generate_footer())
    await channel.send(embed=embed)
    await interaction.response.send_message(f"Promotion logged for {user.mention}", ephemeral=True)

# Infraction command
@bot.tree.command(name="infraction", description="Log an infraction")
@app_commands.describe(user="User infracted", type="Type of action", reason="Reason")
async def infraction(interaction: discord.Interaction, user: discord.Member, type: str, reason: str):
    if not any(role.id in WHITELIST_INFRACTION_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    embed = discord.Embed(title="Infraction Logged", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Type", value=type)
    embed.add_field(name="Reason", value=reason)
    embed.add_field(name="Logged by", value=interaction.user.mention)
    embed.set_footer(text=generate_footer())
    await channel.send(embed=embed)
    await interaction.response.send_message(f"Infraction logged for {user.mention}", ephemeral=True)

# Embed command
@bot.tree.command(name="embed", description="Send a custom embed")
@app_commands.describe(json_code="Embed JSON")
async def embed(interaction: discord.Interaction, json_code: str):
    if not any(role.id in WHITELIST_EMBED_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message("Unauthorized", ephemeral=True)
    try:
        data = discord.Embed.from_dict(eval(json_code))
        await interaction.channel.send(embed=data)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# App results command
@bot.tree.command(name="app_results", description="Send app result")
@app_commands.describe(user="User to DM", result="Pass or fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    if not any(role.id in WHITELIST_APP_RESULTS_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message("Unauthorized", ephemeral=True)
    embed = discord.Embed(title="Application Result", description=f"You have {'passed' if result.lower() == 'pass' else 'failed'} your application.", color=discord.Color.green() if result.lower() == 'pass' else discord.Color.red())
    embed.set_footer(text=generate_footer())
    await user.send(embed=embed)
    await interaction.response.send_message(f"Result sent to {user.mention}.", ephemeral=True)

# Exploiter log command
@bot.tree.command(name="exploiter_log", description="Log an exploiter")
@app_commands.describe(user="Exploiter", evidence="Upload image/video evidence")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, evidence: discord.Attachment):
    if not any(role.id in WHITELIST_EXPLOITER_LOG_ROLES for role in interaction.user.roles):
        return await interaction.response.send_message("Unauthorized", ephemeral=True)
    embed = discord.Embed(title="Exploiter Logged", color=discord.Color.red())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Logged by", value=interaction.user.mention)
    embed.set_image(url=evidence.url)
    embed.set_footer(text=generate_footer())
    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

# Additional commands to be added: flight_briefing, flight_log, flightlog_delete, flightlogs_view, infraction_remove, infraction_view
# Let me know if you'd like those added now or with specific formats.

bot.run(TOKEN)
