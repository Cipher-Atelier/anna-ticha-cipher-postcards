# Card330: seven segmentation references and independent geometric proposals

Two fresh pixel-only AI annotations did **not** establish stroke ownership or a physical writing-unit partition for any of the six inspected groups. This records a bounded negative result, not a completed physical-position ledger. All thirteen masks, the frozen key, earlier ledgers and dates remain unchanged. No class or letter is accepted.

This separate record depends on [draft PR16](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/pull/16), head `c77d23250b61f549a8162ea07f2cd019f8b5876a`, and transitively [draft PR15](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/pull/15), head `8c8ad711e39315620b2c9ba625b4711ba8648d42`. It addresses the seven segmentation/stroke-ownership references in the previous assessment; it does not repeat the class comparison or date inspection.

## Frozen source, subset and context

The same original-named provider file [pc_hcp_330_pic.JPG](https://api.hcportal.eu/media/5007/pc_hcp_330_pic.JPG) supplied **1,431,536 bytes**, **1785 × 1175**, SHA-256 `206f29850350f429346d04bacc37c01bc377e50b1224a59d42bb6e785b781a05`. It is not a new scan or physical-source authentication.

The [protocol](evidence/card330-stroke-ownership-2026-10-11/preregistered-protocol.json) froze the entire seven-reference subset, approximate group windows, broader contexts and comparison rules before either observer began. Historical encoded references below identify saved proposals; **they are not established physical glyph positions**. Two saved references share Z04. No encoded-slot window or expected physical count was supplied to observers.

| Saved unresolved reference | Historical group | Anonymous view | Approximate group locator, original xyxy |
| --- | --- | --- | --- |
| R_L02W04B05 | L02W04 | Z05 | [511,866,646,947] |
| R_L02W07B05 | L02W07 | Z03 | [809,866,920,947] |
| R_L03W11_COUPLED_SPAN | L03W11 | Z01 | [1027,908,1151,988] |
| A007 | L03W16 | Z06 | [1558,908,1621,988] |
| R_L03W17B01 | L03W17 | Z04 | [1620,908,1690,988] |
| A008 | L03W17 | Z04 | [1620,908,1690,988] |
| U001 | L05W09 | Z02 | [1108,988,1233,1068] |

All rectangles use half-open original-image coordinates. The full writing-block context was [60,800,1710,1110]; each local view retained the whole writing-block height and horizontal neighbors, rather than an isolated alleged symbol. Locators were not drawn over ink. Observers could extend envelopes beyond a locator and consult full context. Local side crops do omit peripheral writing, so annotations are not exhaustive editions of those crops.

Seven raw views and seven ruler copies used **native 1:1 scale**, without interpolation, enlargement, thresholding or contrast changes. Rulers occupied separate 48-pixel margins. All raw pixels and ruler interiors were independently checked against the decoded original. The pre-observer [display clarification](evidence/card330-stroke-ownership-2026-10-11/pre-observer-display-clarification.json) specifies that every watermark pixel within each frozen crop is retained; cropping necessarily omits outside pixels, and the full JPEG remains intact locally. No pixels are published.

## Independent proposals and their limits

Each observer received only the [anonymous manifest](evidence/card330-stroke-ownership-2026-10-11/observer-safe-manifest.json), coded native views, coordinates/scale and geometry instructions. Key, plaintext, prior candidates, historical references and expected symbol counts were withheld. They reported selected ink envelopes, uncertain junctions, alternative ownerships and sparse approximate centerlines. An envelope is neither a verified maximal connected component nor a physical writing unit.

The unchanged [O1 record](evidence/card330-stroke-ownership-2026-10-11/observer-O1.json) froze at 02:48:52 UTC; the unchanged [O2 record](evidence/card330-stroke-ownership-2026-10-11/observer-O2.json) froze at 02:49:50 UTC. Both hashes were checked before comparison or cross-reading; the [freeze receipt](evidence/card330-stroke-ownership-2026-10-11/observation-freeze.json) preserves the chain. These were fresh AI contexts from the same model family, with instruction-only restrictions in a shared filesystem. This is procedural concealment, not certified isolation, globally blind ground truth or independent human expert validation.

Neither observer had a calibrated click or contour-tracing tool. O1 estimated generally 4–8 native pixels of boundary uncertainty, with 9 for a faint trace; O2 estimated 5–8. These are uncalibrated self-estimates. Integer coordinates do not imply one-pixel precision. O1 supplied six approximate paths and O2 three; these are not complete traced contours or a stroke-order reconstruction.

## Measured agreement of envelope boundaries

The frozen rule matched boxes one-to-one by maximum total intersection-over-union (IoU), allowing unmatched boxes and excluding zero-overlap pairs. A pair met the descriptive convention only with **IoU ≥ 0.5 and every absolute boundary difference ≤ 8 native pixels**. These exploratory display-coordinate thresholds are not calibrated accuracy criteria.

The [comparison](evidence/card330-stroke-ownership-2026-10-11/agreement.json) retains every paired box, exact IoU, signed and absolute boundary difference, unmatched item and denominator. Independent exhaustive matching reproduced all twelve region/field objectives and every result. Matching is geometric only: paired boxes can describe different extents or roles.

| View | Component proposals O1/O2 | Paired / close | Unmatched O1/O2 | Junction proposals O1/O2 | Paired / close | Unmatched O1/O2 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Z01 | 5/6 | 5/1 | 0/1 | 2/2 | 2/0 | 0/0 |
| Z02 | 4/5 | 4/3 | 0/1 | 2/2 | 2/1 | 0/0 |
| Z03 | 6/7 | 6/5 | 0/1 | 2/2 | 2/1 | 0/0 |
| Z04 | 4/4 | 4/1 | 0/0 | 2/2 | 2/1 | 0/0 |
| Z05 | 6/7 | 4/2 | 2/3 | 2/3 | 1/0 | 1/2 |
| Z06 | 5/5 | 4/0 | 1/1 | 1/3 | 1/0 | 0/2 |
| Total | 30/34 | 27/12 | 3/7 | 11/14 | 10/3 | 1/4 |

“Close” means the stated descriptive convention. Counts are nonexhaustive annotation records, including overlapping views, **not unique glyph counts, coverage rates, accuracy estimates or independent trial probabilities**. Unmatched selection does not prove an observer denied visible ink.

Native-source review identified a coordinate-reliability warning: O1's Z01 isolated-spot box [1156,974,1167,985] appears below the visible spot; O2's [1155,962,1171,975] appears closer. Their algorithmically paired IoU is only 0.0346. Neither raw record is repaired, and the review does not certify the alternative as a calibrated boundary.

Z03-J1 illustrates a scope mismatch: O1 bounded a long horizontal span [790,912,913,930], O2 its right junction [890,905,924,931]. Their 100-pixel left-boundary difference is not a 100-pixel tracing error. In Z05, O1 separates nearby envelopes that O2 combines, while Z05/Z06 neighboring-row selections also differ. The numerical comparison preserves these differences instead of equating all paired rectangles with the same physical object.

## Ownership alternatives remain

All **25** reported junctions have `ownership_resolved=false`. Neither observer proposes an established physical partition in any region. The [assessment](evidence/card330-stroke-ownership-2026-10-11/assessment.json) retains the ledger implications and review cautions.

| View / saved references | Alternatives retained after annotation |
| --- | --- |
| Z05 / R_L02W04B05 | Continuous loop/low curve versus touching or crossing trajectories; neighboring upper-row return may be separate or contact lower ink. Envelope selection differs. |
| Z03 / R_L02W07B05 | Long horizontal stroke as a right-hand return versus separately drawn stroke touching/crossing it. A lower-row tip may be separate or contact the bar. |
| Z01 / R_L03W11_COUPLED_SPAN | Upper-row return meeting lower ink versus shared continuation/superposition; neighboring low contours may be separate or joined. No physical count is inferred from the coupled encoded span. |
| Z06 / A007 | Shared crosswise return/bar versus one contour crossing another versus an independent bar; lower folds and neighboring cluster contact remain uncertain. |
| Z04 / R_L03W17B01 and A008 | Continuous loop/return chain versus neighboring touching/overlapping trajectories, including a higher return crossing another low portion. The two saved masks do not become two asserted physical positions. |
| Z02 / U001 | Upper-row return crossing separate lower curves versus one folded trajectory spanning row levels versus several superposed strokes. |

Even the close Z04 junction pair (IoU approximately 0.785; boundary differences 1,2,1,4 pixels) retains incompatible ownership possibilities. Envelope agreement does not settle who owns a shared bar, return or crossing.

Both observers retained possible right-edge uncertainty in Z04. Their x1710 is the **supplied-context edge**, not the 1785-pixel JPEG edge. A separate [post-freeze coverage audit](evidence/card330-stroke-ownership-2026-10-11/post-freeze-source-coverage-audit.json) inspected the original right margin without resizing: the reviewer did not see handwriting continuing beyond x1710 into the pale outside-card scan margin. No significant omitted rightward continuation was demonstrated. This later unblinded audit neither changes the frozen annotations nor proves the physical endpoint or ownership.

## Ledger delta and stop

New independent proposal envelopes and explicit disputed geometries are now recorded. **Zero source-verified physical boundaries, zero accepted physical positions, zero class assignments and zero letters** are added. The physical body count remains unknown. The physical-position and stroke-ownership gap is not closed, and all thirteen masks survive.

This AI ruler-interpolation path stops here. Lack of calibrated pointing/tracing, nonexhaustive and differently scoped envelopes, a locational warning and unresolved dark contacts prevent a reliable geometric edition. That is a limit of this method and result; it does not prove these JPEG bytes contain no further usable evidence.

A future attempt needs a genuine coordinate-pointing/tracing workflow, explicit distinctions between ink contours, connected envelopes and physical writing units, and independently auditable source-coordinate annotations made without linguistic/count priors. More informative independent scans could help dark crossings, but static geometry may still admit several ownership histories. Any later letter/class acceptance needs an independent class control beyond boundary agreement. No reannotation, criterion tuning or enlarged-JPEG detail claim was used after these results.

The [text packet manifest](evidence/card330-stroke-ownership-2026-10-11/manifest.json) identifies frozen inputs and derived records. Collector/comparison scripts remain local; the comparison record identifies the evaluator hash. Repository fingerprint/replay checks verify integrity of saved records, not these visual judgments. Source credit and restrictions follow the [existing card330 record](../anna-ticha/card-330.md); access does not grant image redistribution rights. No merge, deployment, website or image publication is part of this result.
