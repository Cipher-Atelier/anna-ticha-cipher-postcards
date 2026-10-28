# Anna Tichá: HCPortal register submission

Prepared 28 October 2026. This package supplies the six fields requested for each individual reading: date, record name, recorded AI model/version, AI role, use of AI agents, and a direct URL containing the proposed text.

**154 distinct postcards have published readings, including partial proposals: 137 current canonical-key candidates and 17 legacy-only reports.** Card 204 has a separate external validity/key-consistency confirmation from 20 October. The other entries remain provisional or historical partial readings. The register curator can classify their eligibility individually.

## Open the records

| Need | Open |
| --- | --- |
| Browse all 154 cards with direct text links | [Individual reading index](register.md) |
| Import all six requested fields and qualifications | [UTF-8 CSV](register.csv) |
| Inspect exact metadata values and evidence pointers | [JSON register](register.json) |
| Check a few selected source/language questions | [Three questions on cards 321 and 320](review-request.md) |
| See the 108 cards planned by Eugen Antal and team | [Coordination list](coordination.md) · [JSON](coordination.json) |
| Reproduce and check this snapshot | [Builder](build.py) · [Checker](check.py) · [Validation receipt](validation.json) |

Every reading and metadata link points to repository snapshot [`f1b9c746afbe`](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/commit/f1b9c746afbe589ecc68dbca7bf213fce9e92d70). Later changes on `main` do not silently replace the submitted text. The CSV and JSON contain one entry per card number, even when an older report and a newer candidate both exist.

## How to interpret the requested fields

- **Date of decipherment:** the recorded date of a working candidate, its frozen source/reconciliation stage, or the 204 contribution packet. This does not mean that a complete solve was achieved on that date. An unavailable research date stays `null` in JSON and `Not recorded` in CSV. Repository commit author timestamps and later dated source reviews are separate fields. A commit author timestamp does not establish when a result became publicly available. An original report's website publication timestamp is not silently used as its research date.
- **Record name:** the HCPortal name `pc_hcp_N`. The separate catalogue ID and catalogue URL are supplied alongside it; a card number is not a catalogue ID.
- **AI model and version:** retained labels such as `gpt-6.1-sol` or a recorded GPT-6/Codex family description are reproduced as evidence. They are not converted into guessed public product names or release versions. Exact build/deployment identifiers and some later curator-model identities are unavailable. Early reports with no recorded label say so explicitly.
- **Role of AI:** source transcription, comparison, proposed Czech restoration, English interpretation and curation are described per row. Deterministic Python key replay is distinguished from source/language judgement.
- **AI agents:** 121 canonical candidates have paired related AI source-reader workflows. Cards 371–386 have one recorded root source reader and later nonblind review. Early reports do not fully record their orchestration. These labels describe the source-reading stage, not a census of every agent ever used on a card. Multiple related AI readings do not constitute external or human confirmation.
- **Text URL:** opens the individual reading with its literal/proposed text and uncertainties already present on the page. Metadata evidence links are additional; the reader need not search a directory for the text.

The 137 current candidates use the supplied 22-entry 204/460 key. The 17 legacy-only records retain their historical models and caveats. The 21 card numbers present in both report sets use the current candidate as the submitted text and include an additional link to the preserved report. Experimental or conditional analyses without an individual published reading are not promoted into extra decipherments.

The package records working-stage dates for **146 entries** and explicitly leaves **eight exact research dates unavailable**. A model label or family is recorded for **137 entries**; **17 early reports have no recorded label**. Even a recorded label does not supply an otherwise missing exact build or public release version.

## Coordination and remaining work

The attached 108-card list announced by Eugen Antal on 28 October matches exactly the cards without our separate published readings **except 460**. All 108 already have catalogue entries in the 263-record queue. Their work is recorded as planned, with no completion inferred. Card 460 remains the other team's separate result and is excluded from our 154 entries.

Our current descending source-completion pass covers 67 existing candidates and has **70 remaining**, next card **319**. This is deeper review of existing texts. Separately, **109 of 263** lack our own separate published reading: the team's planned 108 plus card 460. Their announcement changes work coordination, not those coverage totals.

## Reproduce

From the repository root in a full Git clone containing the pinned snapshot, run:

```sh
python3 research-updates/2026-10-28-hcportal-register/build.py
python3 research-updates/2026-10-28-hcportal-register/check.py
python3 verification/check_all.py
```

The builder reads only the pinned Git snapshot and the derived coordination identifiers. The checker verifies unique coverage, required fields, exact metadata pointers, dates, model labels, catalogue bindings, CSV/JSON/index agreement and direct text targets. CI runs it in the full checkout separately from the existing file-based replay checker. These checks establish the inventory's consistency; they do not validate the historical plaintexts. Original scans and private correspondence are not redistributed.
