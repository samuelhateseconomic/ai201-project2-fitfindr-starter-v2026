"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am",
    "an", "and", "any", "are","as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "could", "did", "do", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having",
    "he", "her", "here", "hers", "him", "his", "how", "i", "if", "in",
    "into", "is", "it", "its", "just", "me", "more", "most", "my",
    "nor", "of", "on", "once", "only", "or", "other", "our", "ours",
    "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under",
    "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "while", "who", "whom", "why", "will", "with", "would", "you", "your",
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return { w for w in words if w not in _STOPWORDS and len(w) >1 }

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return { p for p in parts if p }

def _size_matches(wanted: str, listing_size:str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    if not description or not str(description).strip():
        return []

    target_words = _keywords(description)
    if not target_words:
        return []

    matched = []
    for listing in load_listings():
        if max_price is not None and float(listing.get("price", float("inf"))) > float(max_price):
            continue

        if size and not _size_matches(size, listing.get("size", "")):
            continue

        pool = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
            listing.get("category", ""),
        ])
        listing_words = _keywords(pool)
        score = sum(1 for word in target_words if word in listing_words)
        if score > 0:
            matched.append((score, listing))

    matched.sort(key=lambda pair: (-pair[0], pair[1].get("price", 0)))
    return [listing for _, listing in matched[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    if not isinstance(new_item, dict):
        new_item = {}

    wardrobe_items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []

    if not wardrobe_items:
        item_title = new_item.get("title", "this thrifted item")
        item_category = new_item.get("category", "")
        item_color = ", ".join(new_item.get("colors", [])) or "neutral tones"
        item_desc = new_item.get("description", "")
        prompt = (
            f"Give me 1-2 outfit ideas for this thrifted item. "
            f"Item: {item_title}. "
            f"Category: {item_category}. "
            f"Colors: {item_color}. "
            f"Description: {item_desc}. "
            "Keep the suggestions specific and wearable, and mention the overall vibe."
        )
        return generate(prompt, system="You are a fashion stylist helping someone style a thrifted item.")

    wardrobe_text = "\n".join(
        f"- {item.get('name', 'Unknown')} ({item.get('category', 'item')}, colors: {', '.join(item.get('colors', [])) or 'unknown'})"
        for item in wardrobe_items
    )

    prompt = (
        "Suggest 1-2 outfits that pair this thrifted item with the user's existing wardrobe. "
        f"New item: {new_item.get('title', 'Unknown item')} "
        f"({new_item.get('category', '')}, {new_item.get('size', 'size unknown')}, "
        f"${new_item.get('price', 'unknown')}).\n"
        f"Description: {new_item.get('description', '')}\n"
        f"Wardrobe:\n{wardrobe_text}\n"
        "Keep the suggestions concrete, specific, and grounded in the pieces the user already owns."
    )
    return generate(prompt, system="You are a fashion stylist.")


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not isinstance(outfit, str) or not outfit.strip():
        item_title = new_item.get("title", "This thrifted item") if isinstance(new_item, dict) else "This thrifted item"
        return (
            f"{item_title} feels like a standout find. "
            "I’d wear it for a laid-back, easy look and style it with a fresh pair of basics."
        )

    item_title = new_item.get("title", "this item") if isinstance(new_item, dict) else "this item"
    item_price = new_item.get("price", "unknown") if isinstance(new_item, dict) else "unknown"
    item_platform = new_item.get("platform", "unknown") if isinstance(new_item, dict) else "unknown"

    prompt = (
        "Write a short caption someone would actually post about this thrift find. "
        f"Item: {item_title}. "
        f"Price: ${item_price}. "
        f"Platform: {item_platform}. "
        f"Outfit: {outfit}. "
        "Keep it to 2-4 sentences, sound like a real person, and be specific about the vibe."
    )
    return generate(prompt, system="Write natural social captions about thrift finds.")
