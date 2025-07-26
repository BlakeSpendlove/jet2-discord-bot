import discord
from discord import app_commands
from discord.ext import commands
import os
import random
import string
from datetime import datetime

# Load environment variables
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_IDS = os.getenv("GUILD_IDS", "").split(",")

# Intent setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Generate a unique 6-character ID
def generate_unique_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Authorization check
def is_authorized(interaction: discord.Interaction, env_key: str) -> bool:
    author_roles = [role.id for role in interaction.user.roles]
    allowed_roles = [int(r) for r in os.getenv(env_key, "").split(",") if r.isdigit()]
    return any(role in author_roles for role in allowed_roles)

# Embed command
@app_commands.command(name="embed", description="Send a custom embed with title and description")
@app_commands.describe(title="Embed title", description="Embed description")
async def embed_command(interaction: discord.Interaction, title: str, description: str):
    if not is_authorized(interaction, "EMBED_ROLE_IDS"):
        await interaction.response.send_message("❌ You are not authorized to use this command.", ephemeral=True)
        return

    embed = discord.Embed(title=title, description=description, color=discord.Color.red())
    embed.set_footer(text=f"ID: {generate_unique_id()} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S UTC')}")
    await interaction.response.send_message(embed=embed)

# Register slash commands
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        for guild_id in GUILD_IDS:
            guild = discord.Object(id=int(guild_id.strip()))
            bot.tree.add_command(embed_command, guild=guild)
            await bot.tree.sync(guild=guild)
        print("✅ Slash commands synced.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

bot.run(TOKEN)
