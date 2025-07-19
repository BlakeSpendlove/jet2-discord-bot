import os
import random
import string
from datetime import datetime
import pytz

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

# Constants
EMBED_COLOR = 0x7a1a1a
BST = pytz.timezone('Europe/London')

# Get environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
WHITELIST_ROLE_IDS = os.getenv("WHITELIST_ROLE_IDS", "")  # Comma separated role IDs

# Convert role ids to int set for quick lookup
WHITELIST_ROLES = {int(role_id.strip()) for role_id in WHITELIST_ROLE_IDS.split(",") if role_id.strip().isdigit()}

# Helper functions
def gen_random_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_bst_timestamp():
    return datetime.now(BST).strftime("%d/%m/%Y %H:%M BST")

def is_user_whitelisted(interaction: discord.Interaction):
    if not WHITELIST_ROLES:
        # No whitelist set = allow all (optional: change this if you want stricter)
        return True
    user_roles = {role.id for role in interaction.user.roles}
    return bool(user_roles.intersection(WHITELIST_ROLES))

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Sync commands on ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Slash commands

@bot.tree.command(name="announce", description="Announce an embed message with optional ping in a specified channel.")
@app_commands.describe(message="Message to announce", ping="Ping type (@everyone, @here, or mention)", channel_id="Channel ID to send message")
async def announce(interaction: discord.Interaction, message: str, ping: str, channel_id: str):
    if not is_user_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    # Validate ping
    valid_pings = ["@everyone", "@here"]
    channel = interaction.guild.get_channel(int(channel_id)) if interaction.guild else None
    if not channel:
        await interaction.response.send_message("Invalid channel ID.", ephemeral=True)
        return

    # Prepare ping text
    ping_text = ""
    if ping.lower() in valid_pings:
        ping_text = ping.lower()
    else:
        # Try to resolve mention
        if ping.startswith("<@") and ping.endswith(">"):
            ping_text = ping
        else:
            await interaction.response.send_message("Ping must be @everyone, @here, or a valid mention.", ephemeral=True)
            return

    # Create embed
    embed = discord.Embed(description=message, color=EMBED_COLOR)
    embed.set_footer(text=f"ID: {gen_random_id()} | {get_bst_timestamp()}")

    await channel.send(content=ping_text, embed=embed)
    await interaction.response.send_message(f"Announcement sent to {channel.mention}.", ephemeral=True)

@bot.tree.command(name="dm_user", description="DM a user an embed message.")
@app_commands.describe(user="User to DM", message="Message to send")
async def dm_user(interaction: discord.Interaction, user: discord.User, message: str):
    if not is_user_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    embed = discord.Embed(description=message, color=EMBED_COLOR)
    embed.set_footer(text=f"ID: {gen_random_id()} | {get_bst_timestamp()}")

    try:
        # Dot outside embed to force message delivery
        await user.send(".", embed=embed)
        await interaction.response.send_message(f"Message sent to {user}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send DM: {e}", ephemeral=True)

@bot.tree.command(name="flight_notice", description="Send flight notice with buttons.")
@app_commands.describe(host="Host user", flight_code="Flight code", airport_link="Airport/game link", vc_link="Voice channel link")
async def flight_notice(interaction: discord.Interaction, host: discord.User, flight_code: str, airport_link: str, vc_link: str):
    if not is_user_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    embed_desc = (
        f"@everyone\n\n"
        f"@{host.name} ({host.mention})\n"
        f"**{flight_code} | Flight Join**\n"
        f"Please all begin joining for flight briefing.\n\n"
        f"**Host:** {host.mention}\n"
        f"**Aircraft:** B737-800\n"
        f"Ensure you join in a suitable avatar and be ready to get your uniform on."
    )
    embed = discord.Embed(description=embed_desc, color=EMBED_COLOR)
    embed.set_footer(text=f"ID: {gen_random_id()} | {get_bst_timestamp()}")

    # Buttons
    button_game = Button(label="Join the Game", url=airport_link)
    button_vc = Button(label="Join the VC", url=vc_link)

    view = View()
    view.add_item(button_game)
    view.add_item(button_vc)

    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="exam_results", description="DM a user their exam results.")
@app_commands.describe(user="User to DM", score="Exam score", passed="Did they pass? (passed/failed)")
async def exam_results(interaction: discord.Interaction, user: discord.User, score: float, passed: str):
    if not is_user_whitelisted(interaction):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    passed = passed.lower()
    if passed not in ["passed", "failed"]:
        await interaction.response.send_message("Passed must be either 'passed' or 'failed'.", ephemeral=True)
        return

    desc = (
        f"Hello {user.mention},\n\n"
        f"We are here to inform that you have **{passed}** your exam with a score of **{score}**.\n\n"
    )
    if passed == "passed":
        desc += (
            "You will receive all necessary key information if passed in around 10 minutes, maybe less.\n"
            "Ensure that you follow these instructions clearly and complete your designated training as fast as possible."
        )
    else:
        desc += "Please review your results and contact staff for further guidance."

    embed = discord.Embed(description=desc, color=EMBED_COLOR)
    embed.set_footer(text=f"ID: {gen_random_id()} | {get_bst_timestamp()}")

    try:
        await user.send(embed=embed)
        await interaction.response.send_message(f"Exam results sent to {user}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to send DM: {e}", ephemeral=True)

# Run the bot
bot.run(TOKEN)
