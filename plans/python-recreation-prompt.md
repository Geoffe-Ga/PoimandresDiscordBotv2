# Agent Prompt: Recreate the "Poimandres" Discord Bot in Python

You are tasked with recreating an existing Discord bot called **Poimandres** from
scratch. The original is written in **Node.js** using `discord.js` v13. Your job is
to produce a **functionally equivalent bot written in Python**. This document is an
exhaustive specification: build exactly what is described here. Where the original
design is repetitive or violates DRY, you may keep it repetitive or tidy it up —
behavior is what matters, not architecture. Do not add features that are not
described here.

---

## 1. What the bot is

Poimandres is a Discord bot that quotes esoteric, occult, religious, and
philosophical texts on demand via **slash commands**. A user types a slash command
(e.g. `/ch 1.2`) and the bot replies with the requested passage rendered inside a
Discord embed. The bot is themed around Hermeticism; its name and tagline come from
the *Corpus Hermeticum* ("I am Poimandres, Mind of all-masterhood...").

The bot has no database. All text content lives in static JSON files. Every command
is a thin lookup: take the user's input string, use it as a key into a JSON object,
return the matched value (or a "Not found" message).

---

## 2. Critical constraint: the text corpora must be carried over verbatim

The bot's value is ~6 MB of hand-curated public-domain scripture and philosophy text
stored as JSON. **You cannot regenerate this text.** You MUST reuse the existing JSON
data files from the original repository unchanged. They live in `commands/books/` in
the original repo. Copy them verbatim into your Python project (suggested location:
`books/` or `data/books/`). Do not paraphrase, translate, re-key, or "clean up" their
contents. The files are:

| File | Title | Structure |
|---|---|---|
| `ch.json` | The Corpus Hermeticum | flat: `"chapter.verse" -> text`, keys `"1.1"`–`"18.16"` |
| `ah.json` | Asclepius | flat: `"N" -> text`, keys `"1"`–`"42"` |
| `dh.json` | The Definitions of Hermes to Asclepius | flat: `"N.M" -> text`, `"1.1"`–`"10.7"` |
| `oh.json` | The Oxford Fragments | flat: `"N" -> text`, `"1"`–`"5"` |
| `emeraldtablet.json` | The Emerald Tablet | special: has a single `"message"` string field |
| `bible.json` | The King James Bible | **nested**: `"BOOK" -> { "chapter.verse" -> text }` |
| `quran.json` | al-Qurʾān | flat: `"surah.ayah" -> text`, `"1.1"`–`"114.6"` |
| `sepher-yetzirah.json` | Sepher Yetzirah | flat `"chapter.line" -> text` PLUS a nested `"path" -> { "1".."32" -> text }` object |
| `al.json` | Liber AL vel Legis (Book of the Law) | flat: `"chapter.verse" -> text`, `"1.1"`–`"3.75"` |
| `enchiridion.json` | The Enchiridion (Epictetus) | flat: `"N" -> text`, `"1"`–`"51"` |
| `aurelius.json` | Meditations (Marcus Aurelius) | flat: `"book.line" -> text`, `"1.1"`–`"12.27"` |
| `proclus-metaphysics.json` | Proclus' Elements of Metaphysics | flat: `"N" -> text`, `"1"`–`"211"` |
| `yoga.json` | Yoga Sūtras of Patañjali | flat: `"pada.sutra" -> text`, e.g. `"1.1"` |
| `tarot.json` | Tarot Deck (Rider-Waite-Smith) | flat: `"1".."78" -> image URL string` |
| `LIBRARY.json` | (index for the dropdown menu) | a JSON **array** of `{ "label": ..., "value": ... }` |

**Shared shape of every "book" JSON** (except `tarot.json` and `LIBRARY.json`): the
object has two metadata keys — `"bookTitle"` (string) and `"translator"` (string) —
alongside all the passage keys. `tarot.json` also has `bookTitle`/`translator`. Your
lookup code must treat `bookTitle` and `translator` as metadata, not as passages.

If you cannot obtain the original files, the bot is not recreatable — stop and ask
for them. Do not fabricate scripture.

---

## 3. Target tech stack (Python)

- **Language:** Python 3.10+
- **Discord library:** `discord.py` 2.x (it has first-class slash-command / app-command
  support via `discord.app_commands`). `py-cord` is an acceptable alternative; pick one
  and be consistent.
- **Config / secrets:** `python-dotenv`. The bot token must NOT be committed. The
  original stores it in a gitignored `config.json` as `{ "token": "..." }`. In Python,
  read it from a `.env` file (`DISCORD_TOKEN=...`) or environment variable. Also store
  the application/client ID and a development guild ID this way.
- **Process management (optional):** the original uses `pm2`. You may skip this or
  document running under `systemd`/`pm2`/a process supervisor. Not required for
  functional parity.
- Provide a `requirements.txt` and a `README.md`.

`.gitignore` must exclude: the secrets file (`.env` / `config.json`), `__pycache__/`,
a `DEV/` scratch folder, log output, `desktop.ini`, and `guildList.txt`.

---

## 4. Project layout (suggested)

```
poimandres/
├── bot.py                  # main entry point (equivalent of index.js)
├── deploy_commands.py      # optional: explicit slash-command sync (equivalent of deploy-commands.js)
├── server_count.py         # standalone utility (equivalent of server-count.js)
├── commands/               # one module per command
│   ├── __init__.py
│   ├── ch.py  ah.py  dh.py  oh.py  emeraldtablet.py
│   ├── bible.py  quran.py  sepher_yetzirah.py  al.py
│   ├── enchiridion.py  aurelius.py  proclus_metaphysics.py  yoga.py
│   ├── tarot.py  help.py  contents.py
├── books/                  # the verbatim JSON data files from section 2
├── .env.example
├── requirements.txt
└── README.md
```

The original has 16 command files. Each `.js` command exports `{ data, execute }`:
`data` is a `SlashCommandBuilder` describing the command; `execute(interaction)` runs
it. In `discord.py` the equivalent is an `app_commands.Command` (or a method decorated
with `@app_commands.command`). You may organize commands as a `Cog` per command, a
single cog, or loose command functions registered on a `CommandTree` — your choice.
The original dynamically loads every `.js` file in `commands/`; you may replicate this
dynamic loading or register commands explicitly.

---

## 5. Global behavior and shared conventions

These apply across all text-lookup commands. Implement them once (a helper is fine —
DRY is allowed here) or per-command (also fine).

1. **Embed styling.** Every reply is a Discord embed with color `#f15b40` (decimal
   `15817536`, an orange-red).
2. **Footer.** For the standard book-lookup commands the embed footer text is:
   `"{bookTitle} | {lookupKey} | {translator}"`. Exact spacing/format varies slightly
   per command — see section 6 for the exceptions. The footer is built from the
   `bookTitle` and `translator` fields inside that book's JSON.
3. **Colon normalization.** Before looking up a key, most commands replace `:` with
   `.` in the user's input, so `1:2` and `1.2` are equivalent. (Exceptions: `oh` and
   `proclus-metaphysics` do NOT do this — they have this line commented out. Match
   that, or just apply it everywhere; it's harmless for integer-only keys.)
4. **Not-found handling.** If the key is missing from the JSON, the embed body is a
   "Not found" message that includes a usage example, e.g.
   `"**Not found**\ntry: \`/ch  1.2\`"`. Each command has its own example string —
   see section 6.
5. **Body text** of the embed is the looked-up passage (the JSON value), set as the
   embed description.
6. **Discord markdown.** The JSON text values contain Discord markdown (`**bold**`,
   `*italic*`, `` `code` ``, `\n` newlines). Pass them through unmodified — Discord
   renders them.
7. **Replies are public** (visible to the channel) for text-lookup and tarot
   commands. `/help` and `/contents` reply **ephemerally** (only the invoking user
   sees them) — in `discord.py` use `ephemeral=True`.
8. **Slash command options** are all Discord string options unless noted. Required
   vs. optional matters — see section 6.
9. **Error guard.** Wrap command execution so that any exception results in an
   ephemeral reply `"There was an error while executing this command!"` and the error
   is logged to console. The original does this in the central interaction handler.

---

## 6. Per-command specification

The slash-command **name** equals the file name. The slash-command **description**
shown in Discord is `"Lookup {bookTitle}"` for book commands (bookTitle pulled live
from the JSON), except where noted.

### 6.1 Simple flat-lookup commands

These all behave identically: one **required** string option, look it up in the
book JSON, reply with an embed (description = passage, footer =
`"{bookTitle} | {key} | {translator}"`).

| Command | JSON | Option name | Option description | Not-found example |
|---|---|---|---|---|
| `/ch` | `ch.json` | `part` | `book#.verse#` | `/ch  1.2` |
| `/ah` | `ah.json` | `part` | `# 1-41` | `/ah  1` |
| `/dh` | `dh.json` | `part` | `1.1 - 10.7` | `/dh  1.1` |
| `/al` | `al.json` | `part` | `chapter#.verse#` | `/al  3.75` |
| `/enchiridion` | `enchiridion.json` | `part` | `# 1-51` | `/enchiridion  27` |
| `/aurelius` | `aurelius.json` | `part` | `book#.line#` | `/aurelius  1.16` |
| `/quran` | `quran.json` | `part` | `Surah#.Ayah#` | `/quran 1.1` |
| `/yoga` | `yoga.json` | `part` | `Pāda#.sūtra#` | `/yoga  1.1` |
| `/proclus-metaphysics` | `proclus-metaphysics.json` | `part` | `# 1-211` | `/proclus-metaphysics  1` |

Notes:
- `quran`'s not-found message is the one-line form `"**Not found** Try: \`/quran 1.1\`"`.
  The others use the two-line `"**Not found**\ntry: \`...\`"` form. Minor; match it
  if you want exact parity.
- `proclus-metaphysics` does NOT do the `:` -> `.` replacement (keys are plain
  integers anyway).

### 6.2 `/oh` — The Oxford Fragments

Flat lookup against `oh.json`. **Differences from the simple commands:**
- The option is named `fragment` (description `# 1-5`), not `part`.
- No `:` -> `.` replacement.
- The embed additionally has a **title** and a **URL**:
  - title = `"{bookTitle} | Translated by {translator}"`
  - url = `https://sartrix.wordpress.com/the-oxford-hermetica/`
- Footer is still `"{bookTitle} | {key} | {translator}"`.
- Not-found example: `/oh 1`.

### 6.3 `/emeraldtablet` — The Emerald Tablet

Special: this text is short, so it has **no options**. `emeraldtablet.json` contains a
single `"message"` field holding the entire text. The command always replies with an
embed: description = `message`, footer = `"{bookTitle} | 12th Century Latin Version"`
(the string `"12th Century Latin Version"` is hardcoded, not from `translator`).
Command description is `"Lookup {bookTitle}"`.

### 6.4 `/sepher-yetzirah` — Sepher Yetzirah

`sepher-yetzirah.json` is flat (`"1.1"` etc.) but ALSO contains a `"path"` key whose
value is a nested object with keys `"1"`–`"32"` (the 32 paths of wisdom).

The command has **two** string options:
- `part` — **required** — description `chapter#.line#`
- `path` — **optional** — description `(optional) 1-32`

Logic (replicate exactly):
1. Read `part` and `path`. Apply `:` -> `.` to `part`.
2. **If `part` equals the literal string `"path"`**: look up `bookRef["path"][path]`.
   If found, body = that value; else body = the not-found message.
3. **Else**: look up `bookRef[part]` directly. If found, body = that value; else
   not-found.
4. Not-found message:
   `"**Not found**\ntry: \`/sepher-yetzirah  1.1\`\nor: \`/sepher-yetzirah path 1\`"`.
5. Footer: `"{bookTitle} | {part} {path} | {translator}"` (note `path` may be `None`;
   the original concatenates it regardless — when absent it shows as the JS `null`
   stringified; in Python render an empty string instead of `None`).

So a user runs either `/sepher-yetzirah part:1.1` for a verse, or
`/sepher-yetzirah part:path path:7` for the 7th path.

### 6.5 `/bible` — The King James Bible

`bible.json` is **nested**: top level is `"BOOK_NAME"` (uppercase, e.g. `"GENESIS"`,
`"REVELATION"`) -> `{ "chapter.verse" -> text }`. Plus the usual `bookTitle` /
`translator` metadata.

Two **required** string options:
- `book` — description `ie. genesis`
- `chapterverse` — description `ie. 1.1`

Logic:
1. Uppercase the `book` input. Apply `:` -> `.` to `chapterverse`.
2. **Random support — the literal `X`:**
   - If `book` (uppercased) == `"X"`: pick a random book. Get all top-level keys of
     `bible.json`, **exclude `"bookTitle"` and `"translator"`**, pick one at random,
     use it as `book`.
   - If `chapterverse` == `"X"`: pick a random verse — get all keys of
     `bookRef[book]`, pick one at random.
3. Look up `bookRef[book][chapterverse]`. If found, body = that value; else body =
   `"**Not found**\ntry: \`/bible genesis 1.1\`"`.
4. Footer: `"{bookTitle} | {book}  {chapterverse}"` (two spaces between book and
   verse; note: NO translator in the bible footer).

So `/bible book:genesis chapterverse:1.1` returns a verse;
`/bible book:X chapterverse:X` returns a fully random verse.

### 6.6 `/tarot` — Rider-Waite-Smith Tarot pull

Pulls a tarot card and displays its image. One **optional** string option `card`,
description `(optional) number of card (0-77)`.

The original hardcodes an array of **78 image URLs** inside the command (and there is
also a `tarot.json` with the same 78 URLs keyed `"1"`–`"78"`). Use either source —
the canonical list is the 78 `https://www.sacred-texts.com/tarot/pkt/img/...jpg`
URLs in the order: 22 Major Arcana (`ar00`–`ar21`), then Wands (`waki, waqu, wakn,
wapa, wa10..wa02, waac`), Cups (`cu...`), Swords (`sw...`), Pentacles (`pe...`) — each
suit being King, Queen, Knight, Page, 10..2, Ace. Just copy the array verbatim from
the original `tarot.js` / `tarot.json`.

Logic:
- If `card` is provided: show `cardArr[int(card)]` (0-indexed into the 78-element
  list). No bounds checking in the original — out-of-range yields an error caught by
  the global handler.
- If `card` is omitted: pick a uniformly random card from the array.
- Reply with an embed: color `#f15b40`, `image` set to the chosen URL. No description,
  no footer.

### 6.7 `/help` — list all texts

No options. Description: `"List the texts Poimandres can access"`. Replies
**ephemerally** with a single static embed:
- color `#f15b40`
- description: `"The Poimandres Discord bot quotes a variety of texts themed around
  religion, the occult, and the esoteric.\nYou can access them with the following
  slash commands:"`
- A series of embed **fields**, grouped by section headers. Reproduce these fields
  (name -> value), most with `inline=True`; the section-header fields use a
  zero-width-space name (`​`):

  - Header field: name `​`, value `**Hermetic Texts:**`
  - `` `/ch` `` -> `The Corpus Hermeticum\nfrom \`1.1\` to \`18.16\`\nTaken from *Thrice-Greatest Hermes Vol. 2*\nTranslated by G.R.S Mead (1906)` (inline)
  - `` `/ah` `` -> `Asclepius\nfrom \`1\` to \`42\`\nTaken from *Thrice-Greatest Hermes Vol. 2*\nTranslated by G.R.S Mead (1906)` (inline)
  - `` `/emeraldtablet` `` -> `The Emerald Tablet\n*12th Century Latin version*\nTranslated by Steele and Singer (1928)` (inline)
  - `` `/dh` `` -> `The Definitions\nHermes to Asclepius\nfrom \`1.1\` to \`10.7\`\nTranslated by Jean-Pierre Mahé (1999)` (inline)
  - `` `/oh` `` -> `The Oxford Fragments\nfrom \`1\` to \`5\`\nTranslated by Sartrix` (inline)
  - Header field: name `​`, value `**Other Religious/Occult/Esoteric Texts:**`
  - `` `/quran` `` -> `The Qur'an\nfrom \`1.1\` to \`114.6\`\nTranslated by Sahih International` (inline)
  - `` `/bible` `` -> `The Bible\nfrom \`genesis 1.1\` to \`revelation 22.21\`\nKing James Version` (inline)
  - `` `/sepher-yetzirah` `` -> `Sepher Yetzirah\nfrom \`1.1\` to \`6.4\`\n*or* \`/sepher-yetzirah path\` from \`1\` to \`32\`\nTranslated by W.W. Wescott (1887)` (inline)
  - `` `/al` `` -> `Liber AL vel Legis or, *The Book of the Law*\nfrom \`1.1\` to \`3.75\`\nBook by Aiwass, Aleister Crowley, and Rose Edith Kelly (1904)` (inline)
  - `` `/enchiridion` `` -> `Epictetus' Enchiridion\nfrom \`1\` to \`51\`\nTranslated by Thomas W. Higginson` (inline)
  - `` `/aurelius` `` -> `Marcus Aurelius' Meditations\nfrom \`1.1\` to \`12.27\`\nTranslated by Meric Casaubon` (inline)
  - `` `/proclus-metaphysics` `` -> `Proclus' Elements of Metaphysics\nfrom \`1\` to \`211\`\nTranslated by Antonio Vargas (2021)` (inline)
  - Header field: name `​`, value `**Other tools:**`
  - `` `/tarot` `` -> `Rider-Waite-Smith Tarot Card pull\n\`/tarot\` for a random card\n\`/tarot 0-77\` for a specific card` (inline)
  - `` `/contents` `` -> `Select a text from a drop-down menu.\n(Nobody else sees this but you)` (inline)
- footer text: `"Poimandres Discord Bot • /help"`
- a timestamp (current time).

Note: the original `/help` does not currently list `/yoga` even though that command
exists — you may keep the parity gap or add a `/yoga` field (`Yoga Sūtras of
Patañjali`). Adding it is a reasonable fix; mention it if you do.

### 6.8 `/contents` — dropdown text picker

No options. Description: `"Get a "contents page" of the available texts"`. Replies
**ephemerally** with a message containing a **select menu** (dropdown), no embed.

- The select menu has `custom_id` = `"contentsSelect"`, placeholder
  `"Select a text..."`.
- Its options come from `LIBRARY.json` — a JSON array of `{ "label", "value" }`
  objects. Each becomes a select option (label shown to user, value = the book's
  command/JSON name). `LIBRARY.json` contains 13 entries: `ah, bible, ch, dh,
  emeraldtablet, enchiridion, al, aurelius, oh, proclus-metaphysics, quran,
  sepher-yetzirah, tarot` with human-readable labels.

The interaction handling for this select menu is described in section 7.

---

## 7. Central interaction handling (equivalent of `index.js`)

The original `index.js`:
1. Creates a Discord client with the `GUILDS` intent only.
2. Dynamically loads every `.js` file in `commands/` into a name->command map.
3. On `ready`, prints a UTC timestamp, a large ASCII-art "poimandres" banner, the
   guild count, and a line per guild (`name | Members: count`).
4. On `interactionCreate`:
   - **If it's a slash command:** look up the command by name, log
     `"{commandName} request at {guildName} by {memberDisplayName}"` (or
     `"{commandName} request in DM"` if not in a guild), call its `execute`. On
     exception: log it and reply ephemerally `"There was an error while executing
     this command!"`.
   - **If it's a select-menu interaction:** check `custom_id`.
     - If `custom_id == "contentsSelect"`: this is the dropdown from `/contents`. The
       selected value is a book name. Behavior:
       1. Log `"{value} selected by {memberDisplayName}"` (or `in DM`).
       2. Load `books/{value}.json`.
       3. Take `Object.keys()` of that JSON — i.e. all its keys.
       4. Join them into a comma-separated string, then `replaceAll(",", "\` \`")`
          so they render as a row of inline-code chips, then `replaceAll("bookTitle",
          "")` and `replaceAll("translator", "")` to blank out the metadata keys.
       5. Build body text: `` `/{value}` `` + `" + *one of the following:*\n"` +
          the backtick-wrapped key list. Concretely the template is:
          `` `/{value}` `` `+ *one of the following:*` newline `` `{chips}` ``.
       6. **Length cap:** if the body exceeds 950 characters, truncate to the first
          901 chars and append `" ***... Discord message limit exceeded.***"`.
       7. Reply ephemerally with that text.
       This effectively shows the user every valid lookup key for the text they
       picked. (For `bible` this lists the book names; for `tarot` the card numbers;
       for `emeraldtablet` it shows `message`.)
     - Any other select-menu `custom_id`: reply ephemerally
       `"**UNDER DEVELOPMENT** *This menu doesn't lead to anywhere yet*"`.
   - Any other interaction type: ignore.
5. Logs in with the token.

Recreate all of this in `bot.py`. In `discord.py`:
- Use `intents = discord.Intents.default()` with at least `guilds` enabled (members
  intent is NOT required — the original only uses `GUILDS`; `member.displayName` in
  logging comes from the interaction payload, which `discord.py` exposes as
  `interaction.user.display_name`).
- Slash commands are dispatched automatically by the `CommandTree`, so the
  "look up command by name" loop is implicit — just register each command. Keep the
  per-invocation logging (`{command} request at {guild} by {user}`).
- The select-menu logic must be wired up. Either use a persistent
  `discord.ui.View` with a `discord.ui.Select` whose callback implements the
  `contentsSelect` behavior, or handle the raw component interaction in an
  `on_interaction` listener. Either is acceptable; the persistent-View approach is
  idiomatic for `discord.py` 2.x (remember persistent views need the bot to
  re-register the view on startup, or simply attach the view fresh each time
  `/contents` is invoked, which avoids persistence concerns).
- Reproduce the `on_ready` console output: UTC timestamp, the ASCII banner (copy it
  verbatim from the original `index.js` — it spells "poimandres"), the guild count,
  and one line per guild with member counts.

---

## 8. Slash-command registration (equivalent of `deploy-commands.js`)

The original has a separate `deploy-commands.js` that registers all slash commands
with Discord's API, both **globally** and to a specific **development guild** (guild
commands appear instantly; global commands take up to an hour to propagate). It uses
a hardcoded `clientId` and `guildId`.

In `discord.py`:
- Command registration is done by syncing the `CommandTree`: `await tree.sync()` for
  global, `await tree.sync(guild=discord.Object(id=DEV_GUILD_ID))` for a guild.
- Put the dev guild ID in config (`.env`), not hardcoded.
- You can sync inside `on_ready` / `setup_hook`, OR provide a standalone
  `deploy_commands.py` that syncs and exits — replicate the original's separation if
  you like. A common pattern: copy global commands to the dev guild for instant
  testing during development, sync globally for production.
- Do NOT hardcode the original's `clientId` (`955696145613586472`) or `guildId`
  (`702837380163436574`) — those belong to the original author's bot/server. The new
  operator supplies their own.

---

## 9. Server-count utility (equivalent of `server-count.js`)

A standalone script that logs the bot in, on `ready` prints the banner + a list of
every guild (`name | Members: count`) and the total count, then exits. Recreate as
`server_count.py` — a minimal script that connects, dumps the guild list, and
disconnects. Low priority; include for completeness.

---

## 10. Convenience scripts

The original ships Windows `.bat` files:
- `runthebot.bat` -> `node deploy-commands.js` then `node index.js`
- `update-command-list.bat` -> `node deploy-commands.js` (+ pause)
- `count servers.bat` -> `node server-count.js` (+ pause)

Replace these with cross-platform equivalents: a `README.md` "Running" section, and
optionally a `Makefile` or shell scripts (`run.sh`, `deploy.sh`). Not required for
functional parity.

---

## 11. README

Write a `README.md`. The original opens with the Hermetic epigraph and lists the
available texts. Keep that spirit. Required content:
- The epigraph: *"I am Poimandres, Mind of all-masterhood; I know what thou desirest
  and I'm with thee everywhere."* — *The Corpus Hermeticum 1.2*
- A description: a Discord bot that quotes esoteric/occult/religious/philosophical
  texts via slash commands.
- The list of texts (Hermetic: Corpus Hermeticum, Asclepius, Emerald Tablet,
  Definitions of Hermes to Asclepius, Oxford Fragments; Other: Bible, Qur'an, Book of
  the Law, Enchiridion, Meditations, Proclus' Elements of Metaphysics, Sepher
  Yetzirah, Yoga Sūtras of Patañjali; plus Tarot pulls).
- A note that `/help` lists all commands in-server.
- **Setup instructions:** create a Discord application + bot, enable it, invite it
  with the `applications.commands` + `bot` scopes, put the token in `.env`, install
  `requirements.txt`, run the bot.

---

## 12. Acceptance checklist

The recreated bot is correct when:

- [ ] All 16 slash commands exist and are named exactly: `ch, ah, dh, oh,
      emeraldtablet, bible, quran, sepher-yetzirah, al, enchiridion, aurelius,
      proclus-metaphysics, yoga, tarot, help, contents`.
- [ ] Each text-lookup command reads its verbatim JSON and returns the correct
      passage in an embed with color `#f15b40` and the correct footer format.
- [ ] Missing keys produce the correct per-command "Not found" message.
- [ ] `:` is normalized to `.` for the commands that do so.
- [ ] `/bible` handles nested book/chapter.verse lookup, uppercases the book name,
      and supports `X` for random book and/or random verse (excluding the
      `bookTitle`/`translator` metadata keys).
- [ ] `/sepher-yetzirah` supports both direct verse lookup and the `part:path` +
      `path:N` mode against the nested `"path"` object.
- [ ] `/emeraldtablet` returns the single `message` field with no options.
- [ ] `/oh` adds the title + sartrix.wordpress.com URL to its embed.
- [ ] `/tarot` returns a random card image, or a specific one by 0-indexed number.
- [ ] `/help` returns the full ephemeral field-list embed; `/contents` returns an
      ephemeral dropdown.
- [ ] Selecting an item in the `/contents` dropdown (`custom_id = contentsSelect`)
      replies ephemerally with the list of valid lookup keys for that text, with
      `bookTitle`/`translator` blanked out, capped at the 950-char limit.
- [ ] `/help` and `/contents` reply ephemerally; all other replies are public.
- [ ] Exceptions during a command produce the ephemeral error message and a console
      log, never crash the bot.
- [ ] The bot token and IDs come from `.env` / env vars and are gitignored — nothing
      secret is committed.
- [ ] On startup the console prints the timestamp, ASCII banner, and per-guild list.

Build it. When done, summarize any intentional deviations from the original (e.g.
adding `/yoga` to `/help`, bounds-checking `/tarot`).
