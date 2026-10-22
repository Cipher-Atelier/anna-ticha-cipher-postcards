# Anna Tichá postcards: review overview

Prepared 22 October 2026 from the candidate records dated through 22 October. This is a guide to the published proposals, not a new decipherment or source review.

## Collection and reading counts

The saved [official catalogue inventory](research-updates/2026-10-20-confirmed-key-continuation/catalogue-records.json) contains **263 distinct cards**, numbered 198–460, and 526 original image URLs. Two faces of one postcard count as one card. This is the repository's stated catalogue range; it does not independently authenticate the historical collection's authorship or identity.

| Published reading coverage | Unique cards |
| --- | ---: |
| Current canonical-key candidates | 129 |
| Earlier reports without a current canonical-key candidate | 16 |
| Card 204: separate reading with an author-reported external manual check | 1 |
| **Cards with a published reading, including partial proposals** | **146** |
| No card reading published here | 117 |
| **Total catalogue records in the stated range** | **263** |

The count is **129 + 37 − 21 + 1 = 146**. The 37 earlier reports include the original six-card study and the experimental card 330 report; 21 of those cards also have current candidates. They must not be counted twice. The current candidates therefore add **108 card numbers** beyond the earlier reports. The 16 earlier-only cards are 198, 199, 200, 201, 202, 203, 205, 223, 247, 248, 250, 440, 441, 447, 453 and 458.

These are counts of available readings, not counts of completely solved cards. In the saved catalogue response of 20 October, only card 460 is labelled `Solved`; the other 262 are labelled `Not solved`. Card 460 is another team's work and has no plaintext published here. It is included in the 117 without a reading here. Catalogue labels and the author's reported check of 204 are distinct evidence.

## What is new

Card 375 already had an earlier report; its new canonical-key record increases the overlap, so this batch adds three newly represented card numbers (376–378), not four. The earlier 375 report remains unchanged.

The [current package and complete 129-card table](research-updates/2026-10-20-confirmed-key-continuation/README.md) cover **242, 244, 249 and 253–378**. Each card has a Markdown reading and a paired JSON evidence record. The [complete card index](anna-ticha/readings.md#new-candidate-readings--20-october-2026) links every reading directly to its JSON, selected original face and catalogue record. The key is the supplied 22-entry 204/460 key; it is separate from the historical staged key used in older reports.

Read the layers in order: recorded ciphertext → literal key output → qualified Czech proposal → English interpretation. Unknown signs and substantive editorial proposals remain marked. Source references, reader records and uncertainty information are in the paired JSON; the amount and layout of supporting documentation vary by batch. For an accessible partial example, see [257](research-updates/2026-10-20-confirmed-key-continuation/cards/257.md); for the latest batch, see [375](research-updates/2026-10-20-confirmed-key-continuation/cards/375.md), [376](research-updates/2026-10-20-confirmed-key-continuation/cards/376.md), [377](research-updates/2026-10-20-confirmed-key-continuation/cards/377.md) and [378](research-updates/2026-10-20-confirmed-key-continuation/cards/378.md).

## What still needs checking

| Open issue | Scope and review needed |
| --- | --- |
| Source transcription | Faded, merged, overwritten and marked signs retain alternatives. Some masks represent clusters of unknown length. Exact physical glyph totals and boundaries are not established for the current candidates. Compare the saved choices with the original images, rather than treating replay coverage as accuracy. |
| Czech and translation | Some literal outputs remain malformed. Bracketed repairs and English interpretations need Czech-language review; fluent text is not additional graphical evidence. Card 257 is substantially incomplete. |
| External validation | The earlier 121 candidates retain their two frozen related AI source records; cards 371–378 currently have one key-visible source reading each, followed by same-context nonblind review. Neither stage is external confirmation. None of the 129 current candidates is declared solved. The reported check of 204 does not validate the other cards. |
| Historical interpretation | Sender identity, several dates, cross-region reading order and shared authorship remain unresolved. Editorial serialization is not authenticated chronology. |
| Evidence access | Original scans, private crops and supplied correspondence/PDFs are not bundled. Public records provide provider links, hashes and derived observations; private integrity references alone do not permit independent retrieval. |
| Remaining work | The [queue](research-updates/2026-10-20-confirmed-key-continuation/queue.json) separates acquisition, transcription, candidate and validation stages. Its next priority is 379–382. The 117 cards without a published reading here and the existing provisional readings require different kinds of work. |

For corrections, identify the card, face/region, row or position, proposed source reading and effect on the literal. Keep glyph corrections separate from language repairs.

## Reproduce the saved calculations

From the repository root, with Python 3.10 or later:

```sh
python3 verification/check_all.py
python3 -m unittest discover -s research-updates/2026-10-20-confirmed-key-continuation -p test_decode.py -v
python3 research-updates/2026-10-20-confirmed-key-continuation/check.py
```

These commands work offline without source scans or third-party packages. They check saved fingerprints, bounded legacy replay and the current candidate strings against the supplied key. They do not check the ink, establish transcription accuracy or resolve historical questions. See [verification](verification/README.md) and the [current package's reproduction scope](research-updates/2026-10-20-confirmed-key-continuation/README.md#reproduction).
