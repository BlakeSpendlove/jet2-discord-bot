import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import datetime
import os

# Constants (Replace only BOT_TOKEN and GUILD_ID with environment variables)
BOT_TOKEN = os.environ["BOT_TOKEN"]
GUILD_ID = int(os.environ["GUILD_ID"])

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

# Utility to generate a unique 6-character alphanumeric ID
def generate_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Utility to generate a timestamped footer
def generate_footer():
    return f"ID: {generate_id()} • {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"

# On ready
guild = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f"Bot is online as {bot.user}")

@tree.command(name="embed", description="Send a custom embed using Discohook-style JSON.")
@app_commands.describe(json_code="The JSON code for the embed")
async def embed_command(interaction: discord.Interaction, json_code: str):
    # Check role permissions
    if ROLE_EMBED not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return

    try:
        data = json.loads(json_code)

        # Handle single or multiple embeds
        embeds = []
        embed_data_list = data.get("embeds", [data]) if isinstance(data, dict) else data
        if not isinstance(embed_data_list, list):
            embed_data_list = [embed_data_list]

        for embed_data in embed_data_list:
            embed = discord.Embed(
                title=embed_data.get("title", discord.Embed.Empty),
                description=embed_data.get("description", discord.Embed.Empty),
                color=discord.Color.from_str(embed_data.get("color", "#ff0000")) if "color" in embed_data else discord.Color.red()
            )
            if "footer" in embed_data:
                embed.set_footer(text=embed_data["footer"].get("text", ""))
            if "image" in embed_data:
                embed.set_image(url=embed_data["image"].get("url", ""))
            if "thumbnail" in embed_data:
                embed.set_thumbnail(url=embed_data["thumbnail"].get("url", ""))
            if "author" in embed_data:
                embed.set_author(
                    name=embed_data["author"].get("name", ""),
                    url=embed_data["author"].get("url", discord.Embed.Empty),
                    icon_url=embed_data["author"].get("icon_url", discord.Embed.Empty),
                )
            for field in embed_data.get("fields", []):
                embed.add_field(
                    name=field.get("name", "\u200b"),
                    value=field.get("value", "\u200b"),
                    inline=field.get("inline", False),
                )
            embeds.append(embed)

        await interaction.response.send_message("Embed sent.", ephemeral=True)
        for embed in embeds:
            await interaction.channel.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to parse JSON embed: {e}", ephemeral=True)

@tree.command(name="app_results", description="Send application results to a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to send the result to", result="Pass or Fail", reason="Reason for result")
async def app_results(interaction: discord.Interaction, user: discord.User, result: str, reason: str):
    result = result.lower()
    if result not in ["pass", "fail"]:
        await interaction.response.send_message("❌ Result must be `pass` or `fail`.", ephemeral=True)
        return

    color = 0x00ff00 if result == "pass" else 0xff0000
    embed = discord.Embed(
        title=f"Application Result: {result.capitalize()}",
        description=f"**Reason:** {reason}",
        color=color
    )
    embed.set_footer(text=f"Sent by {interaction.user.name}")
    embed.set_thumbnail(url=BANNER_URL)

    try:
        await user.send(embed=embed)
        await interaction.response.send_message("✅ Result sent to user.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Could not send DM to that user.", ephemeral=True)

@tree.command(name="exploiter_log", description="Log an exploiter with proof.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="Username of the exploiter", reason="Reason for logging", proof="Upload proof")
async def exploiter_log(interaction: discord.Interaction, user: str, reason: str, proof: discord.Attachment):
    embed = discord.Embed(
        title="🚨 Exploiter Logged",
        description=f"**User:** {user}\n**Reason:** {reason}",
        color=0xff0000
    )
    embed.set_image(url=proof.url)
    embed.set_footer(text=f"Logged by {interaction.user.name}")
    embed.set_thumbnail(url=BANNER_URL)

    channel = interaction.client.get_channel(EXPLOITER_LOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Exploiter logged.", ephemeral=True)

@tree.command(name="flight_briefing", description="Send a flight briefing embed.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(game_link="Link to the game", vc_link="Voice chat link", flight_code="Flight code")
async def flight_briefing(interaction: discord.Interaction, game_link: str, vc_link: str, flight_code: str):
    embed = discord.Embed(
        title=f"🛫 Flight Briefing - {flight_code}",
        description=f"**Game:** [Click here]({game_link})\n**VC:** [Join VC]({vc_link})",
        color=0x3498db
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Sent by {interaction.user.name}")

    channel = interaction.client.get_channel(BRIEFING_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Briefing sent.", ephemeral=True)

@tree.command(name="flight_log", description="Log a completed flight.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User who hosted", flight_code="Flight code", log_file="Flight log file")
async def flight_log(interaction: discord.Interaction, user: discord.User, flight_code: str, log_file: discord.Attachment):
    embed = discord.Embed(
        title="🛬 Flight Log",
        description=f"**Host:** {user.mention}\n**Flight Code:** `{flight_code}`",
        color=0x2ecc71
    )
    embed.set_footer(text=f"Logged by {interaction.user.name}")
    embed.set_thumbnail(url=BANNER_URL)

    channel = interaction.client.get_channel(FLIGHTLOG_CHANNEL_ID)
    await channel.send(embed=embed)
    await channel.send(file=await log_file.to_file())
    await interaction.response.send_message("✅ Flight log submitted.", ephemeral=True)

@tree.command(name="flightlog_delete", description="Delete a flight log entry by ID.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(message_id="The ID of the flight log message")
async def flightlog_delete(interaction: discord.Interaction, message_id: str):
    channel = interaction.client.get_channel(FLIGHTLOG_CHANNEL_ID)
    try:
        msg = await channel.fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("✅ Log deleted.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not delete that message.", ephemeral=True)

@tree.command(name="flightlogs_view", description="View flight logs for a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view logs for")
async def flightlogs_view(interaction: discord.Interaction, user: discord.User):
    channel = interaction.client.get_channel(FLIGHTLOG_CHANNEL_ID)
    messages = await channel.history(limit=100).flatten()
    logs = [m for m in messages if user.mention in m.content or user.name in m.content]

    if not logs:
        await interaction.response.send_message("❌ No logs found.", ephemeral=True)
        return

    embed = discord.Embed(title=f"📝 Flight Logs - {user.name}", color=0x95a5a6)
    for msg in logs[:5]:
        embed.add_field(name="Log", value=msg.content[:1024], inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="infraction", description="Log an infraction, termination or demotion.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User involved", action="Type of infraction", reason="Reason for the action")
async def infraction(interaction: discord.Interaction, user: discord.User, action: str, reason: str):
    embed = discord.Embed(
        title=f"⚠️ {action.capitalize()} Notice",
        description=f"**User:** {user.mention}\n**Action:** {action}\n**Reason:** {reason}",
        color=0xe67e22
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Issued by {interaction.user.name}")

    channel = interaction.client.get_channel(INFRACTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Infraction logged.", ephemeral=True)

@tree.command(name="infraction_remove", description="Remove an infraction by message ID.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(message_id="Message ID to delete")
async def infraction_remove(interaction: discord.Interaction, message_id: str):
    channel = interaction.client.get_channel(INFRACTION_CHANNEL_ID)
    try:
        msg = await channel.fetch_message(int(message_id))
        await msg.delete()
        await interaction.response.send_message("✅ Infraction removed.", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Could not remove infraction.", ephemeral=True)

@tree.command(name="infraction_view", description="View all infractions for a user.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User to view")
async def infraction_view(interaction: discord.Interaction, user: discord.User):
    channel = interaction.client.get_channel(INFRACTION_CHANNEL_ID)
    messages = await channel.history(limit=100).flatten()
    logs = [m for m in messages if user.mention in m.content or user.name in m.content]

    if not logs:
        await interaction.response.send_message("❌ No infractions found.", ephemeral=True)
        return

    embed = discord.Embed(title=f"⚠️ Infractions for {user.name}", color=0xc0392b)
    for msg in logs[:5]:
        embed.add_field(name="Log", value=msg.content[:1024], inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="promote", description="Log a promotion.")
@app_commands.checks.has_role(WHITELIST_ROLE_ID)
@app_commands.describe(user="User being promoted", new_rank="The new rank", reason="Reason for promotion")
async def promote(interaction: discord.Interaction, user: discord.User, new_rank: str, reason: str):
    embed = discord.Embed(
        title="📈 Promotion",
        description=f"**User:** {user.mention}\n**Promoted To:** {new_rank}\n**Reason:** {reason}",
        color=0x1abc9c
    )
    embed.set_thumbnail(url=BANNER_URL)
    embed.set_footer(text=f"Promoted by {interaction.user.name}")

    channel = interaction.client.get_channel(PROMOTION_CHANNEL_ID)
    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Promotion logged.", ephemeral=True)


# Error handler
@embed_command.error
async def on_embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred.", ephemeral=True)

# Add your 10 other commands here using similar structure

bot.run(BOT_TOKEN)
