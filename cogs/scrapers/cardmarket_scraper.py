import discord
import requests
import xlwt
import xlwt.Utils

import datetime
from bs4 import BeautifulSoup
from discord.ext import commands
from fuzzywuzzy import fuzz
from datetime import date


class CardMarketScraperCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @commands.command()
    async def cardmarket_help(self, ctx):
        date_raw = datetime.datetime.utcnow()  # time at which message was sent
        date = date_raw.strftime(f"%d/%m/%Y")  # converts date to string
        time = date_raw.strftime("%H:%M ")  # converts time to string
        avatar = self.bot.user.avatar_url

        utility = discord.Embed(
            title="HOW TO USE:       '$cardmarket'",
            description=f"`⠀⠀⠀$cardmarket <game> *cardlist.txt ` \n\n"
                        f"<game> is the TCG you want to search. The game options are: \n\n"
                        f"⠀⠀Yugioh \n"
                        f"⠀⠀MTG \n"
                        f"⠀⠀Vanguard \n"
                        f"⠀⠀Pokemon \n"
                        f"⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", inline=True, color=0x00fff7)

        utility.set_footer(text=f"Time: {time} Date: {date}", icon_url=avatar)
        await ctx.send(embed=utility)

    @commands.command()
    async def cardmarket(self, ctx):
        today = date.today().strftime("%d/%m/%Y")  # todays date as dd/mm/yy
        list_path = "data/cardlists"  # points to where look for card lists
        filename = ctx.message.attachments[0].filename

        games = ["yugioh", "magic", "vanguard", "pokemon"]

        game = "yugioh"

        if game not in games:
            await ctx.send("I don't recognise that game, please use 'yugioh', 'magic', 'pokemon' or 'vanguard'")
            return

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
        currency_style.num_format_str = f"#,##€0.00"
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
        sheet.write(4, 2, "Set Code", header_style)
        sheet.write(4, 3, "Prices", header_style)
        sheet.write(4, 4, "URL", header_style)
        sheet.write(4, 7, "REMOVED CARDS", header_style)

        # This section changes the width of some columns so they're always as big as they need to be
        sheet.col(1).width = (len("Quantity") + 10) * 256
        sheet.col(2).width = (len("Set Code") + 10) * 256
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
                product_data = []
                card_data = []
                quantity_data = []
                price_data = []
                lowest_prices = []
                url_data = []
                set_data = []
                similarity_data = []
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

                    card = card.replace(" ", "+")
                    new_card = card.replace("+", ' ')
                    card_data.append(new_card)
                    quantity_data.append(int(quantity))

                    # progress tracking and message update
                    content = f"Progress: {progress}%"
                    increment = 100 / (len(cards) + 1)
                    progress = round(progress + increment, 1)
                    await progress_msg.edit(content=content)

        # ----------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------
                    # code for scraping ebay using bs4
                    URL = f"https://www.cardmarket.com/en/{game}/Products/Singles?idCategory=5&idExpansion=0&searchString={card}&idRarity=0"
                    url_data.append(URL)
                    page = requests.get(URL)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    data = soup.find_all('div', {'class': 'row no-gutters'})

                    for i in data:
                        try:
                            (i['id'])
                        except:
                            continue

                        st = i.find_all('div')
                        data = []
                        for s in st:
                            data.append(s.text)
                        # data 3 = product name
                        product_data.append(data[3])
                        # data 2 = set code
                        set_data.append(data[2])
                        # data -1 = pricing
                        price_data.append(data[-1])
                        # print(data_[-2])

                        # a small loop to eliminate unwanted sets
                        excluded_sets = ['PROM', 'YGPR']
                        if any(x in set_data for x in excluded_sets):
                            product_data.pop()
                            set_data.pop()
                            price_data.pop()

                        # a small loop to elimate unwanted products
                        excluded_words = ['playmat', 'sleeves', 'field center']
                        for product in product_data:
                            for word in excluded_words:
                                if word in product.lower():
                                    product_data.pop()
                                    set_data.pop()
                                    price_data.pop()


                        # loop to split the price from the currency symbol and convert to int
                        for i, price in enumerate(price_data):
                            price = price.split(" ")[0].replace(",", ".")
                            price_data[i] = price

                        # if statement to find longest card name for column width later
                        if longest_card < len(max(product_data, key=len)):
                            longest_card = len(max(product_data, key=len))

                    # loop to remove the set number from the card names
                    for i, product in enumerate(product_data):
                        product = product[:-3]
                        product_data[i] = product

                    for product in product_data:
                        Str1 = new_card.lower()
                        Str2 = product.lower()
                        similarity_ratio = fuzz.token_sort_ratio(Str1, Str2)
                        similarity_data.append(similarity_ratio)

                        lowest = min(similarity_data)
                        if lowest < 60:
                            product_data.pop()
                            set_data.pop()
                            price_data.pop()
                            similarity_data.pop()

                    # loop to convert the price to floats
                    for i in range(0, len(price_data)):
                        price_data[i] = float(price_data[i])

                    try:
                        lowest_prices.append(min(price_data))

                    except ValueError:
                        removed_cards.append(new_card)
                        continue
        # ----------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------
                    # inputting all of the data into the .xls file
                    stuff = True
                    if stuff == True:
                        sheet.write(row, column + 1, quantity, column_style)
                        sheet.write(row, column + 4, xlwt.Formula('HYPERLINK("%s";"Card Link")' % URL), column_style)
                        for i in range(len(set_data)):
                            try:
                                sheet.write(row, column + 1, "", column_style)
                                sheet.write(row, column + 4, "", column_style)
                                sheet.row(row).height = 18 * 18
                            except:
                                pass
                            sheet.write(row, column, product_data[i], column_style)
                            sheet.write(row, column + 2, set_data[i], column_style)
                            sheet.write(row, column + 3, f"€{'{:.2f}'.format(price_data[i])}", currency_style)
                            sheet.row(row).height = 18 * 18
                            row += 1
                        for j in range(5):
                            sheet.write(row, column + j, "", border_style)
                            sheet.row(row).height = 18 * 14
                        row += 1
                    similarity_data.clear()
                    set_data.clear()
                    price_data.clear()
                    product_data.clear()

            # adding the price to the bottom of the spreadsheet
            lowest_price = 0
            for i in range(len(lowest_prices)):
                lowest_price = lowest_price + (lowest_prices[i] * quantity_data[i])

            sheet.write(row + 1, column, "Lowest Price", price_style)
            sheet.write(row + 2, column, f"€{'{:.2f}'.format(lowest_price)}", currency_style)
            sheet.row(row + 1).height = 18 * 20
            sheet.row(row + 2).height = 18 * 20

            # for loop to add "removed cards" to the xls file
            row = 5
            for i in range(len(removed_cards)):
                sheet.row(row).height = 18 * 20
                sheet.write(row, column + 7, removed_cards[i], column_style)
                row += 1
            try:
                removed_width = (len(max(removed_cards, key=len)) + 10) * 256
                if removed_width > (len("REMOVED THINGS") + 15) * 256:
                    sheet.col(column + 7).width = removed_width
            except ValueError:
                sheet.col(7).width = (len("REMOVED THINGS") + 15) * 256

            try:
                if longest_card > len("CLICK HERE TO DONATE"):
                    sheet.col(0).width = (longest_card +15) * 256
                else:
                    sheet.col(column).width = (len("CLICK HERE TO DONATE") + 15) * 256 # edits just the "Card" columns width
            except ValueError:
                sheet.col(0).width = (len("CLICK HERE TO DONATE") + 15) * 256

            # save updated xls file
            workbook.save(f"{list_path}/{processed_name}")

            # send final file to user who triggered the command
            await progress_msg.edit(content="Processed: 100%")
            await ctx.author.send(file=discord.File(f"{list_path}/{processed_name}"))

#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
#  ---------------------------------------------------------------------------------------------------------------------
    @cardmarket.error
    async def cardmarket_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.author.send(f" <@!{ctx.author.id}>, please add a game onto your command, for example: \n \n "
                                  f"$cardmarket yugioh      or       $cardmarket pokemon")