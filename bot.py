import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import random
import string

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = list(map(int, os.getenv("GUILD_IDS", "").split(",")))

WHITELIST_PROMOTE_ROLES = list(map(int, os.getenv("WHITELIST_PROMOTE_ROLES", "").split(",")))
WHITELIST_INFRACTION_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_ROLES", "").split(",")))
WHITELIST_INFRACTION_REMOVE_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_REMOVE_ROLES", "").split(",")))
WHITELIST_INFRACTION_VIEW_ROLES = list(map(int, os.getenv("WHITELIST_INFRACTION_VIEW_ROLES", "").split(",")))
WHITELIST_EMBED_ROLES = list(map(int, os.getenv("WHITELIST_EMBED_ROLES", "").split(",")))
WHITELIST_APP_RESULTS_ROLES = list(map(int, os.getenv("WHITELIST_APP_RESULTS_ROLES", "").split(",")))
WHITELIST_EXPLOITER_LOG_ROLES = list(map(int, os.getenv("WHITELIST_EXPLOITER_LOG_ROLES", "").split(",")))
WHITELIST_FLIGHTLOG_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_ROLES", "").split(",")))
WHITELIST_FLIGHTLOG_DELETE_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTLOG_DELETE_ROLES", "").split(",")))
WHITELIST_FLIGHTBRIEFING_ROLES = list(map(int, os.getenv("WHITELIST_FLIGHTBRIEFING_ROLES", "").split(",")))

PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID"))
FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

def generate_footer():
    uid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    return f"ID: {uid} • Logged {timestamp}"

def is_whitelisted(interaction: discord.Interaction, allowed_roles: list):
    return any(role.id in allowed_roles for role in interaction.user.roles)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_IDS[0]))
    print(f"Bot connected as {bot.user}")

@bot.tree.command(name="promote", description="Log a promotion to a specific channel")
@app_commands.describe(user="User to promote", reason="Reason for the promotion")
async def promote(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not is_whitelisted(interaction, WHITELIST_PROMOTE_ROLES):
        return await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)

    embed = discord.Embed(
        title="📈 Promotion Logged",
        description=f"**User:** {user.mention}\n**Promoted by:** {interaction.user.mention}\n**Reason:** {reason}",
        color=discord.Color.green()
    )
    embed.set_footer(text=generate_footer())

    channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Promotion logged successfully.", ephemeral=True)

# Add more commands here following the same pattern...

bot.run(TOKEN)
