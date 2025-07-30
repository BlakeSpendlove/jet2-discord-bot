import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random
import string
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Load environment variables (Railway)
TOKEN = os.environ.get("BOT_TOKEN")
WHITELIST_ROLE_ID = int(os.environ.get("WHITELIST_ROLE_ID"))
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID"))
BANNER_URL = os.environ.get("BANNER_URL")
APPLICATION_RESULTS_CHANNEL_ID = int(os.environ.get("APPLICATION_RESULTS_CHANNEL_ID"))
FLIGHT_LOG_CHANNEL_ID = int(os.environ.get("FLIGHT_LOG_CHANNEL_ID"))
INFRACTION_CHANNEL_ID = int(os.environ.get("INFRACTION_CHANNEL_ID"))
PROMOTION_CHANNEL_ID = int(os.environ.get("PROMOTION_CHANNEL_ID"))
EXPLOITER_LOG_CHANNEL_ID = int(os.environ.get("EXPLOITER_LOG_CHANNEL_ID"))

# Utility functions
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_footer():
    return {
        "text": f"ID: {generate_id()} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    }

# Register application commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot connected as {bot.user}")

# 1. /embed
@bot.tree.command(name="embed")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(json="Paste your Discohook-style JSON here")
async def embed(interaction: discord.Interaction, json: str):
    try:
        data = json.strip().replace("```json", "").replace("```", "")
        payload = json.loads(data)
        embed = discord.Embed.from_dict(payload["embeds"][0])
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Error parsing embed JSON: {e}", ephemeral=True)

# 2. /app_results
@bot.tree.command(name="app_results")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to DM", result="Pass or Fail", reason="Reason for the result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    embed = discord.Embed(
        title="Application Result",
        description=f"You have **{result.upper()}ED** your application.",
        color=discord.Color.green() if result.lower() == "pass" else discord.Color.red()
    )
    embed.add_field(name="Reason", value=reason, inline=False)
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer()["text"])
    await user.send(embed=embed)
    await interaction.response.send_message(f"Sent application result to {user.mention}", ephemeral=True)

# 3. /exploiter_log
@bot.tree.command(name="exploiter_log")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User exploiting", reason="What they did", evidence="Screenshot/Proof")
async def exploiter_log(interaction: discord.Interaction, user: discord.User, reason: str, evidence: discord.Attachment):
    embed = discord.Embed(
        title="Exploiter Logged",
        description=f"**User:** {user.mention}\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    embed.set_image(url=evidence.url)
    embed.set_footer(text=get_footer()["text"])
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    embed.set_image(url=BANNER_URL)
    channel = bot.get_channel(EXPLOITER_LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("Exploiter logged.", ephemeral=True)

# 4. /flight_briefing
# 5. /flight_log
# 6. /flightlog_delete
# 7. /flightlogs_view
# 8. /infraction
# 9. /infraction_remove
# 10. /infraction_view
# 11. /promote

# [The remaining 8 commands will be appended here if you confirm we're ready to continue]

# Run the bot
bot.run(TOKEN)
