import discord
from discord.ext import commands


class Event(commands.Cog):
    def __init__(self, bot, cr):
        self.bot = bot
        self.cr = cr

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.guild is None or ctx.author.bot:
            return
        data = self.cr.execute('SELECT * FROM reply_messages').fetchall()
        if data == []:
            return
        messages = [i[1] for i in data]
        if ctx.content in messages:
            reply = [i for i in data if ctx.content in i]
            await ctx.channel.send(reply[0][2])


def setup(bot):
    bot.add_cog(Event(bot, bot.cr))
