"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""
import re
import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    The query parser uses a compact regex approach: it extracts an optional size
    and a price cap, then treats the remaining words as the description.
    """
    trace.start_trace()
    session = new_session(query, wardrobe)

    size_match = re.search(r"\b(?:size|sz)\s*[:=]?\s*([A-Za-z0-9/]+)", query, re.I)
    size = size_match.group(1).strip() if size_match else None

    max_price = None
    price_match = re.search(r"\b(?:under|max(?:imum)?|budget|up\s+to)\s*\$?\s*(\d+(?:\.\d+)?)\b", query, re.I)
    if price_match:
        max_price = float(price_match.group(1))
    else:
        price_match = re.search(r"\$\s*(\d+(?:\.\d+)?)\b", query, re.I)
        if price_match:
            max_price = float(price_match.group(1))

    description = query
    if size_match:
        description = description[: size_match.start()] + description[size_match.end():]
    if price_match:
        description = description[: price_match.start()] + description[price_match.end():]

    description = re.sub(r"\b(?:looking|for|a|an|the|want|need|find|search(?:ing)?)\b", " ", description, flags=re.I)
    description = " ".join(part for part in re.findall(r"[A-Za-z0-9'/-]+", description) if part)
    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }
    trace.step(
        "parse_query",
        inputs={"query": query},
        returned=session["parsed"],
        note="regex extraction for description, size, and max_price",
    )

    iteration = 0
    while True:
        iteration += 1
        trace.check_iterations(iteration)

        session["search_results"] = search_listings(
            description=session["parsed"]["description"],
            size=session["parsed"]["size"],
            max_price=session["parsed"]["max_price"],
        )
        trace.step(
            "search_listings",
            inputs={
                "description": session["parsed"]["description"],
                "size": session["parsed"]["size"],
                "max_price": session["parsed"]["max_price"],
            },
            returned=session["search_results"],
            note="branch: empty list stops before outfit generation",
        )

        if not session["search_results"]:
            session["error"] = (
                "No listings matched that request. Try a broader description, "
                "a different size, or a higher budget."
            )
            return session

        session["selected_item"] = session["search_results"][0]
        trace.step(
            "select_item",
            inputs={"search_results": session["search_results"]},
            returned=session["selected_item"],
            note="first ranked result becomes selected_item",
        )

        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"],
            session["wardrobe"],
        )
        trace.step(
            "suggest_outfit",
            inputs={"new_item": session["selected_item"], "wardrobe": session["wardrobe"]},
            returned=session["outfit_suggestion"],
        )

        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"],
            session["selected_item"],
        )
        trace.step(
            "create_fit_card",
            inputs={"outfit": session["outfit_suggestion"], "new_item": session["selected_item"]},
            returned=session["fit_card"],
        )
        return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    happy = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    print("session:", happy)
    _show(happy)

    print("\n=== A query it can't ===")
    empty = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print("session:", empty)
    _show(empty)

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
