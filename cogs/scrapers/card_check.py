import discord
import datetime

from discord.ext import commands
from datetime import date

from core.utils import yugioh_image, yugioh_prices, yugioh_check


class CardCheckCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def info(self, ctx, *, card):
        if not yugioh_check(card):
            await ctx.send(f"'{card}' wasn't recoginised!")
            return

        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        img_path = yugioh_image(card)

        card_data = discord.Embed(title=f"Searched:     '{card}'", color=0x00fff7)
        card_data.add_field(name="Website", value=f"eBay \n"
                                           f"Cardmarket \n"
                                           f"TCGPlayer \n")

        card_data.add_field(name="Prices", value=f"£{yugioh_prices(card)[2]} \n"
                                           f"€{yugioh_prices(card)[0]} \n"
                                           f"${yugioh_prices(card)[1]} \n")

        card_data.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        file = discord.File(img_path, filename="image.jpeg")
        card_data.set_image(url=f"attachment://image.jpeg")
        await ctx.send(file=file, embed=card_data)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------


