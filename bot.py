import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WHITELISTED_ROLE_ID = int(os.getenv("WHITELISTED_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTION_CHANNEL_ID = int(os.getenv("PROMOTION_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = client.tree

def generate_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

# Helper: Check role
async def is_whitelisted(interaction: discord.Interaction):
    role = discord.utils.get(interaction.user.roles, id=WHITELISTED_ROLE_ID)
    return role is not None

@tree.command(name="embed", description="Send a custom embed using Discohook JSON format.")
@app_commands.describe(json="The JSON of the embed")
async def embed(interaction: discord.Interaction, json: str):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    try:
        data = eval(json)
        embed = discord.Embed.from_dict(data)
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send embed: {e}", ephemeral=True)

@tree.command(name="app_results", description="DM a user their application result.")
@app_commands.describe(user="User to notify", result="pass or fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission.", ephemeral=True)
        return
    result = result.lower()
    if result not in ["pass", "fail"]:
        await interaction.response.send_message("Result must be 'pass' or 'fail'.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Application Result",
        description=f"You have **{result.upper()}ED** your application!",
        color=discord.Color.green() if result == "pass" else discord.Color.red()
    )
    await user.send(embed=embed)
    await interaction.response.send_message(f"Sent result to {user.name}.", ephemeral=True)

@tree.command(name="exploiter_log", description="Log an exploiter with evidence.")
@app_commands.describe(user="User being reported", reason="Reason", evidence="Attach proof")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, reason: str, evidence: discord.Attachment):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Exploiter Log",
        description=f"**User:** {user.mention}\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_image(url=evidence.url)
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await client.get_channel(LOG_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

@tree.command(name="flight_briefing", description="Send a flight briefing with buttons.")
@app_commands.describe(game_link="Game URL", vc_link="VC URL")
async def flight_briefing(interaction: discord.Interaction, game_link: str, vc_link: str):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Flight Briefing",
        description="Click the buttons below to join the game and VC.",
        color=discord.Color.blue()
    )
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Join Game", url=game_link))
    view.add_item(discord.ui.Button(label="Join VC", url=vc_link))
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Flight briefing sent.", ephemeral=True)

@tree.command(name="flight_log", description="Log a completed flight.")
@app_commands.describe(user="User to tag", file="Attach log file")
async def flight_log(interaction: discord.Interaction, user: discord.User, file: discord.Attachment):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Flight Log Submitted",
        description=f"Flight log submitted by {user.mention}.",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await interaction.channel.send(embed=embed)
    await interaction.channel.send(file=await file.to_file())
    await interaction.response.send_message("Flight log recorded.", ephemeral=True)

@tree.command(name="flightlog_delete", description="Delete a flight log by ID.")
@app_commands.describe(log_id="6-character ID")
async def flightlog_delete(interaction: discord.Interaction, log_id: str):
    await interaction.response.send_message(f"Delete command received for log ID: {log_id}. (Functionality not implemented)", ephemeral=True)

@tree.command(name="flightlogs_view", description="View a user's flight logs.")
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"Viewing flight logs for {user.name}. (Functionality not implemented)", ephemeral=True)

@tree.command(name="infraction", description="Log an infraction, termination, or demotion.")
@app_commands.describe(user="User being logged", reason="Reason", action="infraction/termination/demotion")
async def infraction(interaction: discord.Interaction, user: discord.User, reason: str, action: str):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title=f"{action.capitalize()} Logged",
        description=f"**User:** {user.mention}\n**Action:** {action}\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await client.get_channel(INFRACTION_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Infraction recorded.", ephemeral=True)

@tree.command(name="infraction_remove", description="Remove an infraction by ID.")
@app_commands.describe(infraction_id="6-character ID")
async def infraction_remove(interaction: discord.Interaction, infraction_id: str):
    await interaction.response.send_message(f"Removing infraction {infraction_id}. (Functionality not implemented)", ephemeral=True)

@tree.command(name="infraction_view", description="View infractions for a user.")
@app_commands.describe(user="User to check")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    await interaction.response.send_message(f"Viewing infractions for {user.name}. (Functionality not implemented)", ephemeral=True)

@tree.command(name="promote", description="Log a promotion.")
@app_commands.describe(user="User promoted", reason="Promotion reason")
async def promote(interaction: discord.Interaction, user: discord.User, reason: str):
    if not await is_whitelisted(interaction):
        await interaction.response.send_message("Not authorized.", ephemeral=True)
        return
    embed = discord.Embed(
        title="Promotion Logged",
        description=f"**User:** {user.mention}\n**Reason:** {reason}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"ID: {generate_id()} | {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    await client.get_channel(PROMOTION_CHANNEL_ID).send(embed=embed)
    await interaction.response.send_message("Promotion logged.", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot connected as {client.user}")

client.run(TOKEN)
