import os
import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import random

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)

guild_id = int(os.getenv("GUILD_ID"))
support_forum_id = int(os.getenv("SUPPORT_FORUM_CHANNEL_ID"))
affiliates_channel_id = int(os.getenv("AFFILIATES_CHANNEL_ID"))
application_results_role_id = int(os.getenv("APPLICATION_RESULTS_ROLE_ID"))
flight_briefing_channel_id = int(os.getenv("FLIGHT_BRIEFING_CHANNEL_ID"))
flight_log_channel_id = int(os.getenv("FLIGHT_LOG_CHANNEL_ID"))
infractions_channel_id = int(os.getenv("INFRACTIONS_CHANNEL_ID"))
promotions_channel_id = int(os.getenv("PROMOTIONS_CHANNEL_ID"))
exploit_log_channel_id = int(os.getenv("EXPLOIT_LOG_CHANNEL_ID"))
logs_storage_file = "flightlogs.json"
whitelisted_role_id = int(os.getenv("WHITELISTED_ROLE_ID"))
embed_banner_url = os.getenv("EMBED_BANNER_URL")
schedule_role_id = int(os.getenv("SCHEDULE_ROLE_ID"))
airline_name = os.getenv("AIRLINE_NAME")
TOKEN = os.getenv("TOKEN")

tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    print(f"✅ Logged in as {client.user}")
    print(f"✅ Synced to guild {guild_id}")

# COMMAND 1: /embed
@tree.command(name="embed", description="Send a custom embed using Discohook JSON", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def embed(interaction: discord.Interaction, json_code: str):
    try:
        embed_data = eval(json_code)
        e = discord.Embed.from_dict(embed_data)
        await interaction.response.send_message(embed=e)
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

# COMMAND 2: /app_results
@tree.command(name="app_results", description="DM a user their application result", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    embed = discord.Embed(title="Application Result", description=f"You have **{result.upper()}** your application!\nReason: {reason}", color=discord.Color.green() if result.lower() == "pass" else discord.Color.red())
    embed.set_footer(text=f"Jet2 Application System", icon_url=embed_banner_url)
    await user.send(embed=embed)
    await interaction.response.send_message(f"Sent result to {user.mention}", ephemeral=True)

# COMMAND 3: /exploiter_log
@tree.command(name="exploiter_log", description="Log an exploiter with evidence", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def exploiter_log(interaction: discord.Interaction, username: str, reason: str, evidence: discord.Attachment):
    embed = discord.Embed(title="🚨 Exploiter Logged", color=discord.Color.red())
    embed.add_field(name="Username", value=username, inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=evidence.url)
    embed.set_footer(text=f"Logged by {interaction.user} | ID: {random.randint(100000,999999)}")
    await interaction.guild.get_channel(exploit_log_channel_id).send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

# COMMAND 4: /flight_briefing
@tree.command(name="flight_briefing", description="Post a flight briefing.", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    embed = discord.Embed(title="🛫 Flight Briefing", description=f"Flight Code: **{flight_code}**", color=discord.Color.blue())
    embed.add_field(name="Game Link", value=f"[Click here]({game_link})", inline=True)
    embed.add_field(name="VC Link", value=f"[Join VC]({vc_link})", inline=True)
    embed.set_footer(text=f"Briefed by {interaction.user} | ID: {random.randint(100000,999999)}")
    embed.set_thumbnail(url=embed_banner_url)
    await interaction.guild.get_channel(flight_briefing_channel_id).send(embed=embed)
    await interaction.response.send_message("Flight briefing sent.", ephemeral=True)

# COMMAND 5: /flight_log
@tree.command(name="flight_log", description="Log a flight with a file.", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def flight_log(interaction: discord.Interaction, flight_code: str, file: discord.Attachment):
    embed = discord.Embed(title="📘 Flight Logged", description=f"Flight: **{flight_code}**", color=discord.Color.green())
    embed.set_footer(text=f"Logged by {interaction.user} | ID: {random.randint(100000,999999)}")
    await interaction.guild.get_channel(flight_log_channel_id).send(embed=embed)
    await interaction.guild.get_channel(flight_log_channel_id).send(file=await file.to_file())
    await interaction.response.send_message("Flight log submitted.", ephemeral=True)

# COMMAND 6: /flightlog_delete
@tree.command(name="flightlog_delete", description="Delete a flight log by ID.", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    # In production, you’d match log_id to a message ID or stored log file.
    await interaction.response.send_message(f"Flight log ID `{log_id}` marked for deletion. (manual cleanup required)", ephemeral=True)

# COMMAND 7: /flightlogs_view
@tree.command(name="flightlogs_view", description="View flight logs for a user.", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    # Replace with actual log retrieval logic
    embed = discord.Embed(title="📘 Flight Logs", description=f"Showing logs for {user.mention}", color=discord.Color.blue())
    embed.add_field(name="Sample Log", value="Flight: LS8800 - B737-800\nDate: 26/07/2025\nHost: John#0001", inline=False)
    embed.set_footer(text=f"ID: {random.randint(100000,999999)}")
    await interaction.response.send_message(embed=embed)

# COMMAND 8: /infraction
@tree.command(name="infraction", description="Log an infraction, demotion or termination", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def infraction(interaction: discord.Interaction, user: discord.User, type: str, reason: str):
    embed = discord.Embed(title="⚠️ Infraction Logged", color=discord.Color.orange())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Type", value=type)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=f"Logged by {interaction.user} | ID: {random.randint(100000,999999)}")
    await interaction.guild.get_channel(infractions_channel_id).send(embed=embed)
    await interaction.response.send_message("Infraction logged.", ephemeral=True)

# COMMAND 9: /infraction_remove
@tree.command(name="infraction_remove", description="Remove an infraction by ID", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def infraction_remove(interaction: discord.Interaction, log_id: str):
    await interaction.response.send_message(f"Infraction `{log_id}` marked for removal. (manual process)", ephemeral=True)

# COMMAND 10: /infraction_view
@tree.command(name="infraction_view", description="View all infractions for a user", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed(title="🔍 Infractions", description=f"Infractions for {user.mention}", color=discord.Color.orange())
    embed.add_field(name="Sample", value="Type: Warning\nReason: Failure to follow briefing\nDate: 26/07/2025", inline=False)
    embed.set_footer(text=f"ID: {random.randint(100000,999999)}")
    await interaction.response.send_message(embed=embed)

# COMMAND 11: /promote
@tree.command(name="promote", description="Log a promotion", guild=discord.Object(id=guild_id))
@app_commands.checks.has_role(whitelisted_role_id)
async def promote(interaction: discord.Interaction, user: discord.User, promoted_to: str, reason: str):
    embed = discord.Embed(title="📈 Promotion Logged", color=discord.Color.blue())
    embed.add_field(name="User", value=user.mention)
    embed.add_field(name="Promoted To", value=promoted_to)
    embed.add_field(name="Reason", value=reason)
    embed.set_footer(text=f"Promoted by {interaction.user} | ID: {random.randint(100000,999999)}")
    await interaction.guild.get_channel(promotions_channel_id).send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

client.run(TOKEN)
