# Agent Prompt: Recreate the "Poimandres" Discord Bot in Python

> **Document type:** Build specification, written as a structured agent prompt.
> **Status:** Authoritative. This file supersedes `plans/python-recreation-prompt.md`.
> **How to read it:** Sections 1–6 are the prompt proper (Role, Goal, Context,
> Output Format, Examples, Requirements). Sections 7+ are the reference data the
> prompt depends on — treat them as appendices the Goal points into.

---

## 1. Role

You are a **senior Python engineer** specializing in Discord bot development with
`discord.py` 2.x. You write production-quality, fully typed, well-tested code, and
you are meticulous about reproducing the observable behavior of an existing system
when porting it to a new language. You do not improvise features; when the spec is
silent you ask rather than guess.

---

## 2. Goal

Recreate an existing Discord bot called **Poimandres** — currently written in
Node.js with `discord.js` v13 — as a **functionally equivalent Python bot** using
`discord.py` 2.x.

"Functionally equivalent" means: every slash command, every reply, every embed,
every "Not found" string, and every console log line is observably the same as the
original. Internal architecture may differ; user-visible behavior may not.

**Success is defined by the acceptance checklist in section 12.** The task is
complete when every box there can be honestly checked.

**Out of scope.** Do not add commands, options, or behaviors not described in this
document. The only permitted deviations are the two listed in section 11; if you
take either, record it in your final summary.

---

## 3. Context

### 3.1 What the bot is

Poimandres quotes esoteric, occult, religious, and philosophical texts on demand via
**slash commands**. A user types e.g. `/ch 1.2` and the bot replies with the
requested passage rendered inside a Discord embed. The bot is themed around
Hermeticism; its name and tagline come from the *Corpus Hermeticum* ("I am
Poimandres, Mind of all-masterhood...").

The bot has **no database**. All text content lives in static JSON files. Every
command is a thin lookup: take the user's input string, use it as a key into a JSON
object, return the matched value (or a "Not found" message).

### 3.2 The original codebase (reference only — do not extend it)

- `index.js` — client setup, command loader, central interaction handler.
- `commands/*.js` — 16 command files, each exporting `{ data, execute }`.
- `commands/books/*.json` — the text corpora (see section 7).
- `deploy-commands.js` — slash-command registration script.
- `server-count.js` — standalone guild-count utility.
- `*.bat` — Windows convenience scripts.

### 3.3 Hard constraint — the text corpora are sacred

The bot's entire value is **~6 MB of hand-curated public-domain scripture and
philosophy** stored as JSON. **You cannot regenerate this text.** You MUST reuse the
existing JSON files from the original repo (`commands/books/`) **byte-for-byte**. Do
not paraphrase, translate, re-key, reformat, or "clean up" their contents.

If the original JSON files are unavailable, **stop and ask for them.** Do not
fabricate scripture. The corpus inventory and structure are in section 7.

### 3.4 Tech stack

- **Language:** Python 3.10+
- **Discord library:** `discord.py` 2.x (slash commands via `discord.app_commands`).
  `py-cord` is an acceptable alternative — pick one and stay consistent.
- **Config / secrets:** `python-dotenv`. The bot token, application/client ID, and
  development guild ID come from a `.env` file or environment variables. **Nothing
  secret is ever committed.**
- **Process management:** the original uses `pm2`; this is optional. Document
  `systemd`/`pm2`/supervisor in the README if you wish — not required for parity.

---

## 4. Output Format

### 4.1 Deliverable: a Python package with this layout

```
poimandres/
├── bot.py                  # main entry point          (replaces index.js)
├── deploy_commands.py      # slash-command sync         (replaces deploy-commands.js)
├── server_count.py         # standalone guild-count     (replaces server-count.js)
├── commands/               # one module per command
│   ├── __init__.py
│   ├── ch.py  ah.py  dh.py  oh.py  emeraldtablet.py
│   ├── bible.py  quran.py  sepher_yetzirah.py  al.py
│   ├── enchiridion.py  aurelius.py  proclus_metaphysics.py  yoga.py
│   ├── tarot.py  help.py  contents.py
├── books/                  # the verbatim JSON data files from section 7
├── .env.example
├── requirements.txt
└── README.md
```

The original loads every `.js` file in `commands/` dynamically. In `discord.py` you
may organize commands as one `Cog` per command, a single cog, or loose functions
registered on a `CommandTree` — your choice. You may replicate the dynamic loading
or register commands explicitly.

### 4.2 Per-reply output contract

Every text-lookup reply is a Discord **embed** with:
- **color** `#f15b40` (decimal `15817536`, an orange-red);
- **description** = the looked-up passage text (verbatim JSON value);
- **footer** = `"{bookTitle} | {lookupKey} | {translator}"` unless section 8 lists
  an exception for that command.

`bookTitle` and `translator` are read from the metadata keys inside each book JSON.
Discord markdown in passage text (`**bold**`, `*italic*`, `` `code` ``, `\n`) is
passed through unmodified.

### 4.3 Final report

When the build is complete, output a short summary that:
1. Confirms each acceptance-checklist item (section 12) is satisfied; and
2. Lists every intentional deviation from the original (section 11).

---

## 5. Examples

These illustrate the expected observable behavior. Reproduce them exactly.

### Example A — successful flat lookup

User invokes `/ch part:1.2`. The bot replies publicly with an embed:
- color `#f15b40`
- description = the value at key `"1.2"` in `ch.json`
- footer = `"The Corpus Hermeticum | 1.2 | G.R.S Mead"`

### Example B — colon normalization

User invokes `/ch part:1:2`. Before lookup, `:` is replaced with `.`, so the key
becomes `1.2` — identical result to Example A.

### Example C — key not found

User invokes `/ch part:99.99`. Key is absent from `ch.json`. The bot replies with
an embed whose description is the two-line not-found string:

```
**Not found**
try: `/ch  1.2`
```

(Note the two spaces inside the backticks — match it.)

### Example D — random Bible verse

User invokes `/bible book:X chapterverse:X`. Both inputs are the literal `X`. The
bot picks a random top-level book key (excluding `bookTitle`/`translator`), then a
random `chapter.verse` key within it, and returns that verse. Footer =
`"The King James Bible | GENESIS  3.4"` (book uppercased, two spaces, no translator).

### Example E — contents dropdown selection

User invokes `/contents`, then selects "The Corpus Hermeticum" from the dropdown.
The bot replies ephemerally with text listing every valid lookup key for `ch.json`
as inline-code chips, `bookTitle`/`translator` blanked out — see section 9.

---

## 6. Requirements / Constraints

1. **Behavior over architecture.** Where the original is repetitive or violates DRY,
   you may keep it repetitive or tidy it up. User-visible behavior must not change.
2. **No new features.** Build exactly what sections 7–12 describe. The only allowed
   deviations are in section 11.
3. **Corpora verbatim.** See section 3.3. Never alter passage text or its keys.
4. **No committed secrets.** Token and IDs live in `.env` / env vars only.
5. **`.gitignore` must exclude:** the secrets file (`.env` / `config.json`),
   `__pycache__/`, a `DEV/` scratch folder, log output, `desktop.ini`, and
   `guildList.txt`.
6. **Do not hardcode the original author's IDs:** client ID `955696145613586472`
   and guild ID `702837380163436574` belong to the original operator. The new
   operator supplies their own via config.
7. **Tests required.** Every text-lookup command and the central interaction
   handler must have unit coverage. Follow the project quality gate in `CLAUDE.md`
   (≥90% branch coverage, clean ruff/mypy/bandit, complexity ≤10).
8. **Ask, don't fabricate.** If the corpus files or any required detail are missing,
   stop and ask rather than inventing content.

---

## 7. Reference: the text corpora

Copy these verbatim from the original `commands/books/` into the new `books/`.

| File | Title | Structure |
|---|---|---|
| `ch.json` | The Corpus Hermeticum | flat: `"chapter.verse" -> text`, keys `"1.1"`–`"18.16"` |
| `ah.json` | Asclepius | flat: `"N" -> text`, keys `"1"`–`"42"` |
| `dh.json` | The Definitions of Hermes to Asclepius | flat: `"N.M" -> text`, `"1.1"`–`"10.7"` |
| `oh.json` | The Oxford Fragments | flat: `"N" -> text`, `"1"`–`"5"` |
| `emeraldtablet.json` | The Emerald Tablet | special: a single `"message"` string field |
| `bible.json` | The King James Bible | **nested**: `"BOOK" -> { "chapter.verse" -> text }` |
| `quran.json` | al-Qurʾān | flat: `"surah.ayah" -> text`, `"1.1"`–`"114.6"` |
| `sepher-yetzirah.json` | Sepher Yetzirah | flat `"chapter.line" -> text` PLUS a nested `"path" -> { "1".."32" -> text }` object |
| `al.json` | Liber AL vel Legis (Book of the Law) | flat: `"chapter.verse" -> text`, `"1.1"`–`"3.75"` |
| `enchiridion.json` | The Enchiridion (Epictetus) | flat: `"N" -> text`, `"1"`–`"51"` |
| `aurelius.json` | Meditations (Marcus Aurelius) | flat: `"book.line" -> text`, `"1.1"`–`"12.27"` |
| `proclus-metaphysics.json` | Proclus' Elements of Metaphysics | flat: `"N" -> text`, `"1"`–`"211"` |
| `yoga.json` | Yoga Sūtras of Patañjali | flat: `"pada.sutra" -> text`, e.g. `"1.1"` |
| `tarot.json` | Tarot Deck (Rider-Waite-Smith) | flat: `"1".."78" -> image URL string` |
| `LIBRARY.json` | index for the dropdown menu | a JSON **array** of `{ "label", "value" }` |

**Shared shape** of every "book" JSON (except `LIBRARY.json`): the object carries two
metadata keys — `"bookTitle"` (string) and `"translator"` (string) — alongside the
passage keys. `tarot.json` has them too. Lookup code MUST treat `bookTitle` and
`translator` as metadata, never as passages.

---

## 8. Reference: global conventions and per-command spec

### 8.1 Global behavior (applies to all text-lookup commands)

1. **Embed styling** — color `#f15b40` on every reply.
2. **Footer** — `"{bookTitle} | {lookupKey} | {translator}"`, built from the JSON
   metadata. Per-command exceptions are noted below.
3. **Colon normalization** — most commands replace `:` with `.` in user input before
   lookup, so `1:2` ≡ `1.2`. Exceptions: `oh` and `proclus-metaphysics` do NOT (the
   original has this line commented out). Applying it everywhere is harmless for
   integer-only keys — either match the exceptions or apply uniformly.
4. **Not-found handling** — a missing key yields an embed whose body is a "Not found"
   message with a usage example, e.g. `"**Not found**\ntry: \`/ch  1.2\`"`. Each
   command's exact example string is in the tables below.
5. **Body text** — the looked-up passage becomes the embed description.
6. **Discord markdown** — pass passage text through unmodified.
7. **Reply visibility** — text-lookup and `/tarot` replies are **public**; `/help`
   and `/contents` reply **ephemerally** (`ephemeral=True`).
8. **Slash options** — all Discord string options unless noted; required vs.
   optional matters (see tables).
9. **Error guard** — wrap command execution so any exception produces an ephemeral
   reply `"There was an error while executing this command!"` plus a console log.

The slash-command **name** equals the file name. The Discord-facing **description**
is `"Lookup {bookTitle}"` for book commands (bookTitle pulled live from JSON),
except where noted.

### 8.2 Simple flat-lookup commands

One **required** string option; look it up; reply with the standard embed.

| Command | JSON | Option | Option description | Not-found example |
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
- `quran`'s not-found message uses the one-line form
  `"**Not found** Try: \`/quran 1.1\`"`. All others use the two-line
  `"**Not found**\ntry: \`...\`"` form. Match it for exact parity.
- `proclus-metaphysics` does NOT do `:` → `.` (keys are plain integers anyway).

### 8.3 `/oh` — The Oxford Fragments

Flat lookup against `oh.json`. Differences from the simple commands:
- Option is named `fragment` (description `# 1-5`), not `part`.
- No `:` → `.` replacement.
- The embed additionally has a **title** and **URL**:
  - title = `"{bookTitle} | Translated by {translator}"`
  - url = `https://sartrix.wordpress.com/the-oxford-hermetica/`
- Footer stays `"{bookTitle} | {key} | {translator}"`.
- Not-found example: `/oh 1`.

### 8.4 `/emeraldtablet` — The Emerald Tablet

**No options.** `emeraldtablet.json` holds the whole text in a single `"message"`
field. Always replies with an embed: description = `message`, footer =
`"{bookTitle} | 12th Century Latin Version"` — the string `"12th Century Latin
Version"` is **hardcoded**, not from `translator`. Command description =
`"Lookup {bookTitle}"`.

### 8.5 `/sepher-yetzirah` — Sepher Yetzirah

`sepher-yetzirah.json` is flat (`"1.1"` etc.) but also has a `"path"` key whose value
is a nested object keyed `"1"`–`"32"` (the 32 paths of wisdom).

Two string options:
- `part` — **required** — description `chapter#.line#`
- `path` — **optional** — description `(optional) 1-32`

Logic (replicate exactly):
1. Read `part` and `path`. Apply `:` → `.` to `part`.
2. **If `part` == the literal string `"path"`:** look up `bookRef["path"][path]`.
   Found → body = that value; else → not-found message.
3. **Else:** look up `bookRef[part]` directly. Found → body; else → not-found.
4. Not-found message:
   `"**Not found**\ntry: \`/sepher-yetzirah  1.1\`\nor: \`/sepher-yetzirah path 1\`"`.
5. Footer: `"{bookTitle} | {part} {path} | {translator}"`. `path` may be absent —
   the original concatenates it regardless; in Python render an **empty string**
   where the value is `None` (not the literal `"None"`).

Usage: `/sepher-yetzirah part:1.1` for a verse, or
`/sepher-yetzirah part:path path:7` for the 7th path.

### 8.6 `/bible` — The King James Bible

`bible.json` is **nested**: top level `"BOOK_NAME"` (uppercase, e.g. `"GENESIS"`,
`"REVELATION"`) → `{ "chapter.verse" -> text }`, plus the `bookTitle`/`translator`
metadata.

Two **required** string options:
- `book` — description `ie. genesis`
- `chapterverse` — description `ie. 1.1`

Logic:
1. Uppercase the `book` input. Apply `:` → `.` to `chapterverse`.
2. **Random support — the literal `X`:**
   - If uppercased `book` == `"X"`: pick a random top-level key of `bible.json`,
     **excluding `"bookTitle"` and `"translator"`**, and use it as `book`.
   - If `chapterverse` == `"X"`: pick a random key of `bookRef[book]`.
3. Look up `bookRef[book][chapterverse]`. Found → body; else → body =
   `"**Not found**\ntry: \`/bible genesis 1.1\`"`.
4. Footer: `"{bookTitle} | {book}  {chapterverse}"` — two spaces between book and
   verse, and **no translator**.

Usage: `/bible book:genesis chapterverse:1.1`, or `/bible book:X chapterverse:X` for
a fully random verse.

### 8.7 `/tarot` — Rider-Waite-Smith Tarot pull

One **optional** string option `card`, description `(optional) number of card (0-77)`.

The original hardcodes an array of **78 image URLs** in the command; `tarot.json`
holds the same 78 URLs keyed `"1"`–`"78"`. Use either source — copy the array
verbatim. Canonical order: 22 Major Arcana (`ar00`–`ar21`), then Wands, Cups,
Swords, Pentacles — each suit being King, Queen, Knight, Page, 10..2, Ace —
all `https://www.sacred-texts.com/tarot/pkt/img/...jpg` URLs.

Logic:
- `card` provided → show `cardArr[int(card)]` (0-indexed). The original does **no**
  bounds checking; an out-of-range value raises an error caught by the global guard.
  (Adding bounds checking is an allowed deviation — see section 11.)
- `card` omitted → pick a uniformly random card.
- Reply with an embed: color `#f15b40`, `image` = the chosen URL. No description, no
  footer.

### 8.8 `/help` — list all texts

No options. Description: `"List the texts Poimandres can access"`. Replies
**ephemerally** with one static embed:
- color `#f15b40`
- description: `"The Poimandres Discord bot quotes a variety of texts themed around
  religion, the occult, and the esoteric.\nYou can access them with the following
  slash commands:"`
- a series of embed **fields** grouped by section headers. Most fields are
  `inline=True`; the section-header fields use a zero-width-space name (`​`):

  - Header — name `​`, value `**Hermetic Texts:**`
  - `` `/ch` `` → `The Corpus Hermeticum\nfrom \`1.1\` to \`18.16\`\nTaken from *Thrice-Greatest Hermes Vol. 2*\nTranslated by G.R.S Mead (1906)`
  - `` `/ah` `` → `Asclepius\nfrom \`1\` to \`42\`\nTaken from *Thrice-Greatest Hermes Vol. 2*\nTranslated by G.R.S Mead (1906)`
  - `` `/emeraldtablet` `` → `The Emerald Tablet\n*12th Century Latin version*\nTranslated by Steele and Singer (1928)`
  - `` `/dh` `` → `The Definitions\nHermes to Asclepius\nfrom \`1.1\` to \`10.7\`\nTranslated by Jean-Pierre Mahé (1999)`
  - `` `/oh` `` → `The Oxford Fragments\nfrom \`1\` to \`5\`\nTranslated by Sartrix`
  - Header — name `​`, value `**Other Religious/Occult/Esoteric Texts:**`
  - `` `/quran` `` → `The Qur'an\nfrom \`1.1\` to \`114.6\`\nTranslated by Sahih International`
  - `` `/bible` `` → `The Bible\nfrom \`genesis 1.1\` to \`revelation 22.21\`\nKing James Version`
  - `` `/sepher-yetzirah` `` → `Sepher Yetzirah\nfrom \`1.1\` to \`6.4\`\n*or* \`/sepher-yetzirah path\` from \`1\` to \`32\`\nTranslated by W.W. Wescott (1887)`
  - `` `/al` `` → `Liber AL vel Legis or, *The Book of the Law*\nfrom \`1.1\` to \`3.75\`\nBook by Aiwass, Aleister Crowley, and Rose Edith Kelly (1904)`
  - `` `/enchiridion` `` → `Epictetus' Enchiridion\nfrom \`1\` to \`51\`\nTranslated by Thomas W. Higginson`
  - `` `/aurelius` `` → `Marcus Aurelius' Meditations\nfrom \`1.1\` to \`12.27\`\nTranslated by Meric Casaubon`
  - `` `/proclus-metaphysics` `` → `Proclus' Elements of Metaphysics\nfrom \`1\` to \`211\`\nTranslated by Antonio Vargas (2021)`
  - Header — name `​`, value `**Other tools:**`
  - `` `/tarot` `` → `Rider-Waite-Smith Tarot Card pull\n\`/tarot\` for a random card\n\`/tarot 0-77\` for a specific card`
  - `` `/contents` `` → `Select a text from a drop-down menu.\n(Nobody else sees this but you)`
- footer text: `"Poimandres Discord Bot • /help"`
- a timestamp (current time).

The original `/help` does **not** list `/yoga`. Keeping the gap is parity; adding a
`/yoga` field (`Yoga Sūtras of Patañjali`) is an allowed deviation — see section 11.

### 8.9 `/contents` — dropdown text picker

No options. Description: `"Get a "contents page" of the available texts"`. Replies
**ephemerally** with a message containing a **select menu** (dropdown), no embed.
- select menu `custom_id` = `"contentsSelect"`, placeholder `"Select a text..."`.
- options come from `LIBRARY.json` — a JSON array of `{ "label", "value" }`. Each
  becomes a select option (label shown to user, value = the book's command/JSON
  name). `LIBRARY.json` has 13 entries: `ah, bible, ch, dh, emeraldtablet,
  enchiridion, al, aurelius, oh, proclus-metaphysics, quran, sepher-yetzirah, tarot`
  with human-readable labels.

Selection handling is in section 9.

---

## 9. Reference: central interaction handling (replaces `index.js`)

The original `index.js`:
1. Creates a Discord client with the `GUILDS` intent only.
2. Dynamically loads every `.js` file in `commands/` into a name→command map.
3. On `ready`: prints a UTC timestamp, a large ASCII-art "poimandres" banner, the
   guild count, and one line per guild (`name | Members: count`).
4. On `interactionCreate`:
   - **Slash command:** look up by name, log `"{commandName} request at {guildName}
     by {memberDisplayName}"` (or `"{commandName} request in DM"` outside a guild),
     run its `execute`. On exception: log it and reply ephemerally `"There was an
     error while executing this command!"`.
   - **Select-menu interaction:** check `custom_id`.
     - `custom_id == "contentsSelect"` (the `/contents` dropdown). The selected value
       is a book name:
       1. Log `"{value} selected by {memberDisplayName}"` (or `in DM`).
       2. Load `books/{value}.json`.
       3. Take all its keys.
       4. Join them comma-separated, then `replaceAll(",", "\` \`")` so they render
          as inline-code chips, then `replaceAll("bookTitle", "")` and
          `replaceAll("translator", "")` to blank the metadata keys.
       5. Body text: `` `/{value}` `` + `" + *one of the following:*\n"` + the
          backtick-wrapped key list.
       6. **Length cap:** if the body exceeds 950 characters, truncate to the first
          901 chars and append `" ***... Discord message limit exceeded.***"`.
       7. Reply ephemerally with that text.
     - Any other `custom_id`: reply ephemerally `"**UNDER DEVELOPMENT** *This menu
       doesn't lead to anywhere yet*"`.
   - Any other interaction type: ignore.
5. Logs in with the token.

Recreate this in `bot.py`. In `discord.py`:
- `intents = discord.Intents.default()` with at least `guilds`. The members intent
  is **not** required — `member.displayName` logging comes from the interaction
  payload, exposed as `interaction.user.display_name`.
- Slash dispatch is automatic via the `CommandTree`; the "look up by name" loop is
  implicit. Keep the per-invocation log line.
- Wire the select-menu logic via either a persistent `discord.ui.View` with a
  `discord.ui.Select`, or a raw `on_interaction` listener. The persistent-View
  approach is idiomatic; attaching a fresh view each time `/contents` runs avoids
  persistence concerns.
- Reproduce the `on_ready` console output: UTC timestamp, the ASCII banner (copy it
  verbatim from `index.js` — it spells "poimandres"), guild count, per-guild lines.

---

## 10. Reference: registration, utilities, and README

### 10.1 Slash-command registration (replaces `deploy-commands.js`)

The original registers commands both **globally** and to a **development guild**
(guild commands appear instantly; global commands take up to an hour to propagate).

In `discord.py`: sync the `CommandTree` — `await tree.sync()` for global,
`await tree.sync(guild=discord.Object(id=DEV_GUILD_ID))` for the guild. Put the dev
guild ID in `.env`. Sync inside `setup_hook`/`on_ready`, or provide a standalone
`deploy_commands.py` that syncs and exits. Do not hardcode the original author's IDs
(section 6, item 6).

### 10.2 Server-count utility (replaces `server-count.js`)

`server_count.py` — a minimal standalone script that logs in, prints the banner +
per-guild list (`name | Members: count`) + total count on `ready`, then exits.
Low priority; include for completeness.

### 10.3 Convenience scripts

The original ships Windows `.bat` files (`runthebot.bat`, `update-command-list.bat`,
`count servers.bat`). Replace with a cross-platform README "Running" section, and
optionally a `Makefile` or `run.sh`/`deploy.sh`. Not required for parity.

### 10.4 README

Write `README.md` containing:
- The epigraph: *"I am Poimandres, Mind of all-masterhood; I know what thou desirest
  and I'm with thee everywhere."* — *The Corpus Hermeticum 1.2*
- A description: a Discord bot quoting esoteric/occult/religious/philosophical texts
  via slash commands.
- The list of texts (Hermetic: Corpus Hermeticum, Asclepius, Emerald Tablet,
  Definitions of Hermes to Asclepius, Oxford Fragments; Other: Bible, Qur'an, Book of
  the Law, Enchiridion, Meditations, Proclus' Elements of Metaphysics, Sepher
  Yetzirah, Yoga Sūtras of Patañjali; plus Tarot pulls).
- A note that `/help` lists all commands in-server.
- **Setup instructions:** create a Discord application + bot, enable it, invite with
  the `applications.commands` + `bot` scopes, put the token in `.env`, install
  `requirements.txt`, run the bot.

---

## 11. Allowed deviations

These are the **only** permitted departures from the original. Taking either is
optional; if you do, record it in the final report (section 4.3).

1. **Add `/yoga` to `/help`.** The original `/help` omits `/yoga` though the command
   exists. Adding a `Yoga Sūtras of Patañjali` field is a reasonable fix.
2. **Bounds-check `/tarot`.** The original does no bounds checking on the `card`
   number. Adding a graceful out-of-range message instead of relying on the global
   error guard is acceptable.

---

## 12. Acceptance checklist

The recreated bot is correct when every box can be honestly checked:

- [ ] All 16 slash commands exist, named exactly: `ch, ah, dh, oh, emeraldtablet,
      bible, quran, sepher-yetzirah, al, enchiridion, aurelius, proclus-metaphysics,
      yoga, tarot, help, contents`.
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
      replies ephemerally with the valid lookup keys for that text, with
      `bookTitle`/`translator` blanked out, capped at the 950-char limit.
- [ ] `/help` and `/contents` reply ephemerally; all other replies are public.
- [ ] Exceptions during a command produce the ephemeral error message and a console
      log, never crashing the bot.
- [ ] The bot token and IDs come from `.env` / env vars and are gitignored — nothing
      secret is committed.
- [ ] On startup the console prints the timestamp, ASCII banner, and per-guild list.
- [ ] Tests cover every text-lookup command and the central interaction handler;
      the `CLAUDE.md` quality gate passes.

When done, summarize any intentional deviations (section 11) in the final report.
```
