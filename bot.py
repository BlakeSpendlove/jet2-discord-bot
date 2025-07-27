import os
import discord
from discord.ext import commands
from discord import app_commands, File, ui
from datetime import datetime
import random
import string

# Initialize bot
intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

# Helper to generate unique 6-character ID
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Role and channel IDs from Railway environment
WHITELIST_ROLE_ID = int(os.getenv("WHITELIST_ROLE_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
PROMOTION_CHANNEL_ID = int(os.getenv("PROMOTION_CHANNEL_ID"))
EXPLOITER_LOG_CHANNEL_ID = int(os.getenv("EXPLOITER_LOG_CHANNEL_ID"))
FLIGHT_LOG_CHANNEL_ID = int(os.getenv("FLIGHT_LOG_CHANNEL_ID"))

@client.event
async def on_ready():
    await client.tree.sync()
    print(f'Bot connected as {client.user}')

# Command: /embed
@client.tree.command(name="embed", description="Send a custom Discohook-style embed.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(json="Paste Discohook JSON here")
async def embed(interaction: discord.Interaction, json: str):
    try:
        embed_dict = eval(json)
        embed_obj = discord.Embed.from_dict(embed_dict["embeds"][0])
        await interaction.channel.send(embed=embed_obj)
        await interaction.response.send_message("✅ Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# Command: /app_results
@client.tree.command(name="app_results", description="Send application result to a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to DM", result="pass or fail")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str):
    embed = discord.Embed(
        title="Application Result",
        description=f"Your application has been **{result.upper()}**.",
        color=discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await user.send(embed=embed)
    await interaction.response.send_message(f"✅ Result sent to {user.mention}.", ephemeral=True)

# Command: /exploiter_log
@client.tree.command(name="exploiter_log", description="Log an exploiter report.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="Offender", reason="What they did", evidence="Image/video evidence")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str, evidence: discord.Attachment):
    embed = discord.Embed(
        title="🚨 Exploiter Report",
        description=f"**Offender:** {user}\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_image(url=evidence.url)
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channel = client.get_channel(EXPLOITER_LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Exploiter logged.", ephemeral=True)

# Command: /flight_briefing
@client.tree.command(name="flight_briefing", description="Send a flight briefing with buttons.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(route="Route", time="Time", game_link="Game URL", vc_link="VC URL")
async def flight_briefing(interaction: discord.Interaction, route: str, time: str, game_link: str, vc_link: str):
    embed = discord.Embed(
        title="🛫 Flight Briefing",
        description=f"**Route:** {route}\n**Time:** {time}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    view = ui.View()
    view.add_item(ui.Button(label="Join Game", url=game_link))
    view.add_item(ui.Button(label="Join VC", url=vc_link))
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Briefing sent.", ephemeral=True)

# Command: /flight_log
@client.tree.command(name="flight_log", description="Log a flight with file evidence.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="Who hosted it", file="Attach evidence file")
async def flight_log(interaction: discord.Interaction, user: discord.User, file: discord.Attachment):
    embed = discord.Embed(
        title="🧾 Flight Log",
        description=f"Flight hosted by {user.mention}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channel = client.get_channel(FLIGHT_LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await channel.send(file=await file.to_file())
    await interaction.response.send_message("✅ Flight log recorded.", ephemeral=True)

# Command: /flightlog_delete
@client.tree.command(name="flightlog_delete", description="Delete a flight log by ID.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(message_id="Message ID to delete")
async def flightlog_delete(interaction: discord.Interaction, message_id: str):
    channel = client.get_channel(FLIGHT_LOG_CHANNEL_ID)
    try:
        msg = await channel.fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("✅ Flight log deleted.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Message not found.", ephemeral=True)

# Command: /flightlogs_view
@client.tree.command(name="flightlogs_view", description="View flight logs for a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to check")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed(
        title="📄 Flight Logs",
        description=f"Showing logs for {user.mention}\n*(placeholder view)*",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Command: /infraction
@client.tree.command(name="infraction", description="Log an infraction/termination/demotion.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User", action="Infraction type", reason="Why")
async def infraction(interaction: discord.Interaction, user: discord.User, action: str, reason: str):
    embed = discord.Embed(
        title="⚠️ Staff Action Logged",
        description=f"**User:** {user.mention}\n**Action:** {action}\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channel = client.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Infraction logged.", ephemeral=True)

# Command: /infraction_remove
@client.tree.command(name="infraction_remove", description="Remove an infraction by message ID.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(message_id="Message ID to delete")
async def infraction_remove(interaction: discord.Interaction, message_id: str):
    channel = client.get_channel(INFRACTION_CHANNEL_ID)
    try:
        msg = await channel.fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("✅ Infraction deleted.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Message not found.", ephemeral=True)

# Command: /infraction_view
@client.tree.command(name="infraction_view", description="View user infractions (placeholder).")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    embed = discord.Embed(
        title="🧾 Infractions",
        description=f"Infractions for {user.mention}\n*(placeholder)*",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Command: /promote
@client.tree.command(name="promote", description="Log a promotion.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="Promoted user", reason="Why they're being promoted")
async def promote(interaction: discord.Interaction, user: discord.User, reason: str):
    embed = discord.Embed(
        title="📈 Promotion",
        description=f"{user.mention} has been promoted!\n**Reason:** {reason}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"ID: {generate_id()} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    channel = client.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Promotion logged.", ephemeral=True)

# Run the bot
client.run(os.getenv("DISCORD_TOKEN"))
