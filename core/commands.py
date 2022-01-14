import os
import discord

from discord.ext import commands
from datetime import datetime
from datetime import date

from config import DISCORD_PREFIX, INVITE_URL, discord_client
from discord_components import Button


class TCGPlayerBotCore(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged on as', self.bot.user)
        servers_total = str(len(self.bot.guilds))

        # creating the necessary directories
        try:
            os.makedirs("data")
        except FileExistsError:
            pass
        try:
            os.makedirs("data/cardlists")
        except FileExistsError:
            pass
        try:
            os.makedirs("data/logs")
        except FileExistsError:
            pass
        try:
            os.makedirs("data/ygo_images")
        except FileExistsError:
            pass

        # await self.bot.change_presence(activity=discord.Game(name="Type $help"))
        await self.bot.change_presence(activity=discord.Game(name=f"{DISCORD_PREFIX}help"))

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def help(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        invite = [Button(id="invite", label="Invite", style=5, url=INVITE_URL)]

        help_embed = discord.Embed(
            title="HELP",
            description=f"Hello! I am your friendly Yugioh Bot!I have a selection of commands that will \n"
                        f"You may also use $'command'_help for more information \n"
                        f"", inline=True, color=0x00fff7)

        help_embed.add_field(name="Commands", value=f"{DISCORD_PREFIX}example \n"
                                              f"{DISCORD_PREFIX}ebay \n"
                                              f"{DISCORD_PREFIX}cardmarket \n"
                                              f"{DISCORD_PREFIX}tcgplayer \n"
                                              f"{DISCORD_PREFIX}info \n")

        help_embed.add_field(name="Functions", value="Sends user a text file in the correct format \n"
                                               "Searches ebay for your card list \n"
                                               "Searches carkmarket for your card list \n"
                                               "Search TCGPlayer for your card list \n"
                                               "Using $info <cardname> will show an image of the card \n")

        help_embed.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        await ctx.send(embed=help_embed, components=invite)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def support(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        support = discord.Embed(
            title="How to Support",
            description=f"Hey! Making Bots takes a lot of time and effort! If you would like to support my existence"
                        "in some capacity, I would greatly appreciate it!"
                        f"", inline=True, color=0x00fff7)
        support.add_field(name="Wallets", value=f"```Coinbase Wallet: 0x94CCC7691a9d9a50F3c27fd3174Ff04905bF3583 \n"
                                                "BTC: bc1q22l6cwzfwuevt50npx5fjhpa8smhcr9llr4hwh \n"
                                                "ETH: 0x7A3bdb7B964893c252Ae70B5ACdB496fF71555bf \n"
                                                "BNB: bnb16cmy4mts8ea6k2mz49ygfx4nq8rdtswuc5zfc6 \n"
                                                "BCH: qzyr8gm9m0g9gj87fyjhn7zuuw3yv9rsm57gn8jpf0 \n"
                                                "LTC: LTYfjjN9acJyNUrY5hk9u7MihJ1c2EHUYD```")

        #support.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        await ctx.send(embed=support)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.Cog.listener(name='on_command')
    async def on_command(self, ctx):
        user = ctx.author
        command = ctx.command
        try:
            today = date.today().strftime("%d-%m-%Y")
            time = datetime.now().time().strftime("%H:%M:%S")
            server = ctx.guild.name

            log_file = open(f"data/logs/{today}.txt", 'a')
            log_file.write(f"{time} -> {user} used {command} in {server} \n")
            return
        except AttributeError:
            server = "DMs"
            with open(f"data/logs/{today}.txt", 'a') as log_file:
                log_file.write(f"{time} -> {user} used {command} in {server} \n")
                return

    @commands.Cog.listener(name='on_command_error')
    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            return


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------

def setup(bot):
    bot.add_cog(TCGPlayerBotCore(bot))
