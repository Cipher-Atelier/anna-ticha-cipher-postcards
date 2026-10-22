# Read this investigation

## Start here — 23 October 2026

Follow [overview and current status](README.md) → [cards and evidence levels](anna-ticha/readings.md) → the chosen card’s literal and supporting evidence → [methods](anna-ticha/methods.md) and [dated audits](research-updates/README.md). [Card 204](anna-ticha/card-204.md) publishes the original diplomatic reading, editorial Czech, English translation and twelve caveats, with an author-reported external check; no complete positional/replay package is added. The later [four Russian readers](research-updates/README.md#four-russian-readers) are selected conditional reports published in PR #19; English guides explain their scope.

The examples below explain the existing public checking package. They do not establish the correctness of every source assignment; consult the [later key-foundation qualifications](research-updates/README.md#key-foundation-and-later-outcomes).

[Repository overview](README.md) · [Technical verification](verification/README.md)

For connected text from the original six-card study, choose a [readable Czech/English edition](anna-ticha/readings.md#readable-editions). Contextual proposals stay marked and linked to disputes; card 250’s source-based `MOJE` candidate is used in the interpretation, separately from its unchanged frozen literal. The later [canonical audit](research-updates/2026-10-20-confirmed-key-continuation/old-six-audit.md) retains `?OJE` and M/N alternatives, with M visually favored.

## Understand the document

A set of personal postcards written in cipher and addressed to Anna Tichá. The proposed readings are in Czech; the writer’s identity and several dates remain unresolved.

Start with the [source catalogue or manuscript](https://crypto.hcportal.eu/dashboard/cryptograms/1518). It identifies the historical object. Card number 199 is not its catalogue-record ID; HCPortal indexes this card as cryptogram 1518. The source image is the evidence; the tables in this repository are recorded readings of that evidence.

## Read the current result

Cards [380](research-updates/2026-10-20-confirmed-key-continuation/cards/380.md), [381](research-updates/2026-10-20-confirmed-key-continuation/cards/381.md), [382](research-updates/2026-10-20-confirmed-key-continuation/cards/382.md), [383](research-updates/2026-10-20-confirmed-key-continuation/cards/383.md), [384](research-updates/2026-10-20-confirmed-key-continuation/cards/384.md), [385](research-updates/2026-10-20-confirmed-key-continuation/cards/385.md) and [386](research-updates/2026-10-20-confirmed-key-continuation/cards/386.md) have complete Czech working texts and English interpretations. The latest 380 edition covers all twelve preserved rows with zero selected unknown-glyph masks and one explicit language proposal, source SVEM/editorial SVEMU. The source choices UCTY and ZVANOU, all revised contours, q/g and CH remain provisional. Card 381 retains provisional numeral/connector roles and three language proposals; 382 retains two source masks and three proposals; 383 retains four and five; 384 retains two overwritten groups and a spelling proposal; 385 has a complete provisional literal; 386 retains two dark-source masks and three proposals. Reading order and source accuracy remain open. Next is deeper completion of earlier partial 379; new 387–390 remain held. The JSON/revisions preserve literal output, whole earlier editions and alternatives separately from editorial proposals.

For collection counts and a concise list of missing evidence, start with the [review overview](REVIEW_STATUS.md): 154 of the 263 cards have a published reading, including partial proposals. This is not a solved-card count.

The [continuation package](research-updates/2026-10-20-confirmed-key-continuation/README.md) now has 137 canonical-key research candidates, most recently cards 383–386 (22 October 2026), with separate literal, qualified Czech and English layers. The earlier 121 candidates retain their two frozen related AI source records; cards 371–386 currently have one key-visible source reading each, followed by same-context nonblind review. Neither stage is external confirmation. None is declared solved. The 37 preserved reports include the original six-card records and the experimental 330 proposal; their evidence statuses remain distinct.

[All 37 card reports](anna-ticha/readings.md) distinguish literal readings, qualified English interpretations and evidence levels. Selected cards can be read in part. The most complete public checking package is for card 199: it records each of its 532 symbol positions and the proposed letters. Other cards have separate reading reports, with different amounts of evidence.

Open [Card 199: literal reading](verification/anna-ticha/literal.txt) and the [research account](anna-ticha/article.md). A literal preserves the recorded output before making it smoother to read. An English explanation or translation adds interpretation and should not silently repair it.

Example:

```text
vrely dik za drahy listek byl
```

The opening of card 199 expresses warm thanks for a dear letter. This is a summary of the proposed Czech reading, not an identification of its writer.

The supported check now also replays twelve saved contextual ledgers and card318 margins, as listed in the [verification guide](verification/README.md). This checks saved proposals. Card330 has a separate [experimental graphical replay](anna-ticha/card-330.md), with unresolved masks and no accepted physical body count or written/postal date; other cards are not automatically covered. Cards 440 and 453 contribute limited examples; cards 247 and 248 have qualified text reports without complete public positional packages. Card330’s 264 encoded slots, 251 assignments and 254 known letters are different units; all 13 masks and date alternatives remain. The later [feature-control](research-updates/2026-10-11-card330-cross-card-feature-control.md) and [stroke-ownership](research-updates/2026-10-11-card330-stroke-ownership.md) checks accepted no additional letters. Their collector/comparison scripts are not published; replaying the proposal does not regenerate perceptual judgments. A smooth Czech paraphrase can conceal uncertain signs, spacing or dates.

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
