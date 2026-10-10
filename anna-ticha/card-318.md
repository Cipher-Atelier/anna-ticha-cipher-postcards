# Card 318: a preliminary May Day greeting

[Anna Tichá investigation](README.md) · [All card readings](readings.md)

Research recorded on 9 October 2026. Initial source comparison, transcription, translation and mechanical checks by Codex (GPT-6), using the previously published Cipher-Atelier key. A separately tasked Codex reviewer (GPT-6-astra) compared the proposed main-block reading with the source and atlas before publication. No new key is proposed. This is a preliminary reading, without independent human palaeographic validation.

## Scope and literal

The four-line main block on [HCPortal record 1637, pc_hcp_318](https://crypto.hcportal.eu/dashboard/cryptograms/1637) gives a connected Czech greeting under the unchanged key. The proposed transcription contains 96 mapped bodies in 17 words, exercising 19 existing classes. These counts describe accepted assignments in this selected block, not historical accuracy or whole-card coverage. The later strip-B follow-up below records part of the marginal text separately; other margins remain outside this edition.

```text
v den prvniho maje srdecny
pozdrav a dlouhou. vrelou pusu
sve touzene, predrahe andulce
posila vzpominajici pepous.
```

The dot after `dlouhou`, comma after `touzene` and final dot are recorded separately from the 96 class assignments. In particular, the unusual dot is not silently replaced with a comma. Faint incidental traces and complete mark ownership have not been systematically inventoried, so this is a base-class reading rather than a complete diplomatic edition.

## Interpretation

Proposed sense: “On the first of May, a heartfelt greeting and a long, warm kiss to his longed-for, dearest Andulka, sent by Pepouš, who is thinking of her.” The punctuation in this fluent interpretation is editorial; the literal above remains unchanged.

Accent restoration would give `prvního`, `máje`, `srdečný`, `vřelou`, `své`, `toužené`, `předrahé`, `posílá` and `vzpomínající`. Initial capitals and `Andulka`/`Pepouš` are editorial normalizations. No accepted base letter was replaced to make the passage fluent. The affectionate address and proposed signature do not identify the writer or establish a relationship or a delivered kiss.

The catalogue gives 1 May 1901. The opening agrees with its day and month; it does not independently establish the year. The address face and postal markings were not examined in this experiment.

## Source and evidence

- [Original picture-side JPEG](https://api.hcportal.eu/media/4971/pc_hcp_318_pic.JPG): 1785 × 1175 pixels; SHA-256 `ad2a5267d2038072fb2d0306d12393616a79239937879d0691bcde2ce76c147e`.
- Main-block source context, in original pixels: approximately `[5,470,205,1100]`, rotated exactly 90 degrees counterclockwise for reading.
- [Word ledger](../research-updates/evidence/card318-2026-10-09/word-ledger.csv): 17 contextual source boxes, manually assigned class sequences, resulting words and body counts. Boxes may contain neighboring strokes and are not isolated full-glyph segmentations.
- [Saved literal](../research-updates/evidence/card318-2026-10-09/literal.txt) and [input fingerprints](../research-updates/evidence/card318-2026-10-09/manifest.json).
- Existing [key](../verification/anna-ticha/data/key.csv) and [graphical reference atlas](../verification/anna-ticha/docs/GLYPH_ATLAS.md), read at commit `985167d8a5bf20cf6c74f3b58c32396929fcbd35`.

The atlas's downloaded card199 and card440 source bytes matched their published hashes. Comparison used their source crops and the complete new main block, with exact rotations and display enlargement only. No reconstructed or added ink was used. Images and crops are linked through their providers rather than redistributed here; no new licence is asserted over them. Credit for source access belongs to HCPortal and the collection holders, and for the existing key to the researchers credited in the [original study](article.md).

## Checks and limitations

The saved ledger was checked against the unchanged key: all 17 class sequences reproduce their saved words; they sum to 96 bodies and 19 distinct classes. Joining the four lines and separately transcribed punctuation reproduces `literal.txt` exactly. Input and output hashes match the manifest. All source boxes lie inside the original JPEG; a 17-word contact sheet and the full block were visually inspected.

For manual replay, look up each space-separated class ID in `word-ledger.csv` against `class_id,literal` in the existing `key.csv`, concatenate values within a word, and join words in their recorded line/word order. Add the three punctuation marks described above. The expected output is the four-line literal. This checks the lookup procedure, not the correctness of the manual source classifications.

Historical input check: `python3 verification/check_all.py` passed at `985167d8a5bf20cf6c74f3b58c32396929fcbd35` with 69 retained files and the card199 baseline replay. At that revision it did not decode the new card318 ledger. The supported command now also replays this saved main ledger and the B/C/D marginal ledgers below, checking derived literals, declarations, counts, ordering and context bounds. It does not establish source-classification accuracy or historical correctness.

The initial AI reader saw the key and emerging language throughout. This is not a blind transfer experiment; language expectations could have influenced classification. The later AI reviewer also saw the proposed output, so that comparison is not a fresh holdout or independent human authentication. It corrected the first body of line 3's `touzene` from G18 to the existing `H440_N01_UNBARRED_LEFT_BOWL` class: the source lacks G18's upper horizontal bar. Both classes emit `t`, so the literal and 96/19 body/class counts are unchanged. The manifest preserves the earlier ledger fingerprint and the reason for this correction.

No heldout accuracy, independent source truth, complete mark inventory, full-card transcription or worldwide priority is claimed. A bounded search found no card318 reading page or explicit card318 reference in the public repository at the recorded input commit; private and earlier external readings are not excluded.

The next useful step is an independent source comparison of these 96 bodies and a separately recorded transcription of the marginal text, preserving overwritten signs and alternatives. Publicly available digital sources suffice for that attempt; no library or archive inquiry was made.

## Follow-up: marginal strip B

A later source comparison on the same day examined the strip at original coordinates `[770,45,1410,105]`, rotated 180 degrees. It does not change the four-line main-block literal above. The separately tasked AI reviewer compared the graphical forms with the atlas, without being asked to complete a fluent sentence; both readers had already seen the key and the card's main-block context. This was exploratory, not a preregistered or blind experiment.

The [strip B source ledger](../research-updates/evidence/card318-2026-10-09/margin-b-ledger.json) records five word groups and a separately recorded question-mark-like terminal mark. Its [partial literal](../research-updates/evidence/card318-2026-10-09/margin-b-literal.txt) is:

```text
dosel muj l[i/y]sle[UNRESOLVED_CLUSTER] z nedele [QUESTION_LIKE_MARK]
```

The bracketed labels describe observations and alternatives; they are not literal encrypted words or established body counts. Nineteen source bodies have invariant proposed class assignments. One additional body retains the class choice G07/G05 (`i/y`), with G07 favored by the later comparison. The final group-3 ink cluster remains unresolved, including whether it contains one body or overlapping/overwritten bodies. There is no established total body count for the strip or the whole card.

The stable outer groups give `dosel muj` and `z nedele`, suggesting “Did my [unresolved word] from Sunday arrive?” The middle word must not silently become `listek` (with editorial accent, *lístek*, a card or note):

- The fourth body has two stacked bowls and is retained as G04 = `l`. Replacing it with G18 = `t` for fluency is unsupported by the source. The alternative unbarred-t class has a different, single-stem/left-bowl profile.
- The second body has a short upper cross-stroke/cup and foot, favoring G07 over the simpler oblique G05. The initial reader's G05/G07 alternative remains visible rather than being erased.
- The final heavy cluster has a lower returned contour compatible with G08_N01 = `k` **if** it is one body. A compound or overwritten two-body interpretation cannot be excluded, and no two-class sequence is accepted. The `k` is therefore a conditional candidate, not an established letter.

Thus *došel můj lístek z neděle?* is a linguistic conjecture requiring a resolved-letter `l`→`t` substitution and an unresolved-cluster expansion. It is not the fixed-key output. The negative result rejects that silent repair, not every explanation of the writer's marks. Remaining margins and their reading order have not been transcribed completely. The address face was subsequently opened, but its postal date was not resolved or used to establish the catalogue year.

## Follow-up: marginal strips C and D

Further exploratory source comparison examined C at `[1640,100,1710,1140]`, rotated clockwise 90 degrees, and D at `[550,1100,1390,1168]`, upright. The [source ledger](../research-updates/evidence/card318-2026-10-09/margin-cd-ledger.json) and [partial literal](../research-updates/evidence/card318-2026-10-09/margin-cd-literal.txt) preserve:

```text
C: ma z[C.cluster]ta anusko mam le tak nevys[l/o]ovytelne rad
D: tecim se nesmirne na [D.cluster1][D.cluster2]ibeny dopis
```

Punctuation and unresolved flourish ownership are recorded separately in the ledger. C has 35 invariant proposed body assignments, one `l/o` alternative and one touching cluster; D has 27 invariant assignments and two overwritten clusters. These are selected-source counts, not a complete card inventory. No fixed body count is assigned to the clusters.

The long C group combines three adjacent source-review segments for display; joining them is editorial grouping, not proof of historical word spacing. Pre-commit source replay found that approximate boxes clipped several outer strokes. Boxes were padded by 15 oriented pixels on each side within the strip region and visually rechecked; the original boxes remain in the ledger. This changed neither classes nor literal output.

A separately tasked AI reader compared source forms with the existing atlas before receiving these partial literals; the key and main-block context were already visible. In C, the preferred two-body partition of the touching cluster is G04/G09 (`la`), but shared ink leaves that partition unaccepted. The narrow signs underlying the `l/o` disagreement remain faint. Footed oblique forms are retained as G05 = `y`; the tall single-left-bowl forms use the existing unbarred-t class.

C suggests an affectionate address to Anuška and a declaration of affection, but a fluent reconstruction would change `le` to `te` and a later `y` to `i`, as well as resolving the cluster and `l/o` alternative. These changes are not inserted into the literal. D's opening remains `tecim`, rather than silently changing `c` to `s` for *těším*. Its `se nesmirne na` and `dopis` suggest anticipation of a letter, while the intervening overwritten adjective remains unresolved. The later long descending stem supports G17 = `b`, not a more convenient short-stem letter.

No new key, whole-card solution, resolved global reading order, new date or sender identity follows. The retained partial readings and explicit failed smooth reconstructions are the result of this stage; a human source comparison may revise them.
