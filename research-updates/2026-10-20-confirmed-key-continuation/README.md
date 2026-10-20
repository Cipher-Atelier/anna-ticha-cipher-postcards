# Confirmed-key continuation: first source batch, 20 October 2026

This experiment transcribes and decodes the complete selected picture-side bodies of **253,254,255,256 and258** with the unchanged supplied 204/460 key. These are research candidates, with uncertain glyphs and segmentation; none is declared solved. The earlier public records remain unchanged.

[253](cards/253.md) asks about a long silence. [254](cards/254.md) proposes a visit with a broom. [255](cards/255.md) thanks the addressee for a note and asks about her health. [256](cards/256.md) mentions an examination and music during leave. [258](cards/258.md) sends greetings after examinations. These descriptions follow tentative editorial readings. Ciphertext, strict literal output, Czech editorial text and English translation are separate in every record.

| Card | Visual rows | Selected encoded bodies | Known expanded letters | CH bodies | Unmapped bodies | AI source review |
|---|---:|---:|---:|---:|---:|---|
|253|9|310|313|3|0|Two frozen readings; reconciled candidate|
|254|23|389|386|1|4|Two frozen readings; reconciled candidate|
|255|14|395|399|4|0|Two frozen readings; reconciled candidate|
|256|17|498|498|2|2|Single reader; independent check pending|
|258|18|492|495|4|1|Single reader; independent check pending|

There are 2,084 selected encoded bodies across 81 visual rows. Counts depend on the selected segmentation and do not certify physical body counts or reading accuracy. “Known expanded letters” excludes preserved unknown placeholders; CH is one body emitting two letters. Zero unmapped bodies on253/255 does **not** mean zero uncertain signs: their alternative ledgers remain substantial. Written question marks are distinguished from unresolved body placeholders using explicit punctuation metadata.

The supplied 20 October comparison contains 22 assignments:21 ordinary values and marked-r CH. Canonical q means K; canonical g means Z. The earlier 460 ASCII g/9 convention is different notation and is rejected by this decoder. F,G,Q,W,X are unassigned by this supplied key. Missing assignments do not prove that these letters or their glyphs never occur.

The user reports external confirmation of the 204 solution and agreement with an independently reconstructed 460 key. This is author-supplied provenance, not a public verification receipt and not external confirmation of any newly read card. The later supplied 204 reading is frozen separately from the older public snapshot. [key.json](key.json) records the supplied PDF’s SHA256; [anchor204.json](anchor204.json) preserves all 14 normalized ciphertext/literal rows. Visual inspection covered complete relevant PDF pages 3–6, including the table, CH discussion, transcript and source image. The replay reproduces 571 bodies, 576 known letters and 5 CH occurrences. That verifies the supplied transcript/key relationship, not independent correctness of every source sign.

The [old-six audit](old-six-audit.md) reinspects 14 disputed loci on 198,199,250,329,440,453. It retains awkward source-supported literals such as DLOHYCH, CURNALISTU, AVAAK, VYRADNE, ANISKO, NELREBA and MESCISLNEKRATE. A visibly separate low glyph in RUDOL?INA remains unassigned by this key. The local q/g and CH comparisons do not construct a complete canonical-to-legacy G-class bridge. On 453, the underlined 14 is explicitly treated as a local numeral candidate, with YI as the cipher alternative. No general underline rule or historical correspondence link is established.

The [source inventory](source-inventory.json) finds 55 explicitly recorded card IDs and 83 exact image URLs in tracked repository text: 55 picture-side URLs and 28 address-side URLs. 38 cards have an explicit catalogue link in their published card page. This is a reproducible reference inventory, **not** a full catalogue or a fresh availability test. The historical 263-card assertion and 71 conditional reports are not counted as verified solutions. No missing media or catalogue IDs are calculated.

The [queue](queue.json) records the actual status of each observed ID. Current next priorities are blind second source readings of 256/258, resolution of 253–255 disagreements, then a whole-body batch 257,242,244,249 using their explicit recorded URLs. This is a saved first-batch checkpoint; a full collection investigation remains unfinished.

Research protocol and limits:

- Original HCPortal source scans were obtained by ordinary public GET, hashed and retained privately, with watermarks. Public records contain original derived transcriptions, exact URLs, hashes and locators; no scan/PDF/email bytes are included. HCPortal and source rights holders retain their rights.
- First readers froze source transcriptions before programmatic decoding and before seeing other full transcripts. The fixed key was visible; language influence cannot be excluded. The second 253 reader did not see the pilot; root 253 had seen its opening. Both 255 readers and both 254 readers froze separately. Subsequent reconciliation is explicitly nonblind.
- The delegated readers and reviewer used gpt-6.1-sol. The supervising Codex session inherited a GPT-6-family deployment whose exact model identifier was unavailable. Temperature and seed were unavailable. Tools: local view_image, Pillow for private lossless rotation/crop/enlargement, standard-library hashing/substitution, ordinary HTTP source access and Git. These are related AI readings, not independent human or historical validation.
- Canonical base-form labels preserve selected bodies; extra marks, alternate family readings, underlines and segmentation are recorded separately. Every minute incidental stroke has not been classified. No general mark-normalization rule is inferred. Substantive editorial repairs are marked as proposals and never fed back automatically into ciphertext.
- A passing replay verifies deterministic substitutions and saved counters. It does not inspect ink, prove independence, identify authors, authenticate dates or establish priority. Unknown and alternative glyphs remain unresolved evidence.

From the repository root, replay the frozen anchor and five candidate records:

```sh
python3 research-updates/2026-10-20-confirmed-key-continuation/check.py
```

Run the focused decoder tests from the experiment directory:

```sh
python3 -m unittest -v test_decode
```

The separate old-six locus replay command is in [its audit](old-six-audit.md). Existing repository verification remains:

```sh
python3 verification/check_all.py
python3 -m unittest discover -s verification/tests -v
```

The decoder was written after failing tests, including CH, q/g convention separation, unknown bodies, numeral metadata, written-question punctuation, invalid spans, anchor mutation and saved-literal mutation.10 new tests passed; the existing 100 tests passed. The existing 412-file manifest replay passed before adding this package. The final manifest includes only intentionally added derived text/code and the unchanged historical entries. [Review and validation record](validation.json).

No new research is merged, no email is sent, and no personal site is changed by this checkpoint.
