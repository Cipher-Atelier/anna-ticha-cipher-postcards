#!/usr/bin/env python3
"""Pinned public JSON bindings for the source257 canonical evidence checker.

Original hashes identify frozen scientific records; selected hashes identify
actual published bytes. Only the fixed seed selection below bridges them. This
module never reads source images, follows proof references or attaches final AI
reviews. Call canonical_repeat_evidence.attach_review separately with real pins.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat

import canonical_repeat_evidence as canonical
import spatial_preparation as spatial


LEDGER_NAME = "selection-ledger-stage-v1.json"
LEDGER_SHA256 = "6dbcd3ae6bcaedd4914ed656bc845a0f194f90a8b193d53ba6f01ce3d3dcaba0"

# name: (public repository path, immutable original/actual byte hash)
PUBLIC_BASE = {
    "D9": ("research-updates/2026-10-13-source257-fullcard-map/data/fullcard-map-v2.json", "f58877d0b28fcedfac8ab6b336757988283aebdcc843aa1e8d90bccea82f1d34"),
    "D10": ("research-updates/2026-10-13-source257-class-candidates/data/candidate-inventory-v1.json", "a2f13278119c6437821a416e1cf56483e7d3d879a48e3adaa363023c314b87a0"),
    "D11": ("research-updates/2026-10-13-source257-exclusion-refinement/data/context-refinement-delta-v2.json", "9bc9f35a2427dc2fad36bdff3cae8ca7d7ae4fb5c74844a46885f4c5fc8926a4"),
}

# name: (source logical ID, selected filename, original identity, selected bytes)
# Every entry is explicit: an arbitrary ledger cannot authorize a new filter.
SEED_BINDINGS = {
    "profiles": ("D12_RESULTS:effective70-profile-references-v1.json", "effective70-profile-references-v1.json", "b5d588bbeb4e0210d4f3cd0cc3bea45cd7d77a88bdad9fe5037fc979d15e81bf", "b5d588bbeb4e0210d4f3cd0cc3bea45cd7d77a88bdad9fe5037fc979d15e81bf"),
    "metadata": ("D12_RESULTS:input-pins-metadata-v1.json", "input-pins-metadata-v1.json", "50d3ed50aa6a10233ce081c6bf575c7e5f11ea73fe35a0debe9df1685ce584dc", "50d3ed50aa6a10233ce081c6bf575c7e5f11ea73fe35a0debe9df1685ce584dc"),
    "architecture": ("D12_RESULTS:metadata-inventory-and-architecture-v1.json", "metadata-inventory-and-architecture-v1.json", "97dd365f39757c691f68e52f2585a6d187ffcb53550c01567cb5904f5ba191d4", "97dd365f39757c691f68e52f2585a6d187ffcb53550c01567cb5904f5ba191d4"),
    "inherited": ("D12_RESULTS:inherited-candidate-sets-v1.json", "inherited-candidate-sets-v1.json", "4bd2aa9a9589a5698d80abb07e19e53e0f0ec4a983ea0cfda4003ff8dd063139", "4bd2aa9a9589a5698d80abb07e19e53e0f0ec4a983ea0cfda4003ff8dd063139"),
    "core_pairs": ("D12_RESULTS:pair-coverage-deferred-v1.json", "pair-coverage-deferred-v1.json", "298caa5929a2432f369d8cce01f4cc320076d8cdea3140df6454887f5568465e", "298caa5929a2432f369d8cce01f4cc320076d8cdea3140df6454887f5568465e"),
    "protocol": ("D12_RESULTS:comparison-protocol-v1.json", "comparison-protocol-v1.json", "e0d0f9563e29af6463621f168b2d0797025b41d6fcb5d5e005063b098697691a", "e0d0f9563e29af6463621f168b2d0797025b41d6fcb5d5e005063b098697691a"),
    "scope_addendum": ("D12_RESULTS:scope-handling-addendum-v1.json", "scope-handling-addendum-v1.json", "f178d453c17930cbeed20aedeb95f70567b3c7d16708ec4ebfd555109985e647", "f178d453c17930cbeed20aedeb95f70567b3c7d16708ec4ebfd555109985e647"),
    "method_gate": ("D12_RESULTS:methods-protocol-gate-private-v2.json", "methods-protocol-gate-v2.json", "6678176673747857d9da60fb8552e8659282d6b24653ebfe7e74d9195fb48ae5", "0308cdc2a3d9413bce661d2e16ac182244afa74d9b42de68d312d21fd5c22dc8"),
    "reader_A": ("D12_RESULTS:repeat-reader-A-v1.json", "repeat-reader-A-v1.json", "1ee9e7f155562098018fbf7b471c8a83713b1216ddef5a8b78f057eb396f586d", "73387ba16f0508fa24ce31b92e4d3260bd4fc1d0e4a2cced1988543917ce22c5"),
    "reader_B": ("D12_RESULTS:repeat-reader-B-v1.json", "repeat-reader-B-v1.json", "57c34ca20119a8de119fef941f5d3be18e9d7185f0f7c5060e485b41d93160b2", "57c34ca20119a8de119fef941f5d3be18e9d7185f0f7c5060e485b41d93160b2"),
    "confirmation_B": ("D12_RESULTS:repeat-reader-B-paired-confirmation-addendum-v1.json", "repeat-reader-B-paired-confirmation-addendum-v1.json", "1a1827cff72705dcbe683799619c2e700fc7a451deb84af497144810eeaddf06", "1a1827cff72705dcbe683799619c2e700fc7a451deb84af497144810eeaddf06"),
    "closure_prelog": ("D12_RESULTS:targeted-closure-prelog-v1.json", "targeted-closure-prelog-v1.json", "cba6e8bd6da5f3cb779181e9c5e1636c27790ad1047126d17df55e3de2c55229", "cba6e8bd6da5f3cb779181e9c5e1636c27790ad1047126d17df55e3de2c55229"),
    "closure_A": ("D12_RESULTS:repeat-reader-A-closure-v1.json", "repeat-reader-A-closure-v1.json", "ef374c4da855a2097cc47d63f73faee36be8b12bf87540d6c2b4c65c97231e2b", "07b7c90606b110296f1af7bf77e212955c68792611f1d84e2e8908b56926c26e"),
    "closure_B": ("D12_RESULTS:repeat-reader-B-closure-v1.json", "repeat-reader-B-closure-v1.json", "8f4c78dba4cbb06b3b5159554c39f0c23601166820819a0d29be61b1deae03c2", "44205cbe4ac4e7d9f7a4090aad75fc5729d0226c40262f6e9528cccf3356a235"),
    "context_index": ("PACK:context-index.json", "context-index-v1.json", "76f81e4db718f3d9bfcf991e9c233d52e961a2dedc7163c4acc22c79abbf1333", "76f81e4db718f3d9bfcf991e9c233d52e961a2dedc7163c4acc22c79abbf1333"),
    "reader_A_closure_prelog": ("D12_RESULTS:repeat-reader-A-closure-prelog-v1.json", "repeat-reader-A-closure-prelog-v1.json", "01d87ec888eba0b76ed06acb678b5869318d9fc0a7e062ae872912a7bf9d722b", "01d87ec888eba0b76ed06acb678b5869318d9fc0a7e062ae872912a7bf9d722b"),
    "context_protocol": ("D12_RESULTS:comparison-context-pack-protocol-v1.json", "comparison-context-pack-protocol-v1.json", "c7d4f479ce0deec2e0513beeff85db2696bbb6db2338a4497c16373ad1cd4383", "c7d4f479ce0deec2e0513beeff85db2696bbb6db2338a4497c16373ad1cd4383"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_relative(value, *, json_only=True):
    require(isinstance(value, str) and bool(value), "Unsafe public relative path")
    path = PurePosixPath(value)
    require(not path.is_absolute() and ".." not in path.parts and path.as_posix() == value
            and re.fullmatch(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*", value)
            and all(part not in (".", "..") for part in path.parts), "Unsafe public relative path")
    if json_only:
        require(path.suffix == ".json", "Only pinned public JSON inputs are allowed")
    return path


def safe_file(anchor, relative):
    parts = safe_relative(relative).parts
    path = anchor
    for part in parts:
        path = path / part
        require(not path.is_symlink(), "Public input path traverses a symlink")
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), "Public input is not a regular file")
    require(path.resolve().is_relative_to(anchor), "Public input escapes its explicit directory")
    return path


def json_object(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON object key")
            result[key] = value
        return result
    value = json.loads(raw, object_pairs_hook=unique)
    require(isinstance(value, dict), "Public input JSON must be an object")
    return value


def expected_transformations(name):
    if name in {"reader_A", "closure_A"}:
        return [{"json_pointer": "/reader", "operation": "REPLACE_OPERATIONAL_READER_IDENTIFIER", "selected_value": "Separate AI reader A"}]
    if name == "method_gate":
        return [{"json_pointer": "/reviewer", "operation": "REPLACE_OPERATIONAL_REVIEWER_IDENTIFIER", "selected_value": "Separate AI methods reviewer"}]
    if name == "closure_B":
        return [{"json_pointer": f"/results/{i}/proved_source_panels/{j}/rgb_sha256", "operation": "REMOVE_PRIVATE_PANEL_RGB_HASH_VALUE"} for i in range(12) for j in range(4)]
    return []


def validate_ledger(ledger):
    """Check binding semantics as well as the externally pinned ledger bytes."""
    require(ledger.get("schema") == "source257-d12-publication-selection-stage-v1"
            and ledger.get("status") == "MECHANICAL_FROZEN_DATA_SELECTION_ONLY"
            and ledger.get("scientific_acceptance_claim") is False, "Wrong seed ledger scope")
    rows = ledger.get("files")
    require(isinstance(rows, list) and len(rows) == ledger.get("selected_evidence_file_count") == 17, "Wrong exact seed binding count")
    by_logical = {binding[0]: (name, binding) for name, binding in SEED_BINDINGS.items()}
    result = {}
    fields = {"source_logical_id", "original_whole_file_sha256", "selected_file", "selected_whole_file_sha256", "selected_bytes", "byte_identical", "role", "exact_json_pointer_transformations"}
    for row in rows:
        require(isinstance(row, dict) and set(row) == fields, "Unexpected seed ledger entry fields")
        safe_relative(row["selected_file"])
        require(row["source_logical_id"] in by_logical, "Unlisted original logical identity")
        name, (_, filename, original, selected) = by_logical[row["source_logical_id"]]
        require(name not in result, "Duplicate original binding")
        require(row["selected_file"] == filename and row["original_whole_file_sha256"] == original
                and row["selected_whole_file_sha256"] == selected, "Rebound original or selected byte identity")
        transformations = expected_transformations(name)
        require(row["exact_json_pointer_transformations"] == transformations, "Unknown privacy filter or transformed pointer")
        require(row["byte_identical"] is (not transformations), "Incorrect original/selected identity status")
        require(type(row["selected_bytes"]) is int and row["selected_bytes"] > 0, "Invalid selected byte count")
        result[name] = row
    require(set(result) == set(SEED_BINDINGS), "Missing seed original binding")
    return result


def validate_reference_universe(data):
    """Retain canonical.load's 307 original-record hash check, with uniqueness."""
    references = data["metadata"]["annotations"]
    records = data["D9"]["frozen_first_band"]["units"] + data["D9"]["new_units"]
    refs = {row["id"]: row for row in references}
    units = {row["id"]: row for row in records}
    require(len(records) == len(references) == len(refs) == len(units) == 307
            and set(refs) == set(units), "Immutable307 reference universe mismatch")
    for ident, record in units.items():
        require(spatial.record_sha(record) == refs[ident]["immutable_record_canonical_sha256"], "Immutable source record changed")


def check_consumer_pins():
    """Consumer code changes cannot silently select another scientific origin."""
    for name, (_, expected) in spatial.PINS.items():
        require(name in PUBLIC_BASE and expected == PUBLIC_BASE[name][1], "Unbound consumer original input")
    require(set(spatial.PINS) == set(PUBLIC_BASE), "Public base input universe changed")
    for name, (_, expected) in {**spatial.LOCAL_PINS, **canonical.RAW_PINS}.items():
        require(name in SEED_BINDINGS and expected == SEED_BINDINGS[name][2], "Unbound consumer original input")


def load(repository_root: Path, data_directory: Path, *, published_data_relative=None):
    """Return canonical-compatible (data, protected), using public JSON only.

    Both directory arguments are explicit. Actual repository-relative paths are
    inferred when data_directory is inside the repository. Staging outside it
    requires an explicit public destination; the post-copy load must agree with
    the actual directory. Extra files are not opened or trusted by this adapter.
    """
    repository_root, data_directory = Path(repository_root), Path(data_directory)
    require(not repository_root.is_symlink() and not data_directory.is_symlink(), "Explicit input directory cannot be a symlink")
    repository_root, data_directory = repository_root.resolve(strict=True), data_directory.resolve(strict=True)
    require(repository_root.is_dir() and data_directory.is_dir(), "Explicit input directory missing")
    if published_data_relative is not None:
        safe_relative(published_data_relative, json_only=False)
    if data_directory.is_relative_to(repository_root):
        actual_relative = data_directory.relative_to(repository_root).as_posix()
        safe_relative(actual_relative, json_only=False)
        require(published_data_relative in (None, actual_relative), "Declared public data path disagrees with actual repository location")
        bound_data_relative = actual_relative
    else:
        require(published_data_relative is not None, "External staging requires an explicit published_data_relative")
        bound_data_relative = published_data_relative
    check_consumer_pins()
    ledger_path = safe_file(data_directory, LEDGER_NAME)
    ledger_raw = ledger_path.read_bytes()
    require(digest(ledger_raw) == LEDGER_SHA256, "Unknown seed selection ledger hash")
    ledger = validate_ledger(json_object(ledger_raw))
    data, protected, hashes, paths, bindings = {}, {"selection_ledger": (ledger_path, LEDGER_SHA256)}, {}, {}, {}
    specifications = {name: (repository_root, relative, pin, pin, relative) for name, (relative, pin) in PUBLIC_BASE.items()}
    specifications.update({name: (data_directory, filename, original, selected, bound_data_relative + "/" + filename)
                           for name, (_, filename, original, selected) in SEED_BINDINGS.items()})
    for name, (anchor, relative, original, selected, logical_path) in specifications.items():
        path = safe_file(anchor, relative)
        raw = path.read_bytes()
        require(digest(raw) == selected, f"Public selected byte hash mismatch: {name}")
        if name in ledger:
            require(len(raw) == ledger[name]["selected_bytes"], f"Public selected byte count mismatch: {name}")
        data[name] = json_object(raw)
        protected[name], hashes[name], paths[name] = (path, selected), original, logical_path
        filter_identity = ("READER_IDENTIFIER_ONLY" if name in {"reader_A", "closure_A"}
                           else "METHOD_REVIEWER_IDENTIFIER_ONLY" if name == "method_gate"
                           else "REMOVE_48_PRIVATE_PANEL_RGB_HASH_LEAVES" if name == "closure_B"
                           else "BYTE_IDENTICAL")
        bindings[name] = {"path": logical_path, "original_whole_file_sha256": original,
                          "selected_whole_file_sha256": selected, "filter_identity": filter_identity}
    validate_reference_universe(data)
    data["_hashes"], data["_paths"] = hashes, paths
    data["_public_bindings"] = {"seed_ledger_sha256": LEDGER_SHA256, "inputs": bindings}
    spatial.verify_unchanged(protected)
    return data, protected
