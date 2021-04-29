import discord
from discord.ext import commands
import sqlite3
import asyncio
import os
import json

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)

bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=True, Intents=discord.Intents.default())


db = sqlite3.connect('db.sqlite')
cr = db.cursor()

bot.cr = cr
bot.load_extension('cogs.event')
bot.remove_command('help')

cr.execute("""
CREATE TABLE IF NOT EXISTS reply_messages(
id INTEGER PRIMARY KEY AUTOINCREMENT,
first_reply TEXT NOT NULL,
last_reply TEXT NOT NULL
)
""")


@bot.command(name='add-reply', help='add new reply')
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
async def add_reply(ctx):
    message = await ctx.send('please type the first message, **Example: `HI`** >>>')

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        reply = await bot.wait_for("message", timeout=180.0, check=check)
    except asyncio.TimeoutError:
        await message.delete()
        return
    else:
        first_reply = reply.content
        await reply.add_reaction('✔')

    message = await ctx.send('please type the last message, **Example: `Hello`** >>>')

    try:
        reply = await bot.wait_for("message", timeout=180.0, check=check)
    except asyncio.TimeoutError:
        await message.delete()
        return
    else:
        last_reply = reply.content
        await reply.add_reaction('✔')

    cr.execute('INSERT INTO reply_messages(first_reply, last_reply) VALUES(?, ?)', (first_reply, last_reply))
    db.commit()
    embed = discord.Embed(
        description='**New reply**',
        color=0x008000
    )
    embed.add_field(name='✏️ message:', value=f"```\n{first_reply}\n```", inline=False)
    embed.add_field(name='🗨️ reply:', value=f"```\n{last_reply}\n```", inline=False)
    await ctx.send(embed=embed)


@bot.command(name='remove-reply', help="remove reply from id")
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
async def remove_reply(ctx, id: int):
    info = cr.execute('SELECT * FROM reply_messages WHERE id = ?', (id,)).fetchone()
    if info is None:
        await ctx.send('please check the id')
        return
    cr.execute('DELETE FROM reply_messages WHERE id = ?', (id,))
    db.commit()
    embed = discord.Embed(
        description='**remove reply**',
        color=0xFF0000
    )
    embed.add_field(name='🆔 ID:', value=f"```\n{info[0]}\n```")
    embed.add_field(name='✏️ message:', value=f"```\n{info[1]}\n```", inline=False)
    embed.add_field(name='🗨️ reply:', value=f"```\n{info[2]}\n```", inline=False)
    await ctx.send(embed=embed)


@bot.command(name='list-reply', help="check list reply")
@commands.has_permissions(manage_messages=True)
@commands.guild_only()
async def list_reply(ctx):
    data = cr.execute('SELECT * FROM reply_messages').fetchall()
    if data == []:
        await ctx.send(embed=discord.Embed(description='The list reply is empty', color=0xFF0000))
        return
    embed = discord.Embed(
        description="**List reply**",
        color=0x0000FF
    )
    for i in data:
        embed.add_field(name=f'ID `{i[0]}`', value=f'**message:** `{i[1]}`\n**reply:** `{i[2]}`', inline=False)
    await ctx.send(embed=embed)


@bot.command(name='help', help='Show this list')
@commands.guild_only()
async def help_command(ctx):
    embed = discord.Embed(
        description="**Help Command**\n{}".format("\n".join([f"`{bot.command_prefix}{i.name}` - {i.help}" for i in bot.commands])),
        color=ctx.author.color
    )
    await ctx.send(embed=embed)


@bot.event
async def on_ready():
    print(f"------\nbot: {bot.user}\nID: {bot.user.id}\n------")
    print("Copyright (c) 2021 HazemMeqdad & OTTAWA team\nSupport: https://discord.gg/sUZ2W8FDKr\nContent: H A Z E M ᵒᵗ#0090")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(ctx.channel, discord.channel.DMChannel):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            description=f"{bot.command_prefix}{ctx.command.name} {ctx.command.signature}",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            description=f"{bot.command_prefix}{ctx.command.name} {ctx.command.signature}",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("the bot missing permissions")
        return
    elif isinstance(error, commands.errors.MissingPermissions):
        await ctx.send("your missing permissions `manage_messages`")
        return
    elif isinstance(error, discord.errors.Forbidden):
        return

bot.run(os.environ['token'])
