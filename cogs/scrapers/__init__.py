from cogs.utility.utility_cog import UtilitiesCog
from .ebay_scraper import EbayScraperCog
from .cardmarket_scraper import CardMarketScraperCog
from .tcgplayer_scraper import TCGScraperCog
from .card_check import CardCheckCog


def setup(bot):
    bot.add_cog(UtilitiesCog(bot))
    bot.add_cog(EbayScraperCog(bot))
    bot.add_cog(CardMarketScraperCog(bot))
    bot.add_cog(TCGScraperCog(bot))
    bot.add_cog(CardCheckCog(bot))
