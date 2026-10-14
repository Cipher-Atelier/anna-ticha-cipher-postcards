# Source257: first 64 direct comparisons from a 772-pair queue

This bounded batch directly compares the first 64 previously uninspected pairs in a fixed queue of 772. Each pair has two fresh AI source readings and a final AI source adjudication of the same original pixels. The remaining 708 pairs have `NOT_INSPECTED` status and no source verdict. Resume at ordinal **65**, **`FC015--FC125`**.

## Scope and method

The [frozen protocol](results/direct772-protocol-v2.json) and [complete ordered queue](results/direct772-queue-v1.json) precede the new source readings. Order is ASCII lexical `pair_id`; no similarity metric was used. The first batch covers 36 annotation targets in 64 distinct pairs, ending at `FC015--FC123`. Its limit is administrative capacity, with the remaining comparisons still available and authorized. The queue excludes previous direct comparisons, including the separate 38-pair route review.

Readers examined paired tight and expanded native views. They independently checked the original source identity, 72 reused crops and all 256 saved panels before viewing the 16 boards. Exact 90-degree rotation preserves source pixels; labels sit outside them. Fidelity checks establish correspondence to the original pixels, while stroke ownership remains a source judgment supported by explicit continuity observations and neighboring context. Approximate locator boxes do not determine ownership.

Every checked pair records all eight dimensions: path topology, enclosures, openings, stem pattern, attached bars, connected extra strokes, terminals and owned-mark profile. Full-repeat support requires complete owned constructions and positive compatibility across all eight dimensions in both fresh readings and the final review. A visible difference requires a common, positively observed owned feature and difference kind in all three reports. An unrelated uncertain fine junction does not erase a visible local difference. `VISIBLE_FORM_VARIATION` retains differences of contour, direction, extent or position with unknown cipher and allographic significance. An uninspected pair receives no uncertainty verdict.

## Results and evidence

The 64 checked pairs have **64 observed graphical differences**, all released as visible owned-contour form variations; **0 full graphical repeats** are supported and **0 checked pairs** receive an aggregate uncertainty verdict. This does not resolve every feature: fine joins, disputed loop closures and FC123 basal-foot direction remain uncertain in the evidence. Cipher identity and allographic significance remain unknown.

The [checkpoint JSON](results/direct772-checkpoint-v2.json) retains each reader's actual local observations, variations and uncertainties. The [772-row status TSV](results/direct772-queue-status-v2.tsv) makes the checked prefix and untouched remainder explicit. TSV cells use standard CSV quoting; an uninspected pair has an empty source-observation value. Raw evidence is preserved in [reader A](results/source-reader-A-initial-v1.json), [reader B](results/source-reader-B-initial-v1.json) and the [final source review](results/direct772-final-ai-v1.json).

The fresh readers saw only the selected geometry and source guidance, without historical feature claims or each other's initial reports. The final AI review read both frozen initials and discloses prior source-review exposure. These are separate AI judgments of the same pixels, with a conditioned final adjudication; agreement supplies no independent historical source or external expert validation. Fine closure, contact and terminal-direction disagreements remain recorded even where a broader contour contrast is supported.

The historical 58-edge candidate graph, its 15 overlapping cliques and the 307-row spatial reference sequence are reused unchanged. This batch adds no graph edge, transitive inference, cipher cannot-link, alphabet, letter value or global reading order. The [earlier repeat package](../2026-10-14-source257-repeat-sequence/README.md) and [38-pair route review](../2026-10-14-source257-conflict-route-review/README.md) retain their original scope and limits. Only source257 was inspected in this batch.

## Public verification

From the repository root, with Python 3.10+ and Pillow 11.3.0 for the synthetic native fixtures:

```sh
python3 -m unittest discover -s research-updates/2026-10-14-source257-direct772-batch01/code -v
python3 research-updates/2026-10-14-source257-direct772-batch01/code/check_direct772_checkpoint.py research-updates/2026-10-14-source257-direct772-batch01/results/direct772-checkpoint-v2.json --repository-root . --queue-tsv research-updates/2026-10-14-source257-direct772-batch01/results/direct772-queue-status-v2.tsv
```

The standard-library checkpoint checker validates pinned saved evidence, exact queue coverage, source-fact references, conservative release gates, unchanged baseline use and the status TSV. It performs no current JPEG or private-proof read and cannot mechanically establish physical stroke ownership. Published code covers bounded metadata preparation, crop-fidelity utilities, synthetic fixtures and checkpoint replay. Rebuilding the actual native boards requires omitted private source inputs.

The [selection ledger](results/publication-selection-ledger-v1.json) records exact selected bytes and two public test-loader adaptations. [Nested checksums](SHA256SUMS.txt) bind the package. Only whole-original and whole-proof-document hashes are included; original images, crops, boards, private proof payloads and per-panel pixel hashes are omitted.
