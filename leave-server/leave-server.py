import discord
from discord.ext import commands
from discord.ext.commands.errors import GuildNotFound

class GuildConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, guild_id: str):
        guild = None
        try:
            guild_id = int(guild_id)
            guild = ctx.bot.get_guild(guild_id)
        except:
            pass

        if guild is None:
            guild = discord.utils.find(lambda x: x.name.lower().__contains__(str(guild_id).lower()), ctx.bot.guilds)

        if guild is None:
            raise GuildNotFound(guild_id)
        return guild

class LeaveGuildPlugin(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, guild: GuildConverter):
        """
        Force your bot to leave a specified server
        """
        if guild.id in (self.bot.modmail_guild.id, self.bot.guild.id):
            return await ctx.send(f"Ahem! You can't just leave the {guild.name}. This server is necessary for bot")

        def check(message: discord.Message):
            return message.author.id == ctx.author.id and message.channel.id == ctx.channel.id
        try:
            await ctx.reply(embed=discord.Embed(title="Are you sure?", description=f"Type `yes` if you want bot to leave **{guild.name}** or type `cancel` if you want bot to not leave the server.", colour=discord.Color.blurple()))
            msg: discord.Message = await self.bot.wait_for("message", check=check, timeout=30)
            if msg.content.lower() in ('yes', 'y', 'true', '1'):
                try:
                    await guild.leave()
                    await ctx.send("Left! {.name}".format(guild))
                    return
                except:
                    await ctx.send("Error!")
                    return
            else:
                return await ctx.send("Bot will not leave server {.name} as per your request".format(guild))
        except TimeoutError:
            return await ctx.send("OOps timeup bot will not leave the server.")

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
