import discord
from discord.ext import commands
from discord import app_commands
import os
import datetime
import random
import string

# Environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

# Hardcoded constants
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
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot connected as {bot.user}")

# Command 1: /embed
@tree.command(name="embed", description="Send a custom embed.", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(ROLE_EMBED)
@app_commands.describe(json_code="Paste your Discohook JSON here")
async def embed(interaction: discord.Interaction, json_code: str):
    try:
        data = eval(json_code)  # Only for trusted use
        embed = discord.Embed.from_dict(data["embeds"][0])
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Embed sent.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

# Additional commands (2-11) will be filled in below...
