from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.epibench.spec import DEFAULT_SCHEMA_ROOT


class SchemaValidationError(ValueError):
    """Raised when an EpiBench artifact violates its schema."""


SCHEMA_BY_ARTIFACT = {
    "dataset-card": "dataset_evidence_card.schema.json",
    "split": "split_manifest.schema.json",
    "failure-trace": "failure_trace.schema.json",
    "result-bundle": "result_bundle.schema.json",
    "claim-eligibility": "claim_eligibility.schema.json",
    "sota-registry": "sota_registry.schema.json",
}


def load_structured(path: str | Path) -> Any:
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(f) or {}
        if path.suffix.lower() == ".json":
            return json.load(f)
    raise ValueError(f"Unsupported structured artifact format: {path}")


def load_schema(artifact_type: str, schema_root: str | Path = DEFAULT_SCHEMA_ROOT) -> dict[str, Any]:
    if artifact_type not in SCHEMA_BY_ARTIFACT:
        raise ValueError(f"Unknown EpiBench artifact type: {artifact_type}")
    schema_path = Path(schema_root) / SCHEMA_BY_ARTIFACT[artifact_type]
    return load_structured(schema_path)


def validate_artifact(
    artifact_type: str,
    artifact_path: str | Path,
    schema_root: str | Path = DEFAULT_SCHEMA_ROOT,
) -> dict[str, Any]:
    data = load_structured(artifact_path)
    schema = load_schema(artifact_type, schema_root)
    errors = validate_against_schema(data, schema)
    if errors:
        rendered = "\n".join(f"- {error}" for error in errors)
        raise SchemaValidationError(f"{artifact_path} is not EpiBench-valid:\n{rendered}")
    return data


def validate_against_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    return _validate_node(data, schema, "$", schema)


def _validate_node(data: Any, schema: dict[str, Any], path: str, root: dict[str, Any]) -> list[str]:
    if "$ref" in schema:
        return _validate_node(data, _resolve_ref(schema["$ref"], root), path, root)

    errors: list[str] = []
    allowed_type = schema.get("type")
    if allowed_type is not None and not _type_matches(data, allowed_type):
        return [f"{path}: expected {allowed_type}, got {type(data).__name__}"]

    if "const" in schema and data != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}, got {data!r}")
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}, got {data!r}")
    if isinstance(data, str):
        if "minLength" in schema and len(data) < int(schema["minLength"]):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: value {data!r} is below minimum {schema['minimum']!r}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: value {data!r} is above maximum {schema['maximum']!r}")

    if isinstance(data, dict):
        errors.extend(_validate_object(data, schema, path, root))
    elif isinstance(data, list):
        errors.extend(_validate_array(data, schema, path, root))
    return errors


def _validate_object(data: dict[str, Any], schema: dict[str, Any], path: str, root: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required", []))
    missing = sorted(required - set(data))
    for key in missing:
        errors.append(f"{path}: missing required property {key!r}")

    properties = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)
    for key, value in data.items():
        child_path = f"{path}.{key}"
        if key in properties:
            errors.extend(_validate_node(value, properties[key], child_path, root))
        elif isinstance(additional, dict):
            errors.extend(_validate_node(value, additional, child_path, root))
        elif additional is False:
            errors.append(f"{child_path}: additional property is not allowed")

    if "minProperties" in schema and len(data) < int(schema["minProperties"]):
        errors.append(f"{path}: object has fewer than {schema['minProperties']} properties")
    return errors


def _validate_array(data: list[Any], schema: dict[str, Any], path: str, root: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "minItems" in schema and len(data) < int(schema["minItems"]):
        errors.append(f"{path}: array has fewer than {schema['minItems']} items")
    item_schema = schema.get("items")
    if item_schema:
        for index, value in enumerate(data):
            errors.extend(_validate_node(value, item_schema, f"{path}[{index}]", root))
    return errors


def _resolve_ref(ref: str, root: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local JSON Schema refs are supported by the reference validator: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"JSON Schema ref does not resolve to an object: {ref}")
    return node


def _type_matches(data: Any, allowed_type: str | list[str]) -> bool:
    if isinstance(allowed_type, list):
        return any(_type_matches(data, candidate) for candidate in allowed_type)
    if allowed_type == "object":
        return isinstance(data, dict)
    if allowed_type == "array":
        return isinstance(data, list)
    if allowed_type == "string":
        return isinstance(data, str)
    if allowed_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if allowed_type == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if allowed_type == "boolean":
        return isinstance(data, bool)
    if allowed_type == "null":
        return data is None
    raise ValueError(f"Unsupported JSON Schema type in reference validator: {allowed_type}")
