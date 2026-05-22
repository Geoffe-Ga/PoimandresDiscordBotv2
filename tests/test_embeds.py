"""Tests for the pure embed builders."""

from poimandres import embeds
from poimandres.books import load_book
from poimandres.books import text_keys
from poimandres.constants import EMBED_COLOR
from poimandres.help_content import HELP_FIELDS
from poimandres.tarot_cards import TAROT_CARDS


def test_canonical_key_normalizes_colon() -> None:
    assert embeds.canonical_key("1:2") == "1.2"


def test_canonical_key_strips_leading_zeros() -> None:
    assert embeds.canonical_key("01.02") == "1.2"


def test_canonical_key_accepts_whitespace_and_dash() -> None:
    assert embeds.canonical_key("  1 - 2 ") == "1.2"


def test_canonical_key_accepts_comma_and_semicolon() -> None:
    assert embeds.canonical_key("1,2") == "1.2"
    assert embeds.canonical_key("1;2") == "1.2"


def test_canonical_key_empty_input() -> None:
    assert embeds.canonical_key("") == ""
    assert embeds.canonical_key("   ") == ""


def test_canonical_key_lowercases_non_digit_segments() -> None:
    assert embeds.canonical_key("Path") == "path"


def test_resolve_key_finds_exact_match() -> None:
    assert embeds.resolve_key(load_book("ch"), "1.1") == "1.1"


def test_resolve_key_finds_lenient_match() -> None:
    book = load_book("ch")
    assert embeds.resolve_key(book, "1:1") == "1.1"
    assert embeds.resolve_key(book, "01.01") == "1.1"
    assert embeds.resolve_key(book, "1 1") == "1.1"
    assert embeds.resolve_key(book, "1-1") == "1.1"


def test_resolve_key_returns_none_for_missing() -> None:
    assert embeds.resolve_key(load_book("ch"), "999.999") is None


def test_resolve_key_returns_none_for_metadata() -> None:
    assert embeds.resolve_key(load_book("ch"), "bookTitle") is None


def test_resolve_key_returns_none_for_empty_input() -> None:
    assert embeds.resolve_key(load_book("ch"), "") is None


def test_flat_lookup_embed_hit() -> None:
    book = load_book("ch")
    embed = embeds.flat_lookup_embed(book, "1.1", "missing")

    assert embed.color is not None
    assert embed.color.value == EMBED_COLOR
    assert embed.description == book["1.1"]
    assert embed.footer.text == "The Corpus Hermeticum | 1.1 | G.R.S. Mead"


def test_flat_lookup_embed_normalizes_colon() -> None:
    book = load_book("ch")
    embed = embeds.flat_lookup_embed(book, "1:1", "missing")

    assert embed.description == book["1.1"]


def test_flat_lookup_embed_strips_leading_zeros() -> None:
    book = load_book("proclus-metaphysics")
    embed = embeds.flat_lookup_embed(book, "007", "missing")

    assert embed.description == book["7"]


def test_flat_lookup_embed_accepts_alternate_separators() -> None:
    book = load_book("ch")
    embed = embeds.flat_lookup_embed(book, "1 - 1", "missing")

    assert embed.description == book["1.1"]


def test_flat_lookup_embed_miss_uses_not_found() -> None:
    embed = embeds.flat_lookup_embed(load_book("ch"), "999", "**Not found**")

    assert embed.description == "**Not found**"
    assert embed.footer.text == "The Corpus Hermeticum | G.R.S. Mead"


def test_flat_lookup_embed_random_draws_real_passage() -> None:
    book = load_book("ch")
    embed = embeds.flat_lookup_embed(book, None, "missing")

    key = (embed.footer.text or "").split(" | ")[1]
    assert key in text_keys(book)
    assert embed.description == book[key]


def test_oxford_embed_adds_title_and_url() -> None:
    embed = embeds.oxford_embed(load_book("oh"), "1", "missing")

    assert embed.url == embeds.OXFORD_URL
    assert "Translated by" in (embed.title or "")


def test_oxford_embed_miss() -> None:
    embed = embeds.oxford_embed(load_book("oh"), "999", "**Not found**")

    assert embed.description == "**Not found**"
    assert embed.url == embeds.OXFORD_URL


def test_oxford_embed_random() -> None:
    book = load_book("oh")
    embed = embeds.oxford_embed(book, None, "missing")

    key = (embed.footer.text or "").split(" | ")[1]
    assert key in text_keys(book)
    assert embed.description == book[key]


def test_emerald_embed_uses_message_field() -> None:
    book = load_book("emeraldtablet")
    embed = embeds.emerald_embed(book)

    assert embed.description == book["message"]
    assert embed.footer.text.endswith("12th Century Latin Version")


def test_sepher_embed_direct_verse() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, "1.1", None)

    assert embed.description == book["1.1"]


def test_sepher_embed_lenient_verse() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, "1:1", None)

    assert embed.description == book["1.1"]


def test_sepher_embed_path_mode() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, "path", "1")

    assert embed.description == book["path"]["1"]


def test_sepher_embed_path_mode_random() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, "path", None)

    assert embed.description in book["path"].values()
    assert "path" in (embed.footer.text or "")


def test_sepher_embed_path_only_argument_acts_as_path_lookup() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, None, "2")

    assert embed.description == book["path"]["2"]


def test_sepher_embed_path_mode_no_path_dict() -> None:
    fake_book = {"bookTitle": "X", "translator": "Y", "1.1": "verse"}
    embed = embeds.sepher_embed(fake_book, "path", "1")

    assert embed.description == embeds.SEPHER_NOT_FOUND


def test_sepher_embed_path_mode_unknown_path() -> None:
    embed = embeds.sepher_embed(load_book("sepher-yetzirah"), "path", "999")

    assert embed.description == embeds.SEPHER_NOT_FOUND


def test_sepher_embed_missing_verse() -> None:
    embed = embeds.sepher_embed(load_book("sepher-yetzirah"), "999.999", None)

    assert embed.description == embeds.SEPHER_NOT_FOUND


def test_sepher_embed_random() -> None:
    book = load_book("sepher-yetzirah")
    embed = embeds.sepher_embed(book, None, None)

    key = (embed.footer.text or "").split(" | ")[1].strip()
    assert key in text_keys(book)
    assert embed.description == book[key]


def test_sepher_embed_footer_blank_path() -> None:
    embed = embeds.sepher_embed(load_book("sepher-yetzirah"), "1.1", None)

    assert " | 1.1  | " in (embed.footer.text or "")


def test_bible_embed_direct_lookup() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "genesis", "1.1")

    assert embed.description == book["GENESIS"]["1.1"]
    assert embed.footer.text == "The King James Bible | GENESIS  1.1"


def test_bible_embed_lenient_verse() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "genesis", "1:1")

    assert embed.description == book["GENESIS"]["1.1"]


def test_bible_embed_lenient_book_name() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "1 samuel", "1.1")

    assert embed.description == book["1SAMUEL"]["1.1"]


def test_bible_embed_missing_verse() -> None:
    embed = embeds.bible_embed(load_book("bible"), "genesis", "999.999")

    assert embed.description == embeds.BIBLE_NOT_FOUND


def test_bible_embed_invalid_book() -> None:
    embed = embeds.bible_embed(load_book("bible"), "notabook", "1.1")

    assert embed.description == embeds.BIBLE_NOT_FOUND


def test_bible_embed_empty_book_name() -> None:
    embed = embeds.bible_embed(load_book("bible"), "", "1.1")

    assert embed.description == embeds.BIBLE_NOT_FOUND


def test_bible_embed_random_book_via_x() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "X", "1.1")

    chosen = (embed.footer.text or "").split(" | ")[1].split("  ")[0]
    assert chosen in book
    assert chosen not in {"bookTitle", "translator"}


def test_bible_embed_random_verse_via_x() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "genesis", "X")

    verse = (embed.footer.text or "").split("  ")[-1]
    assert embed.description == book["GENESIS"][verse]


def test_bible_embed_random_book_via_none() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, None, "1.1")

    chosen = (embed.footer.text or "").split(" | ")[1].split("  ")[0]
    assert chosen in book
    assert chosen not in {"bookTitle", "translator"}


def test_bible_embed_random_verse_via_none() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, "genesis", None)

    verse = (embed.footer.text or "").split("  ")[-1]
    assert embed.description == book["GENESIS"][verse]


def test_bible_embed_fully_random() -> None:
    book = load_book("bible")
    embed = embeds.bible_embed(book, None, None)

    footer = embed.footer.text or ""
    chosen_book, verse = footer.split(" | ")[1].split("  ")
    assert isinstance(book.get(chosen_book), dict)
    assert embed.description == book[chosen_book][verse]


def test_tarot_embed_specific_card() -> None:
    embed = embeds.tarot_embed("0")

    assert embed.image.url == TAROT_CARDS[0]


def test_tarot_embed_random_card() -> None:
    embed = embeds.tarot_embed(None)

    assert embed.image.url in TAROT_CARDS


def test_tarot_embed_out_of_range() -> None:
    embed = embeds.tarot_embed("999")

    assert embed.description == embeds.TAROT_NOT_FOUND


def test_tarot_embed_non_numeric() -> None:
    embed = embeds.tarot_embed("abc")

    assert embed.description == embeds.TAROT_NOT_FOUND


def test_help_embed_has_every_field() -> None:
    embed = embeds.help_embed()

    assert len(embed.fields) == len(HELP_FIELDS)
    assert embed.footer.text == "Poimandres Discord Bot • /help"
    assert embed.timestamp is not None


def test_help_embed_lists_yoga() -> None:
    embed = embeds.help_embed()

    assert any(field.name == "`/yoga`" for field in embed.fields)


def test_contents_text_blanks_metadata_keys() -> None:
    text = embeds.contents_text("emeraldtablet", load_book("emeraldtablet"))

    assert "message" in text
    assert "bookTitle" not in text
    assert "translator" not in text


def test_contents_text_mentions_random_option() -> None:
    text = embeds.contents_text("ch", load_book("ch"))

    assert "nothing" in text


def test_contents_text_truncates_long_listings() -> None:
    text = embeds.contents_text("quran", load_book("quran"))

    assert text.endswith(embeds._CONTENTS_OVERFLOW)
    assert len(text) <= embeds._CONTENTS_TRUNCATE + len(embeds._CONTENTS_OVERFLOW)
