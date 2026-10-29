# Anna Tichá postcards: review overview

Updated 29 October 2026. This page summarizes published readings, review status and remaining work. It adds no new decipherment or source judgment.

## Collection and reading counts

The saved [official catalogue inventory](research-updates/2026-10-20-confirmed-key-continuation/catalogue-records.json) contains **263 distinct cards**, numbered 198–460, and 526 original image URLs. Two faces of one postcard count as one card. This is the repository's stated catalogue range; it does not independently authenticate the historical collection's authorship or identity.

| Published reading coverage | Unique cards |
| --- | ---: |
| Current canonical-key candidates | 137 |
| Earlier reports without a current canonical-key candidate | 16 |
| Card 204: separate reading with an author-reported external manual check | 1 |
| **Cards with a published reading, including partial proposals** | **154** |
| No card reading published here | 109 |
| **Total catalogue records in the stated range** | **263** |

The count is **137 + 37 − 21 + 1 = 154**. The 37 earlier reports include the original six-card study and the experimental card 330 report; 21 of those cards also have current candidates. They must not be counted twice. The current candidates therefore add **116 card numbers** beyond the earlier reports. The 16 earlier-only cards are 198, 199, 200, 201, 202, 203, 205, 223, 247, 248, 250, 440, 441, 447, 453 and 458.

These are counts of available readings, not counts of completely solved cards. In the saved catalogue response of 20 October, only card 460 is labelled `Solved`; the other 262 are labelled `Not solved`. Card 460 is another team's work and has no plaintext published here. It is included in the 109 without a reading here. Catalogue labels and the author's reported check of 204 are distinct evidence.

## What is new

The [28 October HCPortal submission package](research-updates/2026-10-28-hcportal-register/README.md) inventories all 154 published readings including partial, records available AI/date metadata and missing fields, and provides three bounded review questions. The [108-card coordination list](research-updates/2026-10-28-hcportal-register/coordination.md) records planned work by Eugen Antal and team. This announcement adds no completed readings or external confirmations; card 460 remains their separate comparison result.

The latest source completion is [card 316](research-updates/2026-10-20-confirmed-key-continuation/cards/316.md#complete-working-reading--29-october-2026). Card 316 has four-row working coverage with explicit gaps. R03 opening mask provisionally becomes p/B, yielding BOLI; 105 slots/100 known letters/zero CH/five masks. NES?SLNE has a qualified NESCISLNE language proposal, with CI supplied only in prose. AO NEJDRYVE and PUSI retain language repairs; middle/terminal clusters, missing opening verb and cross-region order stay unresolved. No external confirmation or new key assignment.

The preceding external source review is the [external manual review of cards 320 and 321](research-updates/2026-10-29-antal-review/README.md). Eugen Antal supplied manually checked transcriptions and Czech readings for 320 and 321 on 28 October, incorporated 29 October. Card 320 has eight source-sign substitutions: 200 slots/203 known letters/three CH/zero unknowns. Card 321 adds one 4/I in ANDULIKO: 135 slots/134 known letters/zero CH/one unassigned v. Czech doufati confirmed; no v→F key assignment. Earlier raw readings, key, QA and dated snapshots retained; review does not authenticate identity/date or validate the other candidates.

| Current work | Status |
| --- | --- |
| Cards 316–386 | Editorial working coverage of selected entries; masks, word hypotheses, mark/contour alternatives and some ordering questions remain. |
| Remaining in descending completion pass | **66 of 137 existing candidates**; 71 have working coverage in this pass (316–386). This is deeper review, not new-card coverage or independently solved cards. |
| Next source review | [Card 315](research-updates/2026-10-20-confirmed-key-continuation/cards/315.md), followed by the [active completion queue](research-updates/2026-10-20-confirmed-key-continuation/queue.json). |
| New card numbers | The latest addition was 383–386 on 22 October. New 387–390 remain held during deeper completion of existing readings. |
| Source and language confirmation | External manual review received for 320/321; other candidates and the unassigned v in 321 still need checking. None of the 137 current candidates is declared solved. |

The [complete card index](anna-ticha/readings.md) links directly to readings, evidence JSON, selected original faces and catalogue records. The [current candidate table](research-updates/2026-10-20-confirmed-key-continuation/README.md#candidate-readings) lists all 137 candidates: 242, 244, 249 and 253–386. The key is the supplied 22-entry 204/460 key, separate from the historical staged key used in earlier reports.

For per-card changes and earlier checkpoints, open the [package's dated source-review history](research-updates/2026-10-20-confirmed-key-continuation/README.md#current-source-completion--card-316). Its earlier counts and review statuses apply to their recorded stages. For an accessible current example use [316](research-updates/2026-10-20-confirmed-key-continuation/cards/316.md); for a substantially incomplete example use [257](research-updates/2026-10-20-confirmed-key-continuation/cards/257.md).

## What still needs checking

| Open issue | Scope and review needed |
| --- | --- |
| Source transcription | Faded, merged, overwritten and marked signs retain alternatives. Some masks represent clusters of unknown length. Exact physical glyph totals and boundaries are not established for the current candidates. Compare the saved choices with the original images, rather than treating replay coverage as accuracy. |
| Czech and translation | Some literal outputs remain malformed. Bracketed repairs and English interpretations need Czech-language review; fluent text is not additional graphical evidence. Card 257 is substantially incomplete. |
| External validation | The earlier 121 candidates retain their two frozen related AI source records; cards 371–386 currently have one key-visible source reading each, followed by same-context nonblind review. Neither AI stage is external confirmation. Eugen Antal’s later manual review of 320/321 is separate. None of the 137 current candidates is declared solved. The checks of 204/320/321 do not validate other cards. |
| Historical interpretation | Sender identity, several dates, cross-region reading order and shared authorship remain unresolved. Editorial serialization is not authenticated chronology. |
| Evidence access | Original scans, private crops and supplied correspondence/PDFs are not bundled. Public records provide provider links, hashes and derived observations; private integrity references alone do not permit independent retrieval. |
| Remaining work | The [queue](research-updates/2026-10-20-confirmed-key-continuation/queue.json) separates acquisition, transcription, candidate and validation stages. Its next active source-completion work is 315; unresolved groups and provisional 316–386 contour/role/language choices await better evidence or another reader. New-card priority 387–390 remains held. The 109 cards without a published reading here and the existing provisional readings require different kinds of work. |

For corrections, identify the card, face/region, row or position, proposed source reading and effect on the literal. Keep glyph corrections separate from language repairs.

## Reproduce the saved calculations

From the repository root, with Python 3.10 or later:

```sh
python3 verification/check_all.py
python3 -m unittest discover -s research-updates/2026-10-20-confirmed-key-continuation -p test_decode.py -v
python3 research-updates/2026-10-20-confirmed-key-continuation/check.py
```

These commands work offline without source scans or third-party packages. They check saved fingerprints, bounded legacy replay and the current candidate strings against the supplied key. They do not check the ink, establish transcription accuracy or resolve historical questions. See [verification](verification/README.md) and the [current package's reproduction scope](research-updates/2026-10-20-confirmed-key-continuation/README.md#reproduction).
