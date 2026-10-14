# Offline verification

Run from the repository root with Python 3.10 or later, without optimization. The main assembler, checker and its 57 gate fixtures use only the standard library. Inputs are the frozen JSON files in this package's `results/`, its numerical paired-panel index and the existing public D12 baseline. No source JPEG or private proof payload is read.

## Check the saved delta

```sh
PKG=research-updates/2026-10-14-source257-conflict-route-review
python3 "$PKG/code/check_conflict_delta.py" "$PKG/results/conflict-route-delta-v1.json" \
  --repository-root .
```

The checker reconstructs the full compact delta from fixed input hashes and requires exact equality. It verifies the declared fresh-reader, historical-audit and final-review gates, the narrow historical correction and the unchanged graph overlay. Historical literals are resolved through the existing D12 baseline's original-to-selected public byte bindings. Original scientific identities and actual selected file hashes remain distinct.

Passing validates saved bytes, references and source-review attestations. It is not a current source-image inspection or a mechanical proof of target binding.

## Regenerate into a new directory

```sh
PKG=research-updates/2026-10-14-source257-conflict-route-review
D13_REPLAY_OUT=$(mktemp -d)
D13_REPLAY_OUT=$(cd "$D13_REPLAY_OUT" && pwd -P)
python3 "$PKG/code/conflict_delta.py" --repository-root . \
  --output "$D13_REPLAY_OUT/conflict-route-delta-v1.json"
```

The assembler rejects existing output paths, aliases of protected inputs and synthetic reports presented as production evidence. This version changes no graph memberships, so it reuses the pinned D12 307-row TSV and does not produce another sequence file.

## New fixtures

The 57 standard-library fixtures can run alone:

```sh
python3 -m unittest discover \
  -s research-updates/2026-10-14-source257-conflict-route-review/code \
  -p test_conflict_delta.py -v
```

The complete new package suite has 66 fixtures: those 57 plus nine synthetic native-layout, corruption and method-gate fixtures. The latter require Pillow 11.3.0 and reuse the existing public D12 helper code; they need no original image.

```sh
python3 -m unittest discover \
  -s research-updates/2026-10-14-source257-conflict-route-review/code -v
```

The optional `build_blinded_pair_pack.py` is the unchanged source-pack utility. Full production rebuilding of its private pixel pack requires original images and private D12 preparation inputs that are not bundled. Its public fixture has one documented sibling-directory substitution; scientific assertions and source data are unchanged. Image generation or proof reconstruction is not part of the default offline checker.
