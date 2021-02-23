from discord.ext import commands, tasks
import discord
from discord import ChannelType
import pymanga
from chiichan import Manga
import typing
import re

class TwCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group()
    async def tw(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid usage of command :/')
            h = f"""
    **{ctx.prefix}tw show [manga name | mangaupdates link]**
    see trigger warnings submitted for this manga by other users. (p.s: the triggers are spoilered. you can also use this command in a dm with this bot.)

    **{ctx.prefix}tw add [manga name | mangaupdates link]**
    submit trigger warnings for this manga. (p.s: you can also use this command in a dm with this bot.)

    *ex: {ctx.prefix}tw show Still Sick*
    *or: {ctx.prefix}tw show <https://www.mangaupdates.com/series.html?id=148031>*

    *ex: {ctx.prefix}tw add Still Sick*
    *or: {ctx.prefix}tw add <https://www.mangaupdates.com/series.html?id=148031>*
            """
            await ctx.send(h)

    @tw.command(name="show")
    async def get_triggers(self,ctx,*,manga: Manga):
        if not manga:
            return

        id = manga['id']
        triggers = await ctx.db.get_triggers(id)
        if not triggers:
            await ctx.send("No one has added trigger warnings for this manga yet.")
            return

        await ctx.send("people have added the following trigger warnings for this manga:")

        msg = "||"
        for t,amount in triggers.items():
            msg += f"{t} *({amount} {'user' if amount == 1 else 'users'})*" + '\n'
        msg += "||"
        await ctx.send(msg)

    @tw.command(name="add")
    async def add_triggers(self,ctx,*,manga: typing.Optional[Manga]):
        if not manga:
            return

        id = manga['id']
        question = await ctx.send("What trigger warnings would you like to add to this manga? (*separate multiple warnings using ';'.*)\n*p.s: please spoiler your message if you're in a server!*")

        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id)

            triggers = [warning.strip() for warning in msg.content.replace('||','').split(';')]
            await ctx.db.add_triggers(id,ctx.author.id,triggers)

            channel = await self.bot.fetch_channel(msg.channel.id)
            if channel.type != ChannelType.private and channel.type != ChannelType.group:
                await msg.delete()
        except asyncio.TimeoutError:
            await question.delete()

        await ctx.send("trigger warnings added to database. thank you for submitting them :)")

def setup(bot):
    bot.add_cog(TwCog(bot))
