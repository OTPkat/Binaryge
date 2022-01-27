import os

import discord
from discord.ext import commands
from cogs.loader import Loader
from cogs.matchmaking import MatchMaking
from cogs.match_handler import MatchHandler


from src.logger import create_logger
from src.secret import get_json_dict_from_secret_resource_id


def main():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-creds.json"
    discord_secret_resource_id = "projects/148433842428/secrets/binaryge-discord-token/versions/1"
    discord_secret = get_json_dict_from_secret_resource_id(discord_secret_resource_id)
    logger = create_logger()
    intents = discord.Intents.default()  # Allow the use of custom intents
    intents.members = True

    discord_token = discord_secret["api_key"]

    archive_bot = commands.Bot(
        command_prefix="!",
        intents=intents
    )

    archive_bot.add_cog(
        Loader(
            bot=archive_bot,
            logger=logger
        )
    )

    archive_bot.add_cog(
        MatchHandler(
            bot=archive_bot,
            logger=logger,
        )
    )

    archive_bot.add_cog(
        MatchMaking(
            bot=archive_bot,
            logger=logger,
            category_name="binaryge",
            channel_name="bynaryge-matchmaking",
        )
    )
    archive_bot.run(discord_token)


if __name__ == "__main__":
    main()
