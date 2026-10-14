# Native neighbor context pack

This separate experiment utility reads the pinned source, full-card annotation
map, candidate inventory, and a cohort protocol. It does not rerun the prior
candidate experiment or modify earlier crops. Pillow is the only dependency.

From this directory:

```sh
python3 build_neighbor_context_pack.py SOURCE BASE INVENTORY PROTOCOL OUTPUT_ROOT --protocol-sha256 PROTOCOL_WHOLE_FILE_SHA256
python3 -m unittest test_neighbor_context_pack.py -v
```

`OUTPUT_ROOT` must not exist; its parent must already exist. All input pins,
aliases (including hardlinks), geometry, and RGB proofs are checked before the
first output write. Input symlinks and output aliases are rejected. Existing
packs are never overwritten. The optional CLI hash externally pins the exact
protocol file. Use it for the real experiment.

Protocol JSON shape:

```json
{
  "schema": "source257-neighbor-context-protocol-v1",
  "pins": {
    "source_sha256": "7407bb54bcfbf69af61d801fb04a0b4de8fce9d8c24976ba1a3f4c3f2120aae4",
    "source_rgb_sha256": "5861cd6fe98334bc983dda575a6c36bb3222e73a71329865a42e8cc492f2db94",
    "source_size": [1785, 1175],
    "base_sha256": "f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34",
    "inventory_sha256": "a2f13278119c6437821a416e1cf56483e7d3d879a48e3adaa363023c314b87a0"
  },
  "selected_ids": ["REPLACE_WITH_PINNED_COHORT"],
  "trajectory_padding": {"cross_axis": 80, "along_axis": 40},
  "focus": {"enabled": true, "x_padding": 80, "y_padding": 90}
}
```

The three required top-level fields are `schema`, `pins`, and `selected_ids`.
All five pin fields are required. Unknown protocol keys are rejected. Padding
is a nonnegative integer count of native pixels. Omitted padding/focus fields
use the values shown. `focus.enabled: false` skips focus images.

Alternatively, `focus.windows` can be a nonempty list of supplied native
windows, each shaped as:

```json
{
  "id": "provided-focus-1",
  "target_ids": ["SELECTED_ID"],
  "native_bbox_xyxy_halfopen": [0, 0, 100, 100]
}
```

Every supplied target must belong to the selected cohort and intersect its
window. Windows must be nonempty integer half-open rectangles within the
source. A provided window covering more than one target region must explicitly
specify `rotation_degrees_clockwise` as `0` or `90`. A single-region window
follows that region's rotation. Without supplied windows, one enlarged focus
window is made per target, using native x/y padding and source clipping.

Every touched region contributes one trajectory image. Its rectangle is the
union of **all** map units in that region, including unresolved spans, expanded
by the trajectory padding and clipped to the source. The frozen units are
assigned the geometry-only region name `frozen-first-band`. For `right-R*`,
cross-axis padding affects native x, along-axis affects native y, and the
result rotates exactly 90 degrees clockwise. For bottom/frozen contexts,
cross-axis affects y, along-axis affects x, and pixels stay unrotated. Focus
images for right-region targets also rotate exactly 90 degrees clockwise.

Output:

- `context-index.json`: public-safe whole-file input pins, source dimensions,
  cohort, native rectangles, rotations, target and intersecting annotation
  IDs/coordinates. Intersections explicitly make no ownership claim. All 307
  annotations remain map units, including unresolved spans; they are not
  asserted to be tokens. No per-image or crop-body hashes or raster payloads
  appear here.
- `private/context-NNN.png`: native RGB crops, with integer transpose as needed.
  No rescale, filters, recognition, enhancement, segmentation, or pixel labels.
- `private/pixel-proof.json`: private PNG/RGB digests, source row ranges and
  row digests, plus an exact inverse-transform verification and formulas.
  Its whole-file SHA256 can separately be recorded by the experiment owner.

The utility reads inventory ID collections and the map/source pin only. It
does not use class memberships, signatures, adjudications, or labels.

The seven tests use temporary synthetic RGB fixtures. They never load corpus
pixels, earlier image packs, or prior experiment tests.
