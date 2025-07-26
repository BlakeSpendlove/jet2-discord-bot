import os
import discord
from discord.ext import commands
import random
import string
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def parse_id_list(env_var):
    raw = os.getenv(env_var, "")
    return [int(id.strip()) for id in raw.split(",") if id.strip().isdigit()]

# Load environment variables for role whitelists and guild IDs
WHITELIST_INFRACTION_ROLES = parse_id_list("WHITELIST_INFRACTION_ROLES")
WHITELIST_FLIGHTLOG_ROLES = parse_id_list("WHITELIST_FLIGHTLOG_ROLES")
WHITELIST_PROMOTE_ROLES = parse_id_list("WHITELIST_PROMOTE_ROLES")
WHITELIST_EMBED_ROLES = parse_id_list("WHITELIST_EMBED_ROLES")
WHITELIST_FLIGHTBRIEFING_ROLES = parse_id_list("WHITELIST_FLIGHTBRIEFING_ROLES")
WHITELIST_FLIGHTLOG_DELETE_ROLES = parse_id_list("WHITELIST_FLIGHTLOG_DELETE_ROLES")
WHITELIST_INFRACTION_REMOVE_ROLES = parse_id_list("WHITELIST_INFRACTION_REMOVE_ROLES")
WHITELIST_INFRACTION_VIEW_ROLES = parse_id_list("WHITELIST_INFRACTION_VIEW_ROLES")
WHITELIST_APP_RESULTS_ROLES = parse_id_list("WHITELIST_APP_RESULTS_ROLES")
WHITELIST_EXPLOITER_LOG_ROLES = parse_id_list("WHITELIST_EXPLOITER_LOG_ROLES")

GUILD_IDS = parse_id_list("GUILD_IDS")

def user_has_role(member: discord.Member, role_list: list[int]) -> bool:
    return any(role.id in role_list for role in member.roles)

def is_guild_allowed(guild: discord.Guild) -> bool:
    return guild.id in GUILD_IDS

def generate_footer_id(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_embed(title: str, description: str, color=0x1ABC9C, footer_text=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if footer_text is None:
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        footer_text = f"ID: {generate_footer_id()} | {now}"
    embed.set_footer(text=footer_text)
    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_guild_join(guild):
    if not is_guild_allowed(guild):
        print(f"Leaving guild {guild.name} ({guild.id}) - not whitelisted.")
        await guild.leave()

# --- COMMANDS ---

# 1. /promote
@bot.command()
async def promote(ctx, member: discord.Member, *, role_name: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_PROMOTE_ROLES):
        return await ctx.reply("You don't have permission to use this command.")

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        return await ctx.reply(f"Role `{role_name}` not found.")
    try:
        await member.add_roles(role)
        embed = create_embed(
            "Promotion Success",
            f"{ctx.author.mention} promoted {member.mention} by adding role `{role_name}`."
        )
        await ctx.reply(embed=embed)
    except discord.Forbidden:
        await ctx.reply("I do not have permission to add that role.")
    except Exception as e:
        await ctx.reply(f"An error occurred: {e}")

# 2. /infraction
@bot.command()
async def infraction(ctx, member: discord.Member, *, reason: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_INFRACTION_ROLES):
        return await ctx.reply("You don't have permission to use this command.")

    embed = create_embed(
        "Infraction Logged",
        f"User {member.mention} was given an infraction by {ctx.author.mention}.\nReason: {reason}"
    )
    await ctx.send(embed=embed)

# 3. /flight_log
@bot.command()
async def flight_log(ctx, flight_code: str, *, details: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_FLIGHTLOG_ROLES):
        return await ctx.reply("You don't have permission to use this command.")

    embed = create_embed(
        f"Flight Log: {flight_code}",
        details
    )
    await ctx.send(embed=embed)

# 4. /flightlog_delete
@bot.command()
async def flightlog_delete(ctx, log_id: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_FLIGHTLOG_DELETE_ROLES):
        return await ctx.reply("You don't have permission to delete flight logs.")

    # For demo purposes, just respond
    await ctx.reply(f"Flight log with ID `{log_id}` deleted (simulated).")

# 5. /infraction_remove
@bot.command()
async def infraction_remove(ctx, infraction_id: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_INFRACTION_REMOVE_ROLES):
        return await ctx.reply("You don't have permission to remove infractions.")

    # Simulate removal
    await ctx.reply(f"Infraction with ID `{infraction_id}` removed (simulated).")

# 6. /infraction_view
@bot.command()
async def infraction_view(ctx, member: discord.Member):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_INFRACTION_VIEW_ROLES):
        return await ctx.reply("You don't have permission to view infractions.")

    # Dummy view response
    embed = create_embed(
        f"Infractions for {member}",
        "List of infractions would appear here (simulated)."
    )
    await ctx.send(embed=embed)

# 7. /app_results
@bot.command()
async def app_results(ctx, member: discord.Member):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_APP_RESULTS_ROLES):
        return await ctx.reply("You don't have permission to view application results.")

    embed = create_embed(
        f"Application Results for {member}",
        "Application results would appear here (simulated)."
    )
    await ctx.send(embed=embed)

# 8. /exploiter_log
@bot.command()
async def exploiter_log(ctx, member: discord.Member, *, details: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_EXPLOITER_LOG_ROLES):
        return await ctx.reply("You don't have permission to log exploiters.")

    embed = create_embed(
        f"Exploiter Log: {member}",
        details,
        color=0xFF0000
    )
    await ctx.send(embed=embed)

# 9. /flight_briefing
@bot.command()
async def flight_briefing(ctx, flight_code: str, *, briefing: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_FLIGHTBRIEFING_ROLES):
        return await ctx.reply("You don't have permission to send flight briefings.")

    embed = create_embed(
        f"Flight Briefing: {flight_code}",
        briefing
    )
    await ctx.send(embed=embed)

# 10. /embed
@bot.command()
async def embed(ctx, *, content: str):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_EMBED_ROLES):
        return await ctx.reply("You don't have permission to use this command.")

    embed = create_embed("Custom Embed", content)
    await ctx.send(embed=embed)

# 11. /flightlogs_view
@bot.command()
async def flightlogs_view(ctx):
    if ctx.guild is None or not is_guild_allowed(ctx.guild):
        return await ctx.reply("This command cannot be used in this server.")
    if not user_has_role(ctx.author, WHITELIST_FLIGHTLOG_ROLES):
        return await ctx.reply("You don't have permission to view flight logs.")

    embed = create_embed(
        "Flight Logs",
        "Listing all recent flight logs (simulated)."
    )
    await ctx.send(embed=embed)

# --- Run bot ---
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("Error: DISCORD_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)
