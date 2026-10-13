# Source257 full-card physical map — 13 October 2026

This corrected source-only map records **307 physical annotation records: 172 visually whole constructions and 135 unresolved spans/overlays**, across the first band and twelve additional visible trajectories. The map supports **two checked graphical groups with seven distinct complete-body members**, leaves **300 records ungrouped**, and retains **three deferred proposals**. Every cipher role remains **UNKNOWN**. These are physical annotation and visual similarity results, with no new letters or decipherment claim.

| Component | Records | Visually whole | Unresolved spans/overlays |
| --- | ---: | ---: | ---: |
| Immutable first band | 56 | 33 | 23 |
| New source regions | 251 | 139 | 112 |
| Total | 307 | 172 | 135 |

The [canonical v2 map](data/fullcard-map-v2.json) is a byte-identical copy, SHA256 `f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34`. It maps visible manuscript trajectories and inspected reserve regions; it does not certify pixelwise exhaustive manual-ink segmentation or a perfect glyph total. Eight new frozen-overlap scopes and nine frozen-overlay conflict entries remain explicit. The [adjudication evidence](data/fullcard-adjudication-evidence-v2.json) preserves finer raw partitions and ownership alternatives inside conservative unresolved spans, rather than deleting disagreements to obtain a count.

## Source review changed the result

The first assembled version reproduced byte-for-byte and passed its closed-record checks, but exact per-body source review found boundary/target errors beyond the approximate tolerance. The corrected map reinspects all 39 previously whole bottom constructions: **10 envelopes corrected, seven records downgraded to unresolved, and 22 whole records retained**. Total records remain 307; whole declarations fell from 179 to 172. Superseded v1 remains a private immutable input, identified by whole-file hashes in the selection ledger.

Corrected FC195 `[240,1045,264,1081]` bounds the complete bowed curve; FC196 `[262,1045,292,1081]` bounds the neighboring upper-bar/neck/low-return body. FC193 is expanded to `[165,1036,203,1079]` and remains unresolved. FC152/154/167/168/171/198 are the other downgrades. The opening-direction wording for FC179/183/195 now states a bowed LEFT contour and RIGHT opening. Erroneous v1 windows are not retroactively justified by the approximate ±4-pixel convention.

The [independent scientific review](data/independent-fullcard-scientific-review-v1.json) passes the final v2 products with explicit limits and no remaining blocking findings. It verified 91 revision detail/context/tight views and supports the ten corrections and seven conservative downgrades. A specific B6 left-edge check found FC208 covers the first low-arch ink within the stated tolerance; it did not establish a separate missing body in the following interval. Whole-file view-proof hashes and aggregate checks are public; per-body image/RGB hashes remain private.

This correction demonstrates why byte reproducibility and structural validity do not establish visual correctness. Bounds and source judgments required actual native-pixel review. The final public closed-record check validates the corrected records and group constraints; it is not another source inspection.

## Checked complete-body graphical groups

| Group | Members | Shared visible geometry |
| --- | --- | --- |
| VG001 | FC179, FC183, FC195, FC066, FC121 | Continuous bowed left contour, right-open interior and short terminals |
| VG002 | FC196, FC093 | Upper bar, descending left neck and one rounded lower return, open on the left |

The [final groups](data/visual-repeat-groups-v2.json) compare complete visible connected bodies in the native bottom orientation or exact 90CW right-block orientation. Seven members are distinct native occurrences, declared whole and free of unresolved frozen-instance overlaps/conflicts. No attached stem, bar, bowl or connecting path was removed to force agreement. Terminal lengths, angles, thickness and lower-return depth vary. These are nonexhaustive checked visual similarities, not repeated cipher-unit identities or two established alphabet classes.

[Matching evidence](data/visual-repeat-canonical-matching-evidence-v2.json) retains source-occurrence choices, features, alternatives and deferrals. Source-only proposals were frozen before canonical matching; corrected native bodies were then checked explicitly. FC193 remains deferred because its ownership and body partition are unresolved. Two other deferred proposal records and all 300 ungrouped canonical records remain listed. No accepted class is forced from an unresolved mark or span.

## Source, scope and preservation

This stage extends the source-only physical map across visible manuscript regions of source257. Physical record counts describe annotation granularity, not a perfect count of cipher glyphs. Cipher roles remain UNKNOWN; repeated graphical similarity is not a letter assignment, inferred alphabet or historical decipherment. Sources258 and222 were untouched. No earlier numerical experiment was rerun or tuned, and the old seven claims were not projected onto these forms.

The [first-band canonical annotation](../2026-10-13-native-source257-annotation/data/reconciled-native-annotation-v1.json) remains byte-identical at SHA256 `bdb98089160dea39306bdce159c0d9bed88fc6eab7f75aaf7bc6a25ed2cd9c91`. The full map copies its 56 units unchanged and references all remaining top-level uncertainty, ownership, alternatives, quality and scope information in that immutable file. Preservation does not upgrade those first-band records into cipher units or exact contours.

The original source identity remains 1,288,265 encoded bytes, native RGB 1785×1175, encoded SHA256 `7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4`, decoded RGB SHA256 `5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94`. Publication preparation used code and JSON only; it did not inspect source pixels. Original/source checks below are recorded evidence from the source stage, distinct from the publication's local schema and replay checks.

## Native views and physical boundaries

The [native view manifest](data/native-views-manifest.json) records 30 unchanged lossless views and exact row-slice/rotation proofs. Bottom context `[65,810,1710,1140]` and right context `[1330,50,1705,855]` overlap at `[1330,810,1705,855]`. The manifest's 18 reserve rectangles plus these two context rectangles cover every original pixel. Geometric rectangle coverage does not prove every visible mark was annotated.

The right block uses an exact 90° clockwise transpose, without scaling or enhancement. Native-local pixels map as `u=H-1-y; v=x`, with H=805; half-open native-local boxes map as `[H-y1,x0,H-y0,x1]`. The [validation metadata](data/native-views-validation.json) records exact source identity, all 30 PNG hashes, original-row equality, rotated-tile equality and three synthetic tests. No image files are redistributed here.

The sourcepack's [initial independent scientific inventory](data/independent-sourcepack-initial-review-v1.json) distinguishes geometric coverage from mark completeness. The thin red trace near `[565,25,577,52]` remains manual/text residue with UNKNOWN role. The oblique separator near `[1640,579,1707,615]` reaches the physical card edge after extended available-pixel inspection; its endpoint remains uncertain. These marks are not automatically treated as cipher constructions.

## Raw annotation alternatives

The selected raw [right A](data/right-A-v2.json), [right B](data/right-B-v1.json), [bottom A](data/bottom-A-v1.json) and [bottom B](data/bottom-B-v1.json) files preserve scientific geometry, uncertainties, source-quality notes and proposed correspondences. Operational view histories, reader identifiers and personal paths are removed; these are public selections rather than full exact copies. The private originals remain unchanged and their whole-file hashes are recorded in the selection ledger.

Right A has 171 physical records; right B has 170. Bottom A has 266 records (240 bounded constructions and 26 unresolved spans), 14 unallocated marks and 10 frozen-overlap candidates. Bottom B uses a coarser representation: 171 records, comprising 38 whole records, 116 spans and 17 marks. These counts cannot be compared as cipher-glyph totals or used to infer accuracy. Competing partitions and ownership hypotheses remain evidence for adjudication rather than votes for one alphabet.

An overlap may be a second view of the same occurrence. Neither crossing context rectangles nor a new record near a frozen bbox establishes an independent repeat. Unresolved frozen-instance overlaps and conflicting frozen overlays are excluded from accepted flat repeated groups by the schema check; whole physical extents alone do not resolve instance identity.

## Reproduction and publication boundary

[The selection ledger](data/publication-selection-ledger.json) identifies each whole input SHA256, public output SHA256 and transformation. It makes no claim that filtered files are exact full copies. Only metadata, approximate physical geometry and own code are published. Images, books, private letters, masks, RLE, pixel intersection indices and other raster reconstruction payloads are excluded. All prior scientific files remain bytewise unchanged.

[Native view code](code/native_views.py) and its three fixtures are exact supplied files. It takes explicit local `INPUT OUTPUTROOT`, reads only that local source, and produces private crops under the output root. There is no automatic fetch, enhancement or image resampling; the optional transpose is exact. Operators who already hold an authorized original may run:

```sh
python3 research-updates/2026-10-13-source257-fullcard-map/code/native_views.py INPUT_JPEG /tmp/source257-private-views
```

Place generated output outside the checkout. The report's `.gitignore` excludes private-pixels, private-results, results, image extensions and bytecode. The native utility verifies crop/transpose preservation for the supplied RGB input; the manifest records the actual source identity used in this study.

[Closed-record validation code](code/fullmap_checks.py) checks fixed source identity/bounds, exact frozen-file digest and deep unit copies, references to all frozen annotation keys, valid physical states and UNKNOWN new roles, overlap restrictions, group membership and remaining-unit lists. It rejects semantic mapping fields and does not correct input records. The frozen file is operator-selected: its SHA256 must also be independently pinned. Coverage/source-quality states and visual evidence entries remain declarations, not visual or historical proof. Thirteen schema fixtures cover positive and negative cases; they are not a claim of robustness for every possible malformed object.

From the repository root with Pillow 11.3.0 installed:

```sh
python3 -m unittest discover -s research-updates/2026-10-13-source257-fullcard-map/code -v
python3 research-updates/2026-10-13-source257-fullcard-map/code/fullmap_checks.py research-updates/2026-10-13-source257-fullcard-map/data/fullcard-map-v2.json research-updates/2026-10-13-native-source257-annotation/data/reconciled-native-annotation-v1.json --groups research-updates/2026-10-13-source257-fullcard-map/data/visual-repeat-groups-v2.json /tmp/source257-fullmap-result.json
```

Computational reproducibility establishes declared structure and saved-file consistency. Checked visual similarity remains a bounded source judgment. Neither establishes historical identity, alphabet equivalence, plaintext or decipherment accuracy.

The [v1 assembly helper](code/assemble_fullmap.py) and [v2 correction helper](code/assemble_fullmap_v2.py) contain explicit source-inspected manual decision tables. They require byte-exact pinned private raw/v1/proof inputs. Published raw selections have different hashes because private operational fields were removed, and per-body crop proof hashes remain private, so these helpers do **not** provide a complete rebuild from the filtered public files. No adapter that changes those pins is supplied. Public users can inspect the manual tables, preserved alternatives and final map and run the closed-record checks directly. [V2 assembly reproducibility](data/fullcard-map-reproducibility-v2.json) verifies exact pinned-input output bytes, frozen/raw preservation and changed-pin rejection. It cannot recreate or independently validate source judgments.

## Local validation

All **130 tests passed**: 100 existing regressions, six portable numerical fixtures, eight first-band fixtures and 16 new fixtures (three native-view, thirteen closed-map). Fresh public v2 map + pinned frozen file + final groups validation passed with zero errors and no input changes; the [saved diagnostic](data/actual-fullmap-withgroups-validation-v2.json) reports 307 records and seven group members. Workflow parsing passed both PyYAML safe_load and BaseLoader, preserving existing checks, NumPy 2.2.6/Pillow 11.3.0, pinned actions and the Python 3.10/3.13 matrix. Local tests used Python 3.13.9; the two-version matrix remains a CI check. Both manifests and the complete offline verification pass; prior scientific data and the frozen canonical remain byte-identical.

Remaining uncertainty includes 135 unresolved scopes, approximate body boundaries, detached-mark ownership, local watermark/ink interference, frozen overlaps, the card-edge endpoint and the upper red trace. Full visible-region inventory and two graphical groups do not establish a historical alphabet, exact cipher-unit count or decipherment. No execution blockers remain for this bounded public package.
