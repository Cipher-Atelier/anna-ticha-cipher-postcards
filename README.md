# Cipher postcards addressed to Anna Tichá

Research by Maxim Egorov on personal postcards written in cipher, with proposed Czech readings. The collection remains partly read; the writer’s identity and several dates remain unresolved.

[Cipher Atelier](https://github.com/Cipher-Atelier) · [Research index](https://github.com/Cipher-Atelier/research-index) · [Reading guide](READING_GUIDE.md) · [Verification](verification/README.md)

## Current status — 20 October 2026

| Status | Scope and evidence |
| --- | --- |
| Reported external check | [Card 204](anna-ticha/card-204.md): the author reports manual validation of its reading on 20 October. The [original diplomatic text, editorial Czech, English translation and uncertainty ledger](anna-ticha/card-204.md#diplomatic-reading) are published with their alternatives; this is not a claim of blind independent reconstruction. |
| New candidate readings | [25 source-based candidates](research-updates/2026-10-20-confirmed-key-continuation/README.md): cards 242, 244, 249, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273 and 274, with separate literal, editorial Czech and English layers. Each has two related AI source readings and nonblind reconciliation; these are not external confirmation or solved-card claims. |
| Partial readings | [37 preserved card reports](anna-ticha/readings.md#preserved-card-reports). Card 199 has the most complete public positional package: 532 positions, 522 mapped, ten unknown. Cards 205 and 323 remain partial/conditional. |
| Conditional analysis | [Four later Russian readers](research-updates/README.md#four-russian-readers) and later graphical audits are collected in the audit index; [PR #19](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/pull/19) records their publication. A historical registry of 71 conditional reports is not 71 solved cards or a public 71-card reader index. |
| Archived methodology | The [six-card study](anna-ticha/article.md), [saved literals](anna-ticha/saved-six-card-literals.md), [key snapshot](anna-ticha/key-and-rules.md) and [website updates through 5 October](anna-ticha/updates.md) preserve their original stages. Read them with the [later qualifications](research-updates/README.md). |

Card 460 belongs to another team’s comparison: the author reports consistency with that team’s reconstructed key, not a solve produced here. The reported check does not validate the whole collection. **Coverage measures mapped positions, not verified accuracy.**

The [official-catalogue inventory and 263-record queue](research-updates/2026-10-20-confirmed-key-continuation/README.md#catalogue-and-next-work) track source availability and research stages; they do not represent 263 decipherments.

## Start here

1. **Overview:** read the status above and the [plain-language reading guide](READING_GUIDE.md).
2. **Cards and evidence status:** choose a card in the [card index](anna-ticha/readings.md), including the [25 new candidates](anna-ticha/readings.md#new-candidate-readings--20-october-2026) and [204’s reading and qualifications](anna-ticha/card-204.md).
3. **Literal text and supporting evidence:** open the card’s literal beside its interpretation. For a worked example, use [card 199](anna-ticha/card-199.md), its [saved literal](verification/anna-ticha/literal.txt) and [position table](verification/anna-ticha/data/card199_positions.csv).
4. **Method and historical audits:** follow [methods](anna-ticha/methods.md) and the [dated audit index](research-updates/README.md). Later qualifications are linked separately from frozen records.

[Readable editions for the original six cards—198, 199, 250, 329, 440 and 453](anna-ticha/readings.md#readable-editions) place connected Czech and English translations before the historical reports, with disputed places linked separately. These editions interpret historical staged-key outputs; the current bounded audit is linked from their index.

## Reproduce the checks

From this repository’s top-level folder, use Python 3.10 or later:

```sh
python3 verification/check_all.py
python3 -m unittest discover -s research-updates/2026-10-20-confirmed-key-continuation -p test_decode.py -v
python3 research-updates/2026-10-20-confirmed-key-continuation/check.py
```

These standard-library commands run offline without extra packages. They check file fingerprints and replay the saved proposals; they do not certify the source readings. The [new package’s reproduction scope](research-updates/2026-10-20-confirmed-key-continuation/README.md#reproduction) distinguishes selected-string replay from image-level correctness. The [verification instructions](verification/README.md) cover expected output, limitations and troubleshooting. The [existing CI workflow](.github/workflows/verify.yml) also runs regression tests and additional research fixtures with pinned NumPy and Pillow dependencies.

### What can be checked publicly?

| Evidence | Open this | Limit |
| --- | --- | --- |
| Original source | [Card 199 catalogue record](https://crypto.hcportal.eu/dashboard/cryptograms/1518) · [original image](https://api.hcportal.eu/media/4614/pc_hcp_199_pic.JPG) | Card number 199 differs from catalogue ID 1518. Images remain with the provider. |
| Recorded signs and mapping | [Card 199 positions](verification/anna-ticha/data/card199_positions.csv) · [candidate key](verification/anna-ticha/data/key.csv) | Recorded assignments are proposals; context boxes are not exact glyph outlines. |
| Saved output | [Card 199 literal](verification/anna-ticha/literal.txt) · [six-card snapshot](anna-ticha/saved-six-card-literals.md) | Unknowns and malformed strings remain; fluent interpretation is separate. |
| Mechanical consistency | [Verification instructions](verification/README.md) · [one hand check](READING_GUIDE.md#check-one-example-by-hand) | Replay checks saved proposals, not historical letter accuracy. |
| Later limitations | [Audit index](research-updates/README.md) · [research publication PR #19](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/pull/19) | Historical evidence is identified and linked at a fixed revision. |

Card 199’s two `ch` assignments explain why 522 mapped positions emit 524 letters. Twelve later cards have contextual-ledger replay, with additional card 318 marginal strips; see the [card index](anna-ticha/readings.md#evidence-levels). Card 330 has a separate [experimental graphical proposal](anna-ticha/card-330.md): 65 display groups, 264 encoded slots, 251 provisional assignments, 254 known letters and thirteen retained masks. Physical segmentation and written/postal date remain unresolved. Later [feature controls](research-updates/2026-10-11-card330-cross-card-feature-control.md) and [stroke-ownership checks](research-updates/2026-10-11-card330-stroke-ownership.md) accepted no additional letters; their collector/comparison scripts are not published.

## Research scope and limitations

AI-assisted checks do not constitute external human expert review. The dated card 204 status note describes a separate author-reported check. The collection remains partly read, with unresolved identity and dates; the status and evidence limits above apply to each saved proposal.

## Contribute

This is part of [Cipher Atelier](https://github.com/Cipher-Atelier), founded by [Maxim Egorov](https://github.com/cayde-6). See the [research index](https://github.com/Cipher-Atelier/research-index), [contribution guide](https://github.com/Cipher-Atelier/.github/blob/main/CONTRIBUTING.md) and [research workflow](https://github.com/Cipher-Atelier/research-index/blob/main/START_HERE.md). To propose a bounded source check or alternative reading, use [Work on existing research](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/issues/new?template=research.yml) and identify the card, position, source and effect on the saved output.

## Sources and rights

[Sources and earlier work](anna-ticha/sources.md) retain item-specific credits and restrictions. Scans, crops, restricted materials and private correspondence are excluded. No new blanket licence is asserted.

[Publication provenance](SOURCE_PROVENANCE.json) records the original release. Historical research files remain preserved; current navigation and later qualifications are editorial additions.
