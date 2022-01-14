import discord
import requests
from discord.ext import commands

from requests_html import AsyncHTMLSession

import xlwt
import xlwt.Utils
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

import datetime
from datetime import date

from config import DISCORD_PREFIX


class TCGScraperCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------

    @commands.command()
    async def tcgplayer_help(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        utility = discord.Embed(
            title=f"HOW TO USE:       '{DISCORD_PREFIX}'",
            description=f"`⠀⠀⠀{DISCORD_PREFIX}tcgplayer <game> *cardlist.txt ` \n\n"
                        f"<game> is the TCG you want to search. The game options are: \n\n"
                        f"⠀⠀Yugioh \n"
                        f"⠀⠀Magic \n"
                        f"⠀⠀Vanguard \n"
                        f"⠀⠀Pokemon \n"
                        f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", inline=True, color=0x00fff7)

        utility.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        await ctx.send(embed=utility)

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def tcgplayer(self, ctx):
        game = "yugioh"

        today = date.today().strftime("%d/%m/%Y")  # todays date as dd/mm/yy
        list_path = "data/cardlists"  # points to where look for card lists
        filename = ctx.message.attachments[0].filename

        # Check message for attachment
        if not ctx.message.attachments:
            await ctx.send("There doesn't seem to be a list for me to process, please try again!")
            return

        if not ctx.message.attachments[0].url.endswith("txt"):
            await ctx.send("I don't recoginise that file type! Please make sure you are sending me a .txt file...")
            return

        # the file is in the correct format and ready to be processed
        await ctx.author.send("Your list is being processed, please wait a moment... \n")
        progress_msg = await ctx.author.send(f"Progress: 0% ")

        if ctx.message.attachments[0].url.endswith("txt"):
            processed_name = f"{filename.replace('.txt', '')}.xls"

        if ctx.message.attachments[0].url.endswith("doc"):
            processed_name = f"{filename.replace('.doc', '')}.xls"

# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------     CREATING THE WORKBOOK FORMAT     --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
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
        currency_style.num_format_str = "$#,##0.00"
        currency_style.font = currency_font

        # create style for the spacer cells
        border_style = xlwt.easyxf('alignment: horz centre;'
                                   'pattern: pattern solid, fore_colour border grey;'
                                   'borders: left thin, right thin, top thin, bottom thin;')

        paypal = "https://www.paypal.com/donate?hosted_button_id=JNDLMJBNZQQ3N"
        sheet.write(0, 0, xlwt.Formula('HYPERLINK("%s";"CLICK HERE FOR DONATION LINK")' % paypal), column_style)
        sheet.write(2, 0, today, header_style)
        for i in range(0, 5):
            sheet.row(i).height = 18 * 20
        sheet.write(4, 0, "Card", header_style)
        sheet.write(4, 1, "Quantity", header_style)
        sheet.write(4, 2, "Rarity", header_style)
        sheet.write(4, 3, "Set", header_style)
        sheet.write(4, 4, "Prices", header_style)
        sheet.write(4, 5, "Total", header_style)
        sheet.write(4, 6, "URL", header_style)
        sheet.write(4, 9, "REMOVED CARDS", header_style)

        # This section changes the width of some columns so they're always as big as they need to be
        sheet.col(1).width = (len("Quantity") + 10) * 256
        sheet.col(2).width = (len("Rarity") + 10) * 256
        sheet.col(3).width = (len("Set") + 10) * 256
        sheet.col(4).width = (len("Prices") + 10) * 256
        sheet.col(5).width = (len("Total") + 10) * 256
        sheet.col(6).width = (len("URL") + 10) * 256
        sheet.col(9).width = (len("REMOVED THINGS") + 15) * 256

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
        async with ctx.typing():
            with open(f"{list_path}/{filename}", "wb") as file:
                # discord link for attachment
                url = ctx.message.attachments[0].url
                # request file from discord
                file_request = requests.get(url)
                # write sent discord file to text file on server
                file.write(file_request.content)

            # open text file of the card list
            file = open(f"{list_path}/{filename}", "r")
            # creating your python list from file
            with file as card_list:
                # reading each line and adding it to list
                cards = [line.strip() for line in card_list]
                removed_cards = []
                for card in reversed(cards):
                    # removes empty spaces
                    if card == "":
                        cards.remove(card)
                        continue
                    if "monster" in card.lower():
                        cards.remove(card)
                        continue
                    if "spells" in card.lower():
                        cards.remove(card)
                        continue
                    if "trap" in card.lower():
                        cards.remove(card)
                        continue
                    if "extra" in card.lower():
                        cards.remove(card)
                        continue
                    if "side" in card.lower():
                        cards.remove(card)
                        continue

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
            product_data = []
            processed_cards = []
            list_data = []
            card_data = []
            quantity_data = []
            price_data = []
            set_data = []
            similarity_data = []
            lowest_prices = []
            longest_card = 0
            progress = 0

            # for loop to cycle through each card in the list
            for c in cards:
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

                card = card.replace(" ", "%20")
                card = card.replace("&", "%26")
                new_card = card.replace("%20", " ")
                new_card = new_card.replace("%26", "&")
                list_data.append(new_card)
                card_data.append(card)
                quantity_data.append(int(quantity))

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
                # code for scraping tcgplayer using bs4
                for card in reversed(card_data):
                    session = AsyncHTMLSession()
                    URL = f"https://www.tcgplayer.com/search/{game}/product?productLineName={game}&q={card}&view=grid"
                    page = await session.get(URL)
                    await page.html.arender()
                    soup = BeautifulSoup(page.html.raw_html, 'lxml')

                    data_set = soup.find_all(
                        'section', {'class': 'search-result__product'})
                    for data in data_set:
                        try:
                            title = data.find(
                                'span', {'class': 'search-result__title'}).text
                        except:
                            continue
                        try:
                            set = data.find(
                                'section', {'class': 'search-result__rarity'}).text
                        except:
                            continue
                        try:
                            price = data.find(
                                'span', {'class': 'search-result__market-price--value'}).text
                        except:
                            continue

                        product_data.append(title)
                        set_data.append(set)
                        price_data.append(price)

                    if not product_data:
                        # if there is no product data, the loop restarts (website doesn't load in time)
                        continue

                    # a small loop to eliminate unwanted products
                    excluded_words = ['playmat', 'sleeves', 'field center', 'folder']
                    for product in product_data:
                        for word in excluded_words:
                            if word in product.lower():
                                product_data.pop()
                                set_data.pop()
                                price_data.pop()

                    rarity = []
                    set_code = []
                    for i in set_data:
                        rarity.append(i.split()[0])
                        full_set = i.split()[-1]
                        full_set = full_set.replace("#", "")
                        full_set = full_set.replace("-", " ")
                        set_code.append(full_set.split()[0])

                    # a small loop to remove cards that do not match sufficiently
                    for product in product_data:
                        Str1 = new_card.lower()
                        Str2 = product.lower()
                        similarity_ratio = fuzz.token_sort_ratio(Str1, Str2)
                        similarity_data.append(similarity_ratio)

                        lowest = min(similarity_data)
                        if lowest < 80:
                            product_data.pop()
                            set_data.pop()
                            price_data.pop()
                            similarity_data.pop()

                    # loop to split the price from the currency symbol and convert to float
                    for i, price in enumerate(price_data):
                        price = price.replace(",", "")
                        price = float(price.replace("$", ""))
                        price_data[i] = price

                    # if statement to find longest card name for column width later
                    try:
                        if longest_card < len(max(product_data, key=len)):
                            longest_card = len(max(product_data, key=len))
                    except ValueError:
                        removed_cards.append(new_card)
                        continue

                    # loop to convert the price to floats
                    for i in range(0, len(price_data)):
                        price_data[i] = float(price_data[i])
                    try:
                        lowest_prices.append(min(price_data))

                    except ValueError:
                        removed_cards.append(new_card)
                        continue

                    # progress tracking and message update
                    content = f"Progress: {progress}%"
                    increment = 100 / (len(cards) + 1)
                    progress = round(progress + increment, 2)
                    await progress_msg.edit(content=content)

    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
                    # inputting all of the data into the .xls file
                    stuff = True
                    quantity_cell = xlwt.Utils.rowcol_to_cell(row, column + 1)
                    if stuff == True:
                        sheet.write(row, column + 1, quantity, column_style)
                        sheet.write(row, column + 6, xlwt.Formula('HYPERLINK("%s";"Card Link")' % URL), column_style)
                        for i in range(len(set_data)):
                            price_cell = xlwt.Utils.rowcol_to_cell(row, column + 4)
                            try:
                                sheet.write(row, column + 1, "", column_style)
                                sheet.write(row, column + 6, "", column_style)
                            except:
                                pass
                            sheet.write(row, column, product_data[i], column_style)
                            sheet.write(row, column + 2, rarity[i], column_style)
                            sheet.write(row, column + 3, set_code[i], column_style)
                            sheet.write(row, column + 4, price_data[i], currency_style)
                            sheet.write(row, column + 5, xlwt.Formula(f"({quantity_cell}*{price_cell})"), currency_style)
                            sheet.row(row).height = 18 * 18
                            row += 1
                        for j in range(7):
                            sheet.write(row, column + j, "", border_style)
                            sheet.row(row).height = 18 * 14
                        row += 1

                    card_data.remove(card)
                    processed_cards.append(card)
                    similarity_data.clear()
                    product_data.clear()
                    set_data.clear()
                    price_data.clear()

        # adding the price to the bottom of the spreadsheet
        lowest_price = 0
        for i in range(len(lowest_prices)):
            lowest_price = lowest_price + (lowest_prices[i] * quantity_data[i])

        # adding the price to the bottom of the spreadsheet
        sheet.write(row + 1, column, "Lowest Price", price_style)
        sheet.write(row + 2, column, lowest_price, currency_style)
        sheet.row(row + 1).height = 18 * 20
        sheet.row(row + 2).height = 18 * 20

        row = 4
        for i in range(len(removed_cards)):
            sheet.row(row).height = 18 * 20
            sheet.write(row, column + 9, removed_cards[i], column_style)
            row += 1
        try:
            removed_width = (len(max(removed_cards, key=len)) + 10) * 256
            if removed_width > (len("REMOVED THINGS") + 15) * 256:
                sheet.col(column + 9).width = removed_width
        except ValueError:
            sheet.col(9).width = (len("REMOVED THINGS") + 15) * 256

        # change product column to longest card width for main data
        column_width = (longest_card + 10) * 256
        sheet.col(column).width = column_width  # edits just the "Card" columns width

        # save updated xls file
        workbook.save(f"{list_path}/{processed_name}")

        # send final file to user who triggered the command
        await progress_msg.edit(content="Processed: 100%")
        await ctx.author.send(file=discord.File(f"{list_path}/{processed_name}"))

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @tcgplayer.error
    async def tcgplayer_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(f" <@!{ctx.author.id}>, please add a game onto your command, for example: \n \n "
                                  f"$tcgplayer yugioh      or       $tcgplayer pokemon")
