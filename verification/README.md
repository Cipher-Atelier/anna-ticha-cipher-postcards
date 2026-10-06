# Verify anna-ticha

[Repository overview](../README.md) · [Read the result and check one example by hand](../READING_GUIDE.md)

## What this check does

The supported command first checks the published file fingerprints in `SHA256SUMS.txt`, then repeats this investigation’s saved calculation. A fingerprint (SHA-256) identifies exact file bytes; it is not a scientific correctness score.

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

The following are the expected status/topic/replay fields; the actual report also includes `files_checked` and scope limits:

```json
{
  "status": "passed",
  "topic": "anna-ticha",
  "replay": {
    "status": "passed",
    "output": "PASS: public inventory; exact retained key/rules/tokens; all 532 CSV/JSON rows; 24 atlas classes; unchanged viewer data\nPASS: 522 mapped, 10 unknown, 524 emitted characters, 23 observed classes, no secondary transformation\nPASS: exact historical literal SHA-256 b7aa7b869b73efa7a0907b48a655833cfd9b75128be0db7126b1880bd0798832\nLIMIT: deterministic replay is not proof of correct source classification, historical truth, authorship or priority."
  }
}
```

In ordinary words: **532 symbol positions; 522 mapped and 10 unknown; 524 emitted letters. The checker also verifies retained key/rules/tokens, the CSV/JSON tables and embedded viewer data.**

## What passing does not establish

The other cards are not all covered by the card-199 checker. Cards 440 and 453 contribute limited examples; cards 247 and 248 have qualified text reports without complete public positional packages. A smooth Czech paraphrase can conceal uncertain signs, spacing or dates.

Passing verifies that these published inputs and saved rules give the recorded result. It does not certify source-image transcription, historical truth, a unique interpretation, author identity, discovery priority or external expert review. To inspect those questions, follow [the manual example and source-checking route](../READING_GUIDE.md#check-one-example-by-hand).

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

## Preserved publication scope

Partial card readings. Complete positional replay for card 199 only; cards 440 and 453 supply limited examples. Cards 247 and 248 remain qualified text reports, without complete evidence packages or complete plaintext.

Full 532-position replay for card 199 only: 522 mapped, ten unknown, 524 emitted characters. Cards 440 and 453 provide limited examples. Other cards, including 247 and 248, have text reports without complete public positional packages. The optional image-free HTML viewer has not passed end-to-end browser QA; local source-image use is explicit opt-in.

From the repository root run `python3 verification/check_all.py` with Python 3.10 or later, without optimization. It verifies the repository checksum inventory and invokes only [anna-ticha/verify.py](anna-ticha/verify.py). The check uses the standard library and makes no network requests. Obtain source images separately under their provider terms for visual review. Source credit is not image redistribution permission.

See the [research record](../anna-ticha/article.md) and [machine-readable scope](TOPIC_SCOPE_INDEX.json). Successful arithmetic or exact output replay does not prove historical truth, unique interpretation or priority.
