# External manual review: postcards 320 and 321

Eugen Antal replied on **28 October 2026, 23:00 CET** with manually checked transcriptions and Czech readings of both cards. Changes were incorporated on **29 October**. He had our proposed text and three questions: this is external human review, not a blind reconstruction of the key. [Derived reviewer text](review.json) · [Validation](validation.json) · [Checker](check.py)

## Results

| Card | Adopted source changes | Current replay | Remaining scope |
| --- | --- | --- | --- |
| [320](../2026-10-20-confirmed-key-continuation/cards/320.md) | Eight sign substitutions: five 9→g, r→n in ROZMILA, 1→4 in UPRIMNE, n→p in LIBA | 200 slots, 203 known emitted letters, three CH, zero unknowns | Existing roof/physical/identity/date and isolated Address-mark limits remain |
| [321](../2026-10-20-confirmed-key-continuation/cards/321.md) | Insert 4/I in ANDULIKO; shift exclamation tag by one | 135 slots, 134 known emitted letters, zero CH, one unassigned v | Czech doufati confirmed, glyph-to-F value unresolved |

## What the corrections resolve

320 no longer needs the five language-only 9→Z conjectures or the H→M/Y→I/M→B word repairs. Its updated literal already yields ROZMILA, UPRIMNE and LIBA under the unchanged key. The substitutions are specific reviewed source selections, not a rule that every 9-like form on other cards means Z. The original two AI readings and their differences remain unchanged.

321 uses **Anduliko** exactly as supplied, including the added 4/I. This records a textual address form rather than identifying a recipient. The reviewer also confirms **doufati**, but his own transcription still contains **t32v6d4 / DOUvATI**. The reader therefore shows the confirmed word alongside the unresolved literal. The key is unchanged; source f still maps V and no F assignment is supplied.

[320 revision](../2026-10-20-confirmed-key-continuation/revisions/320-external-review-20261029.json) · [321 revision](../2026-10-20-confirmed-key-continuation/revisions/321-external-review-20261029.json) pin previous editions, exact edit groups, remapped spans/tags and protected fields. Earlier source-completion, freeze, raw/strict, QA18 and address/date records retain their original dated scope. Current broad row geometry is reused as context; it does not establish exact ink ownership or physical body counts. No fresh source-acquisition or blind-review claim is made.

## Reviewer-supplied Czech

### Card 320

Vřelý dík a pusu za drahý dopis, Anduličko moje rozmilá. Přeji Ti navzájem, abys strávila svátky v kruhu svých drahých co nejpříjemněji. Budu na Tě stále vzpomínati. Dopis zašlu Ti co nejdříve po svátcích. Nesčíslněkráte Tě upřímně líbá Tvůj Pepouš.

### Card 321

Vřelý dík za drahý dopis, Anduliko moje! Zodpovím jej co nejdříve. Těším se nyní tím více na jaro, když mohu doufati, že mi Tě přivede. Vřelý pozdrav a tisíc pus od Pepouše.

The English interpretations are our editorial translations, not translations supplied or separately certified by the reviewer. Textual name forms and unverified historical events/dates remain distinct from the reviewed reading.

## Register and next work

For subsequent source reviews, these corrections identify specific checks to prioritize: returning g-like forms previously recorded as unassigned 9, n/p and 1/4 distinctions, and missed narrow signs inside name-like groups. These are comparison prompts grounded in 320/321, not automatic substitutions on other cards. The full reviewer transcription was compared, rather than applying only the three originally requested word repairs; this also recovered the other g selections and the extra 4/I in 321. The v/F question remains a separate source/key issue for a future small review batch.

Eugen reports that the submitted readings have been added to the AI decipherments register and that database records will be updated gradually. This records his correspondence statement; no separate live-register or database audit was performed. It is not blanket validation of all 154 submitted readings. The [submitted CSV/JSON/index](../2026-10-28-hcportal-register/README.md) stay pinned to their original texts; this dated addendum records the later review.

Our existing deeper pass still has **70 of 137 candidates remaining**, next **319**, with 67 having working coverage. The **108 cards planned by Eugen Antal and team** remain separate. Collection coverage remains **154 of 263 including partial**, with **109** without our separate reading (the planned 108 plus the team’s 460 comparison). No additional full data package was requested in this reply.

## Verification

```sh
python3 research-updates/2026-10-29-antal-review/check.py
python3 research-updates/2026-10-28-hcportal-register/check.py
python3 verification/check_all.py
```

The new checker compares exact reviewed strings, source edits, decoder outputs, projected current spans/tags and immutable historical fields against the prior Git snapshot. It requires a full Git clone. Passing replay does not independently authenticate every source shape or historical assertion. Original correspondence and source images remain private.
