# Verify anna-ticha

[Repository overview](../README.md) · [Read the result and check one example by hand](../READING_GUIDE.md)

## What this check does

The supported command first checks the published file fingerprints in `SHA256SUMS.txt`, then repeats the unchanged card199 calculation and replays twelve saved contextual word ledgers plus card318’s marginal strips B, C and D. A fingerprint (SHA-256) identifies exact file bytes; it is not a scientific correctness score.

The optional HTML viewer is not the required entry point and has not passed end-to-end browser QA. The ordinary check uses text/data only; optional source-image and crop checking is a separate procedure in [the packet guide](anna-ticha/README.md).

It uses Python’s standard library, makes no network requests, and needs no downloaded scans or extra packages for this default check. It does not fit a new key or edit the research evidence.

## Download and open the folder

1. On [this repository’s main page](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards), choose **Code → Download ZIP**, following [GitHub’s download instructions](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).
2. Extract the whole ZIP. Keep its folders and files together; do not download only `check_all.py`.
3. Open a terminal in the extracted top-level folder: it contains `README.md`, `SHA256SUMS.txt` and the `verification` folder. For example, after navigating to its parent directory:

```sh
cd anna-ticha-cipher-postcards-main
```

If you already use Git, cloning the full repository is an alternative:

```sh
git clone https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards.git
cd anna-ticha-cipher-postcards
```

## Run the supported check

Use **Python 3.10 or later**. On macOS/Linux, check the installed version and run:

```sh
python3 --version
python3 verification/check_all.py
```

On Windows, if the Python launcher is installed, use:

```powershell
py -3 --version
py -3 verification/check_all.py
```

If your Python command is `python` rather than `python3` or `py -3`, use that command after confirming it is Python 3.10+. If Python is absent, obtain it from [python.org](https://www.python.org/downloads/) or your operating system’s supported installation method.

Run ordinary Python, with no `-O`/`-OO` options and no `PYTHONOPTIMIZE` setting that enables optimization: the checker relies on assertions.

## What a successful run looks like

The command exits successfully and prints a JSON report with top-level `"status": "passed"`. It also reports how many fingerprinted files were checked. That file count can change when documentation is updated.

The report retains `replay` for the unchanged card199 check: 532 positions, 522 mapped, ten unknown and 524 emitted letters. Its new `ledger_replay` field lists cards **314, 315, 316, 318, 319, 320, 322, 324, 325, 326, 327 and 328**, with each package’s derived counts, followed by card318 strips B/C/D. All these status fields must say `passed`. The required card set is explicit: deleting a package does not reduce the checked set.

The ledger replay derives words from class sequences using the unchanged BOM-aware `key.csv`, then compares each derived word with its CSV literal and the complete assembled output with `literal.txt` and the corresponding diplomatic article block. It checks CSV schemas, unique ordered indices, required records and regions, declared unknown/alternative IDs, candidate classes, row and aggregate counts, current and initial context bounds, and key/atlas/ledger/literal fingerprints. Bodies and emitted letters are separate: one `G10_CAP` body emits two letters, `ch`; the existing unbarred-t class emits `t`.

Unknown clusters render their declared labels and receive no accepted body count or key value. Alternatives render the declared `[y/i]` or `[k/z]` choices and are excluded from invariant body, letter and distinct-class totals. Card318’s marginal candidate partitions are also excluded; B/C/D retain 19/35/27 invariant proposed mappings. The retained card319 token `UNKNOWN` refers only to its declared U1 at L7W1. Regions and punctuation preserve the saved display; none establishes inscription chronology.

Structured replay punctuation was added by transcribing already documented positions for cards318/319 and card325’s intraword hyphen. Card315’s separate dash is retained. Missing accounting fields and card318 marginal fingerprints were made explicit; existing descriptive fields remain. Card319’s CSV line endings changed from CRLF to LF without changing parsed rows, class sequences, coordinates or text. The key and atlas bytes remain unchanged. See [publication provenance](../SOURCE_PROVENANCE.json) for the base revision and formatting hashes.

## Separate experimental card330 replay

The `experimental_card330` report is separate from the unchanged required set of twelve earlier CSV packages. It derives the [card330 masked literal](../anna-ticha/card-330.md) from the V3 journal and unchanged key, retains all 65 spatial display groups, and checks immutable A/B snapshots and append-only identifier errata. The derived report distinguishes **264 encoded slots**, **251 provisional assignments to known classes**, **254 emitted known letters**, **13 unresolved occurrences** and **11 unresolved families**. Three capped-ch slots emit two letters each; the physical body count remains null.

Every unresolved occurrence renders `[ID]`, including a sole candidate and class alternatives that share a letter. L03W11 retains one correlated span mask with its two complete candidate sequences; cross-combinations are not admitted. Uncertain punctuation is `[?]`, `[!]` or `[-]`. Required group/slot/punctuation windows are checked for explicit presence and source bounds, alongside fingerprints, row/aggregate counters, historical-to-final slot mapping and diplomatic CSV/literal/article agreement. These are consistency checks; they do not inspect ink or certify source classification, reader blinding, human accuracy or a date. A003’s finite family comparison remains negative/inconclusive, and written/postal dates remain unresolved.

The adapter can run separately:

```sh
python3 verification/card330_replay.py
```

An optional `--source-image /path/to/picture.jpg` checks only an explicitly supplied picture file’s exact known SHA-256 and byte count. Exact bytes pin recorded dimensions; no pixel decoding, source fetching, crop output or image dependency is involved. Frozen relative references in the text snapshots are historical labels for local views, not bundled source files. The experimental adapter also cannot disprove coherent coordinated edits.

The later [feature-control](../research-updates/2026-10-11-card330-cross-card-feature-control.md) and [stroke-ownership](../research-updates/2026-10-11-card330-stroke-ownership.md) reports publish saved observations and scoring rules. Their collector/comparison scripts are not included, so these ordinary commands do not rerun the perceptual experiments. Both follow-ups accepted no additional letters; all thirteen masks remain.

## Regression tests and CI

From the repository root:

```sh
python3 -m unittest discover -s verification/tests -v
python3 verification/check_all.py
```

The standard-library tests use temporary evidence copies, fixed saved-output examples and negative mutations. Semantic mutations refresh the affected ledger/literal fingerprints so they test the relevant guard rather than stopping at a hash error. They cover wrong supported classes, literals, counts, capped-ch accounting, missing/duplicate/reordered records, mask declarations, marginal partitions, bounds, punctuation and article differences. Card330 adds real-package mutations with refreshed fingerprints for coupled candidate correlation, missing coordinate windows, physical-count/date claims and frozen-snapshot tampering.

The [GitHub Actions workflow](../.github/workflows/verify.yml) runs both commands plus `git diff --check` on Python 3.10 and 3.13 for ordinary push and pull-request events. It checks the triggering SHA and the committed diff against the PR base or previous push revision, with complete Git history. Its token has read-only contents permission, checkout credentials are not persisted, and it uses pinned actions with no dependencies, source-image downloads or artifact publication.

## What passing does not establish

The listed saved-ledger packages are checked for mechanical consistency; other cards are not automatically covered by their replay. Cards 440 and 453 contribute limited examples; cards 247 and 248 have qualified text reports without complete public positional packages. A smooth Czech paraphrase can conceal uncertain signs, spacing or dates.

Passing verifies that these published inputs and saved rules give the recorded result. Saved dimensions support bounds checks but do not verify a source image. Coherent coordinated edits to the evidence and expected outputs cannot be disproved by consistency checks. Card330 now has a separate experimental saved-graphical package with original-named provider fingerprints. Its physical body count and written/postal date remain unestablished. It does not certify source-image transcription, historical truth, a unique interpretation, author identity, discovery priority or external expert review. To inspect those questions, follow [the manual example and source-checking route](../READING_GUIDE.md#check-one-example-by-hand).

## If it fails

| Symptom | What to do |
| --- | --- |
| Python command not found, or version below 3.10 | Install/use Python 3.10+; confirm its version first |
| Cannot open `verification/check_all.py` | Move into the extracted repository’s top-level folder |
| Missing file | Extract the complete ZIP again; retain the directory structure |
| `Hash mismatch: ...` | Compare with an untouched download of the same version; edits change the fingerprint |
| Optimization warning | Run without `-O`/`-OO` and disable any `PYTHONOPTIMIZE` setting |
| Assertion, replay mismatch or another error on an untouched package | Save the complete error, Python version and repository commit/download reference; report it in a [research issue](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/issues/new?template=research.yml) |

Do not change the evidence, expected results or fingerprints just to make a failing check pass. If reporting reproduction, record the commit SHA shown on GitHub; a later `main` download may contain documentation updates. A [commit-specific archive](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives#source-code-archive-urls) pins the file version.

## Publication scope

Complete 532-position replay remains limited to card199. The twelve later contextual packages and card318 margins now have deterministic replay of their saved proposals, including uncertainty masks; this does not turn them into complete source-position editions. Cards440/453 supply limited examples, and cards 247/248 remain qualified text reports without complete public positional packages or complete plaintext. Card330 has a separate experimental source-first package and replay; it is not a complete solution or a verified date correction.

The supported command runs the checksum inventory, [card199 verifier](anna-ticha/verify.py), [saved-ledger replay](ledger_replay.py) and the separate [card330 experimental adapter](card330_replay.py), entirely offline with the standard library. Optional source-image and crop verification in the card199 packet is a separate explicit procedure. Obtain images separately under provider terms; source credit is not redistribution permission.

See the [research record](../anna-ticha/article.md) and [machine-readable scope](TOPIC_SCOPE_INDEX.json). Exact arithmetic or output replay does not certify source classification, historical truth, author identity, unique interpretation or priority.
