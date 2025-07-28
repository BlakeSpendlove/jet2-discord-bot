import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import datetime
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
tree = app_commands.CommandTree(client)

# Load Railway environment variables
WHITELIST_ROLE_ID = int(os.environ['WHITELIST_ROLE_ID'])
LOG_CHANNEL_ID = int(os.environ['LOG_CHANNEL_ID'])
BANNER_URL = os.environ['BANNER_URL']
SCHEDULE_ROLE_ID = int(os.environ['SCHEDULE_ROLE_ID'])
EMBED_CHANNEL_ID = int(os.environ['EMBED_CHANNEL_ID'])
APP_RESULTS_CHANNEL_ID = int(os.environ['APP_RESULTS_CHANNEL_ID'])
FLIGHT_LOG_CHANNEL_ID = int(os.environ['FLIGHT_LOG_CHANNEL_ID'])
FLIGHT_BRIEFING_CHANNEL_ID = int(os.environ['FLIGHT_BRIEFING_CHANNEL_ID'])
INFRACTION_CHANNEL_ID = int(os.environ['INFRACTION_CHANNEL_ID'])
PROMOTE_CHANNEL_ID = int(os.environ['PROMOTE_CHANNEL_ID'])
TICKET_FORUM_CHANNEL_ID = int(os.environ['TICKET_FORUM_CHANNEL_ID'])
FLIGHT_CREATE_CHANNEL_ID = int(os.environ['FLIGHT_CREATE_CHANNEL_ID'])
AFFILIATE_CHANNEL_ID = int(os.environ['AFFILIATE_CHANNEL_ID'])
EXPLOITER_LOG_CHANNEL_ID = int(os.environ['EXPLOITER_LOG_CHANNEL_ID'])
GUILD_ID = int(os.environ['GUILD_ID'])

# Data storage
flight_logs = {}
infractions = {}
application_results = {}

# Generate unique ID
def generate_id():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"Bot is ready. Logged in as {client.user}.")

# /flightlogs_view command
@tree.command(name="flightlogs_view", description="View a user’s flight logs", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    logs = flight_logs.get(user.id, [])
    if not logs:
        await interaction.response.send_message("No flight logs found.", ephemeral=True)
        return

    for log in logs:
        embed = discord.Embed(
            description=(
                f"**🛬 Jet2.com | Flight Log Submitted**\n\n"
                f"**👤 Staff Member:** {user.mention}\n"
                f"**🛫 Flight Code:** {log['flight_code']}\n"
                f"**📎 Evidence:** [Attachment]({log['evidence_url']})\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Your flight has been successfully logged and submitted to our records system.\n"
                f"Staff activity will be reviewed and tracked to ensure high performance and flight standards.\n\n"
                f"Please do not delete your evidence. If further clarification is needed, a member of management will contact you.\n\n"
                f"**✈️ Thank you for contributing to Jet2.com — Friendly low fares. Friendly people.**"
            ),
            color=10364968
        )
        embed.set_author(name="Jet2.com Flight Log")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395760490982150194/1398426011007324220/Jet2_Transparent.png")
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=f"Log ID: {log['id']} • {log['timestamp']}")
        await interaction.followup.send(embed=embed, ephemeral=True)

# /infraction_view command
@tree.command(name="infraction_view", description="View a user’s infractions", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    logs = infractions.get(user.id, [])
    if not logs:
        await interaction.response.send_message("No infractions found.", ephemeral=True)
        return

    for log in logs:
        embed = discord.Embed(
            description=(
                f"**⚠️ Jet2.com | Infraction Notice**\n\n"
                f"This is a notice of your infraction.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**👤 User:** {user.mention}\n"
                f"**📄 Infraction:** {log['type']}\n"
                f"**📝 Reason:** {log['reason']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**🔁 What Happens Next?**\n"
                f"You are expected to acknowledge this notice and take appropriate steps to correct your behaviour. Repeated infractions may lead to more severe consequences, including permanent removal from the community or staff team.\n\n"
                f"If you believe this notice was issued in error, you may appeal by contacting a member of management respectfully.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**✈️ Jet2.com — Friendly low fares. Friendly people.**"
            ),
            color=10364968
        )
        embed.set_author(name="Jet2.com Infraction")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395760490982150194/1398426011007324220/Jet2_Transparent.png")
        embed.set_image(url=BANNER_URL)
        embed.set_footer(text=f"Infraction ID: {log['id']} • {log['timestamp']}")
        await interaction.followup.send(embed=embed, ephemeral=True)

# /app_results_view command
@tree.command(name="app_results_view", description="View a user’s application result", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
async def app_results_view(interaction: discord.Interaction, user: discord.User):
    result = application_results.get(user.id)
    if not result:
        await interaction.response.send_message("No application result found.", ephemeral=True)
        return

    passed = result['passed']
    reason = result['reason']
    emoji = "✅" if passed else "❌"
    label = "Passed" if passed else "Failed"

    embed = discord.Embed(
        description=(
            f"**📢 Staff Application Update**\n\n"
            f"**{emoji} Result:** {label}\n"
            f"**📝 Reason:** {reason}\n\n"
            f"If you failed, we strongly encourage you to try again.\n"
            f"If you passed, congratulations and await a further DM with an invite to the server.\n\n"
            f"Welcome to the team — we look forward to flying with you!"
        ),
        color=10364968
    )
    embed.set_author(name="Jet2.com Application")
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1395760490982150194/1398426011007324220/Jet2_Transparent.png")
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=f"App ID: {result['id']} • {result['timestamp']}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

client.run(os.environ['DISCORD_TOKEN'])
