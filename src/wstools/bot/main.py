import argparse
import logging
import math
import sys
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

from wstools import config
from wstools.errors import BotCommandError

_log = logging.getLogger(__name__)
settings: dict[str, Any] = {}


class WSToolsClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        try:
            await self.load_extension("wstools.bot.cogs.proxy")
            _log.info("Extensions loaded.")
        except Exception as exc:
            _log.exception("Failed to load extensions: %s", exc)
            raise

        for guild_id in settings["GUILDS"]:
            guild = discord.Object(id=guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        _log.info("Commands synced.")


intents = discord.Intents.default()
client = WSToolsClient(intents=intents)


@client.tree.error
async def on_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    user_info = f"User: {interaction.user} ({interaction.user.id})"
    command_name = interaction.command.name if interaction.command else "Unknown"
    original_error = getattr(error, "original", error)

    match original_error:
        case app_commands.CommandOnCooldown() as exc:
            message = format_cooldown_message(exc.retry_after)
            _log.warning(
                "%s - Command '%s' hit cooldown, retry_after=%.2fs.",
                user_info,
                command_name,
                exc.retry_after,
            )
        case BotCommandError() as exc:
            message = str(exc)
            log_level = getattr(exc, "log_level", logging.INFO)
            _log.log(log_level, "%s - Handled (%s): %s", user_info, type(exc).__name__, message)
        case discord.Forbidden():
            message = "The bot lacks permissions to upload the generated PDF."
            _log.warning("%s - discord.Forbidden for command '%s'.", user_info, command_name)
        case _:
            _log.error(
                "%s - Unhandled command error for '%s': %s",
                user_info,
                command_name,
                error,
                exc_info=original_error,
            )
            message = "An unexpected error occurred while generating the proxy PDF."

    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
    except discord.HTTPException as exc:
        _log.error("%s - Failed to send error response: %s", user_info, exc)


def format_cooldown_message(retry_after: float) -> str:
    seconds = max(1, math.ceil(retry_after))
    noun = "second" if seconds == 1 else "seconds"
    return f"Rate limit hit. Please wait {seconds} {noun} before generating another proxy PDF."


@client.event
async def on_ready() -> None:
    _log.info("Logged in as %s", client.user)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="wstools Discord bot")
    parser.add_argument("--config-path", type=str, default="config.json")
    return parser.parse_args()


def main() -> None:
    global settings
    args = parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
    )
    logging.getLogger("discord").setLevel(logging.WARNING)

    try:
        config.load_config(args.config_path)
    except config.ConfigError as exc:
        _log.critical("Fatal Error: Failed to load configuration - %s", exc)
        sys.exit(1)

    settings = config.get_config()

    if not settings["DISCORD_TOKEN"]:
        _log.critical("DISCORD_TOKEN is not set")
        sys.exit(1)

    if not settings["GUILDS"]:
        _log.critical("GUILDS is not set")
        sys.exit(1)

    try:
        client.run(settings["DISCORD_TOKEN"], log_handler=None)
    except Exception as exc:
        _log.exception("Fatal error running bot: %s", exc)
        sys.exit(1)
