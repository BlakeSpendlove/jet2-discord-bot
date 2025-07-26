```python
import discord
from discord.ext import commands
from discord import app_commands, Embed
import os
import datetime
import random

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS", "").split(",")
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))

# Role whitelists
ROLE_VARS = [
    "WHITELIST_APP_RESULTS_ROLES",
    "WHITELIST_EMBED_ROLES",
    "WHITELIST_EXPLOITER_LOG_ROLES",
    "WHITELIST_FLIGHTBRIEFING_ROLES",
    "WHITELIST_FLIGHTLOG_DELETE_ROLES",
    "WHITELIST_FLIGHTLOG_ROLES",
    "WHITELIST_INFRACTION_REMOVE_ROLES",
    "WHITELIST_INFRACTION_ROLES",
    "WHITELIST_INFRACTION_VIEW_ROLES",
    "WHITELIST_PROMOTE_ROLES"
]
ROLE_WHITELISTS = {
    var: [int(rid) for rid in os.getenv(var, "").split(",") if rid.strip().isdigit()]
    for var in ROLE_VARS
}

bot = commands.Bot(command_prefix="/", intents=intents)

def has_whitelisted_role(interaction: discord.Interaction, role_var):
    return any(role.id in ROLE_WHITELISTS.get(role_var, []) for role in interaction.user.roles)

def generate_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    for guild_id in GUILD_IDS:
        guild = discord.Object(id=int(guild_id))
        await bot.tree.sync(guild=guild)
    print("Slash commands synced.")

@bot.tree.command(name="app_results")
async def app_results(interaction: discord.Interaction, user: discord.Member, result: str):
    if not has_whitelisted_role(interaction, "WHITELIST_APP_RESULTS_ROLES"):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    embed = Embed(title="Application Result", description=f"**{user.mention}** has been **{result.upper()}**.", color=discord.Color.green())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="embed")
async def send_embed(interaction: discord.Interaction, json: str):
    if not has_whitelisted_role(interaction, "WHITELIST_EMBED_ROLES"):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    try:
        import json as js
        embed_data = js.loads(json)
        embed = Embed.from_dict(embed_data)
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Error parsing embed JSON: {e}", ephemeral=True)

@bot.tree.command(name="exploiter_log")
async def exploiter_log(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not has_whitelisted_role(interaction, "WHITELIST_EXPLOITER_LOG_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    embed = Embed(title="Exploiter Log", description=f"User: {user.mention}\nReason: {reason}", color=discord.Color.red())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Logged.", ephemeral=True)

@bot.tree.command(name="flight_briefing")
async def flight_briefing(interaction: discord.Interaction, user: discord.Member, info: str):
    if not has_whitelisted_role(interaction, "WHITELIST_FLIGHTBRIEFING_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    embed = Embed(title="Flight Briefing", description=f"Host: {user.mention}\nDetails: {info}", color=discord.Color.blurple())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Briefing sent.", ephemeral=True)

@bot.tree.command(name="flight_log")
async def flight_log(interaction: discord.Interaction, user: discord.Member, flight_code: str, route: str):
    if not has_whitelisted_role(interaction, "WHITELIST_FLIGHTLOG_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    embed = Embed(title="Flight Log", description=f"Pilot: {user.mention}\nFlight Code: {flight_code}\nRoute: {route}", color=discord.Color.blue())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Flight logged.", ephemeral=True)

@bot.tree.command(name="flightlog_delete")
async def flightlog_delete(interaction: discord.Interaction, message_id: str):
    if not has_whitelisted_role(interaction, "WHITELIST_FLIGHTLOG_DELETE_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
    try:
        msg = await channel.fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("Message deleted.", ephemeral=True)
    except:
        await interaction.response.send_message("Could not delete message.", ephemeral=True)

@bot.tree.command(name="flightlogs_view")
async def flightlogs_view(interaction: discord.Interaction):
    if not has_whitelisted_role(interaction, "WHITELIST_FLIGHTLOG_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    await interaction.response.send_message("Please check the flight log channel for history.", ephemeral=True)

@bot.tree.command(name="infraction")
async def infraction(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not has_whitelisted_role(interaction, "WHITELIST_INFRACTION_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    embed = Embed(title="Infraction Logged", description=f"User: {user.mention}\nReason: {reason}", color=discord.Color.orange())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await bot.get_channel(INFRACTION_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

@bot.tree.command(name="infraction_remove")
async def infraction_remove(interaction: discord.Interaction, message_id: str):
    if not has_whitelisted_role(interaction, "WHITELIST_INFRACTION_REMOVE_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    try:
        msg = await bot.get_channel(INFRACTION_CHANNEL_ID).fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("Infraction removed.", ephemeral=True)
    except:
        await interaction.response.send_message("Could not remove infraction.", ephemeral=True)

@bot.tree.command(name="infraction_view")
async def infraction_view(interaction: discord.Interaction):
    if not has_whitelisted_role(interaction, "WHITELIST_INFRACTION_VIEW_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    await interaction.response.send_message("Please check the infraction log channel.", ephemeral=True)

@bot.tree.command(name="promote")
async def promote(interaction: discord.Interaction, user: discord.Member, new_rank: str):
    if not has_whitelisted_role(interaction, "WHITELIST_PROMOTE_ROLES"):
        await interaction.response.send_message("No permission.", ephemeral=True)
        return
    embed = Embed(title="Promotion Log", description=f"User: {user.mention}\nPromoted to: {new_rank}", color=discord.Color.green())
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await bot.get_channel(PROMOTE_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

bot.run(TOKEN)
```
