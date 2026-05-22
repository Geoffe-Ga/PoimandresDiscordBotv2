"""Static field content for the ``/help`` embed.

The text is copied verbatim from the original Node.js ``help.js``, with one
intentional addition: a ``/yoga`` field, which the original omitted even though
the command exists.
"""

_ZWS = "\u200b"
"""Zero-width space used as the name of section-header fields."""

HELP_DESCRIPTION = (
    "The Poimandres Discord bot quotes a variety of texts themed around "
    "religion, the occult, and the esoteric.\n"
    "You can access them with the following slash commands:"
)
"""Embed description shown above the command fields."""

HELP_FOOTER = "Poimandres Discord Bot • /help"
"""Footer text of the ``/help`` embed."""

HELP_FIELDS: list[tuple[str, str, bool]] = [
    (_ZWS, "**Hermetic Texts:**", False),
    (
        "`/ch`",
        "The Corpus Hermeticum\n"
        "from `1.1` to `18.16`\n"
        "Taken from *Thrice-Greatest Hermes Vol. 2*\n"
        "Translated by G.R.S Mead (1906)",
        True,
    ),
    (
        "`/ah`",
        "Asclepius\n"
        "from `1` to `42`\n"
        "Taken from *Thrice-Greatest Hermes Vol. 2*\n"
        "Translated by G.R.S Mead (1906)",
        True,
    ),
    (
        "`/emeraldtablet`",
        "The Emerald Tablet\n"
        "*12th Century Latin version*\n"
        "Translated by Steele and Singer (1928)",
        True,
    ),
    (
        "`/dh`",
        "The Definitions\n"
        "Hermes to Asclepius\n"
        "from `1.1` to `10.7`\n"
        "Translated by Jean-Pierre Mahé (1999)",
        True,
    ),
    (
        "`/oh`",
        "The Oxford Fragments\nfrom `1` to `5`\nTranslated by Sartrix",
        True,
    ),
    (_ZWS, "**Other Religious/Occult/Esoteric Texts:**", False),
    (
        "`/quran`",
        "The Qur'an\nfrom `1.1` to `114.6`\nTranslated by Sahih International",
        True,
    ),
    (
        "`/bible`",
        "The Bible\n"
        "from `genesis 1.1` to `revelation 22.21`\n"
        "King James Version",
        True,
    ),
    (
        "`/sepher-yetzirah`",
        "Sepher Yetzirah\n"
        "from `1.1` to `6.4`\n"
        "*or* `/sepher-yetzirah path` from `1` to `32`\n"
        "Translated by W.W. Wescott (1887)",
        True,
    ),
    (
        "`/al`",
        "Liber AL vel Legis or, *The Book of the Law*\n"
        "from `1.1` to `3.75`\n"
        "Book by Aiwass, Aleister Crowley, and Rose Edith Kelly (1904)",
        True,
    ),
    (
        "`/enchiridion`",
        "Epictetus' Enchiridion\nfrom `1` to `51`\nTranslated by Thomas W. Higginson",
        True,
    ),
    (
        "`/aurelius`",
        "Marcus Aurelius' Meditations\n"
        "from `1.1` to `12.27`\n"
        "Translated by Meric Casaubon",
        True,
    ),
    (
        "`/proclus-metaphysics`",
        "Proclus' Elements of Metaphysics\n"
        "from `1` to `211`\n"
        "Translated by Antonio Vargas (2021)",
        True,
    ),
    (
        "`/yoga`",
        "Yoga Sūtras of Patañjali\n"
        "from `1.1` to `4.34`\n"
        "Public-domain translation",
        True,
    ),
    (_ZWS, "**Other tools:**", False),
    (
        "`/tarot`",
        "Rider-Waite-Smith Tarot Card pull\n"
        "`/tarot` for a random card\n"
        "`/tarot 0-77` for a specific card",
        True,
    ),
    (
        "`/contents`",
        "Select a text from a drop-down menu.\n(Nobody else sees this but you)",
        True,
    ),
]
"""The ordered ``(name, value, inline)`` fields of the ``/help`` embed."""
