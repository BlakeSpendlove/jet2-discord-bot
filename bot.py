import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime
import random
import os

# Required env variables (these must be set in Railway)
TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")

# Constants
WHITELIST_ROLE_ID = 1397864367680127048
ROLE_EMBED = 1396992153208488057
ROLE_SESSION_LOG = 1395904999279820831
INFRACTION_CHANNEL_ID = 1398731768449994793
PROMOTION_CHANNEL_ID = 1398731752197066953
FLIGHTLOG_CHANNEL_ID = 1398731789106675923
EXPLOITER_LOG_CHANNEL_ID = 1398732140975358044
APPLICATION_RESULT_CHANNEL_ID = 1399447841658896454
BRIEFING_CHANNEL_ID = 1399056411660386516
BANNER_URL = "https://media.discordapp.net/attachments/1395760490982150194/1395769069541789736/Banner1.png?ex=688c217e&is=688acffe&hm=5f2119aabe9e7d3d0350d3520a4fa543f79c2475e48523add80a5722dede0365&=&format=webp&quality=lossless&width=843&height=24"

intents = discord.Intents.default()
intents.message_content = True
tree = app_commands.CommandTree(commands.Bot(command_prefix="!", intents=intents))
bot = tree._bot

# Utility

def generate_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=int(GUILD_ID)))
    print(f"Bot connected as {bot.user}.")

# EMBED command
@tree.command(name="embed", description="Send a custom embed.", guild=discord.Object(id=int(GUILD_ID)))
@app_commands.checks.has_role(ROLE_EMBED)
@app_commands.describe(json_code="Paste the Discohook-style JSON embed code")
async def embed_command(interaction: discord.Interaction, json_code: str):
    try:
        parsed = discord.Embed.from_dict(eval(json_code))
        await interaction.channel.send(embed=parsed)
        await interaction.response.send_message("✅ Embed sent successfully.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error parsing embed: {e}", ephemeral=True)

# Error handler
@embed_command.error
async def embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ An error occurred.", ephemeral=True)

# Run bot
if TOKEN is None or GUILD_ID is None:
    print("DISCORD_TOKEN and GUILD_ID must be set as environment variables.")
else:
    bot.run(TOKEN)
