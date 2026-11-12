import asyncio
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

ROLES = [
    ("Admin", 0xE74C3C, discord.Permissions(administrator=True)),
    ("Moderator", 0x3498DB, discord.Permissions(
        kick_members=True, ban_members=True,
        manage_messages=True, moderate_members=True)),
    ("Scripter", 0x9B59B6, discord.Permissions()),
    ("Builder", 0xF1C40F, discord.Permissions()),
    ("Member", 0x95A5A6, discord.Permissions()),
]

# (type, name, mode)  type: text/voice/forum   mode: open/readonly/staff
LAYOUT = [
    ("👋 START HERE", [
        ("text", "👋┃welcome", "readonly"),
        ("text", "📜┃rules", "readonly"),
        ("text", "📢┃announcements", "readonly"),
        ("text", "🎭┃get-roles", "open"),
    ]),
    ("🎬 CONTENT", [
        ("text", "👀┃sneak-peeks", "readonly"),
        ("text", "▶️┃new-videos", "readonly"),
        ("text", "💡┃tutorial-requests", "open"),
    ]),
    ("🧰 RESOURCES", [
        ("text", "📦┃models", "open"),
        ("text", "📝┃scripts", "open"),
        ("text", "🔗┃asset-links", "open"),
        ("text", "🌐┃website", "readonly"),
    ]),
    ("🛠️ HELP", [
        ("forum", "🧠┃scripting-help", "open"),
        ("forum", "🏗️┃building-help", "open"),
        ("text", "🐞┃bug-reports", "open"),
    ]),
    ("💬 COMMUNITY", [
        ("text", "💬┃general", "open"),
        ("text", "🎮┃showcase", "open"),
        ("text", "🤣┃memes", "open"),
        ("text", "🌟┃game-ideas", "open"),
        ("text", "☕┃off-topic", "open"),
        ("text", "🤖┃bot-commands", "open"),
    ]),
    ("🔊 VOICE", [
        ("voice", "🔊 General VC", "open"),
        ("voice", "🧱 Co-Build VC", "open"),
        ("voice", "📚 Focus VC", "open"),
    ]),
    ("🔒 STAFF ONLY", [
        ("text", "🔒┃staff-chat", "staff"),
        ("text", "📋┃mod-log", "staff"),
        ("text", "⚙️┃admin-commands", "staff"),
    ]),
]


def overwrites_for(guild, mode, roles):
    ow = {}
    if mode == "readonly":
        ow[guild.default_role] = discord.PermissionOverwrite(
            send_messages=False, add_reactions=False)
    elif mode == "staff":
        ow[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
        for name in ("Admin", "Moderator"):
            ow[roles[name]] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True)
    return ow


async def make_channel(guild, cat, kind, name, mode, roles):
    ow = overwrites_for(guild, mode, roles)
    try:
        if kind == "voice":
            await guild.create_voice_channel(name, category=cat, overwrites=ow)
        elif kind == "forum":
            try:
                await guild.create_forum(name, category=cat, overwrites=ow)
            except Exception:
                await guild.create_text_channel(name, category=cat, overwrites=ow)
        else:
            await guild.create_text_channel(name, category=cat, overwrites=ow)
        print("Created:", name)
    except Exception as e:
        print("FAILED:", name, "->", repr(e))
    await asyncio.sleep(0.6)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}. Now type !setup CONFIRM in your server.")


@bot.event
async def on_command_error(ctx, error):
    print("COMMAND ERROR:", repr(error))
    try:
        await ctx.author.send(f"Error: {error}")
    except Exception:
        pass


@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup_server(ctx, confirm: str = None):
    if confirm != "CONFIRM":
        await ctx.send("This deletes ALL channels. Type `!setup CONFIRM` to continue.")
        return

    guild = ctx.guild
    author = ctx.author
    print("Starting setup in:", guild.name)

    for ch in list(guild.channels):
        try:
            await ch.delete()
            print("Deleted:", ch.name)
        except Exception as e:
            print("Could not delete", ch.name, "->", repr(e))
        await asyncio.sleep(0.5)

    roles = {}
    for name, color, perms in ROLES:
        existing = discord.utils.get(guild.roles, name=name)
        try:
            roles[name] = existing or await guild.create_role(
                name=name, colour=discord.Colour(color), permissions=perms)
            print("Role ready:", name)
        except Exception as e:
            print("FAILED role:", name, "->", repr(e))
        await asyncio.sleep(0.6)

    for cat_name, channels in LAYOUT:
        cat_ow = {}
        if cat_name.startswith("🔒") and "Admin" in roles and "Moderator" in roles:
            cat_ow[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
            for rn in ("Admin", "Moderator"):
                cat_ow[roles[rn]] = discord.PermissionOverwrite(view_channel=True)
        try:
            cat = await guild.create_category(cat_name, overwrites=cat_ow)
            print("Category:", cat_name)
        except Exception as e:
            print("FAILED category:", cat_name, "->", repr(e))
            continue
        await asyncio.sleep(0.6)
        for kind, name, mode in channels:
            await make_channel(guild, cat, kind, name, mode, roles)

    print("DONE")
    try:
        await author.send("✅ Stable Studio setup is done!")
    except Exception:
        pass
