import os
import discord
import random
import string
import datetime
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Load environment variables
token = os.getenv("DISCORD_TOKEN")
guild_ids = os.getenv("GUILD_IDS", "").split(",")

# Role whitelists
whitelist_embed_roles = os.getenv("WHITELIST_EMBED_ROLES", "").split(",")
whitelist_app_roles = os.getenv("WHITELIST_APP_RESULTS_ROLES", "").split(",")
whitelist_exploit_roles = os.getenv("WHITELIST_EXPLOITER_LOG_ROLES", "").split(",")
whitelist_promote_roles = os.getenv("WHITELIST_PROMOTE_ROLES", "").split(",")
whitelist_flightlog_roles = os.getenv("WHITELIST_FLIGHTLOG_ROLES", "").split(",")
whitelist_flightlog_delete_roles = os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES", "").split(",")
whitelist_flightbriefing_roles = os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES", "").split(",")
whitelist_infraction_roles = os.getenv("WHITELIST_INFRACTION_ROLES", "").split(",")
whitelist_infraction_remove_roles = os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES", "").split(",")
whitelist_infraction_view_roles = os.getenv("WHITELIST_INFRACTION_VIEW_ROLES", "").split(",")

# Channel IDs
channel_appresults = int(os.getenv("APPRESULTS_CHANNEL_ID", 0))
channel_exploitlog = int(os.getenv("EXPLOITLOG_CHANNEL_ID", 0))
channel_promote = int(os.getenv("PROMOTE_CHANNEL_ID", 0))
channel_flightlog = int(os.getenv("FLIGHTLOG_CHANNEL_ID", 0))
channel_infraction = int(os.getenv("INFRACTION_CHANNEL_ID", 0))

def generate_footer():
    uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ID: {uid} • {datetime.datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}"

def check_whitelist(interaction, whitelist):
    return any(str(role.id) in whitelist for role in interaction.user.roles)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

@tree.command(name="embed")
async def embed(interaction: discord.Interaction, title: str, description: str):
    if not check_whitelist(interaction, whitelist_embed_roles):
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
        return
    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Embed sent.", ephemeral=True)

@tree.command(name="app_results")
async def app_results(interaction: discord.Interaction, result: str, user: discord.User):
    if not check_whitelist(interaction, whitelist_app_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Application Result", description=f"**User:** {user.mention}\n**Result:** {result}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    channel = bot.get_channel(channel_appresults)
    await channel.send(embed=embed)
    await interaction.response.send_message("Application result sent.", ephemeral=True)

@tree.command(name="exploiter_log")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, reason: str):
    if not check_whitelist(interaction, whitelist_exploit_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Exploiter Logged", description=f"**User:** {user.mention}\n**Reason:** {reason}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_exploitlog).send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

@tree.command(name="promote")
async def promote(interaction: discord.Interaction, user: discord.User, new_rank: str):
    if not check_whitelist(interaction, whitelist_promote_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Promotion", description=f"**User:** {user.mention}\n**New Rank:** {new_rank}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_promote).send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

@tree.command(name="flight_log")
async def flight_log(interaction: discord.Interaction, host: discord.User, flight_code: str, route: str):
    if not check_whitelist(interaction, whitelist_flightlog_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Flight Logged", description=f"**Host:** {host.mention}\n**Code:** {flight_code}\n**Route:** {route}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_flightlog).send(embed=embed)
    await interaction.response.send_message("Flight logged.", ephemeral=True)

@tree.command(name="flightlog_delete")
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    if not check_whitelist(interaction, whitelist_flightlog_delete_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Flight Log Deleted", description=f"**Log ID:** {log_id}\nDeleted by {interaction.user.mention}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_flightlog).send(embed=embed)
    await interaction.response.send_message("Flight log deletion recorded.", ephemeral=True)

@tree.command(name="flight_briefing")
async def flight_briefing(interaction: discord.Interaction, flight_code: str, details: str):
    if not check_whitelist(interaction, whitelist_flightbriefing_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Flight Briefing", description=f"**Flight Code:** {flight_code}\n**Details:** {details}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_flightlog).send(embed=embed)
    await interaction.response.send_message("Flight briefing sent.", ephemeral=True)

@tree.command(name="infraction")
async def infraction(interaction: discord.Interaction, user: discord.User, reason: str):
    if not check_whitelist(interaction, whitelist_infraction_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Infraction Issued", description=f"**User:** {user.mention}\n**Reason:** {reason}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_infraction).send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

@tree.command(name="infraction_remove")
async def infraction_remove(interaction: discord.Interaction, user: discord.User, reason: str):
    if not check_whitelist(interaction, whitelist_infraction_remove_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Infraction Removed", description=f"**User:** {user.mention}\n**Reason:** {reason}\n**Removed by:** {interaction.user.mention}", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await bot.get_channel(channel_infraction).send(embed=embed)
    await interaction.response.send_message("Infraction removal logged.", ephemeral=True)

@tree.command(name="infraction_view")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    if not check_whitelist(interaction, whitelist_infraction_view_roles):
        await interaction.response.send_message("Unauthorized", ephemeral=True)
        return
    embed = discord.Embed(title="Infraction Lookup", description=f"Showing recent infractions for {user.mention}.\n(Feature stubbed — implement log fetch.)", color=discord.Color.red())
    embed.set_footer(text=generate_footer())
    await interaction.response.send_message(embed=embed)

bot.run(token)
