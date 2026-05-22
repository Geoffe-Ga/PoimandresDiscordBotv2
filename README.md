<h3> "I am Poimandres, Mind of all-masterhood; I know what thou desirest and I'm with thee everywhere." </h3>

*-The Corpus Hermeticum 1.2*

Poimandres can be called upon (with easy-to-use slash commands) to quote a variety of esoteric/occult/religious/philosophical texts:

<h4> Hermetic Texts: </h4>

> The Corpus Hermeticum

> Asclepius

> Emerald Tablet

> Definitions of Hermes to  Asclepius

> Oxford Fragments

<h4> Other: </h4>

> Bible

> Qur'an

> Book of  the Law (Liber AL vel Legis)

> Epictetus' Enchiridion

> Marcus Aurelius' Meditations

> Proclus' Elements of Metaphysics

> Sepher Yetzirah

> Yoga Sūtras of Patañjali

**Poimandres also supports Tarot card pulls from the RWS deck**

Once in your server, a full list of commands can be accessed with `/help`

---

## Setup

1. **Create a Discord application and bot.** In the
   [Discord Developer Portal](https://discord.com/developers/applications),
   create a new application, add a bot, and copy the bot **token**.
2. **Invite the bot.** Generate an OAuth2 invite URL with the
   `applications.commands` and `bot` scopes, then add the bot to your server.
3. **Configure secrets.** Copy `.env.example` to `.env` and fill in:
   - `DISCORD_TOKEN` — the bot token (required).
   - `DISCORD_CLIENT_ID` — the application/client ID.
   - `DISCORD_DEV_GUILD_ID` — a guild ID for instant command sync while
     developing.

   `.env` is gitignored — never commit real secrets.
4. **Install dependencies.**

   ```bash
   pip install -r requirements.txt
   ```

## Running

```bash
python -m poimandres.deploy_commands   # register the slash commands (run once)
python -m poimandres.bot               # start the bot
```

`python -m poimandres.server_count` prints the bot's guild list and exits.

Global slash commands can take up to an hour to propagate; commands copied to
`DISCORD_DEV_GUILD_ID` appear instantly.

## Development

```bash
pip install -r requirements-dev.txt
pre-commit install && pre-commit install --hook-type commit-msg
pre-commit run --all-files             # the single local quality gate
```

The bot is built in Python with `discord.py` 2.x. See
[`plans/2026-05-21-PYTHON_REFACTOR.md`](plans/2026-05-21-PYTHON_REFACTOR.md)
for the authoritative build specification.
