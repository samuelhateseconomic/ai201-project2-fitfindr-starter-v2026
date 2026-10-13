# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr helps a shopper search thrift listings by description, size, and price, then choose the strongest match from the results. Once a listing is selected, the app builds outfit ideas from the user’s wardrobe and turns that into a post-ready fit card. The user can run the same flow from the terminal with `app.py` or inspect the data model with `listings` and `fields` before asking a question.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** This tool is intended to find listings related to a product description. It filters out listings that do not match the requested size or exceed the price limit, then ranks the remaining listings by keyword overlap with the description.
- **Inputs:** It takes a `description` (string), and optionally a `size` (string) and `max_price` (float, in dollars).
- **Returns:** A list of matching listing dictionaries, ranked by keyword overlap and limited to the configured result limit. Each dictionary contains listing details such as its title, description, size, price, colors, and platform.
- **When it has nothing:** Returns an empty list (`[]`) if nothing matches.

### `suggest_outfit`

- **What it does:** Suggests one or two ways to style the thrift listing with clothes the user already owns.
- **Inputs:** `new_item` (dict), one listing the user is considering; `wardrobe` (dict), containing an `items` list of the user's clothing and accessories.
- **Returns:** A non-empty string with outfit suggestions that use pieces from the wardrobe when available.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns general styling advice for `new_item` instead of an empty string.

### `create_fit_card`

- **What it does:** Writes a short, post-ready caption about the thrift find and a suggested outfit.
- **Inputs:** `outfit` (str), the suggestion from `suggest_outfit`; `new_item` (dict), one listing containing the item's details.
- **Returns:** A two-to-four-sentence caption that mentions the item, its price, and its platform, and describes its style.
- **When it has nothing:** If `outfit` is empty or only whitespace, returns a descriptive fallback message.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If the MCP `search_listings` call returns an empty list, put a message in `session["error"]` explaining what the user could change, then stop before calling `suggest_outfit`. Otherwise, save the first (highest-ranked) result as `session["selected_item"]`, pass it and the wardrobe to `suggest_outfit`, then pass the item and outfit suggestion to `create_fit_card`. If either model-backed tool raises `ModelUnavailable`, save its actionable message in `session["error"]`, trace the failed tool result, and stop — `agent.py::run_agent`.

**How the query is parsed:** Regular expressions extract an optional size and a dollar cap; the remaining words become the product description.

**What moves through the session:** Store the original `query` and `wardrobe`, then the parsed description, size, and price in `session["parsed"]`. Store search results in `session["search_results"]`. If there is a match, pass the first result through `session["selected_item"]`, `session["outfit_suggestion"]`, and finally `session["fit_card"]`. If there are no matches, store an explanation in `session["error"]` and stop before the later fields are filled.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked the AI to help me define the `search_listings` behavior and edge cases before I wrote the function, especially what happened when a query matched nothing.
- *What came back:* It suggested the tool should return an empty list rather than `None` or an exception, and it also reminded me to handle size and price filtering before keyword scoring.
- *What I changed:* I updated the implementation so `search_listings` returns `[]` on no matches, filters by max price and size before ranking, and keeps the loop branch safe: no model call runs when the search is empty.

**Moment 2**

- *What I asked for:* I asked the AI to help me turn the branch logic into a concrete session-based loop, including which values should be stored and what the no-results message should say.
- *What came back:* It proposed storing everything in `session["parsed"]`, `session["search_results"]`, and `session["selected_item"]` and said the error message should tell the user what to change instead of just saying "No results."
- *What I changed:* I changed `run_agent` so it parses the query, writes the values into the session, stops early on the empty-search branch, and returns a message like "No listings matched that request. Try a broader description, a different size, or a higher budget." This made the state visible and testable.

---

## Run Log — Before

Command: `python run_eval.py --label before`
Produced by `run_eval.py::main` / `run_eval.py::run_once`, which call
`agent.py::run_agent`; five tries per scenario, cache off. The full captured
output is in [results/run_2026-10-13_1606_before.md](results/run_2026-10-13_1606_before.md).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item remains consistent through the loop | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card is 2–4 sentences and mentions price and platform | 5 of 5 | PASS | PASS | PASS | PASS | FAIL | MISSED (4/5) |
| 5. Empty wardrobe produces a non-empty suggestion | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

The run report records a selected item on every matching try. In
`agent.py::run_agent`, that same `session["selected_item"]` is passed to both
`suggest_outfit` and `create_fit_card`. Fit-card try 5 omitted the platform,
so criterion 4 missed its target despite all five cards mentioning the $18
price and meeting the sentence-count requirement. Try 4 did mention Depop.

**Real output — Criterion 1, Try 1** (`run_eval.py::run_once` calling
`agent.py::run_agent`):

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10
Fit card:
Okay but this butterfly tee is literally straight out of a 2000s music video 🦋✨ Only $18 on my Depop so grab it before I change my mind and keep it for myself. Pair it with baggy low-rise denim or khaki cargos and combat boots for the ultimate pop-star-off-duty vibe.
```

**Real output — Criterion 2, Try 1** (`agent.py::run_agent` trace and session):

```
[2] search_listings (via MCP)
      out: [] (empty)
      →    branch: empty list stops; otherwise continue with the first result
- stopped early: yes — No listings matched that request. Try a broader description, a different size, or a higher budget.
- selected_item: (none)
- search_results: 0
```

**Real output — Criterion 3, Try 1** (`agent.py::run_agent` session and tool trace):

```
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
[5] create_fit_card
      in:  dict with keys: outfit, new_item
```

The implementation passes `session["selected_item"]` as `new_item` to both
tools; the recorded selected item was the same on all five tries.

**Real output — Criterion 4, Try 1** (`tools.py::create_fit_card` via
`agent.py::run_agent`):

```
Okay but this butterfly tee is literally straight out of a 2000s music video 🦋✨ Only $18 on my Depop so grab it before I change my mind and keep it for myself. Pair it with baggy low-rise denim or khaki cargos and combat boots for the ultimate pop-star-off-duty vibe.
```

Try 5’s card omitted the platform:

```
Found the ultimate 2000s butterfly baby tee for just $18 and I’m never taking it off. Gives major model-off-duty energy when paired with baggy low-rise denim, but it's just as cute dressed down with khaki trousers. Grab it before I change my mind and keep it for myself! 🦋✨
```

**Real output — Criterion 5, Try 1** (`tools.py::suggest_outfit` via
`agent.py::run_agent`, empty wardrobe):

```
Oh, what a find! A butterfly print baby tee is the ultimate Y2K holy grail. Since it’s cropped and fitted (and runs a bit small), the key is balancing the proportions while leaning fully into that nostalgic, effortless 2000s energy.

Here are two specific, highly wearable ways to style your new favorite top:
```

The report contains the complete suggestion and all five tries for each criterion.

---

## Run Log — After

**One change:** in `tools.py::create_fit_card`, I made the prompt explicitly
require the caption to name the listing platform exactly as provided and forbid
omitting or replacing it with a generic phrase. No other behavior or prompt was
changed.

Command: `python run_eval.py --label after`
Produced by `run_eval.py::main` / `run_eval.py::run_once`, calling
`agent.py::run_agent`; five tries per scenario, cache off. Full captured
output is in [results/run_2026-10-13_1618_after.md](results/run_2026-10-13_1618_after.md).

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The selected item remains consistent through the loop | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card is 2–4 sentences and mentions price and platform | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Empty wardrobe produces a non-empty suggestion | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real post-change outputs** (`run_eval.py::run_once` calling
`agent.py::run_agent`):

- Criterion 1, Try 1: selected “Y2K Baby Tee — Butterfly Print” ($18.0,
  depop); search, outfit suggestion, and fit card all completed.
- Criterion 2, Try 1: `stopped early: yes — No listings matched that request.
  Try a broader description, a different size, or a higher budget.`
- Criterion 3, Try 1: selected “Y2K Baby Tee — Butterfly Print” ($18.0,
  depop); `agent.py::run_agent` passed `session["selected_item"]` to both
  `suggest_outfit` and `create_fit_card`.
- Criterion 4, all five actual fit cards from `tools.py::create_fit_card`:

```
1. Scored this absolute dream Y2K Baby Tee — Butterfly Print on depop for $18. It’s giving major 2000s model-off-duty, especially when paired with baggy dark wash denim and chunky sneakers. Such a nostalgic little find!
2. Still not over this Y2K Butterfly Baby Tee I manifested on depop for just $18. It's giving total early 2000s pop star off-duty, whether I style it with baggy dark wash denim or edgy combat boots. Such a good little score!
3. Manifesting warm weather just so I can wear this Y2K Butterfly Baby Tee on repeat. Found it on depop for $18 and honestly, the nostalgic print is giving all the effortless 2000s vibes I've been looking for. Can't wait to style this with baggy denim or wide-leg trousers for the ultimate off-duty look!
4. Found the ultimate Y2K Baby Tee — Butterfly Print on depop for just $18! I’m totally obsessed with how fitted it is and already styling it with baggy jeans and my black zip-up for that ultimate early 2000s streetwear vibe. Thrift gods seriously delivered with this one. ✨🦋
5. Found the ultimate Y2K butterfly baby tee scrolling on depop for just $18, and I am obsessed. The fit is so flattering and it instantly gives off that effortless early-2000s model-off-duty vibe. Can't wait to style this with some baggy denim!
```

- Criterion 5, Try 1: `tools.py::suggest_outfit` returned a non-empty
  two-outfit styling suggestion for the selected tee with an empty wardrobe;
  the complete suggestion is in the linked after-run report.

**Did it help?** Yes, for this measured run. Criterion 4 improved from 4/5
before to 5/5 after, meeting its target. The other four criteria remained at
5/5. This is evidence from five uncached fit-card tries, not a guarantee for
future model outputs; the prompt still depends on the model following its
instructions.

---

## Loop Trace

**Happy path**

Command: `python app.py ask 'vintage graphic tee under $30' --trace`

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    regex extraction for description, size, and max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    branch: empty list stops; otherwise continue with the first result
[3] select_item
      in:  dict with keys: search_results
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
      →    first ranked result becomes selected_item
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Here are two concrete outfit suggestions that balance the Y2K aesthetic of your new baby tee with pieces alrea…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Found the holy grail of Y2K baby tees for only $18 🦋 Obsessed with the butterfly print and how cropped it is. …
```

## Failure Checks

**Empty search** — `python app.py ask 'designer ballgown size XXS under $5' --trace`

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
      →    regex extraction for description, size, and max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty list stops; otherwise continue with the first result
```

Agent message: “No listings matched that request. Try a broader description, a different size, or a higher budget.”

**Empty wardrobe** — `python app.py ask 'vintage graphic tee under $30' --empty-wardrobe --trace`

Agent message: “Ooh, a butterfly print baby tee is the ultimate Y2K grail find! Since it runs small and is cropped, we want to lean into that quintessential early 2000s silhouette while keeping it wearable for today. Here are two distinct outfit ideas for your thrifted tee:” It then gave two specific outfits and a fit card; the suggestion was non-empty and the run did not crash.

**Model unavailable** — tested with caching disabled and a temporary invalid `GEMINI_API_KEY` process variable using the uncached query `vintage band tee under $27`; `.env` was not changed.

Agent message: “Model unavailable: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.”

---

## The Improvement

**What I changed:** I routed the search through `mcp_client.call_tool` and added `ModelUnavailable` handlers around both model-backed tools. Failed model calls now put an actionable message in `session["error"]`, record the failed tool in the trace, and return the session instead of bubbling an exception out of the agent.

**Which failure it was meant to fix:** A model outage or rejected key previously aborted the agent before it could return a session or trace the failed tool result. The empty-search check still stops before model calls, and all search results now arrive through the MCP boundary.

## Before-run Verdicts and Diagnosis

Criteria 1, 2, 3, and 5 **MET** their targets (5/5 each; criterion 1 required
4/5). Criterion 4 **MISSED** its 5/5 target with 4/5 passes.

The miss occurred at the `create_fit_card` step: on try 5, the generated
caption mentioned the $18 price and styling but did not name Depop, the
platform in the selected listing. `tools.py::create_fit_card` includes the
platform in the model prompt, but relies on generated prose to repeat it; the
model treated that detail as optional. This is a model-output reliability
problem in that one tool, not a search, branch, or session-state failure. The
other four cards named Depop, including try 4 (“only $18 on my Depop”).
The criterion is measurable and tests the intended contract, so it remains
unchanged; the missed try is not a reason to lower the target.

---

## What's Still Broken

The before run missed criterion 4, but after the prompt change it passed all
five uncached tries. No criterion missed its target in the after run. The
model can still vary on future inputs, so the fit-card requirement should
continue to be checked in later evaluations. The MCP server is registered and
the agent's search uses it.

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
