import asyncio
from discord.ext import commands
import discord
from core import checks
from core.models import PermissionLevel
import re

class AutoReplyCog(commands.Cog):
  """
  Manage auto responses for your threads. 
  These responses support [python regex](https://www.w3schools.com/python/python_regex.asp) and use re.search function to search content.
  Plugin converts the message context in lowercase so you do not have worry about lower or upper case while creating your regex.
  """
  def __init__(self, bot):
    self.bot: commands.Bot = bot
    self.db = bot.plugin_db.get_partition(self)
    self.auto_replies = {}
    asyncio.create_task(self._get_all_db_())
  
  async def _get_all_db_(self):
    db = await self.db.find_one({ '_id': 'config'})
    if db is None:
      await self.db.find_one_and_update(
        {"_id": "config"},
        {"$set": {"auto_reply": dict()}},
        upsert=True,
      )
      return

    for regex, content in db.get('auto_reply', {}).items():
      if regex in self.auto_replies:
        continue
      self.auto_replies[str(regex)] = content

  async def _update_db_(self):
    await self.db.find_one_and_update(
      {"_id": "config"},
      {"$set": {"auto_reply": self.auto_replies}},
      upsert=True,
    )
  
  @commands.command(name="addautoreply", aliases=['aar'])
  @checks.has_permissions(PermissionLevel.OWNER)
  async def add_auto_reply(self, ctx: commands.Context, regex: str, *, content: str):
    """
    Add regex if match with the context then bot will send auto response.
    """
    self.auto_replies[str(regex)] = content
    await self._update_db_()
    embed = discord.Embed(colour=0x36393E, description=f"Added snippet **{regex}** in bot database.")
    return await ctx.reply(embed=embed)

  @commands.command(name="listautoreply", aliases=['lar'])
  @checks.has_permissions(PermissionLevel.OWNER)
  async def list_auto_reply(self, ctx: commands.Context):
    """
    List all the snippets available in your bot.
    """
    desc = "**All the snippets available in the bot.**\n\n"
    desc += ", ".join(map(lambda x: f"`{x}`", self.auto_replies.keys()))

    embed = discord.Embed(colour=discord.Color.blurple(), description=desc)
    return await ctx.reply(embed=embed)

  @commands.command(name="editautoreply", aliases=['ear'])
  @checks.has_permissions(PermissionLevel.OWNER)
  async def edit_auto_reply(self, ctx: commands.Context, regex: str, *, new_content: str):
    """
    Edit the pre-existing auto-response.
    """
    if regex not in self.auto_replies.keys():
      return await ctx.reply(f"Key {regex} is not available in our database. Use command `{ctx.prefix}addautoreply` to add it")
    try:
      self.auto_replies[regex] = new_content
      await self._update_db_()
      return await ctx.reply("Done!")
    except:
      return await ctx.reply("Some sort of error occured while running the command. Please contact Shashank#3736 for solution.")

  @commands.command(name="deleteautoreply", aliases=['dar'])
  @checks.has_permissions(PermissionLevel.OWNER)
  async def delete_auto_reply(self, ctx: commands.Context, regex: str):
    """
    Delete a snippet from your database.
    """
    if regex not in self.auto_replies.keys():
      return await ctx.reply(f"{regex} is not available in database. Please check the name and try again!")

    try:
      del self.auto_replies[regex]
      await self._update_db_()
      return await ctx.reply("Done!")
    except:
      return await ctx.reply("Some sort of error occured while running the command. Please contact Shashank#3736 for solution.")    

  @commands.Cog.listener()
  async def on_thread_reply(self, thread, from_mod, message, anonymous, plain):
    if from_mod:
      return

    for key in self.auto_replies.keys():
      is_present = re.search(key, message.content.lower())

      if is_present:
        message.content = self.auto_replies[key]
        message.content += "\n\n> Response is auto generated so it may not be that helpful. Please patiently wait for staff response."
        message.author = self.bot.modmail_guild.me
        await thread.reply(message,anonymous=True)
        break

def setup(bot: commands.Bot):
  bot.add_cog(AutoReplyCog(bot))
