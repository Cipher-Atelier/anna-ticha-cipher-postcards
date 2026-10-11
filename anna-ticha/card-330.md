# Card 330: source-first graphical proposal

Research recorded on 11 October 2026 for [HCPortal record 1649, pc_hcp_330](https://crypto.hcportal.eu/dashboard/cryptograms/1649). This follows the [9 October screen-reading note](../research-updates/2026-10-09-card330-screen-reading.md), whose historical candidates remain preserved. Newly obtained original-named provider files support a text-only, reproducible experimental package. This is a provisional source-class proposal, not a complete decipherment, accuracy score or verified date correction.

## Diplomatic projection

The display preserves all 65 spatial groups in five lines. Every unresolved occurrence is a named mask, including a single-candidate family and alternatives whose existing classes both emit `t`. Ordinary commas and points are displayed; uncertain punctuation remains `[?]`, `[!]` and `[-]`.

```text
vrely dik, srde[R_L01W03B05]ko moje, za drahy listek. proc litujes, ze [A001]en
tvuj nebyl pravdou[?] vzdy[R_L02W04B05] mam te toli[R_L02W07B05] rad[!] pra ve se chystam na zpate[A001]ni
cestu do prahy. prijel jsem sem na pozi hod v n[R_L03W11_COUPLED_SPAN]i. vzpo mi nal jsem zd[A007] [R_L03W17B01][A008]a[-]
le na svoji tak drahou amumku. tesim se na psanko nes mirne. vrely
p[A002]zdrav a tisic dlouhych, va[A001]nivych p[A003]s od vecne [U001]veho pepouse.
```

The projection has **264 encoded slots: 251 provisional assignments to known classes and 13 unresolved occurrences across 11 families**. The assignments to known classes emit 254 letters through 23 existing classes. Three `G10_CAP` assignments each emit `ch` from one provisionally mapped encoded slot. The physical body count is **not established**: historical A/B 265 entries, final encoded slots and actual glyph bodies are distinct quantities. A mask for an unsegmented span does not mean one physical glyph.

## Source-first records and reconciliation

Two separately tasked AI readers inspected original pixels and graphical atlas references before producing key-based projections. Their [frozen A snapshot](../research-updates/evidence/card330-2026-10-11/phase-a-ledger.json) and [frozen B survey](../research-updates/evidence/card330-2026-10-11/reader-b-initial.json) are retained byte-for-byte. Reader B’s first atlas filter accidentally exposed example metadata mentioning the existing unbarred-t assignment; that limitation is preserved in B’s snapshot. These runs are not certified blind tests or external human authentication. Familiar forms could evoke prior mappings.

A’s shorthand encoder wrote `GA006`, `GA007` and `GA008` for already declared unresolved IDs. The separate [identifier errata](../research-updates/evidence/card330-2026-10-11/encoding-errata.json) normalizes them to `A006`, `A007`, `A008`; the frozen snapshot is unchanged. B’s [pre-A coordinate followup](../research-updates/evidence/card330-2026-10-11/reader-b-source-followup-before-a.json), [detail observations](../research-updates/evidence/card330-2026-10-11/reader-b-detail-followup-before-a.json) and [pre-A key projection](../research-updates/evidence/card330-2026-10-11/reader-b-key-projection-before-a.json) retain the earlier stages.

The [V3 reconciliation journal](../research-updates/evidence/card330-2026-10-11/reconciliation-v3.json) records source comparisons and explicit changes rather than silently rewriting the first transcriptions. It corrects punctuation associations and approximate windows, resolves some earlier class proposals, and retains conflicts. V3 clarifies that two component observations in L03W11 are historical records, not two independently selectable final alternatives; its scientific sequences and conclusions are unchanged from V2.

L03W11’s middle span retains only these coupled candidates: `G19 H440_N01_UNBARRED_LEFT_BOWL` or `G11 G19`. They would project `ct` or `oc`, but neither sequence is accepted. The single `[R_L03W11_COUPLED_SPAN]` mask prevents unreviewed cross-combinations. Other uncertain left-bowl classes retain their distinct identities even when both existing classes emit `t`. The sole candidate `G19` for `A001` does not prove family equality and is not decoded as `c`.

A finite source-to-exemplar comparison of A003’s small closed e-like loop against G03/G13/G16/G12/G19 was negative or inconclusive. A003 remains unresolved; no new key literal was assigned. The journal preserves that experiment’s source window, comparison set and findings. No fluent Czech repair, accent restoration or invented missing letter enters the projection. Forms such as `pozi`, `amumku`, separated `pra ve`, `vzpo mi nal` and `nes mirne` remain as the selected source/display sequence. Spatial groups and optional joining do not establish historical word boundaries.

## Source identity and date limits

The [source metadata](../research-updates/evidence/card330-2026-10-11/sources.json) records two original-named public provider JPEGs, each 1785×1175 pixels:

- [Picture side](https://api.hcportal.eu/media/5007/pc_hcp_330_pic.JPG):1,431,536 bytes; SHA-256 `206f29850350f429346d04bacc37c01bc377e50b1224a59d42bb6e785b781a05`.
- [Address side](https://api.hcportal.eu/media/5008/pc_hcp_330_adr.JPG):1,060,308 bytes; SHA-256 `45d8a90465498208210bf1943c442dfa13d2bea303c705a7a8bd0f40b663d4d0`.

These identify downloaded provider bytes, not physical-source authenticity. All source pixels and crops remain outside the publication; provider watermark was retained during inspection. Frozen relative artifact references identify historical local views and do not promise bundled images. Approximate group and slot windows can overlap neighboring ink or other lines and are not exact glyph segmentations.

The picture inscription retains **14.IV.1903. /14.II.1903.** alternatives. Both graphical readers favor IV’s apparent lower convergence but keep II viable. No accepted written date is supplied. The [initial postal observations](../research-updates/evidence/card330-2026-10-11/postal-date-observations.json) and [later separate postmark review](../research-updates/evidence/card330-2026-10-11/postmark-review.json) did not produce a complete accepted postal date or month. They cannot arbitrate February versus April. The earlier postal record’s awaiting-review status is historical; the separate later record supplies the negative result. No catalogue correction, postal chronology, itinerary or writer identity is established.

## Reproduce the saved proposal

From the repository root run `python3 verification/check_all.py`, or run the separate experimental adapter `python3 verification/card330_replay.py`. The standard-library check is offline, requires no images and derives output from the journal’s class sequences using the unchanged key. It validates immutable input fingerprints, the retained 65-group partition, review-to-final slot mapping, candidate correlation, declared masks, counts, required coordinate windows and exact [CSV](../research-updates/evidence/card330-2026-10-11/word-ledger.csv), [literal](../research-updates/evidence/card330-2026-10-11/literal.txt) and article agreement. The [manifest](../research-updates/evidence/card330-2026-10-11/manifest.json) describes the rendering and scope.

An optional explicit `--source-image /path/to/picture.jpg` checks only the known picture file’s exact hash and byte count; the known bytes pin the recorded dimensions. It does not fetch sources, decode pixels, inspect glyphs or validate the date. Ordinary replay checks saved coordinate bounds, not correct attribution of source ink.

A successful replay establishes consistency of these saved proposals. Coherent coordinated edits cannot be disproved by consistency checks. It does not certify source classification, unique interpretation, historical truth, authorship, priority or complete postcard coverage. Existing key, atlas and earlier cards remain unchanged; the experimental adapter is separate from the strict twelve-card replay. Credit for the key and earlier scholarship remains with the researchers in the [original study](article.md), and source access with HCPortal and the collection holders. No new blanket licence or image redistribution right is asserted.
