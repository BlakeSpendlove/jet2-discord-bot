import os
import discord
from discord import app_commands, ui, File
from discord.ext import commands
import random
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents)

# Load Railway environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WHITELIST_ROLE_ID = int(os.getenv("WHITELIST_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
BANNER_URL = os.getenv("BANNER_URL")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    try:
        synced = await client.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'Synced {len(synced)} command(s).')
    except Exception as e:
        print(e)

# Util for generating unique 6-character alphanumeric IDs
def generate_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

def embed_footer():
    return f"ID: {generate_id()} | {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}"

# 1. /promote
@client.tree.command(name="promote", description="Log a promotion", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to promote", reason="Reason for promotion", promotion_to="New rank")
async def promote(interaction: discord.Interaction, user: discord.Member, reason: str, promotion_to: str):
    embed = discord.Embed(title="Promotion Logged", color=0x3498db)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Promoted To", value=promotion_to, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=embed_footer())
    channel = client.get_channel(LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Promotion for {user.mention} logged.", ephemeral=True)

# 2. /flight_briefing
@client.tree.command(name="flight_briefing", description="Send a flight briefing", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(gamelink="Game join link", vclink="VC link", flight_code="Flight Code")
async def flight_briefing(interaction: discord.Interaction, gamelink: str, vclink: str, flight_code: str):
    embed = discord.Embed(title="Flight Briefing", color=0xe74c3c)
    embed.add_field(name="Flight Code", value=flight_code, inline=False)
    embed.add_field(name="Game", value=f"[Join Here]({gamelink})", inline=True)
    embed.add_field(name="Voice Chat", value=f"[Join Here]({vclink})", inline=True)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=embed_footer())
    await interaction.response.send_message(embed=embed)

# 3. /app_results
@client.tree.command(name="app_results", description="Send application result", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to notify", result="pass or fail", reason="Reason for result")
async def app_results(interaction: discord.Interaction, user: discord.Member, result: str, reason: str):
    result = result.lower()
    embed = discord.Embed(color=(0x2ecc71 if result == "pass" else 0xe74c3c))
    embed.title = "Application Result"
    embed.add_field(name="Result", value=result.upper(), inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=embed_footer())
    await user.send(embed=embed)
    await interaction.response.send_message(f"✅ Result sent to {user.mention}.", ephemeral=True)

# 4. /flight_log
@client.tree.command(name="flight_log", description="Log a completed flight", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="Who hosted", flight_code="Flight Code", proof="Flight proof")
async def flight_log(interaction: discord.Interaction, user: discord.Member, flight_code: str, proof: discord.Attachment):
    embed = discord.Embed(title="Flight Logged", color=0xf1c40f)
    embed.add_field(name="Host", value=user.mention, inline=True)
    embed.add_field(name="Flight Code", value=flight_code, inline=True)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=embed_footer())
    file = await proof.to_file()
    await interaction.channel.send(embed=embed, file=file)
    await interaction.response.send_message(f"✈️ Flight log submitted for {user.mention}.", ephemeral=True)

# 5. /infract
@client.tree.command(name="infract", description="Log an infraction", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User being infracted", type="Infraction type", reason="Reason for action")
async def infract(interaction: discord.Interaction, user: discord.Member, type: str, reason: str):
    embed = discord.Embed(title="Infraction Logged", color=0xe67e22)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="User", value=user.mention, inline=True)
    embed.add_field(name="Type", value=type, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=embed_footer())
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message(f"⚠️ Infraction logged for {user.mention}.", ephemeral=True)

# Other 6 commands preserved from original working version
# (Use your original logic, unchanged, for: /embed, /exploiter_log, /flightlog_delete, /flightlogs_view, /infraction_remove, /infraction_view)

client.run(TOKEN)
