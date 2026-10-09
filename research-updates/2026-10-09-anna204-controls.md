# Anna204: control audit, 9 October 2026

The tested image comparator failed its control gates. A later check of complete glyph boundaries also failed to admit the full control set, and a proposed new control pool stopped at metadata selection. These results support keeping M11.17 unresolved. The cipher key and earlier readings have not changed.

## Sources and scope

The graphical controls came from [Anna199's source JPEG](https://api.hcportal.eu/media/4614/pc_hcp_199_pic.JPG), SHA256 `f50ac01e9e219b7f50d79a2373a81355ce81dbf94da43b12be1b1e7ff9a6a9ce`. The disputed target is on [Anna204](https://api.hcportal.eu/media/4629/pc_hcp_204_pic.JPG), SHA256 `4bef5c8218f2bdc21d93743e1e9f2862d2d08d38bec3f2356203338e86a06fb0`. Sources remain credited to their providers; links provide access without redistributing pixels.

The saved atlas and control metadata derive from the [public checking record at commit d91cd02](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/tree/d91cd02d10d68ce7d3780910620b0727b7eb2792/verification/anna-ticha). The follow-up tests below were local research, separate from that public baseline.

## Four bounded stages

1. **Initial comparator.** Twenty-seven combinations of ink threshold and crop displacement correctly classified 54 of 162 development-control evaluations. The target had no stable nearest class. This did not establish a letter.
2. **Controls-only extraction audit.** Context windows were being used as if they isolated individual glyph ink. All 12 recorded coordinate conversions were consistent with the specified CCW90 rotation. The single predeclared amendment removed thresholded pixels outside the saved horizontal assignment interval. Development performance improved, but held-out performance fell and glyph strokes were clipped.

| Recorded evaluations | Baseline | Amendment |
| --- | ---: | ---: |
| Development matches | 54/162 | 108/162 |
| Held-out matches | 135/162 | 108/162 |
| Held-out matches per setting | 5/6 | 4/6 |
| Extractions touching a boundary | 27/324 | 297/324 |
| Settings passing the full gate | 0/27 | 0/27 |

The six original examples remained development material. Held-out IDs were excluded from parameter choice, but some source context had already appeared in an earlier grid. This was a numerical/procedural holdout, with no claim of globally unseen pixels, independent class truth, or human expert validation. Repeated settings are dependent evaluations, not letter probabilities.

3. **Complete-boundary check.** Of the same 12 controls, five were accepted, five failed and two remained uncertain. The gate required all 12 to have complete, uncontaminated bodies with resolved stroke ownership. AI review used source contexts and proposed boundaries without letter values or the target; it was not independent human palaeography. Three controls had joined/overlapping contours with unresolved ownership. Four other problematic boundaries were not established as inherently unrepairable.
4. **New-pool feasibility.** The frozen rule requested six new bodies per class, at most two per class per line, after excluding the previous 12 IDs. G17 had eight eligible bodies distributed 1, 5, 1, 1 across four lines. Its maximum allowed capacity was `1 + 2 + 1 + 1 = 5 < 6`. The deterministic outcome was ABORT, before image review or blind classification. G02 had capacity 12; G20 had capacity 6. The six-per-class preliminary pool must be distinguished from the planned later three-per-class accepted test set.

## Evidence boundary and next step

Stages 2–4 did not classify M11.17. The semantic suggestion `byla` remains graphically unconfirmed. No new letter, key correction or complete plaintext follows from these tests.

The comparator rejection applies to this extraction procedure, these controls and these pixels. The pool abort applies to the fixed selection rule; it does not rule out a smaller new pool or establish that remaining glyph images are unusable. Further work needs a separately frozen protocol or additional independently annotated controls. Where stroke ownership cannot be separated, a genuinely more informative source copy may help; enlarging the existing image adds no evidence.

## Publication checks and access limits

This publication pass checked the local prose against saved numeric outputs and the pool-capacity arithmetic. It did not rerun the image experiments or reproduce the visual judgments. Earlier local integrity/replay checks are recorded in the retained research dossiers.

Local record identifiers (bytes are retained privately, not included here):

- Combined stages 1–2 report SHA256: `c6cdb0d9dfb4dc7277220f73b0f8e89229d4661297a491e4be2ea802f94e7ecd`.
- Stage 2 summary SHA256: `19e289d41450795d91e387bdb7683208bc35ae142b5b4f9b3060b01731da64a7`.
- Stage 3 report SHA256: `6374c9818a1ca49aa84ddb27f073a5a6c27e514819ba6c64020e28b38997cfbc`.
- Stage 4 report SHA256: `068a484a65a9f705c9ab279998a909d819d133421165ccf5cc04cd6d8be3609c`.
- Stage 4 abort record SHA256: `c759216a7abfacc3a4251acfa27ad9ddec8b292e50bbc722c80bf07192b02cec`.

This is a text-only research summary. Full replay requires the retained experiment code, metadata and source images, which this update does not distribute. Hashes identify records; they do not certify visual decisions or independently timestamp a protocol. No new blanket licence is asserted. Codex assisted the local research and this summary; AI agreement does not substitute for human source review.
