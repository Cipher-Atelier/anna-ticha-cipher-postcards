# Public verification

Run from the repository root with Python 3.10 or later, without optimization. The canonical assembler and checker use only the standard library. They load public JSON through `public_repeat_bindings.py`; the original JPEG and private pixel proofs are never default inputs.

## Check the saved canonical result and 307-row TSV

```sh
PKG=research-updates/2026-10-14-source257-repeat-sequence
python3 "$PKG/code/check_canonical_repeat_evidence.py" "$PKG/data/canonical-repeat-evidence-v1.json" \
  --public-repository-root . --public-data-directory "$PKG/data" \
  --final-core "$PKG/data/repeat-final-ai-review-v2.json" \
  --final-core-sha256 25dae066532e513ffc25d9f9db838915f5836177241d610aafbdcd00e661d8dd \
  --final-closure "$PKG/data/repeat-closure-final-ai-review-v2.json" \
  --final-closure-sha256 1ce734f238a5e9dd88db22205fea108cc53c7f19f4cc10d7bfd2cf5f8e37072e \
  --sequence-tsv "$PKG/data/spatial-reference-sequence-v1.tsv"
```

The checker rebuilds the complete canonical object from pinned inputs and compares every field. It also reconstructs the TSV and requires exact equality. Its validation status describes the declared source-evidence gates and saved data, not a new visual inspection.

## Regenerate into a new directory

Outputs cannot overwrite existing files or alias protected inputs.

```sh
PKG=research-updates/2026-10-14-source257-repeat-sequence
REPLAY_OUT=$(mktemp -d)
python3 "$PKG/code/canonical_repeat_evidence.py" \
  --public-repository-root . --public-data-directory "$PKG/data" \
  --final-core "$PKG/data/repeat-final-ai-review-v2.json" \
  --final-core-sha256 25dae066532e513ffc25d9f9db838915f5836177241d610aafbdcd00e661d8dd \
  --final-closure "$PKG/data/repeat-closure-final-ai-review-v2.json" \
  --final-closure-sha256 1ce734f238a5e9dd88db22205fea108cc53c7f19f4cc10d7bfd2cf5f8e37072e \
  --output "$REPLAY_OUT/canonical-repeat-evidence-v1.json" \
  --sequence-tsv "$REPLAY_OUT/spatial-reference-sequence-v1.tsv"
```

The public adapter checks the fixed seed ledger, all selected byte hashes, exact original-to-selected mappings and all 307 original annotation record hashes. Embedded historical hashes remain original scientific identities; `public_selection_bindings` records the hashes of the actual selected files separately. Actual repository-relative paths are inferred. An external staging directory requires an explicitly declared public destination, which must agree after copying into the repository. Unknown ledger bytes, unknown filters, rebinding, unsafe paths and symlinks are rejected.

## New package fixtures

```sh
python3 -m unittest discover -s research-updates/2026-10-14-source257-repeat-sequence/code -v
```

There are 94 fixtures: 43 canonical, 33 spatial, 16 public binding and two native-sheet layout/mapping fixtures. Public fixture setup uses pinned JSON and requires no original source. The optional native-sheet utility and its two synthetic fixtures require Pillow 11.3.0; they do not generate manuscript pixels for the public check. To run the 92 standard-library fixtures individually, invoke `test_canonical_repeat_evidence.py`, `test_spatial_preparation.py` and `test_public_repeat_bindings.py` with `unittest discover -p`.

An optional explicit `--verify-original-source` argument on the canonical CLI checks supplied original JPEG bytes against their fixed encoded hash. It performs no pixel decoding and is not used by public CI. Native context-sheet generation remains a separate optional source-image operation; it is not invoked by the canonical checker or fixture setup.
