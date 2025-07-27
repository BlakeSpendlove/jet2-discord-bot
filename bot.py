import os
import discord
import random
import string
from discord.ext import commands
from discord import app_commands, File, ButtonStyle
from discord.ui import Button, View
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value

# Environment variables
TOKEN = get_env_variable("DISCORD_TOKEN")
GUILD_ID = int(get_env_variable("GUILD_ID"))
WHITELIST_ROLE_ID = int(get_env_variable("WHITELIST_ROLE_ID"))
SCHEDULE_ROLE_ID = int(get_env_variable("SCHEDULE_ROLE_ID"))
FLIGHT_CHANNEL_ID = int(get_env_variable("FLIGHT_CHANNEL_ID"))
LOG_CHANNEL_ID = int(get_env_variable("LOG_CHANNEL_ID"))

BANNER_URL = "https://media.discordapp.net/attachments/1395760490982150194/1395769069541789736/Banner1.png"
THUMBNAIL_URL = "https://media.discordapp.net/attachments/1395760490982150194/1398426011007324220/Jet2_Transparent.png"

# Helper functions

def generate_uid():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_footer():
    return {
        "text": f"ID: {generate_uid()} | {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    }

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot connected as {bot.user}")

# --- /promote ---
@bot.tree.command(name="promote", description="Log a promotion")
@app_commands.describe(user="User to promote", promotion_to="New rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.User, promotion_to: str, reason: str):
    if WHITELIST_ROLE_ID not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("You don't have permission.", ephemeral=True)

    embed = discord.Embed(
        description=f"**🎖️ Jet2.com | Promotion Notice**\n\nWe are pleased to announce that the following staff member has received a **promotion** within Jet2.com for their outstanding performance and dedication to the airline.\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n**👤 Staff Member:** {user.mention}\n**⬆️ New Rank:** {promotion_to}\n**📜 Reason for Promotion:**  \n{reason}\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nPlease join us in congratulating them on this well-earned advancement. We look forward to seeing their continued contributions to Jet2.com.\n\n**✈️ Jet2.com — Friendly low fares. Friendly people.**",
        color=10364968
    )
    embed.set_author(name="Jet2.com Promotion")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=create_footer()['text'])

    await interaction.response.send_message(f"{user.mention}", embed=embed)

# --- /flight_briefing ---
@bot.tree.command(name="flight_briefing", description="Send a flight briefing")
@app_commands.describe(flight_code="Flight code (e.g., LS8800)", game_link="Flight game link", vc_link="VC link")
async def flight_briefing(interaction: discord.Interaction, flight_code: str, game_link: str, vc_link: str):
    if WHITELIST_ROLE_ID not in [role.id for role in interaction.user.roles]:
        return await interaction.response.send_message("You don't have permission.", ephemeral=True)

    embed = discord.Embed(
        description="**📋 Jet2.com | Flight Briefing Notice**\n\n**All available staff are requested to attend the upcoming flight briefing.**\n\nWe are preparing for our next scheduled flight, and all assigned crew — including **Flight Deck**, **Cabin Crew**, and **Ground Operations** — are **required to join the briefing before departure**.\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n**📍 Briefing Includes:**  \n• **Flight route & departure time**  \n• **Role assignments**  \n• **Uniform and conduct check**  \n• **Safety & security procedures**\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nPlease ensure you are in **full uniform**, **ready**, and **on time**.  \nLate arrival may result in being **removed from the flight roster**.\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n**✈️ Let’s work together to deliver a smooth, professional, and enjoyable experience for all passengers.**\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n**🤝 Click the button below to Join Briefing**  \n**📞 Click the button to join VC**",
        color=10364968
    )
    embed.set_author(name="Jet2.com Briefing")
    embed.set_image(url=BANNER_URL)
    embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.set_footer(text=create_footer()['text'])

    view = View()
    view.add_item(Button(label="Join Briefing", url=game_link, style=ButtonStyle.link))
    view.add_item(Button(label="Join VC", url=vc_link, style=ButtonStyle.link))

    await interaction.response.send_message(embed=embed, view=view)

# --- Add other 9 commands in the same format ---
# (/app_results, /exploiter_log, /flight_log, /flightlog_delete, /flightlogs_view, /infraction, /infraction_remove, /infraction_view, /embed)
# Each using updated JSON formatting as shown above.

bot.run(TOKEN)
