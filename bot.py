import os
import discord
from discord.ext import commands
import random
import string
from datetime import datetime, timezone

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --- Helper to parse comma-separated IDs into int list ---
def parse_id_list(env_var_name):
    value = os.getenv(env_var_name, "")
    return [int(x.strip()) for x in value.split(",") if x.strip().isdigit()]

# --- Load environment variables ---
TOKEN = os.getenv("DISCORD_TOKEN")

FLIGHTLOG_CHANNEL_ID = int(os.getenv("FLIGHTLOG_CHANNEL_ID", "0"))
INFRACTION_CHANNEL_ID = int(os.getenv("INFRACTION_CHANNEL_ID", "0"))
PROMOTE_CHANNEL_ID = int(os.getenv("PROMOTE_CHANNEL_ID", "0"))
GUILD_IDS = parse_id_list("GUILD_IDS")

WHITELIST_APP_RESULTS_ROLES = parse_id_list("WHITELIST_APP_RESULTS_ROLES")
WHITELIST_EMBED_ROLES = parse_id_list("WHITELIST_EMBED_ROLES")
WHITELIST_EXPLOITER_LOG_ROLES = parse_id_list("WHITELIST_EXPLOITER_LOG_ROLES")
WHITELIST_FLIGHTBRIEFING_ROLES = parse_id_list("WHITELIST_FLIGHTBRIEFING_ROLES")
WHITELIST_FLIGHTLOG_DELETE_ROLES = parse_id_list("WHITELIST_FLIGHTLOG_DELETE_ROLES")
WHITELIST_FLIGHTLOG_ROLES = parse_id_list("WHITELIST_FLIGHTLOG_ROLES")
WHITELIST_INFRACTION_REMOVE_ROLES = parse_id_list("WHITELIST_INFRACTION_REMOVE_ROLES")
WHITELIST_INFRACTION_ROLES = parse_id_list("WHITELIST_INFRACTION_ROLES")
WHITELIST_INFRACTION_VIEW_ROLES = parse_id_list("WHITELIST_INFRACTION_VIEW_ROLES")
WHITELIST_PROMOTE_ROLES = parse_id_list("WHITELIST_PROMOTE_ROLES")

# Banner URL for embeds
BANNER_URL = os.getenv("BANNER_URL", "https://example.com/banner.png")

# --- Helper functions ---

def generate_unique_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_footer_text():
    unique_id = generate_unique_id()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"ID: {unique_id} | {timestamp}"

def is_guild_whitelisted():
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        if GUILD_IDS and ctx.guild.id not in GUILD_IDS:
            return False
        return True
    return commands.check(predicate)

def has_any_role(role_ids):
    async def predicate(ctx):
        if ctx.guild is None:
            return False
        if not role_ids:
            # If no roles specified, allow all
            return True
        user_roles = {role.id for role in ctx.author.roles}
        if any(r in user_roles for r in role_ids):
            return True
        return False
    return commands.check(predicate)

# --- Commands ---

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_EMBED_ROLES)
async def embed(ctx):
    embed = discord.Embed(title="Embed Command",
                          description="This is a placeholder for the embed command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_APP_RESULTS_ROLES)
async def app_results(ctx):
    embed = discord.Embed(title="Application Results",
                          description="Placeholder for app_results command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_EXPLOITER_LOG_ROLES)
async def exploiter_log(ctx):
    embed = discord.Embed(title="Exploiter Log",
                          description="Placeholder for exploiter_log command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_FLIGHTBRIEFING_ROLES)
async def flight_briefing(ctx):
    embed = discord.Embed(title="Flight Briefing",
                          description="Placeholder for flight_briefing command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_FLIGHTLOG_ROLES)
async def flight_log(ctx):
    embed = discord.Embed(title="Flight Log",
                          description="Placeholder for flight_log command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    if FLIGHTLOG_CHANNEL_ID:
        flightlog_channel = bot.get_channel(FLIGHTLOG_CHANNEL_ID)
        if flightlog_channel:
            await flightlog_channel.send(embed=embed)
        else:
            await ctx.send("Flight log channel not found.")
    else:
        await ctx.send("Flight log channel ID not set.")
    await ctx.send("Flight log sent.")

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_FLIGHTLOG_DELETE_ROLES)
async def flightlog_delete(ctx):
    embed = discord.Embed(title="Delete Flight Log",
                          description="Placeholder for flightlog_delete command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_FLIGHTLOG_ROLES)
async def flightlogs_view(ctx):
    embed = discord.Embed(title="View Flight Logs",
                          description="Placeholder for flightlogs_view command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_INFRACTION_ROLES)
async def infraction(ctx):
    embed = discord.Embed(title="Add Infraction",
                          description="Placeholder for infraction command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    if INFRACTION_CHANNEL_ID:
        infra_channel = bot.get_channel(INFRACTION_CHANNEL_ID)
        if infra_channel:
            await infra_channel.send(embed=embed)
        else:
            await ctx.send("Infraction channel not found.")
    else:
        await ctx.send("Infraction channel ID not set.")
    await ctx.send("Infraction added.")

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_INFRACTION_REMOVE_ROLES)
async def infraction_remove(ctx):
    embed = discord.Embed(title="Remove Infraction",
                          description="Placeholder for infraction_remove command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_INFRACTION_VIEW_ROLES)
async def infraction_view(ctx):
    embed = discord.Embed(title="View Infractions",
                          description="Placeholder for infraction_view command.",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await ctx.send(embed=embed)

@bot.command()
@is_guild_whitelisted()
@has_any_role(WHITELIST_PROMOTE_ROLES)
async def promote(ctx):
    promote_channel = bot.get_channel(PROMOTE_CHANNEL_ID)
    if promote_channel is None:
        await ctx.send("Promote channel not found or not set!")
        return
    embed = discord.Embed(title="Promotion Announcement",
                          description=f"{ctx.author.mention} used the promote command!",
                          color=discord.Color.red())
    embed.set_image(url=BANNER_URL)
    embed.set_footer(text=get_footer_text())
    await promote_channel.send(embed=embed)
    await ctx.send("Promotion announcement sent.")

# --- Run bot ---

if not TOKEN:
    print("ERROR: DISCORD_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)
