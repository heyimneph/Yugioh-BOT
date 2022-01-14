
import datetime, time
import discord
import psutil


from discord.ext import commands
from core.utils import uptime_full

start_time = time.time()
class UtilitiesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    def uptime_stat(self):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        return text
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------

    @commands.command()
    async def stats(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        servers = len(self.bot.guilds)
        channels = len(list(self.bot.get_all_channels()))
        users = len(list(self.bot.get_all_members()))
        ping = round(self.bot.latency * 1000)
        commands = len(list(self.bot.commands))
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        avatar = self.bot.user.avatar_url
        online = self.uptime_stat()

        stats = discord.Embed(
            title="The Machine's Help Page ",
            description=f"Creator = `neph#2791` \n", inline=True,
            color=0x00fff7
        )
        stats.set_thumbnail(url=avatar)
        stats.add_field(name="🏡 Servers", value=f"┕ `{servers}` \n")
        stats.add_field(name="💬 Channels", value=f"┕ `{channels}` \n")
        stats.add_field(name="👥 Users", value=f"┕ `{users}` \n")
        stats.add_field(name="🏓 Ping", value=f"┕ `{ping}ms` \n")
        stats.add_field(name="🪄 Commands", value=f"┕ `{commands}` \n")
        stats.add_field(name="🌐 Language", value=f"┕ `Python` \n")
        stats.add_field(name="🐱‍💻 CPU", value=f"┕ `{cpu}%` \n")
        stats.add_field(name="💾 Memory", value=f"┕ `{memory}%` \n")
        stats.add_field(name="⏳ Uptime", value=f"┕ `{online}` \n")

        stats.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)

        await ctx.send(embed=stats)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def uptime(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url
        online = uptime_full()
        uptime = discord.Embed(
            title="⏳ Uptime ⏳ ",
            description=f"{online}", inline=True,
            color=0x00fff7)

        uptime.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)

        await ctx.send(embed=uptime)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
