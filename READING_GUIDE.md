# Read this investigation

[Repository overview](README.md) · [Technical verification](verification/README.md)

## Understand the document

A set of personal postcards written in cipher and addressed to Anna Tichá. The proposed readings are in Czech; the writer’s identity and several dates remain unresolved.

Start with the [source catalogue or manuscript](https://crypto.hcportal.eu/dashboard/cryptograms/1518). It identifies the historical object. Card number 199 is not its catalogue-record ID; HCPortal indexes this card as cryptogram 1518. The source image is the evidence; the tables in this repository are recorded readings of that evidence.

## Read the current result

Selected cards can be read in part. The most complete public checking package is for card 199: it records each of its 532 symbol positions and the proposed letters. Other cards have separate reading reports, with different amounts of evidence.

Open [Card 199: literal reading](verification/anna-ticha/literal.txt) and the [research account](anna-ticha/article.md). A literal preserves the recorded output before making it smoother to read. An English explanation or translation adds interpretation and should not silently repair it.

Example:

```text
vrely dik za drahy listek byl
```

The opening of card 199 expresses warm thanks for a dear letter. This is a summary of the proposed Czech reading, not an identification of its writer.

The other cards are not all covered by the card-199 checker. Cards 440 and 453 contribute limited examples; cards 247 and 248 have qualified text reports without complete public positional packages. A smooth Czech paraphrase can conceal uncertain signs, spacing or dates.

## Check one example by hand

1. Open the [position table](verification/anna-ticha/data/card199_positions.csv) and find `C199.L01.T01` and `C199.L01.T02`. These are identifiers for the first two symbols in one source region, not names of people.
2. Look up their `class_id` values in the [key](verification/anna-ticha/data/key.csv):

| Recorded position | Symbol class | Proposed output |
| --- | --- | --- |
| `C199.L01.T01` | `G01` | `v` |
| `C199.L01.T02` | `G02` | `r` |

3. Compare `vr` with the start of the [literal](verification/anna-ticha/literal.txt). This checks that the saved assignments were applied consistently.
4. For a source check, open the [original card image](https://api.hcportal.eu/media/4614/pc_hcp_199_pic.JPG). The first record’s original-image context box is `[530, 516, 630, 584]` pixels, measured from the top-left corner. It is a context window, not an exact outline. The recorded region is read after a counterclockwise quarter-turn. Compare the visible shape with the key description before accepting its class.

Card 199 has two source regions. Their relative reading order is unresolved: the order in the file is an indexing convention. Ten positions stay unknown. Two assigned symbols emit `ch`, which explains why 522 mapped symbol positions produce 524 letters. The key includes a later card-440 hypothesis; this release does not establish fresh blind predictions for every card.

## Choose the check you want

- **Understand the result:** read the literal/test result beside the research account. You can do this in GitHub without installing anything.
- **Check the calculation:** follow the example above, then [run the supported Python check](verification/README.md). This verifies the saved transformation or declared model.
- **Check the source:** compare recorded signs with the original image and retain disagreements. Scans/crops are not included; obtain access under the provider’s terms. Original coordinates, when present, refer to the specified image version.
- **Evaluate the historical reading:** examine alternative signs, key evidence, language, document boundaries and prior readings. A successful calculation does not settle these questions.

To report a problem, use [Work on existing research](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/issues/new?template=research.yml). Give the file, row/position, source reference, your observation, and what changes in the output. Distinguish a different source reading from a changed key or an editorial interpretation.

## What the files mean

| Open this | It contains |
| --- | --- |
| [Research account](anna-ticha/article.md) | Historical context, method, interpretation, credits and limits |
| [Card 199: literal reading](verification/anna-ticha/literal.txt) | The saved text or bounded test result |
| [Card 199: one row per symbol](verification/anna-ticha/data/card199_positions.csv) | The recorded input/assignments used in the example |
| [Proposed symbol-to-letter key](verification/anna-ticha/data/key.csv) | The proposed transformation, historical key, or tested assumptions |
| [Technical verification](verification/README.md) | Setup, command, expected output and what the check covers |
| [Source scope](verification/TOPIC_SCOPE_INDEX.json) | Machine-readable release boundaries and omitted material |
| [Publication provenance](SOURCE_PROVENANCE.json) | Where this package came from and what documentation changed |

CSV and TSV are tables: GitHub or a spreadsheet can display them. TSV uses tabs between columns. JSON stores named fields and lists; `null` means no value in that field, and its interpretation depends on the record. You do not need to start by reading every JSON file.

## Terms used in the research

- **Ciphertext:** the recorded encrypted signs or letters.
- **Key/mapping:** the rule assigning output to a cipher sign. It may be a hypothesis, a surviving historical key, or an assumption in a test; those are different kinds of evidence.
- **Literal reading:** the saved output with gaps and awkward wording retained, before editorial translation or repair.
- **Coverage:** how many recorded positions receive a value. It does not measure how many values are historically correct.
- **Frozen:** saved unchanged at a particular stage so a later correction cannot replace an earlier test result.
- **Replay:** applying saved rules to saved inputs again. It checks reproducibility within the declared scope.
- **Training/heldout:** material used to fit a rule, and material excluded from that fitting. Prior viewing or later correction can limit how independent a heldout test is; read the case-specific account.
