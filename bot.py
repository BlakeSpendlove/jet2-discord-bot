import os
import discord
from discord.ext import commands
from discord import app_commands, Embed, File
from datetime import datetime, timedelta
import random
import string

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Railway environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
WHITELIST_ROLE_ID = int(os.getenv("WHITELIST_ROLE_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))
BANNER_URL = os.getenv("BANNER_URL")
APPLICATION_LOG_CHANNEL_ID = int(os.getenv("APPLICATION_LOG_CHANNEL_ID"))
EXPLOITER_LOG_CHANNEL_ID = int(os.getenv("EXPLOITER_LOG_CHANNEL_ID"))
PROMOTION_CHANNEL_ID = int(os.getenv("PROMOTION_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
FLIGHT_LOG_CHANNEL_ID = int(os.getenv("FLIGHT_LOG_CHANNEL_ID"))
BRIEFING_CHANNEL_ID = int(os.getenv("BRIEFING_CHANNEL_ID"))
EVENT_CHANNEL_ID = int(os.getenv("EVENT_CHANNEL_ID"))
SCHEDULE_ROLE_ID = int(os.getenv("SCHEDULE_ROLE_ID"))
EVENT_BANNER_URL = os.getenv("EVENT_BANNER_URL")

# Utility for unique ID

def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- EMBED COMMAND ---

@tree.command(name="embed", description="Send a custom embed via Discohook JSON format.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(json="Paste the Discohook JSON here")
async def embed(interaction: discord.Interaction, json: str):
    try:
        import json as j
        data = j.loads(json)
        embed_data = data["embeds"][0]
        embed = Embed(title=embed_data.get("title"),
                      description=embed_data.get("description"),
                      color=int(embed_data.get("color", 0xFF0000)))
        if "footer" in embed_data:
            embed.set_footer(text=embed_data["footer"].get("text", ""))
        if "image" in embed_data:
            embed.set_image(url=embed_data["image"].get("url", ""))
        if "thumbnail" in embed_data:
            embed.set_thumbnail(url=embed_data["thumbnail"].get("url", ""))
        if "author" in embed_data:
            embed.set_author(name=embed_data["author"].get("name", ""))
        if "fields" in embed_data:
            for field in embed_data["fields"]:
                embed.add_field(name=field["name"], value=field["value"], inline=field.get("inline", False))

        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Invalid JSON: {e}", ephemeral=True)

# --- VIEW COMMANDS ---

@tree.command(name="flightlogs_view", description="View a user's flight logs.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.Member):
    channel = bot.get_channel(FLIGHT_LOG_CHANNEL_ID)
    if not channel:
        return await interaction.response.send_message("Log channel not found.", ephemeral=True)

    async for msg in channel.history(limit=200):
        if msg.embeds and user.mention in msg.embeds[0].description:
            await interaction.followup.send(embed=msg.embeds[0])
            return

    await interaction.response.send_message("No logs found for that user.", ephemeral=True)

@tree.command(name="infraction_view", description="View all infractions for a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view infractions for")
async def infraction_view(interaction: discord.Interaction, user: discord.Member):
    channel = bot.get_channel(INFRACTION_CHANNEL_ID)
    if not channel:
        return await interaction.response.send_message("Infraction channel not found.", ephemeral=True)

    embeds = []
    async for msg in channel.history(limit=200):
        if msg.embeds and user.mention in msg.embeds[0].description:
            embeds.append(msg.embeds[0])

    if not embeds:
        await interaction.response.send_message("No infractions found for this user.", ephemeral=True)
    else:
        for embed in embeds:
            await interaction.followup.send(embed=embed)

@tree.command(name="app_results_view", description="View a user's application result if it exists.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view results for")
async def app_results_view(interaction: discord.Interaction, user: discord.Member):
    channel = bot.get_channel(APPLICATION_LOG_CHANNEL_ID)
    if not channel:
        return await interaction.response.send_message("Application channel not found.", ephemeral=True)

    async for msg in channel.history(limit=100):
        if msg.embeds and user.mention in msg.embeds[0].description:
            await interaction.followup.send(embed=msg.embeds[0])
            return

    await interaction.response.send_message("No application result found.", ephemeral=True)

# --- BOT STARTUP ---

@bot.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)
