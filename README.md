# Cipher postcards addressed to Anna Tichá

A set of personal postcards written in cipher and addressed to Anna Tichá. The proposed readings are in Czech; the writer’s identity and several dates remain unresolved.

## What has been found?

Selected cards can be read in part. The most complete public checking package is for card 199: it records each of its 532 symbol positions and the proposed letters. Other cards have separate reading reports, with different amounts of evidence.

A small example from the recorded result:

```text
vrely dik za drahy listek byl
```

The opening of card 199 expresses warm thanks for a dear letter. This is a summary of the proposed Czech reading, not an identification of its writer.

## Start reading

[Card 318: preliminary May Day greeting](anna-ticha/card-318.md): an unchanged-key reading of the 96-body main block, with a word ledger and explicit single-reader limits. Marginal text remains open.

[Card 319: thanks and a promised reply](anna-ticha/card-319.md): a preliminary ten-line reading with 150 mapped bodies and a retained faded cluster. The ledger, source fingerprints and limits are public.

[Card 316: going home and an affectionate message](anna-ticha/card-316.md): a partial reading with 102 invariant proposed mapped bodies, two y/i alternatives and an unresolved closing. The written year remains unconfirmed.

[Card 320: Easter wishes and a promised letter](anna-ticha/card-320.md): a preliminary ten-line reading with 200 proposed mapped bodies. Includes the literal, interpretation and contextual source ledger.

[Card 315: arrival in Prague and taking up service](anna-ticha/card-315.md): a preliminary six-line reading, with a source ledger and written date 8 June 1901. The kind of service remains unidentified.

[Card 314: a letter for tomorrow and concern for the recipient](anna-ticha/card-314.md): a partial eleven-line reading with 253 proposed mapped bodies and an unresolved overwritten cluster. Literal defects and editorial repairs remain separate.

[9 October control audit](research-updates/2026-10-09-anna204-controls.md): the tested comparator and control gates failed; Anna204's disputed target remains unresolved. This update is a text summary, with full replay materials retained locally.

1. [Read the plain-language guide](READING_GUIDE.md): the document, result, file meanings and one worked check. No programming is required.
2. Open [Card 199: literal reading](verification/anna-ticha/literal.txt) to inspect the saved text or test result itself.
3. Read the [research account](anna-ticha/article.md) for historical context, methods, earlier work and unresolved questions.

## How can I check it?

Follow the worked example in [the reading guide](READING_GUIDE.md#check-one-example-by-hand). It connects a source record, a key or model assumption, and the saved output. For an independent source check, use the [original-source entry](https://crypto.hcportal.eu/dashboard/cryptograms/1518); images are linked, not redistributed here.

If you use Python, follow the [complete verification instructions](verification/README.md), including download/setup, expected results and troubleshooting. The command from this repository’s top-level folder is:

```sh
python3 verification/check_all.py
```

A successful run means the published files and declared calculation reproduce. It does not establish that every source sign or historical interpretation is correct.

## Precise research scope

Partial card readings. Complete positional replay for card 199 only; cards 440 and 453 supply limited examples. Cards 247 and 248 remain qualified text reports, without complete evidence packages or complete plaintext.

This is part of [Cipher-Atelier](https://github.com/Cipher-Atelier), founded by [Maxim Egorov](https://github.com/cayde-6). Explore the [research index](https://github.com/Cipher-Atelier/research-index), [contribution guide](https://github.com/Cipher-Atelier/.github/blob/main/CONTRIBUTING.md), and [step-by-step research workflow](https://github.com/Cipher-Atelier/research-index/blob/main/START_HERE.md).

Source credit and item-specific restrictions remain in the research records. Scans, crops, restricted materials and private correspondence are excluded. No new blanket licence is asserted. AI-assisted work requires evidence checking and does not constitute external human expert review.

[Publication provenance](SOURCE_PROVENANCE.json) records the source commit, retained file hashes and deliberate code/navigation adaptations. The original repository history remains intact.

## Contribute to this investigation

Read the current result and source limitations, then coordinate a bounded task in an existing issue or use [Work on existing research](https://github.com/Cipher-Atelier/anna-ticha-cipher-postcards/issues/new?template=research.yml). Fork the repository and submit a focused pull request with your evidence and checks. Independent replication and constructive alternative readings are welcome. See [Start here](https://github.com/Cipher-Atelier/research-index/blob/main/START_HERE.md) for the shared workflow.
