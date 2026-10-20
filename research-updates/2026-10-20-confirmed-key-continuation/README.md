# Confirmed-key continuation: source research in progress

The unchanged supplied 204/460 key has been applied to nine selected picture sides: **242,244,249,253,254,255,256,257,258**. All remain research candidates. Two separately frozen, related AI source readings now exist for each; later reconciliation is nonblind. This is not independent human/external confirmation and none is declared solved.

The source regions of all nine picture sides have been inspected. Cipher transcription remains partial where faded, overwritten or merged groups prevent confident glyph assignment or segmentation, especially257 and parts of242/244/249. Unknowns and awkward literals remain visible. The provisional red heading on 242 may be printed or handwritten; its cipher intent is not established.

| Card | Selected visual rows | Replay slots | Known emitted letters | CH slots | Unknown display slots |
|---|---:|---:|---:|---:|---:|
| [242](cards/242.md) | 6 | 259 | 262 | 5 | 2 |
| [244](cards/244.md) | 19 | 525 | 527 | 6 | 4 |
| [249](cards/249.md) | 17 | 285 | 282 | 6 | 9 |
| [253](cards/253.md) | 9 | 310 | 313 | 3 | 0 |
| [254](cards/254.md) | 23 | 389 | 386 | 1 | 4 |
| [255](cards/255.md) | 14 | 395 | 399 | 4 | 0 |
| [256](cards/256.md) | 17 | 498 | 497 | 2 | 3 |
| [257](cards/257.md) | 12 | 411 | 380 | 3 | 34 |
| [258](cards/258.md) | 18 | 491 | 494 | 4 | 1 |

Totals: **135 selected rows, 3563 replay slots, 3540 known emitted letters, 34 CH slots and 57 unknown display slots**. These are counters of the selected replay strings. Some `?` masks stand for clusters of unknown physical length, so neither their count nor replay-slot totals are exact physical glyph counts. Physical totals remain `null` where unresolved; no visual accuracy or source-coverage percentage is claimed. Known emitted letters exclude masks; CH is one selected body emitting two letters. Zero masks on 253/255 does not eliminate alternative glyph readings.

Each card JSON contains source URL/hash, orientation and source locators, frozen reader layers or their linked revision record, strict canonical ciphertext/literal output and uncertainty/mark/segmentation ledgers. Czech editorial proposals and English translations are separate and substantive restorations are bracketed or explicitly ledgered.257 provides only readable excerpts rather than reconstructing a full narrative from faded groups.

The [first five candidate artifacts](history/2026-10-20-batch1-b9bbdb9/snapshot.json) remain byte-exact from commit `b9bbdb9`. The [first 242/244/249 artifacts](history/2026-10-20-batch2-first-readings/snapshot.json) were frozen before second-reading reconciliation. [Dated revisions](revisions/) preserve changed and unchanged disputes. One additional nonblind253–255 contour check preferred5 rather than6 in255’s closing `VECNE`; other high-value unresolved forms remain.

The [address-face boundary audit](address-face-audit.json) records ordinary GETs and full-face visual inspection of the same nine address sides. No additional cipher group was observed. This is one nonblind AI face check, not independent proof. Sourcebytes and ordinary address text are not redistributed.

## Catalogue and next work

An ordinary anonymous GET of the [official catalogue API](https://api.hcportal.eu/api/cryptograms?detailed=1) returned one complete page of 1875 records. Filtering actual returned names `pc_hcp_198` through `pc_hcp_460` yielded **263 distinct records and 526 original image URLs**, with no missing name in that stated range. Exact catalogue IDs/media URLs were copied from their records, never inferred arithmetically. See [catalogue-records.json](catalogue-records.json) for source-response SHA256, pagination evidence, exact JSON pointers and thin derived records; [catalogue-access.json](catalogue-access.json) records discovery through the public frontend and ordinary read routes without credentials.

As retrieved, the official status object labels460 “Solved” and the other262 records “Not solved”; it contains a status label, not a plaintext. These are catalogue labels, not acceptance of our candidates.

This verifies catalogue name-range coverage. It does not authenticate historical corpus identity/authorship, prove that every image URL currently resolves, or decipher 263 cards. The older [tracked-text inventory](source-inventory.json) remains unchanged: 55 observed IDs, 83 exact URLs and 2521 cited mentions. Its scope was narrower than the official response. 71 historical conditional reports are not71 solutions.

The [263-record queue](queue.json) separates actual source acquisition, transcription, decoding candidates and source checking. The next source batch **259,260,261,262** is already being worked privately: first readings are frozen and blind second readings are underway. These four are outside the current nine-card replay until reconciled and reviewed. Work continues while sources are available; this is a progress checkpoint.

## Key, provenance and scope

The supplied 20 October comparison has 22 assignments: 21 ordinary values plus marked-r CH. Canonical q=K, g=Z. The older 460 ASCII g/9 convention is distinct and rejected by the decoder. F,G,Q,W,X remain unassigned in this supplied key, not forbidden historical characters. On256, an unassigned initial body is therefore retained as `?` rather than forced into the key.

The user reports external confirmation of 204 and agreement with an independently reconstructed 460 key. This is author-supplied provenance, not a public verification receipt or external validation of newly read cards. [key.json](key.json) records the supplied PDF hash; [anchor204.json](anchor204.json) freezes 14 normalized ciphertext/literal rows, kept separate from the older public204 snapshot. Complete relevant PDF pages 3–6 were visually inspected. Exact replay gives 571 selected bodies, 576 known letters and 5 CH. It verifies the supplied transcript/key relationship, not independent image-level correctness.

The [old-six audit](old-six-audit.md) reinspects 14 disputed loci on 198,199,250,329,440,453. Source-supported defective forms remain, and the separate low glyph in `RUDOL?INA` is unassigned by this key. Local q/g/CH checks do not build a complete legacy G-class bridge. 453’s underlined 14 is a local numeral candidate with YI retained as the cipher alternative. Historical keys/first outputs and their original manifest entries remain unchanged.

All original scans and the supplied PDF/email remain private, with source watermarks retained. Public artifacts contain derived original observations/transcriptions, hashes and cited metadata. HCPortal/source rights holders retain their rights. No email, merge or personal-site update is performed.

Readers/reconcilers and the separate read-only reviewer used gpt-6.1-sol. The supervising Codex session inherited a GPT-6-family deployment whose exact identifier was unavailable. Temperature and seed were unavailable. Tools: local view_image; Pillow for private rotation/crop/enlargement and disclosed contrast views; standard-library hashing/substitution; ordinary anonymous public HTTP GET; Git. The key was visible during source-only reading; language influence and shared-model effects cannot be excluded. Raw layers froze before decoding/other target transcripts, with individual exposure statements. Reconciliation after exchange is explicitly nonblind. No general mark-normalization rule is inferred and every minute incidental stroke has not been classified.

## Reproduction

From the repository root:

```sh
python3 research-updates/2026-10-20-confirmed-key-continuation/check.py
python3 verification/check_all.py
python3 -m unittest discover -s verification/tests -v
```

From the experiment directory:

```sh
python3 -m unittest -v test_decode
```

The separate 14-locus replay command is in [its audit](old-six-audit.md). The standard-library decoder was written after failing tests for CH,q/g conventions,unknown bodies,numerals,written question punctuation,invalid spans and frozen-anchor/literal mutations. 17 focused tests and 100 existing tests passed. [First checkpoint validation](validation.json) is historical; [current checkpoint validation](validation-batch2.json) records the continued source work and review. Current selected uncertainty spans are also checked against their exact line/offset, including valid empty-boundary absence notes. Passing checks establishes saved-string/key consistency and integrity only; it does not inspect ink, resolve masks, prove reader independence, identify authors, authenticate dates or establish priority.
