# wstools

`wstools` is a small Python package for Weiss Schwarz workflows:

- fetch decklists from EncoreDecks
- scrape card sale data from NovaTCG and Yuyutei
- scrape card text metadata from Heart of the Cards
- generate printable proxy images from EncoreDecks card art

## Setup

```powershell
uv sync --dev
uv run prek install
```

## Discord Bot

Create a `config.json` in the repo root:

```json
{
  "DISCORD_TOKEN": "your-bot-token",
  "GUILDS": [123456789012345678],
  "RATE_LIMIT_EXEMPT_USER_IDS": [123456789012345678]
}
```

Run the bot:

```powershell
uv run wstools-bot --config-path config.json
```

Run the bot in Docker:

```bash
scripts/deploy.sh
```

The Docker deploy script will:

- build the image from [Dockerfile](/home/dyreatic/Projects/wstools/Dockerfile)
- pull the latest repo changes with `git pull --ff-only`
- replace any existing `wstools-bot` container
- start the bot detached with `--restart always`
- mount `config.json` into the container at `/app/config.json`

Useful options:

- `--config-path /absolute/path/to/config.json` to use a config outside the repo root
- `--container-name ws-bot` to use a different container name
- `--image-name ws-bot` to tag the built image differently
- `--skip-pull` to deploy without pulling the latest Git changes first
- `--skip-prune` to keep old dangling images

`scripts/deploy_bot_docker.sh` remains as a compatibility wrapper around `scripts/deploy.sh`.

Stop a Docker-deployed bot:

```bash
scripts/kill_bot_docker.sh
```

Useful options:

- `--container-name ws-bot` to stop a non-default container
- `--remove-image --image-name ws-bot:prod` to remove the built image after stopping the container

The bot registers a slash command:

```text
/generate_proxy deck_code:<EncoreDecks code>
```

It generates the deck PDF and uploads it back to Discord.
Users listed in `RATE_LIMIT_EXEMPT_USER_IDS` bypass the `/generate_proxy` cooldown.

## Usage

Generate one proxy image per unique card in an EncoreDecks list:

```powershell
uv run wstools proxy-deck X6LSRnhEL
```

Generate one proxy image for a single card:

```powershell
uv run wstools proxy-card PAD/S105-001
```

Choose a different output path:

```powershell
uv run wstools proxy-card PAD/S105-001 --output-file generated\proxies\pad-001.png
```

Choose a different output directory:

```powershell
uv run wstools proxy-deck X6LSRnhEL --output-dir generated\my-deck
```

Generate a printable letter-size PDF with 5 pages of 5x2 proxies:

```powershell
uv run wstools proxy-pdf X6LSRnhEL
```

Choose a different output path:

```powershell
uv run wstools proxy-pdf X6LSRnhEL --output-file generated\pdfs\my-deck.pdf
```

## Project Layout

- `src/wstools/cli.py`: command-line entrypoint
- `src/wstools/models.py`: core card and deck data models
- `src/wstools/providers/`: data providers for decklists, card metadata, and prices
- `src/wstools/proxy/render.py`: image rendering and print-sheet utilities
- `tests/`: smoke tests for the cleaned package

## Notes

- Proxy generation works best when `NotoSansJP-Regular.ttf` is available in `src/wstools/assets/`.
- Generated images are written under `generated/` by default and are gitignored.
- Printable PDFs use letter landscape pages with 0.25" outer margins, 0.125" gutters, and 2.0" x 2.8" card images.
- Proxy overlay text is slightly oversized to preserve readability after PDF downscaling.
