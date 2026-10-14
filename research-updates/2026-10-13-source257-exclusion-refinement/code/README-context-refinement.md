# Bounded physical-context refinement checker

Run from this directory with Python 3.10+ (stdlib only):

```sh
python3 check_context_refinement.py DELTA BASELINE ASSESSMENT_PROTOCOL NEW_DIAGNOSTIC --context-index CONTEXT_INDEX
python3 -m unittest test_context_refinement.py -v
```

The checker pins the immutable baseline, assessment protocol, and (when supplied)
context index by whole-file SHA256. All inputs are read-only. The diagnostic must
not exist; input and output aliases, including hardlinks, are rejected before any
write. Every input is snapshotted and rechecked immediately before and after the
diagnostic write. The diagnostic is not a visual-proof certificate.

The delta changes eligibility only for the fixed 15 annotation profiles. The 157
other whole records and 135 unresolved source placeholders are inherited from the
exact pinned baseline; there is no patch language for modifying them. No class or
merge assignments are accepted. Counts are annotation-profile counts, never
glyph, token, symbol, or alphabet totals.

## Evidence schema

The delta has exactly these top-level fields:

- `schema`: `source257-context-refinement-delta-v1`.
- `pins`: `baseline_sha256`, `assessment_protocol_sha256`,
  `context_index_sha256`, `reader_A_sha256`, `reader_B_sha256`,
  `reader_A_coordinate_addendum_sha256`, `reader_B_coordinate_erratum_sha256`,
  `reader_B_literal_mark_addendum_sha256`.
  Original readings remain pinned separately from post-feedback corrections.
- `cases`: all 15 cases, including retained and partially resolved cases.
- `unchanged_scope`: sorted `other_whole_annotation_ids`, unchanged ordered
  `unresolved_source_ids`, and `policy` set to
  `BASELINE_UNCHANGED_NO_PATCH_OUTSIDE_COHORT`.
- `class_merge_claims`: empty list.
- `claimed_metrics`: must equal the checker-derived metrics below.

Each case has exactly these fields (native bboxes are integer half-open original
source rectangles, never replacements for base locators):

- `id`, `base_native_bbox_xyxy_halfopen`, `candidate_eligible_before: false`.
- `window_barrier_after`: `DISCHARGED`, `PARTIAL`, or `RETAINED`.
- `old_id_target_identity`: `SUPPORTED_SAME_TARGET` or `UNRESOLVED`;
  `old_id_target_identity_evidence`: grounds object;
  `observed_target_native_bbox_xyxy_halfopen`: sidecar bbox or null. A supported
  identity needs a bbox; an uncertain old ID must not be forced onto one fragment.
- `competing_alternatives`: nonempty list. Every old local-mark locator must occur
  as `old_native_locator`. Each entry also has `new_native_locator`, `side`
  (`LEFT`, `RIGHT`, `OVERLAPPING`), `physical_component_ref` (with `component_id`,
  `annotation_ids`, and `native_bbox_xyxy_halfopen`), `relation`
  (`CONTINUOUS_NEIGHBOR`, `CONTINUOUS_TARGET`, `BOUNDED_SEPARATE_NEIGHBOR`,
  `UNRESOLVED`), `connection_regions` (list of native bboxes), and grounds fields.
  FC108, FC126, FC127 must each explicitly address both LEFT and RIGHT. Complete
  boundary regions may support a separately bounded construction; pale gap,
  proximity, or a reference list alone cannot establish allocation.
- `physical_features`: all eight fields `path_topology`, `enclosures`, `openings`,
  `stem_pattern`, `attached_bars`, `connected_extra_strokes`, `terminal_pattern`,
  `owned_mark_profile`. Each entry has `status` (`KNOWN` or `UNRESOLVED`),
  `description`, `source_view_refs`. `significant_signature` repeats the complete
  eight descriptions verbatim; it cannot omit inconvenient detail.
- `mark_inventory`: nonempty list with each old local-mark locator represented
  in `old_native_locators`. Each entry also contains `native_locator`,
  `appearance`, `physical_allocation` (`TARGET_CONTINUOUS`, `NEIGHBOR_COMPONENT`,
  `UNRESOLVED`), `physical_component_id`, `functional_role: UNKNOWN`, and grounds
  fields. Inventory all newly visible competing marks too. A physically separate
  but unallocated detached mark blocks eligibility.
- `alias_check`: `status`
  (`NO_SAME_INSTANCE_ALIAS_OBSERVED_WITH_REFERENCED_NEIGHBORS` or `UNRESOLVED`),
  explicit `checked_annotation_ids` (whole and/or unresolved neighboring map
  references), and grounds fields. Overlapping envelopes do not prove aliases or
  distinct instances. With the optional context index, the list must include every
  focus-intersecting ID in the pinned baseline unresolved-ID collection, including
  FC and U names. This checks metadata coverage only; each reference still needs
  source-grounded alias review.
- `full_feature_eligibility_after`: boolean.
- `remaining_blockers`, `new_blockers`: lists of objects with `kind`,
  `description`, and grounds fields. Allowed cause kinds are
  `LOCAL_SOURCE_DETAIL_UNRESOLVED_BY_THIS_METHOD`,
  `SOURCE_SUPPORTED_LOCAL_INFORMATION_LOSS`, `UNIDENTIFIABLE_SEMANTIC_ROLE`,
  `SCHEMA_CONVENTION_NEEDING_ANOTHER_INTERVENTION`,
  `RECOVERABLE_CONTEXT_ISSUE_NOT_RESOLVED_HERE`, `UNASSESSED`.
- `source_view_refs`: context IDs including complete region and focus views.
- `reader_disagreements`: list of specific textual differences (empty if none);
  `graphic_resolution`: scientific resolution with graphical basis, including
  conservatively retained uncertainty.
- `reader_support`: A and B objects, each with boolean
  `window_discharge_supported`, boolean `eligibility_supported`,
  `basis_report_sha256`, `support_phase` (`INITIAL_INDEPENDENT_READING` or
  `POST_FEEDBACK_COORDINATE_AUDIT`, or B-only
  `POST_FEEDBACK_LITERAL_MARK_AUDIT`), and grounds fields. The phase is checked
  against the original or supplemental pin. Corrected support must never be
  presented as blind initial consensus. Both readers must support any accepted discharge; both must support a
  promotion. This gate supplements, and does not substitute for, source evidence.
- `adjudicator_source_inspection`: booleans `source_native_and_clockwise_verified`
  and `complete_target_features_inspected` (both true), and grounds fields. This records the adjudicator's inspection;
  a later independent scientific review is a separate pinned artifact.
- `causal_attribution`: `old_context_native_bbox_xyxy_halfopen`,
  `required_evidence_native_bbox_xyxy_halfopen`, boolean
  `required_evidence_within_old_context`, `gain_basis`
  (`INSIDE_OLD_CONTEXT_NEW_COMPONENT_ALLOCATION` or `EXTENDS_BEYOND_OLD_CONTEXT`),
  and grounds fields. The checker computes nominal rectangle containment. This
  characterizes evidence availability and reading procedure; it does not isolate
  a causal effect of widening. Wider display, explicit allocation, new readers,
  and readjudication vary together. Locators are approximate regions, not traced
  masks. Source pixels and resolution are unchanged.
- `cipher_role`, `functional_role`, `letter_value`: all `UNKNOWN`.

Every “grounds object/fields” means nonempty `graphical_grounds` and nonempty
`source_view_refs` using context IDs, with no absolute private path. The optional
context index verifies that these IDs exist and include the target. Descriptive
strings and entered locators still require actual visual scientific review;
passing this checker cannot prove their truth or completeness.

The complete derived metric keys are `window_barrier_before` (15),
`window_barrier_discharged`, `window_barrier_partial`, `window_barrier_retained`,
`cases_with_new_blockers`, `cohort_eligible_before` (0), `cohort_eligible_after`,
`eligible_annotation_profiles_after` (55 + accepted),
`excluded_annotation_profiles_after` (117 - accepted), `unchanged_other_whole`
(157), and `unchanged_unresolved_placeholders` (135).

A discharged window plus a new or remaining closure/mark/identity issue remains
excluded. Eight positive/negative synthetic fixture methods target this and the
other stated failure modes; their synthetic descriptions are not corpus evidence.

Unresolved local wedges, tiny closures, and thick necks default to
`LOCAL_SOURCE_DETAIL_UNRESOLVED_BY_THIS_METHOD`. Irreversible local information
loss requires an explicit source argument and separate scientific support; this
checker cannot establish it.
