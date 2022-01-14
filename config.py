import os
import discord


from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

# Loads the .env file that resides on the same level as the script
load_dotenv("config.env.txt")

# Grab the API token from the .env file
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

# Discord
DISCORD_PREFIX = "$"
intents = discord.Intents.all()

# Other External Keys
INVITE_URL = "https://discord.com/api/oauth2/authorize?client_id=924445224170819614&permissions=34816&scope=bot"
LAUNCH_TIME = datetime.utcnow()


# Login Clients
discord_client = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents, help_command=None)

