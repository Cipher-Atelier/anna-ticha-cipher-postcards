# Reading the Anna Tichá cipher postcards

A partial key transfers from one Czech postcard to five more, with preserved unknowns, staged tests, and a concert reference checked against 1904 newspaper notices.

Author: Maxim Egorov

Prepared (source preparedUtc): 2026-10-04T23:26:32Z

Source: [published article](https://maxim-egorov.dev/research/anna-ticha-postcards/). Exported from the already-published article on 5 October 2026. The preparation timestamp is preserved as supplied; it is not a new publication date. Article wording is preserved below; site-specific HTML presentation has been converted to Markdown and site-root links have been expanded to absolute website URLs.

[Investigation index](README.md) · [Methods](methods.md) · [Readings](readings.md) · [Sources](sources.md)

## A partial decipherment of six postcards

A substitution key developed from one postcard addressed to Anna Tichá produces connected Czech on five more. The readings concern letters that crossed in the post, New Year wishes, an unanswered note, jealousy, a ball, and concert plans. One passage has a particularly useful external check: contemporary newspaper announcements match its proposed sequence of concerts at Prague's Rudolfinum in January and February 1904.

This is a partial decipherment. Unknown signs and malformed words remain. The results support a shared substitution system across these six cards, without establishing a complete solution to the collection, the sender's identity, or historical priority.

HCPortal's preserved catalogue lists 263 Czech cryptograms addressed to Anna Tichá, numbered 198–460 and dated 1900–1908 where dates are available. The catalogue snapshot labels them “Not solved”; that label describes the source record, rather than independently establishing the novelty of this work. The collection also appears in Antal and Zajac's [HistoCrypt 2026 account of HCPortal](https://dspace.ut.ee/server/api/core/bitstreams/31718ebb-5a1e-4c4f-be45-2f8aa869034e/content#page=197), printed page 185.

Relevant prior work includes Antal, Pavuk, and Zajac's [*Solving Historical Ciphers with AI*](https://dspace.ut.ee/items/5cfe6720-b894-4a6d-8419-1deb3907040e) (HistoCrypt 2026, pp. 197–207), which studies AI-assisted transcription and decipherment of other historical postcards. The bounded literature check identified no solution for the three initial target cards, 198, 440, and 441, but cannot rule out unindexed or unpublished work.

## Developing and testing the key

The development card was [pc_hcp_198](https://crypto.hcportal.eu/dashboard/cryptograms/1517), dated 30 January 1904. Its transcription contains 343 source positions. A numerical search used 328 secure, unmarked positions in 21 graphical classes, leaving marked or unresolved positions masked. It scored Czech letter sequences with an accent-folded model trained on Božena Němcová's [*Listy I*](https://web2.mlp.cz/koweb/00/03/34/99/42/listy_I.pdf).

Source review then separated one graphical family into forms interpreted as **k** and **z**, and proposed a capped form for **ch**. Those refinements produced 23 assignments fixed before the first test card was decoded. They were part of key development, not discoveries made by the numerical search alone.

For later tests, separate AI readers transcribed the source against neutral graphical references without consulting the key or plaintext. Their records were reconciled before applying the fixed lookup. Unknown forms stayed unknown. Separate linguistic assessments examined the literal outputs for connected Czech and defects.

These transcriptions and linguistic checks were AI-generated, with restricted inputs between stages. They are not external human expert reviews.

The model changed in documented stages. An unbarred variant assigned **t** became a 24th entry after card 440. Later, marked forms on card 453 supplied development evidence for secondary rules, frozen before card 329. The primary key and secondary rules therefore need separate results:

- **Card [440](https://crypto.hcportal.eu/dashboard/cryptograms/1759) · 24 December 1901.** First primary coverage: 178/196, 90.8%. Secondary result: not part of this test.
- **Card [250](https://crypto.hcportal.eu/dashboard/cryptograms/1569) · 31 December 1902.** First primary coverage: 254/272, 93.4%. Secondary result: not part of this test.
- **Card [453](https://crypto.hcportal.eu/dashboard/cryptograms/1772) · 1 March 1900.** First primary coverage: 138/167, 82.6%. Secondary result: used later to develop rules.
- **Card [329](https://crypto.hcportal.eu/dashboard/cryptograms/1648) · 15 February 1900.** First primary coverage: 223/298, 74.8%. Secondary result: 238/298, 79.9%.
- **Card [199](https://crypto.hcportal.eu/dashboard/cryptograms/1518) · 26 January 1904.** First primary coverage: 522/532, 98.1%. Secondary result: identical; no eligible positions.

**Coverage is not accuracy.** These fractions count source regions or bodies assigned a value, not verified correct plaintext. A single **ch** sign emits two letters. The cards were selected for specific research purposes, not as a random sample of the collection.

The dates are conventional readings of separate inscriptions, not established dispatch or receipt dates.

## What the messages say

Card 440 contains a useful sequence beyond a conventional greeting. An excerpt from its saved first output reads:

```text
drahy dopis kri?oval se s mym
?istkem do zirovnice zasla
nym budu?en?okra?e hod
```

A cautious editorial interpretation is: “The dear letter [crossed] my [note] sent to [probably Žirovnice].” Brackets identify supplied or uncertain content. The connected grammatical frame and a following promise to reply support the reading, while its literal defects remain visible. Elsewhere, **mescislnekra?e** might mean “countless times,” but that interpretation would change an already assigned letter. It is not an accepted correction.

Card 250 brings New Year wishes and a question about continued affection. Card 453 asks after a promised letter. Card 329 thanks the recipient for two notes, contrasting an affectionate picture with a different mood in the second message. The Pepouš-family signoffs suggest an intimate nickname; they do not identify a historical person.

Dates offer another qualified lead. Cards 329 and 453 are 14 days apart. A later image-only review read an underlined pair on card 453 as the conventional numeral **14**, within a days-ago phrase. The first fixed-key output remains **yi**. The possible link between the two cards is plausible, but neither that link nor a general rule for unencrypted underlined numerals is established.

## A concert reference with an external match

Card 199 is the longest completed test. All 23 original assignments occur, including the rare **f** in **rudolfina**; the later unbarred **t** variant is absent. Its concert passage reads:

```text
bavilo v pondeli pujdu do rudolfina na treti
koncert curnalistu chtel jsem jiti jiz vcera
na druhy koncert nebyly vsak jiz listky ??
koupi na ten koncert se tesim je pry pro?ukce
```

The other source region begins:

```text
skoly sevcikovy velkoleba
```

In editorial English, the writer plans to attend a third concert at the Rudolfinum on Monday, having found no tickets for the second concert the previous day, and anticipates a performance by Ševčík's school. Joining the two regions is a linguistic interpretation: their cross-region reading order was unresolved in the frozen source record.

This reading requires care. **curnalistu** is not literal **žurnalistů**: the proposal changes **c** to **z** before adding diacritics. **velkoleba** would require **b** to become **p** for *velkolepá*, “magnificent.” A later source audit did not authorize those repairs. The saved output preserves both strings.

The postcard's separate inscription reads 26 January 1904, a Tuesday. If it dates composition, and “Monday” means the next Monday, “yesterday” points to 25 January and the planned concert to 1 February.

Two notices found after decoding match that sequence. [*Národní listy*, 25 January 1904, page 3](https://www.digitalniknihovna.cz/mzk/uuid/uuid:a934f750-7108-11dc-b40d-000d606f5dc6), announces that day's second concert of the Association of Czech Journalists at the Rudolfinum. [The 31 January issue, page 3](https://www.digitalniknihovna.cz/mzk/uuid/uuid:c586dfe0-7108-11dc-bdb4-000d606f5dc6), announces its third and final concert for Monday 1 February, with a group from Ševčík's master school performing again.

The dates, numbering, venue, organisation, and school form a specific external match. These are advance announcements: they corroborate the proposed reference without proving that the performances occurred as advertised, that the writer attended, or who the writer was. They also do not retroactively repair **curnalistu**.

## Limits and downloadable evidence

Three matched synthetic controls recovered every secure letter under the fixed search budget. That tests the solver on clean, known-truth substitutions; it supplies no historical plaintext accuracy. Earlier failed attempts, including a failed initial fit on card 441 and a failed first mark-rule proposal, remain part of the record. Card 441 was excluded from this first edition because its authoritative full replay was not recovered. A separately labelled [retrospective reconstruction](https://maxim-egorov.dev/research/anna-ticha-postcards/card-441/) is now available; it does not restore the missing old artifact.

Some experimental packaging was lost and only partly recovered. Core numerical inputs and results were reproduced exactly, but the complete original development freeze manifest and key-wrapper file are unavailable. The preserved assignments should not be mistaken for an intact original wrapper.

The downloads retain the distinction between literal output and interpretation:

- [Saved literal readings for the six cards](https://maxim-egorov.dev/downloads/anna-ticha-postcards/anna-ticha-saved-literal-readings.txt), including both first outputs for card 329
- [Partial key and staged mark rules](https://maxim-egorov.dev/downloads/anna-ticha-postcards/anna-ticha-partial-key-and-rules.txt), as a text reference
- [Card 199 validation addendum](https://maxim-egorov.dev/downloads/anna-ticha-postcards/anna-ticha-card199-validation-addendum.pdf), with the full literal and later source checks

Original photographs and newspaper pages remain linked at their institutional sources. Further progress requires new source checks and tests on additional material, with future revisions kept separate from these first predictions.

