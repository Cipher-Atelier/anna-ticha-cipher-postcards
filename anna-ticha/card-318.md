# Card 318: a preliminary May Day greeting

[Anna Tichá investigation](README.md) · [All card readings](readings.md)

Research recorded on 9 October 2026. Initial source comparison, transcription, translation and mechanical checks by Codex (GPT-6), using the previously published Cipher-Atelier key. A separately tasked Codex reviewer (GPT-6-astra) compared the proposed main-block reading with the source and atlas before publication. No new key is proposed. This is a preliminary reading, without independent human palaeographic validation.

## Scope and literal

The four-line main block on [HCPortal record 1637, pc_hcp_318](https://crypto.hcportal.eu/dashboard/cryptograms/1637) gives a connected Czech greeting under the unchanged key. The proposed transcription contains 96 mapped bodies in 17 words, exercising 19 existing classes. These counts describe accepted assignments in this selected block, not historical accuracy or whole-card coverage. Additional cipher text on the margins is outside this edition.

```text
v den prvniho maje srdecny
pozdrav a dlouhou. vrelou pusu
sve touzene, predrahe andulce
posila vzpominajici pepous.
```

The dot after `dlouhou`, comma after `touzene` and final dot are recorded separately from the 96 class assignments. In particular, the unusual dot is not silently replaced with a comma. Faint incidental traces and complete mark ownership have not been systematically inventoried, so this is a base-class reading rather than a complete diplomatic edition.

## Interpretation

Proposed sense: “On the first of May, a heartfelt greeting and a long, warm kiss to his longed-for, dearest Andulka, sent by Pepouš, who is thinking of her.” The punctuation in this fluent interpretation is editorial; the literal above remains unchanged.

Accent restoration would give `prvního`, `máje`, `srdečný`, `vřelou`, `své`, `toužené`, `předrahé`, `posílá` and `vzpomínající`. Initial capitals and `Andulka`/`Pepouš` are editorial normalizations. No accepted base letter was replaced to make the passage fluent. The affectionate address and proposed signature do not identify the writer or establish a relationship or a delivered kiss.

The catalogue gives 1 May 1901. The opening agrees with its day and month; it does not independently establish the year. The address face and postal markings were not examined in this experiment.

## Source and evidence

- [Original picture-side JPEG](https://api.hcportal.eu/media/4971/pc_hcp_318_pic.JPG): 1785 × 1175 pixels; SHA-256 `ad2a5267d2038072fb2d0306d12393616a79239937879d0691bcde2ce76c147e`.
- Main-block source context, in original pixels: approximately `[5,470,205,1100]`, rotated exactly 90 degrees counterclockwise for reading.
- [Word ledger](../research-updates/evidence/card318-2026-10-09/word-ledger.csv): 17 contextual source boxes, manually assigned class sequences, resulting words and body counts. Boxes may contain neighboring strokes and are not isolated full-glyph segmentations.
- [Saved literal](../research-updates/evidence/card318-2026-10-09/literal.txt) and [input fingerprints](../research-updates/evidence/card318-2026-10-09/manifest.json).
- Existing [key](../verification/anna-ticha/data/key.csv) and [graphical reference atlas](../verification/anna-ticha/docs/GLYPH_ATLAS.md), read at commit `985167d8a5bf20cf6c74f3b58c32396929fcbd35`.

The atlas's downloaded card199 and card440 source bytes matched their published hashes. Comparison used their source crops and the complete new main block, with exact rotations and display enlargement only. No reconstructed or added ink was used. Images and crops are linked through their providers rather than redistributed here; no new licence is asserted over them. Credit for source access belongs to HCPortal and the collection holders, and for the existing key to the researchers credited in the [original study](article.md).

## Checks and limitations

The saved ledger was checked against the unchanged key: all 17 class sequences reproduce their saved words; they sum to 96 bodies and 19 distinct classes. Joining the four lines and separately transcribed punctuation reproduces `literal.txt` exactly. Input and output hashes match the manifest. All source boxes lie inside the original JPEG; a 17-word contact sheet and the full block were visually inspected.

For manual replay, look up each space-separated class ID in `word-ledger.csv` against `class_id,literal` in the existing `key.csv`, concatenate values within a word, and join words in their recorded line/word order. Add the three punctuation marks described above. The expected output is the four-line literal. This checks the lookup procedure, not the correctness of the manual source classifications.

The existing `python3 verification/check_all.py` passed on the input commit: 69 retained files and the card199 baseline replay. The publication inventory is updated separately for the authorized documentation and evidence additions. That command does **not** decode the new card318 ledger or establish its historical correctness.

The initial AI reader saw the key and emerging language throughout. This is not a blind transfer experiment; language expectations could have influenced classification. The later AI reviewer also saw the proposed output, so that comparison is not a fresh holdout or independent human authentication. It corrected the first body of line 3's `touzene` from G18 to the existing `H440_N01_UNBARRED_LEFT_BOWL` class: the source lacks G18's upper horizontal bar. Both classes emit `t`, so the literal and 96/19 body/class counts are unchanged. The manifest preserves the earlier ledger fingerprint and the reason for this correction.

No heldout accuracy, independent source truth, complete mark inventory, full-card transcription or worldwide priority is claimed. A bounded search found no card318 reading page or explicit card318 reference in the public repository at the recorded input commit; private and earlier external readings are not excluded.

The next useful step is an independent source comparison of these 96 bodies and a separately recorded transcription of the marginal text, preserving overwritten signs and alternatives. Publicly available digital sources suffice for that attempt; no library or archive inquiry was made.
