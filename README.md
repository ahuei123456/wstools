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
  "GUILDS": [123456789012345678]
}
```

Run the bot:

```powershell
uv run wstools-bot --config-path config.json
```

The bot registers a slash command:

```text
/generate_proxy deck_code:<EncoreDecks code>
```

It generates the deck PDF and uploads it back to Discord.

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
