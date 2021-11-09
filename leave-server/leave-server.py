import discord
from discord import colour
from discord.ext import commands


class LeaveGuildPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild_id):
        """
        Force your bot to leave a specified server
        """
        guild = None
        try:
            guild_id = int(guild_id)
            guild = self.bot.get_guild(guild_id)
        except:
            pass

        if guild is None:
            guild = discord.utils.find(lambda x: x.name.lower().__contains__(str(guild_id).lower()), self.bot.guilds)

        if guild is None:
            return await ctx.send("Not able to find any guild with argument {0}".format(guild_id))

        if guild.id in (self.bot.modmail_guild.id, self.bot.guild.id):
            return await ctx.send(f"Ahem! You can't just leave the {guild.name}. This server is necessary for bot")

        def check(message: discord.Message):
            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id

        await ctx.reply(embed=discord.Embed(title="Are you sure?", description=f"Type yes if you want bot to leave **{guild.name}**. You have 30s to respond.", colour=discord.Color.blurple()))
        msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=30)
        if msg.content.lower() in ('yes', 'y', 'true', '1'):
            try:
                await self.bot.get_guild(guild_id).leave()
                await ctx.send("Left! {.name}".format(guild))
                return
            except:
                await ctx.send("Error!")
                return
        else:
            return await ctx.send("Bot will not leave server {.name} as per your request".format(guild))

    @commands.command()
    @commands.is_owner()
    async def listguild(self, ctx: commands.Context):
        """
        Get a list of server your bot is in.
        """
        list_of_guilds = ["**------------ ID ------------ : -------- Name ----------**\n"]
        for guild in self.bot.guilds:
            list_of_guilds.append(f"{guild.id} : {guild.name}")
        
        embed = discord.Embed(title="List of guilds", colour=discord.Color.blurple(), description="\n".join(list_of_guilds))
        return await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(LeaveGuildPlugin(bot))
