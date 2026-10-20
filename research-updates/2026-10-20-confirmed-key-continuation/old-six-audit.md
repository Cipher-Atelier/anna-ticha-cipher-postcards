# Six earlier cards: bounded source reinspection, 20 October 2026

This recheck inspects 14 specified loci on cards 198, 199, 250, 329, 440 and 453. It is a partial visual audit, not six complete transcriptions. Full picture-side contexts and enlarged private crops were inspected from the saved originals; all six source hashes matched their saved metadata. No source was fetched again. The [machine-readable record](old-six-audit.json) contains source URLs and hashes, oriented and original pixel windows, observations, canonical transcripts, literal outputs and uncertainties.

The reader was **not blinded**: the historical literal strings, earlier audit locators, confirmed key and discussions were visible before this check. The model was `gpt-6.1-sol`; temperature and seed are unavailable. This is one AI reinspection, without external expert or human confirmation.

| Card | Source observation and fixed-key result | Decision |
| --- | --- | --- |
| 198 | `t83r1ř` → `DLOHYCH`; six bodies, final roofed r emits CH. No intervening `2` is visible. | Preserve the defective literal; do not insert U. |
| 199 | Local `t4q g6` → `DIK ZA`; the complete q/g bodies have different lower strokes. Two separate roofed-r examples also remain visible. | Supports these local K/Z and CH readings. It does not construct a global legacy G-class bridge. |
| 199 | `h2t38?4m6` → `RUDOL?INA`; the unknown is the separately visible, low v-like legacy G16 body. | The new key leaves this body unassigned. Its missing F mapping neither deletes the source glyph nor disproves the old proposal. Canonical `f` means V and has a different tall looped form. |
| 199 | `s2hm684cd2` → `CURNALISTU`; `6f66q` → `AVAAK`; `f1h6tm5` → `VYRADNE`. | These source sequences remain awkward. No Z/S substitution or extra H is accepted. |
| 199 | `f58q385?6` → `VELKOLE?A`; the penultimate shoulder-and-descender body remains p/r variant. | Retain local B/H alternatives. The smoother P reading is not established. |
| 250 | `6m4cq3` → `ANISKO`; the fourth body remains a low open c-shaped curve. | Do not replace S with C. Printed background interference is disclosed. |
| 250 | `?375` → `?OJE`; the first body visually favors n/M, but background and hump boundary remain uncertain. | Keep n/m and M/N alternatives; MOJE is a candidate, not an accepted repair of historical NOJE. |
| 329 | `m58h5p6` → `NELREBA`; the third body is visibly double-loop 8. | Retain L; NETREBA would change a resolved source body. |
| 440 | `n5cs4c8m5qh6d5` → `MESCISLNEKRATE`; initial single shoulder differs from the later m-like body. | Retain initial M, without linguistic repair to N. |
| 453 | Separate conventional `14`, with two parallel underlines, between the surrounding cipher groups. | Prefer a local numeral interpretation with explicit metadata. Cipher interpretation YI remains recorded as the alternative. No general underline rule or link to another card is established. |

The canonical transcripts preserve the visible sign distinction, including the marked r convention. Unknown glyphs remain `?` with position ledgers. On card 453, numeral metadata preserves `14` and excludes it from encoded-body totals; it is not an added key assignment. All old keys, first literals and historical reports remain unchanged. Source-image bytes, crop bytes and private input history are omitted.

The ordinary `check.py` command checks the frozen anchor and `cards/*.json`; this separate partial audit has a `loci` schema and is not counted as a full card. Its individual outputs can be replayed from this directory with the standard library:

```sh
python3 - <<'PY'
import json
from decode import decode_text
with open('old-six-audit.json', encoding='utf-8') as stream:
    audit = json.load(stream)
for card in audit['cards']:
    for locus in card['loci']:
        result = decode_text(locus['ciphertext'], notation=locus['notation'],
                             transcription=locus['transcription'])
        for field, value in result.items():
            assert locus[field] == value, (locus['locus_id'], field)
print('PASS: 6 cards, 14 bounded loci; saved literals and ledgers replay exactly')
PY
```

Passing this substitution replay checks the recorded text against the fixed key. It does not independently verify the reader's glyph classifications, disputed alternatives, mark ownership or historical interpretation.
