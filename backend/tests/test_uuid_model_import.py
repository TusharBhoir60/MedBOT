from uuid import UUID

from models.base_model import UUIDMixin, _generate_uuid


def test_uuid_mixin_imports_without_uuid6_dependency() -> None:
    assert UUIDMixin.__name__ == "UUIDMixin"
    assert callable(_generate_uuid)
    assert isinstance(_generate_uuid(), UUID)
