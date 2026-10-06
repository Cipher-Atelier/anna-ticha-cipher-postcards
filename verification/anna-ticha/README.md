# Anna Tichá: independently check the fixed-key reading

This release makes **card 199** reproducible from source positions to the exact literal output. It includes the unchanged key, all 532 recorded bodies, both readers’ retained position records, reconciliation decisions, coordinates, source hashes and runnable verification. Source scans and image-bearing PDFs are deliberately **not** mirrored here.

## Five-minute start

1. Download this directory with its files intact, or clone the repository.
2. From this directory run `python3 verify.py`. No third-party packages, images, network or file writes are needed. Expected: 532 positions, 522 mapped, 10 unknown, 524 emitted nonunknown characters, 23 observed original classes and no secondary mark transformation.
3. For the actual image atlas and source transcript, obtain the original JPEGs linked in [SOURCES.md](SOURCES.md), subject to [HCPortal’s terms](https://hcportal.eu/terms.html). Put them in a local folder using the listed filenames.
4. Run `python3 source_images.py --source-dir /path/to/your/scans --render`. This requires Pillow (`python3 -m pip install Pillow` if needed). Open the resulting `local_preview/index.html`. It shows all 24 classes as actual source crops, the complete card 199 transcript, per-body images and the separate mark examples. All 599 crop pixel checks must pass before completion.
5. For a second read-only check, run `python3 verify.py --source-dir /path/to/your/scans`.

No original scan is required just to reproduce the literal. Original scans are essential to challenge the graphical readings.

### Optional browser-only viewer

Download [viewer.html](viewer.html) and open it as a local file in a modern browser. Select the three JPEGs using its file picker. The file has embedded research metadata, **no scan pixels**, and rejects a source whose SHA-256 differs. It is designed to keep selected files in the browser and make no network requests. Its browser UI has not yet been end-to-end tested in the build environment; the tested Python-generated local preview above is the primary visual route.

### Optional explicit download helper

After reviewing the provider terms and deciding that you may obtain the sources for your use:

`python3 source_images.py --fetch --accept-source-terms`

This requests only the three exact source URLs in the manifest. It does not crawl, bypass access controls, retry a denial, overwrite a mismatched existing file or accept changed source bytes. Without `--fetch`, it makes no network request. If it fails, use the official links normally or ask the provider; do not seek an alternate route around a restriction. The download route was not exercised in this release; all tests used retained originals.

## What is actually covered

| Material | Apparatus in this directory | What it does not claim |
|---|---|---|
| Card 199 | Complete 532-body replay; 22 auxiliary punctuation observations; 16 source lines; unknowns, alternatives, reader IDs and coordinates | A perfect transcription, secure cross-panel order, or historical truth |
| Card 440 | Two source-position examples, P001/P015, for the unbarred-t class | A whole-card position/transcript release or a new held-out success |
| Card 453 | Four source-position training mark examples, P005/P010/P012/P034 | A whole-card position/transcript release or independent validation of the mark operators |
| Every other Anna card | No new whole-card positional packet in this directory | Articles or literal readings elsewhere are not automatically granted this card199 audit trail |

This is one worked-example release, not a claim that every Anna article is equally reproducible here. The 24th key class, unbarred t, is absent from card199; its value was proposed after the first card440 test. None of card199’s ten unknowns passes the strict V2 mark gate.

## Review the evidence, then the language

- Inspect the source image first. Compare complete shapes, including overhead marks and nearby strokes.
- Use [the atlas index](docs/GLYPH_ATLAS.md) and the locally generated image atlas to identify a frozen class, or leave it unknown.
- Reproduce the unchanged lookup. Do not silently fix a glyph to produce a plausible word.
- Assess Czech only afterward. The literal preserves defects such as `curnalistu`, `velkoleba`, `avaak` and `vyradne`. Modern accents and proposed word repairs are not in the first replay.
- Cite position IDs for disagreements. For example, `C199.L07.T19` has clear V-like geometry but uncertain ownership and remains unknown.

## File guide

- [data/card199_positions.csv](data/card199_positions.csv): complete convenience table, one row per body.
- [data/card199_positions.json](data/card199_positions.json): the same table with structured alternatives, marks, original boxes and both reader identifiers.
- [frozen/tokens.json](frozen/tokens.json): unchanged retained reconciliation with both original reader records, all groups and segmentation alternatives.
- [frozen/key.json](frozen/key.json), [frozen/rules.json](frozen/rules.json): unchanged key and strict secondary rules.
- [frozen/first_receipt.json](frozen/first_receipt.json): original replay receipt. References to historical input files are retained evidence, not claims that every historical project file is republished here.
- [data/glyph_atlas.json](data/glyph_atlas.json): 47 selected examples covering all 24 classes, exact coordinates and source hashes. The public file contains references, not image data.
- [data/crop_pixel_checksums.json](data/crop_pixel_checksums.json): 599 reproducible RGB pixel digests; no pixels are encoded in these hashes.
- [literal.txt](literal.txt): exact retained first output.
- [PUBLIC_INVENTORY_SHA256.json](PUBLIC_INVENTORY_SHA256.json): a new inventory of this release, not an original freeze manifest.

## Provenance and limits

This public presentation was assembled on 5 October 2026 from retained verified research evidence. Its atlas selections, convenience tables, scripts and local-view layouts are new presentation work. The frozen key, rules, reconciled token record, geometry record and first literal remain byte-identical to the retained originals. The verifier checks their historical hashes. The selected card199 atlas examples were chosen after the card’s replay and are not passed off as its original predecode reference atlas.

Source readings and linguistic assessments were AI-generated. “Independent readers” means separately tasked AI runs with restricted inputs; no external human expert authentication is claimed. Retained timestamps and hashes establish internal consistency, not independently certified timestamps or proof of reader blinding. Mapping coverage is not accuracy. The packet does not establish authorship, attendance, personal identity, historical priority or decipherment of the entire collection.

See [RIGHTS.md](RIGHTS.md) for the conservative image-publication decision. The locally generated `private_sources/` and `local_preview/` folders are ignored by Git; do not add their scans or derivatives to a public commit without the needed rights.
