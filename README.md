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
- **Inputs:** It takes a `description` (string) and `size` (string) and `maximum price` (float).
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

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` explaining what the user could change, then stop before calling `suggest_outfit`. Otherwise, save the first (highest-ranked) result as `session["selected_item"]`, pass it and the wardrobe to `suggest_outfit`, then pass the item and outfit suggestion to `create_fit_card` — `agent.py::run_agent`.

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

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|-----------|--------|-------|-------|-------|-------|-------|---------|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 3. Something about state | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 4. Something about the fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. Empty wardrobe path | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
=== HAPPY ===
error= None
selected= Y2K Baby Tee — Butterfly Print
fit_card= Found the holy grail of Y2K baby tees for only $18 🦋 Obsessed with the butterfly print and how cropped it is. Literally going to wear this with baggy low-rise jeans and chunky sneakers on heavy rotation.
=== EMPTY ===
error= No listings matched that request. Try a broader description, a different size, or a higher budget.
selected= None
fit_card= None
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** I wired the agent loop in `agent.py::run_agent` to parse the query, write the parsed values into the session, call `search_listings`, and stop early on the empty-search branch instead of continuing into `suggest_outfit`.

**Which failure it was meant to fix:** The only real failure mode here was a missing branch: the loop was not checking `session["search_results"]` before advancing to the model, and it was not storing the selected item in a visible session state.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 3. Something about state | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 4. Something about the fit card | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |
| 5. Empty wardrobe path | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET |

**Did it help, and how do I know:** It helped because the happy path completes correctly and the empty-search path exits before the second tool. The real output below shows the selected item staying in the session and the no-results error stopping the flow before `fit_card` is set.

``` 
=== HAPPY ===
error= None
selected= Y2K Baby Tee — Butterfly Print
fit_card= Found the holy grail of Y2K baby tees for only $18 🦋 Obsessed with the butterfly print and how cropped it is. Literally going to wear this with baggy low-rise jeans and chunky sneakers on heavy rotation.
=== EMPTY ===
error= No listings matched that request. Try a broader description, a different size, or a higher budget.
selected= None
fit_card= None
``` 

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
