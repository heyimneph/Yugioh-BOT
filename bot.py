from config import discord_client, DISCORD_TOKEN


def main():
    cogs = [
        "core.commands",
        "cogs.scrapers"
    ]
    for ext in cogs:
        print(f"Loading {ext}...")
        discord_client.load_extension(ext)
    print(f"Found {len(cogs)} cogs. Starting Bot...")
    discord_client.run(DISCORD_TOKEN)

if __name__ == '__main__':
    main()
