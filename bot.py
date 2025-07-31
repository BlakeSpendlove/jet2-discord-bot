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


# Error handler
@embed_command.error
async def on_embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingRole):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message("An error occurred.", ephemeral=True)

# Add your 10 other commands here using similar structure

bot.run(BOT_TOKEN)
