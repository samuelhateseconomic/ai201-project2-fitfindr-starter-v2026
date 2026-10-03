# Acceptance criteria — FitFindr

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
A matching query completes all three tools in at least 4 of 5 tries because the search is keyword-based and some valid phrasings will still miss. The loop is meant to succeed on the normal cases, not on every possible wording. 
---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
An impossible query stops before the second tool in 5 of 5 tries because the empty-search branch is the core safety check. If no listings match, the loop should end early instead of calling the model with a bad item.

---

## 3. Something about state

The selected item remains consistent through the loop: in 5 of 5 tries and match for all three tools.



**Why this target:**
Because state is not the model output itself. It is the saved values in the session between tool calls. In other words, the tool is working only if the session keeps the right data from one step to the next.


---

## 4. Something about the fit card

The fit card is a real caption, not a product description: in 5 of 5 tries, it is 2–4 sentences long, mentions the item’s price, and mentions the platform it was found on.

**Why this target:**
The model is allowed to vary, but the card still has to be usable as a post caption. A response that omits the price or platform is not a working fit card, and the prompt already requires those details.


---

## 5. Empty wardrobe path

With an empty wardrobe, suggest_outfit returns a non-empty styling suggestion in 5 of 5 tries.



**Why this target:**
The tool is supposed to handle an empty wardrobe gracefully instead of crashing or returning an empty string. This is a clear user-facing failure mode and a simple behavior to verify.


---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
