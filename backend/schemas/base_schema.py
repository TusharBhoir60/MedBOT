"""
Base Pydantic schema with shared configuration.

All API response and request schemas inherit from BaseSchema
to get consistent serialization behavior:
  - from_attributes=True: enables ORM model → schema conversion
  - populate_by_name=True: allows both alias and field name
  - CamelCase alias generation: JSON responses use camelCase keys
"""
from pydantic import BaseModel, ConfigDict


def to_camel_case(field_name: str) -> str:
    """Convert a snake_case field name to camelCase.

    Examples:
        'created_at'    → 'createdAt'
        'db_latency_ms' → 'dbLatencyMs'
        'status'        → 'status'
    """
    parts = field_name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class BaseSchema(BaseModel):
    """Base schema for all AarogyaAgent API models.

    Configuration:
        - from_attributes: enables direct construction from ORM models
        - populate_by_name: accepts both field name and alias
        - alias_generator: auto-generates camelCase aliases for JSON output
        - str_strip_whitespace: strips leading/trailing whitespace from strings
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel_case,
        str_strip_whitespace=True,
    )
