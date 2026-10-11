# Card330: source limits and a controlled cross-card feature test

This follows the [11 October source-ledger proposal](../anna-ticha/card-330.md), recorded in [draft PR15](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/pull/15) at `8c8ad711e39315620b2c9ba625b4711ba8648d42`. The new feature test failed its predeclared control gate. It adds a bounded negative result and an isolated graphical observation, **no accepted class or additional plaintext**. The key, earlier ledgers, masks and dates remain unchanged.

## What the new source files established

Card330 inspection used downloaded original-named provider JPEGs, each **1785 × 1175**, rather than browser screenshots or the earlier 1024 × 674 viewer renditions. These are provider byte identities, not authentication of the physical postcard:

| Side | Provider URL | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Picture | [pc_hcp_330_pic.JPG](https://api.hcportal.eu/media/5007/pc_hcp_330_pic.JPG) | 1431536 | `206f29850350f429346d04bacc37c01bc377e50b1224a59d42bb6e785b781a05` |
| Address | [pc_hcp_330_adr.JPG](https://api.hcportal.eu/media/5008/pc_hcp_330_adr.JPG) | 1060308 | `45d8a90465498208210bf1943c442dfa13d2bea303c705a7a8bd0f40b663d4d0` |

The frozen A graphical draft covers five encoded text lines, 65 spatial groups and 265 historical entries. B separately surveyed the same five lines with a different 65-group display partition. The reconciled proposal uses 264 encoded slots. This is a complete saved class-first draft for the apparent text block; it is **not a complete physical glyph-position edition or certified source-only ground truth**.

The main evidence gaps are approximate slot windows that can include neighbors or other lines, unresolved stroke ownership, unsegmented spans at L03W11/L03W16/L05W09, uncertain family equality and unverified physical body counts. Features often describe a proposed family rather than prove each stroke's membership. Punctuation and display groups do not establish lexical boundaries. Graphical records preceded key projection, but atlas descriptions, model prior familiarity and B's disclosed accidental unbarred-t metadata exposure prevent a certified blind claim. Neither source accuracy nor a written/postal date is established.

## What plaintext was added, and what became less certain

Relative to the 9 October screen note, the source-ledger stage added these tentative fragments. They are already recorded in PR15; this new control test did not add letters. Line breaks, masks and the selected source spelling are retained:

```text
proc litujes, ze [A001]en
tvuj nebyl pravdou[?]

pra ve se chystam na zpate[A001]ni
cestu do prahy. prijel jsem sem na pozi hod v n[R_L03W11_COUPLED_SPAN]i.

tesim se na psanko nes mirne.
p[A002]zdrav a tisic dlouhych, va[A001]nivych p[A003]s od vecne [U001]veho pepouse.
```

The older opening `srdecko` is now `srde[R_L01W03B05]ko`; the older `tolik` is now `toli[R_L02W07B05]`. These are reductions in claimed certainty. No fluent repair of `pozi`, `amumku`, `pra ve`, `vzpo mi nal` or `nes mirne` is accepted, and no itinerary or historical event follows from their linguistic plausibility.

## Why thirteen occurrences remain masked

These are dominant obstacles, not mutually exclusive measured causes. Quality and stroke attribution can interact. An unresolved span is one encoded slot, not necessarily one physical glyph.

| Primary obstacle | Occurrences | Masks/positions | Evidence missing |
| --- | ---: | --- | --- |
| Unestablished family | 4 | A001 at L01W11, L02W14, L05W05; A003 at L05W06 | Rounded-loop versus pointed-family equality; the closed e-like form has no established existing family or literal |
| Available image quality | 1 | A002 at L05W01 | Ink-filled lobes cannot be separated reliably |
| Segmentation or stroke ownership | 7 | A007, A008, U001, R_L02W04B05, R_L02W07B05, R_L03W17B01, R_L03W11_COUPLED_SPAN | Joined components, shared bars, underline, previous-line descender and correlated pair alternatives |
| Disagreement between existing class proposals | 1 | R_L01W03B05 | G05 stem/foot versus G19 pointed contour; neither has been accepted |

There are **zero demonstrated contradictions in frozen key values**. The last row is a graphical class-selection conflict, not evidence that `G05=y` or `G19=c` is wrong. The [assessment record](evidence/card330-feature-control-2026-10-11/card330-substantive-assessment.json) lists all thirteen occurrences and secondary reasons.

## Frozen experiment and prior-work audit

The [protocol](evidence/card330-feature-control-2026-10-11/preregistered-protocol.json) fixed observable separability, external oblique stem, attached baseline foot and closed pointed contour before the new test crops were generated. Category S required separability plus stem/foot and no closed pointed contour; L required a separable closed pointed contour without a distinct external stem/foot. Any unclear feature required N, abstention. The [geometry freeze](evidence/card330-feature-control-2026-10-11/target-window-freeze.json) then fixed the exact ten locators before scoring.

Four canonical controls used both frozen G05 and both G19 examples from card199. Two G11 examples supplied negative controls, expected N. Cross-card transfer selected the first two saved card328 rows containing G05 and the first containing G19: L1W1 body5, L1W4 body5 and L4W3 body1. Card330 L01W03B05 was the disputed target, with no expected family. A deterministic shuffled display concealed roles and key/letter labels from a fresh AI observer. The collector and evaluator knew the roles; all sources had prior exposure in earlier work. This is procedural concealment, not certified global blindness or human validation.

The [bounded duplicate audit](evidence/card330-feature-control-2026-10-11/duplicate-audit.json) checked tracked research, local commit subjects and live branch/PR/issue metadata. Card223 already had a G05/G19 comparison; card330 already had canonical-atlas review; card328's source and provisional classes were previously inspected. None is claimed novel source discovery. No earlier instance of this fixed feature/control/transfer protocol was found. Private or external experiments are not excluded.

Source images remained unmodified apart from cropping, exact quarter turns and 4× nearest-neighbor display. Pixel-transform identity was checked independently. Local coded PNGs and their hashes are described by the [released selection map](evidence/card330-feature-control-2026-10-11/dataset-selection.json), but **no pixels are published**. Target rectangles are approximate locators, not traced ink segmentations.

## Result and stop

The observer's [raw feature record](evidence/card330-feature-control-2026-10-11/observer-observations.json) was frozen before scoring against expected roles. The evaluator independently derived its categories from those features. The [scoring record](evidence/card330-feature-control-2026-10-11/scoring.json) preserves every decision:

| Set | Observations matching predeclared expectations | Limit |
| --- | --- | --- |
| Canonical controls | 3 of 4 | A10, card199 L02.T21, expected L; F1 was unclear, so observer abstained |
| Negative controls | 2 of 2 | Both G11 examples received N; binary matching was not forced |
| Card328 transfer observations | 2 of 3 | A02, L4W3 body1, also abstained on the upper projection; descriptive only because the primary gate failed |
| Card330 disputed target | A06 received L | No expected target truth; control failure prevents accepting G19 or emitting `c` |

For both abstentions, the observer saw a closed pointed loop but could not decide whether the upper projection was a separate stem or its contour junction. The isolated target looked closed/pointed without a resolved external shaft. That observation does not override the failed control gate or prove the target's physical stroke boundaries. **R_L01W03B05 remains masked.** No example substitution, criterion adjustment or repeated scoring was used to obtain a pass. A003's loop comparison and IV/II date were not repeated.

These small dependent examples compare an observer/rule combination with saved proposed labels, not external ground truth. Failure could reflect criterion overlap, locator limits, visibility or observer judgment; it does not prove the key wrong or measure historical accuracy.

## Concrete limits and next data

The present protocol cannot support the class upgrade. The current files also leave twelve other unresolved occurrences and the date untouched. A defensible continuation needs independently annotated stroke ownership for card199 L02.T21, card328 L4W3 body1 and card330 L01W03B05 with neighbor context and plaintext hidden. A genuinely higher-resolution independent scan could clarify the upper junction; scaling the same JPEG adds no ink evidence. Public examples on other cards remain available, but a revised criterion must first be calibrated on a declared development corpus and then frozen for separately selected examples. These ten cannot become a fresh holdout after their results are known.

The [text packet manifest](evidence/card330-feature-control-2026-10-11/manifest.json) identifies all records. Ordinary `verification/check_all.py` checks their fingerprints and retains earlier ledger replay; it does **not** rerun this AI observer or establish the scientific result. Reproducing the visual comparison requires obtaining the identified source bytes separately under provider terms and using the recorded coordinates, rotations and display rules. Source/key credit remains with [the earlier study](../anna-ticha/article.md), HCPortal and collection holders; access is not image redistribution permission.
