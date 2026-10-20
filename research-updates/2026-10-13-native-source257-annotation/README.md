# Native source257 physical annotation — 13 October 2026

This source-only follow-up records **56 approximate physical annotations in the first horizontal band: 33 visually whole singleton exemplars and 23 unresolved spans**. Every cipher-unit identity is **UNKNOWN**, and there are **zero validated repeated equivalence classes**. It accepts no new letters, plaintext or alphabet; it does not project the old seven claims onto these constructions. Sources258 and222 were untouched.

The result is useful physical annotation progress. “Whole” means a visually bounded construction with an approximate native-pixel envelope, typically about ±4 pixels; it does not certify exact contour inclusion, unique detached-mark ownership or a single cipher unit. The first-band record is partial coverage, not an exhaustive full-card inventory. Its 33 singleton classes are exemplar identifiers, not an inferred alphabet size.

## Actual result and disagreement

| Record | Physical records | Singleton geometric exemplars | Unresolved span records | Proven cipher units |
| --- | ---: | ---: | ---: | ---: |
| Raw A | 53 | 19 | see preserved alternatives | 0 |
| Raw B | 56 | 42 | 14 uncertain units | 0 |
| Reconciled canonical | 56 | 33 | 23 | 0 |

The [canonical JSON](data/reconciled-native-annotation-v1.json) is published byte-for-byte. The selected [A](data/native-annotation-A-v1.json) and [B](data/native-annotation-B-v1.json) records retain their conflicting physical partitions, singleton labels, mark ownership alternatives and numerical counts. They are filtered public selections, not exact full copies. Reconciliation follows geometry rather than votes or reader IDs; the [intersection mappings and differences](data/reconciliation-evidence-v1.json) preserve the raw namespaces and correspondence uncertainties.

At x703–763, A combined a crossed stem and neighboring curve while B recorded three local bodies. At x849–911 the shoulder and tall-stroke ownership differ. At x1223–1382 envelopes and divisions drift, so overlapping boxes do not establish matched identity. These differences remain evidence rather than a forced common alphabet. Correlated partition/mark-owner hypotheses and unallocated marks remain explicit in the canonical record.

The visual record was frozen before the machine candidate pack was read. This limits influence from connected-component proposals; it does not establish historical confirmation, independence from every prior expectation, or external human expert review.

## Original integrity and local source limits

The verified original encoded file is 1,288,265 bytes at 1785×1175 pixels, SHA256 `7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4`. Decoded RGB SHA256 is `5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94`. [Provenance](data/provenance.json) retains original/crop hashes and exact-original-row-slice verification metadata, with filenames reduced to basenames. Images and crops are excluded from this package.

The initial ROI was `[170,815,1710,905]`, half-open native xyxy. Local watermark/low-contrast interference near `[1030,835,1225,920]` limits ownership and contour judgments. This is a local quality limit; original bytes and decode were verified, and there is no finding of a globally bad scan. The initial bottom crop clipped continuations in `[1338,905,1440,917]`. Original-context examination recovered visible descenders, expanding approximate envelopes for the affected constructions (including U047/U049). Crop clipping was resolved through original context; endpoint precision and cipher roles remain limited.

## Why the earlier numerical input stopped

The [earlier diagnosis](data/old-input-diagnosis-v2.json) distinguishes source-field availability from actual code guards. The original source-only input declared classes **UNAVAILABLE** and supplied `classes=[]`; the resulting zero classes failed the actual **7..27 numeric class-count guard before the optimizer**. It did not fail because a universal historical authority certificate was required, or because physical annotation was prohibited.

`variants=[]` separately means finite transcription variants were **UNESTABLISHED**, not that zero interpretations were established. The raw `common_identity_stable_occurrences=[]` was a list, separately violating the required integer type. Whole-card coverage and cipher-unit roles were also unestablished scientific facts, but are distinct from those numerical guard conditions. Physical annotation can proceed while cipher identities remain UNKNOWN. The 33 physical singleton exemplars do not satisfy the old 7..27 cipher-class input requirement. No earlier experiment was rerun or tuned for this follow-up, and the old seven legacy claims were not reused as values or shape labels.

## Fixed-threshold diagnostics

The machine stage uses Pillow RGB-to-L conversion, `L <= threshold`, eight-neighbor connectivity, fixed thresholds 65/85/105/125 and the unchanged ROI. It chooses no preferred threshold and assigns no automatic glyph identity, ink ownership or cipher class.

| Threshold | Components | Foreground pixels |
| --- | ---: | ---: |
| 65 | 143 | 220 |
| 85 | 326 | 1,427 |
| 105 | 410 | 4,279 |
| 125 | 265 | 7,851 |

[Selected candidate metadata](data/candidate-pack-selected.json) contains only aggregate component/foreground counts and cross-threshold overlap/split/merge relation-type and degree counts. Individual component boxes, areas and edges are excluded because area-one boxes can reveal exact pixels. Connectivity components can join distinct contours or fragment faint ink; their counts do not substitute for the 56 manual annotations. The public selection also excludes RLE masks, pixel intersection indices, projections, zero-column coordinates and histograms. Whole-file hashes identify the complete private inputs without publishing a raster payload or per-letter hashes.

## Code, review and reproduction

The [publication selection ledger](data/publication-selection-ledger.json) records each whole input file SHA256, output SHA256 and exact selection/adaptation. Earlier scientific files elsewhere in the repository are preserved bytewise. The [scientific review](data/independent-native-annotation-scientific-review-v1.json) records source/crop, connectivity and annotation checks and its original v2 test findings. Its malformed-members TypeError and unit-based repeated-class count were corrected in v3; the separate [v3 review](data/independent-validator-v3-review-v1.json) records the fixes and additional fixtures. These computational and source checks are not historical confirmation.

The standalone [v3 validator](code/native_annotation_diagnostics_v3.py) and its five tests are exact supplied files. Its bbox helper is self-contained and unchanged in behavior. [Fresh actual diagnostics](data/actualnative-annotation-diagnostics-v3.json) validate the canonical typed structure with no errors: 56 annotations, 33 singleton exemplars, 23 unresolved spans, 56 UNKNOWN identities and zero repeated classes. Output SHA256 `bb86a8327528ab480f7f8f64a563e533d6dfe2786311d9d56f386462e5d01910` is byte-identical to the preserved earlier v1/v2 results. Selected malformed schema fixtures do not establish robustness for every possible malformed JSON input.

From the repository root, using Python with Pillow 11.3.0:

```sh
python3 -m unittest discover -s research-updates/2026-10-13-native-source257-annotation/code -v
python3 research-updates/2026-10-13-native-source257-annotation/code/native_annotation_diagnostics_v3.py research-updates/2026-10-13-native-source257-annotation/data/reconciled-native-annotation-v1.json /tmp/native-diagnostics.json
```

The [pixel utility](code/pixel_candidates.py) preserves the performed code's thresholds, geometry, original integrity assertions, crops, eight-neighbor component algorithm and cross-threshold relations. Its publication adaptations remove hardcoded personal SOURCE/BASE paths, add explicit `INPUT OUTPUT_ROOT` arguments and output-directory creation, and use provenance basenames. Raw code SHA256 is `a4903e849bbb0d5f874a3d204e173ecc4265897d2e97aa7fc06b44c8728ae459`. It has no automatic download. If a reader already holds the authorized original JPEG locally:

```sh
python3 research-updates/2026-10-13-native-source257-annotation/code/pixel_candidates.py INPUT_JPEG /tmp/native-private-output
```

This command writes **local private** crops and full candidate RLE/intersection arrays under the chosen output root. Those outputs are excluded from publication; place them outside the checkout. The report's `.gitignore` also excludes private-pixels, private-results, results and bytecode. The public candidate selection is not a substitute for those complete local raster diagnostics.

Local validation passed 8 new tests (3 pixel fixtures and 5 v3 schema fixtures), all 100 existing regression tests, and 6 existing portable numerical fixture tests. Fresh canonical diagnostics passed; workflow parsing passed both PyYAML safe_load and BaseLoader, preserving block-scalar commands, pinned actions and the Python 3.10/3.13 matrix. CI adds Pillow 11.3.0 beside NumPy 2.2.6 and discovers this code directory. `verification/check_all.py` passed with all 236 manifest files and saved replays; local testing used the available Python interpreter, and the two-version matrix remains a CI check.

Remaining scientific work is complete-card annotation, finer contour/mark-owner resolution and explicit tests of repeated physical equivalence and cipher roles. None has been converted into an accepted letter or historical claim here.
