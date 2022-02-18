import os

import discord
from discord.ext import commands
from cogs.loader import Loader
from color_game.cogs.color_game_cog import ColorGame

from utils.logger import create_logger
from utils.secret import get_json_dict_from_secret_resource_id


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
        ColorGame(
            bot=archive_bot,
            logger=logger,
            channel_name="01-color-game",
        )
    )
    archive_bot.run(discord_token)


if __name__ == "__main__":
    main()
