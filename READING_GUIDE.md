# Read this investigation

## Start here

Updated 27 October 2026.

Follow [overview and current status](README.md) → [cards and evidence levels](anna-ticha/readings.md) → the chosen card’s literal and supporting evidence → [methods](anna-ticha/methods.md) and [dated audits](research-updates/README.md). [Card 204](anna-ticha/card-204.md) publishes the original diplomatic reading, editorial Czech, English translation and twelve caveats, with an author-reported external check; no complete positional/replay package is added. The later [four Russian readers](research-updates/README.md#four-russian-readers) are selected conditional reports published in PR #19; English guides explain their scope.

The examples below explain the existing public checking package. They do not establish the correctness of every source assignment; consult the [later key-foundation qualifications](research-updates/README.md#key-foundation-and-later-outcomes).

[Repository overview](README.md) · [Technical verification](verification/README.md)

For connected text from the original six-card study, choose a [readable Czech/English edition](anna-ticha/readings.md#readable-editions). Contextual proposals stay marked and linked to disputes; card 250’s source-based `MOJE` candidate is used in the interpretation, separately from its unchanged frozen literal. The later [canonical audit](research-updates/2026-10-20-confirmed-key-continuation/old-six-audit.md) retains `?OJE` and M/N alternatives, with M visually favored.

## Understand the document

A set of personal postcards written in cipher and addressed to Anna Tichá. The proposed readings are in Czech; the writer’s identity and several dates remain unresolved.

Start with the [source catalogue or manuscript](https://crypto.hcportal.eu/dashboard/cryptograms/1518). It identifies the historical object. Card number 199 is not its catalogue-record ID; HCPortal indexes this card as cryptogram 1518. The source image is the evidence; the tables in this repository are recorded readings of that evidence.

## Read the current result

You can read the proposals in GitHub without installing anything. Start with one card rather than its evidence JSON.

| What you want | Open this |
| --- | --- |
| Latest working reading | [Card 330: Czech proposal and English interpretation](research-updates/2026-10-20-confirmed-key-continuation/cards/330.md#complete-working-reading--28-october-2026) |
| A particular postcard | [Complete card index](anna-ticha/readings.md), or the [137 current candidates and counters](research-updates/2026-10-20-confirmed-key-continuation/README.md#candidate-readings) |
| Collection totals and remaining work | [Review overview](REVIEW_STATUS.md): 154 of 263 cards have a reading here, including partial proposals; 109 have none |
| A calculation you can inspect by hand | [Card 199](anna-ticha/card-199.md) and the example below |
| Detailed source-review history | [Current package and dated checkpoints](research-updates/2026-10-20-confirmed-key-continuation/README.md#current-source-completion--card-330) |

Cards 330–386 now have editorial working texts covering their selected entries. They retain masks, alternative signs, uncertain word repairs and reading-order questions. Earlier candidates also include substantially incomplete readings, particularly 257. The next active source review is [329](research-updates/2026-10-20-confirmed-key-continuation/cards/329.md); new cards 387–390 are held while this completion work continues.

On a card page, distinguish these layers:

| Layer | Meaning |
| --- | --- |
| Czech proposal / English interpretation | A readable interpretation. Brackets and question marks flag tentative words or supplied letters. |
| Ciphertext and literal replay | Recorded signs and the output of the stated key, including awkward words and gaps. A fluent proposal can differ from this literal. |
| What remains uncertain | Which signs, word repairs, marks, names or dates are still unresolved. A literal question mark can be written punctuation or an unknown mask; the card notes distinguish them. |
| Evidence JSON / revision / validation | Source URLs, hashes, stored reader records, exact changes and executed checks. FIRST and SECOND are stored reader labels, not independent human validation. |

To examine a proposed word, compare it with the literal, then follow the original image link and uncertainty notes. Scans and private correspondence are not bundled. Zero unknown replay slots does not mean a card is solved: marks and alternative contours can remain unresolved, and some masks represent clusters of unknown physical length.

The [original six-card readable editions](anna-ticha/readings.md#readable-editions) and [37 earlier reports](anna-ticha/readings.md#preserved-card-reports) retain their own evidence stages. Card 204 has a separate author-reported manual check. Successful replay verifies a saved calculation; it does not establish every source reading, a sender's identity or a date.

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
