# Cipher postcards addressed to Anna Tichá

A set of personal postcards written in cipher and addressed to Anna Tichá. The proposed readings are in Czech; the writer’s identity and several dates remain unresolved.

## Current result — 11 October 2026

This repository contains 37 card reports with different amounts of public evidence. Card199 has a complete 532-position checking package: 522 positions mapped, ten unknown, and two `ch` assignments producing 524 emitted letters. Twelve later cards have replayable contextual ledgers, with additional card318 marginal-strip records. Card330 has a separate experimental graphical proposal. These are partial readings and recorded hypotheses, with qualified English interpretations. Card199’s opening warmly thanks the recipient for a dear letter; the writer remains unidentified.

| Evidence layer | Open this |
| --- | --- |
| All reports / evidence levels | [All 37 card reports](anna-ticha/readings.md) · [current investigation overview](anna-ticha/README.md) |
| Original card199 | [Catalogue 1518](https://crypto.hcportal.eu/dashboard/cryptograms/1518) · [picture](https://api.hcportal.eu/media/4614/pc_hcp_199_pic.JPG) |
| Recorded signs / candidate key | [Card199 positions](verification/anna-ticha/data/card199_positions.csv) · [key](verification/anna-ticha/data/key.csv) |
| Literal | [Card199 saved output](verification/anna-ticha/literal.txt) · [card330 diplomatic projection](anna-ticha/card-330.md#diplomatic-projection) |
| Interpretation | [Card199 English interpretation and repairs](anna-ticha/card-199.md#editorial-interpretation) · each card’s separate report |

`C199.L01.T01 → G01 → v` and `C199.L01.T02 → G02 → r` give `vr`; [check the saved example](READING_GUIDE.md#check-one-example-by-hand). Card number 199 differs from catalogue ID1518. Source-region order is an editorial interpretation, and context boxes are not exact glyph outlines.

Card330’s proposal has 65 display groups, 264 encoded slots, 251 provisional assignments producing 254 known letters, and 13 unresolved occurrences across 11 families. Encoded slots are not a verified physical-glyph count. Subsequent [feature controls](research-updates/2026-10-11-card330-cross-card-feature-control.md) and [stroke-ownership checks](research-updates/2026-10-11-card330-stroke-ownership.md) accepted no further letters.

**Unresolved / missing:** all 13 card330 masks, physical segmentation, written/postal date, writer identity and earlier date alternatives remain. Many card reports have no complete public positional/replay package. Collector/comparison scripts for the perceptual follow-ups are not published; the ordinary replay does not rerun those judgments. Development, post-test learning, retrospective and prospective stages remain separate; card205’s 389/389 coverage is not 100% historical accuracy.

## Start reading

Start with the [all-card index](anna-ticha/readings.md), then choose a literal beside its English interpretation. Recent reports follow.

[Card 318: preliminary May Day greeting](anna-ticha/card-318.md): an unchanged-key reading of the 96-body main block, with a word ledger and explicit single-reader limits. Marginal text remains open.

[Card 319: thanks and a promised reply](anna-ticha/card-319.md): a preliminary ten-line reading with 150 mapped bodies and a retained faded cluster. The ledger, source fingerprints and limits are public.

[Card 316: going home and an affectionate message](anna-ticha/card-316.md): a partial reading with 102 invariant proposed mapped bodies, two y/i alternatives and an unresolved closing. The written year remains unconfirmed.

[Card 320: Easter wishes and a promised letter](anna-ticha/card-320.md): a preliminary ten-line reading with 200 proposed mapped bodies. Includes the literal, interpretation and contextual source ledger.

[Card 315: arrival in Prague and taking up service](anna-ticha/card-315.md): a preliminary six-line reading, with a source ledger and written date 8 June 1901. The kind of service remains unidentified.

[Card 314: a letter for tomorrow and concern for the recipient](anna-ticha/card-314.md): a partial eleven-line reading with 253 proposed mapped bodies and an unresolved overwritten cluster. Literal defects and editorial repairs remain separate.

[Card 322: a Sunday journey home and a Monday return](anna-ticha/card-322.md): preliminary main and left-region readings; 195 proposed mapped bodies emit 196 letters. Source spelling and editorial repairs remain separate.

[Card 324: a day at the office and an uncertain journey home](anna-ticha/card-324.md): preliminary two-region reading, with 166 proposed mapped bodies and explicit editorial repairs. Written date 19 December 1900.

[Card 325: a postal-office visit and a conditional journey to Ústí](anna-ticha/card-325.md): preliminary five-line reading; 283 proposed mapped bodies and two unresolved overwritten clusters. Written date 20 October 1900; editorial repairs and procedural uncertainty disclosed.

[Card 326: thanks, a promised letter and a question about former accommodation](anna-ticha/card-326.md): preliminary three-border reading; 132 invariant proposed mapped bodies emit 135 letters, plus one k/z-ambiguous body, with one unresolved overwritten cluster. Catalogue date 22 September 1900; locality completion and spelling repair remain editorial proposals.

[Card 327: a gift, a likeness and a question about a possible premonition](anna-ticha/card-327.md): preliminary bottom/right reading; 266 invariant proposed mapped bodies emit 268 letters, with one k/z-ambiguous body and three unresolved overwritten clusters. Written date 11 September 1900; editorial changes and conditional interpretations disclosed.

[Card 328: a letter from Pelhřimov and holiday travel questions](anna-ticha/card-328.md): preliminary left/bottom reading; 240 invariant proposed mapped bodies emit 243 letters, with four unresolved clusters. Written date 30 May 1900; letter receipt, kinship and arrival interpretations remain qualified.

[Card330 source-first follow-up, 11 October](anna-ticha/card-330.md): frozen graphical snapshots, a conservative reconciliation journal and the exact masked projection from original-named provider files. Physical body count and written/postal date remain unresolved. The [historical 9 October screen-reading note](research-updates/2026-10-09-card330-screen-reading.md) preserves the earlier browser-only stage.

[9 October control audit](research-updates/2026-10-09-anna204-controls.md): the tested comparator and control gates failed; Anna204's disputed target remains unresolved. This update is a text summary, with full replay materials retained locally.

1. [Read the plain-language guide](READING_GUIDE.md): the document, result, file meanings and one worked check. No programming is required.
2. Open [Card 199: literal reading](verification/anna-ticha/literal.txt) to inspect the saved text or test result itself.
3. Read the [research account](anna-ticha/article.md) for historical context, methods, earlier work and unresolved questions.

## How can I check it?

Follow the worked example in [the reading guide](READING_GUIDE.md#check-one-example-by-hand). It connects a source record, a key or model assumption, and the saved output. For an independent source check, use the [original-source entry](https://crypto.hcportal.eu/dashboard/cryptograms/1518); images are linked, not redistributed here.

If you use Python, follow the [complete verification instructions](verification/README.md), including download/setup, expected results and troubleshooting. The command from this repository’s top-level folder is:

```sh
python3 verification/check_all.py
```

A successful run means the published files and declared calculation reproduce. It does not establish that every source sign or historical interpretation is correct.

## Precise research scope

Partial card readings. Complete positional replay remains limited to card199. The supported offline check also replays the saved contextual ledgers for cards314,315,316,318,319,320,322,324,325,326,327,328 and card318 marginal strips B/C/D, including unresolved masks. These checks establish consistency of saved proposals, not correct source classification or historical accuracy. Cards440/453 supply limited examples; cards247/248 remain qualified text reports without complete public positional packages. Card330 now has a separate [experimental source-first proposal](anna-ticha/card-330.md): 65 spatial display groups, 251 provisional assignments to known classes and 13 unresolved occurrences. Its own replay checks saved graphical consistency; physical body count and written/postal date remain unresolved.

This is part of [Cipher-Atelier](https://github.com/Cipher-Atelier), founded by [Maxim Egorov](https://github.com/cayde-6). Explore the [research index](https://github.com/Cipher-Atelier/research-index), [contribution guide](https://github.com/Cipher-Atelier/.github/blob/main/CONTRIBUTING.md), and [step-by-step research workflow](https://github.com/Cipher-Atelier/research-index/blob/main/START_HERE.md).

Source credit and item-specific restrictions remain in the research records. Scans, crops, restricted materials and private correspondence are excluded. No new blanket licence is asserted. AI-assisted work requires evidence checking and does not constitute external human expert review.

[Publication provenance](SOURCE_PROVENANCE.json) records the source commit, retained file hashes and deliberate code/navigation adaptations. The original repository history remains intact.

## Contribute to this investigation

Read the current result and source limitations, then coordinate a bounded task in an existing issue or use [Work on existing research](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/issues/new?template=research.yml). Fork the repository and submit a focused pull request with your evidence and checks. Independent replication and constructive alternative readings are welcome. See [Start here](https://github.com/Cipher-Atelier/research-index/blob/main/START_HERE.md) for the shared workflow.

[Card330 cross-card feature control](research-updates/2026-10-11-card330-cross-card-feature-control.md) explains the source evidence, remaining masks and new tentative fragments relative to the screen note. Its frozen G05/G19 criteria failed a canonical control, so the disputed target remains masked; no additional plaintext or key change is accepted.

[Card330 geometric annotation](research-updates/2026-10-11-card330-stroke-ownership.md) records two independent pixel-only proposals for all seven saved segmentation references. Approximate envelope agreement did not establish stroke ownership or physical positions; all thirteen masks remain, and this annotation path stops with a documented limit.

## Local corpus update — 13 October 2026

[Four qualified research readers, selected scientific text evidence and frozen reference code](research-updates/2026-10-13-local-corpus/README.md).

## G08 owner study — 13 October 2026

[Recorded primary and separate supplementary source judgments, with endpoint limits](research-updates/2026-10-13-g08-owner-study.md).

## Whole-trajectory owner study — 13 October 2026

[Bounded held support for visible-path ownership and local ink partition, with complete-unit limits](research-updates/2026-10-13-whole-trajectory-owner/README.md).

## Full-unit class bridge — 13 October 2026

[Two complete external constructions, bounded class correspondences and the unresolved value-blinded class bridge](research-updates/2026-10-13-full-unit-class-bridge/README.md).
