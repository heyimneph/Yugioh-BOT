import discord

import requests
import xlwt
import datetime
from discord.ext import commands
from bs4 import BeautifulSoup
from re import sub
from decimal import Decimal
from datetime import date
from config import DISCORD_PREFIX

from core.utils import reject_outliers

class EbayScraperCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def example(self, ctx):
        await ctx.author.send(file=discord.File("data/textfiles/test.txt"))

    @commands.command()
    async def ebay_help(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        utility = discord.Embed(
            title="HOW TO USE:       '$ebay'",
            description=f"⠀⠀⠀⠀⠀⠀`{DISCORD_PREFIX}ebay <keyword> <location> *cardlist.txt ` \n\n"
                        f"The keyword is likely the TCG you want to search; MTG, Yugioh etc... \n\n"
                        f"The location is optional and the options are: \n\n"
                        f"⠀⠀⠀UK = United Kingdom \n"
                        f"⠀⠀⠀US = United States \n"
                        f"⠀⠀⠀CA = Canada \n"
                        f"⠀⠀⠀AU = Austrailia \n"
                        f"⠀⠀⠀FR = France \n"
                        f"⠀⠀⠀IT = Italy \n"
                        f"⠀⠀⠀DE = Germany \n"
                        f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", inline=True, color=0x00fff7)

        utility.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        await ctx.send(embed=utility)

    @commands.command()
    async def ebay(self, ctx, region: str = None):
        game = "yugioh"
        today = date.today().strftime("%d/%m/%Y")  # todays date as dd/mm/yy
        list_path = "data/cardlists"  # points to where look for card lists
        filename = ctx.message.attachments[0].filename

        # Check message for attachment
        if not ctx.message.attachments:
            await ctx.send("There doesn't seem to be a list for me to process, please try again!")
            return

        regions = ["UK", "US", "CA", "AU", "FR", "IT", "DE"]

        if region == "UK":
            currency = "£"
        if region == "US":
            currency = "$"
        if region == "CA":
            currency = "C$"
        if region == "AU":
            currency = "AU$"
        if region == "FR":
            currency = "€"
        if region == "IT":
            currency = "€"
        if region == "DE":
            currency = "€"
        if region is None:
            region = "UK"
            currency = "£"

        if region not in regions:
            await ctx.send("Use $locations to see valid location options!")
            return

        if not ctx.message.attachments[0].url.endswith("txt"):
            await ctx.send("I don't recoginise that file type! Please make sure you are sending me a .txt file...")
            return

        # the file is in the correct format and ready to be processed
        await ctx.author.send("Your list is being processed, please wait a moment... \n")
        progress_msg = await ctx.author.send(f"Progress: 0% ")

        if ctx.message.attachments[0].url.endswith("txt"):
            processed_name = f"{filename.replace('.txt', '')}.xls"
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------     CREATING THE WORKBOOK FORMAT     --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
        print("WORKSHEET")
        # create new spreadsheet for price update of lists
        column = 0
        row = 5

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("LIST")

        xlwt.add_palette_colour("light cyan", 0x21)
        workbook.set_colour_RGB(0x21, 171, 243, 223)

        xlwt.add_palette_colour("light orange", 0x22)
        workbook.set_colour_RGB(0x22, 255, 237, 195)

        xlwt.add_palette_colour("border grey", 0x23)
        workbook.set_colour_RGB(0x23, 211, 211, 211)

        donate_font = xlwt.Font()
        donate_font.name = 'Arial'
        donate_font.height = 14 * 20  # for 14 point
        donate_font.bold = True
        donate_style = xlwt.easyxf('align: horz left;'
                                   'pattern: pattern solid, fore_colour light cyan;'
                                   'borders: left thin, right thin, top thin, bottom thin;')
        donate_style.font = donate_font

        header_font = xlwt.Font()
        header_font.name = 'Arial'
        header_font.height = 14 * 20  # for 14 point
        header_font.bold = True
        header_style = xlwt.easyxf('align: horz centre;'
                                   'pattern: pattern solid, fore_colour light cyan;'
                                   'borders: left thin, right thin, top thin, bottom thin;')
        header_style.font = header_font

        column_font = xlwt.Font()
        column_font.height = 12 * 20  # for 12 point
        column_font.name = 'Arial'
        column_style = xlwt.easyxf('alignment: horz centre;'
                                   'pattern: pattern solid, fore_colour light orange;'
                                   'borders: left thin, right thin, top thin, bottom thin;')
        column_style.font = column_font

        price_font = xlwt.Font()
        price_font.name = 'Arial'
        price_font.height = 12 * 20  # for 14 point
        price_font.bold = True
        price_style = xlwt.easyxf('align: horz centre;'
                                  'pattern: pattern solid, fore_colour light cyan;'
                                  'borders: left thin, right thin, top thin, bottom thin;')
        price_style.font = price_font

        # create style for the currency cells
        currency_font = xlwt.Font()
        currency_font.name = 'Arial'
        currency_font.height = 12 * 20
        currency_font.font = False
        currency_style = xlwt.easyxf('alignment: horz centre;'
                                     'pattern: pattern solid, fore_colour light orange;'
                                     'borders: left thin, right thin, top thin, bottom thin;')
        currency_style.num_format_str = f"{currency}#,##0.00"
        currency_style.font = currency_font

        # create style for the spacer cells
        border_style = xlwt.easyxf('alignment: horz centre;'
                                   'pattern: pattern solid, fore_colour border grey;'
                                   'borders: left thin, right thin, bottom thin')

        paypal = "https://www.paypal.com/donate?hosted_button_id=YANRHRJ5G2CMJ"
        sheet.write(0, 0, xlwt.Formula('HYPERLINK("%s";"CLICK HERE FOR DONATION LINK")' % paypal), column_style)
        sheet.write(2, 0, today, header_style)

        for i in range(0, 5):
            sheet.row(i).height = 18 * 20

        sheet.write(4, 0, "Card", header_style)
        sheet.write(4, 1, "Quantity", header_style)
        sheet.write(4, 2, "Avg. Price", header_style)
        sheet.write(4, 3, "Prices", header_style)
        sheet.write(4, 4, "URL", header_style)
        sheet.write(4, 7, "REMOVED CARDS", header_style)

        # This section changes the width of some columns so they're always as big as they need to be
        sheet.col(1).width = (len("Quantity") + 10) * 256
        sheet.col(2).width = (len("Avg. Price") + 10) * 256
        sheet.col(3).width = (len("Prices") + 10) * 256
        sheet.col(4).width = (len("URL") + 10) * 256
        sheet.col(7).width = (len("REMOVED THINGS") + 15) * 256
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
        # Makes the bot look like it's typing so you know it's working
        async with ctx.typing():
            with open(f"{list_path}/{filename}", "wb") as file:
                # discord link for attachment
                url = ctx.message.attachments[0].url
                # request file from discord
                file_request = requests.get(url)
                # write sent discord file to text file on server
                file.write(file_request.content)

            file = open(f"{list_path}/{filename}", "r")
            with file as card_list:
                # reading each line and adding it to list
                cards = [line.strip() for line in card_list]
                removed_cards = []
                cards.append("")
                for card in reversed(cards):
                    # removes empty spaces
                    if card == "":
                        cards.remove(card)
                        continue
                    if card.lower() == "monster:":
                        removed_cards.append(card)
                        cards.remove(card)
                        continue
                    if card.lower() == "spell:":
                        removed_cards.append(card)
                        cards.remove(card)
                        continue
                    if card.lower() == "trap:":
                        removed_cards.append(card)
                        cards.remove(card)
                        continue
                    if card.lower() == 'extra:':
                        removed_cards.append(card)
                        cards.remove(card)
                        continue
                    if card.lower() == 'side:':
                        removed_cards.append(card)
                        cards.remove(card)
                        continue

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

            total_price = []
            card_data = []
            quantity_data = []
            price_data = []
            url_data = []
            total_cards = len(cards)
            progress = 0

            # for loop to cycle through each card in the list
            for c in cards:
                # prices of the listings for each card
                prices = []
                # reset loop for limiting number of searches
                search_condition = 0

                # split the card text to check for quantities
                line = c.split()
                if 'x' in line[0]:
                    quantity = line[0].replace('x', '')
                    if quantity.isnumeric():
                        line.pop(0)
                        card = c.replace(f"{quantity}x ", '')
                    else:
                        quantity = 1

                if 'x' in line[-1]:
                    quantity = line[-1].replace('x', '')
                    if quantity.isnumeric():
                        line.pop(-1)
                        card = c.replace(f" x{quantity}", '')
                    else:
                        quantity = 1

                card = card.replace(" ", "+")
                new_card = card.replace("+", ' ')
                if region == "UK":
                    URL = f"https://www.ebay.co.uk/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "US":
                    URL = f"https://www.ebay.com/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "CA":
                    URL = f"https://www.ebay.ca/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "AU":
                    URL = f"https://www.ebay.com.au/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "FR":
                    URL = f"https://www.ebay.fr/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "ES":
                    URL = f"https://www.ebay.es/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "IT":
                    URL = f"https://www.ebay.it/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                if region == "DE":
                    URL = f"https://www.ebay.de/sch/i.html?_nkw={game}+{card}+&LH_PrefLoc=1&_sop=15&rt=nc&LH_BIN=1"
                page = requests.get(URL)
                soup = BeautifulSoup(page.content, 'html.parser')

# ----------------------------------------------------------------------------------------------------------------------
                # code for scraping ebay using bs4
                for item in soup.select('.s-item__wrapper.clearfix'):
                    title = item.select_one('.s-item__title').text
                    # things to ignore in the title of the cards e.g. playsets, multibuys etc...
                    if title == "" \
                            or 'choose' in title.lower() \
                            or 'Choose' in title.lower() \
                            or 'CHOOSE' in title.lower() \
                            or '3x' in title.lower() \
                            or '3 x' in title.lower() \
                            or 'x3' in title.lower() \
                            or 'x 3' in title.lower() \
                            or 'X 3' in title.lower() \
                            or '3 X' in title.lower() \
                            or 'deck' in title.lower() \
                            or 'playset' in title.lower() \
                            or 'PLAYSET' in title.lower() \
                            or 'singles' in title.lower() \
                            or "Single" in title.lower() \
                            or "field" in title.lower() \
                            or "PC" in title.lower() \
                            or "RC" in title.lower():
                        continue
                    try:
                        price = item.select_one('.s-item__price').text
                        # things to ignore in the price of the cards e.g. "or" -> £0.99 to £10.00
                        if 'to' in price:
                            continue
                    except:
                        price = None
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
                    if search_condition < 5:
                        search_condition += 1
                        prices.append(Decimal(sub(r'[^\d.]', '', price)))
                        price_conv = []
                        for p in prices:
                            price_conv.append(float(p))

                        if search_condition == 5:
                            outliers = reject_outliers(price_conv, 3.)
                            average = sum(outliers) / len(outliers)
                            total_price.append(average * int(quantity))

                            if total_cards != 0:
                                if progress > 100:
                                    await progress_msg.edit(content="Progress: 100%")
                                else:
                                    content = f"Progress: {progress}%"
                                    interval = (100 / (len(cards) + 1))
                                    progress = round(progress + interval, 1)
                                    await progress_msg.edit(content=content)
                                    total_cards = total_cards - 1

                            card_data.append(new_card)
                            quantity_data.append(quantity)
                            price_data.append(average)
                            url_data.append(URL)
                        continue
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
            # inputting all of the data into the .xls file
            for i in range(len(card_data)):
                quantity_cell = xlwt.Utils.rowcol_to_cell(row, column + 1)
                price_cell = xlwt.Utils.rowcol_to_cell(row, column + 2)
                sheet.row(row).height = 16 * 20
                sheet.write(row, column, card_data[i], column_style)
                sheet.write(row, column + 1, quantity_data[i], column_style)
                sheet.write(row, column + 2, price_data[i], currency_style)
                sheet.write(row, column + 3, xlwt.Formula(f"({quantity_cell}*{price_cell})"), currency_style)
                sheet.write(row, column + 4, xlwt.Formula('HYPERLINK("%s";"eBay Link")' % url_data[i]), column_style)
                row += 1

            # adding the price to the bottom of the spreadsheet
            total_cell_start = xlwt.Utils.rowcol_to_cell(3, column + 3)
            total_cell_end = xlwt.Utils.rowcol_to_cell(row - 1, column + 3)
            sheet.write(row + 1, column, "Approx. Price", price_style)
            sheet.write(row + 2, column, xlwt.Formula(f"SUM({total_cell_start}:{total_cell_end})"), currency_style)
            sheet.row(row + 1).height = 18 * 20
            sheet.row(row + 2).height = 18 * 20


        row = 5
        # for loop to add "removed cards" to the xls file
        for i in range(len(removed_cards)):
            sheet.write(row, column + 7, removed_cards[i], column_style)
            row += 1
        try:
            removed_width = (len(max(removed_cards, key=len)) + 10) * 256
            if removed_width > (len("REMOVED THINGS") + 15) * 256:
                sheet.col(column + 7).width = removed_width
        except ValueError:
            sheet.col(7).width = (len("REMOVED THINGS") + 15) * 256

        # variable to figure out largest card name and calculate column size so it's fits
        # x256 because of width size in excel
        product_width = (len(max(card_data, key=len)) + 15) * 256
        title_width = (len("CLICK HERE FOR DONATE LINK") + 15) * 256
        try:
            if product_width > title_width:
                sheet.col(0).width = product_width
            else:
                sheet.col(0).width = title_width
        except ValueError:
            sheet.col(0).width = title_width

        # save updated xls file
        workbook.save(f"{list_path}/processed/{processed_name}")
        # send final file to user who triggered the command
        await progress_msg.edit(content="Processed: 100%")
        await ctx.author.send(file=discord.File(f"{list_path}/processed/{processed_name}"))


#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @ebay.error
    async def ebay_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(f" <@!{ctx.author.id}>, please add a game onto your command, for example: \n \n "
                                  f"$ebay yugioh      or       $ebay pokemon")

