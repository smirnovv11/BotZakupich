from unittest.mock import Mock

from migrations.utils import create_enum_type, drop_enum_type


def test_create_enum_type_does_not_checkfirst() -> None:
    operations = Mock()
    bind = operations.get_bind.return_value

    create_enum_type(operations, "example_enum", ("one", "two"))

    enum_type = bind._run_ddl_visitor.call_args.args[1]

    bind._run_ddl_visitor.assert_called_once()
    assert bind._run_ddl_visitor.call_args.kwargs["checkfirst"] is False
    assert enum_type.name == "example_enum"
    assert enum_type.enums == ["one", "two"]


def test_drop_enum_type_does_not_checkfirst() -> None:
    operations = Mock()
    bind = operations.get_bind.return_value

    drop_enum_type(operations, "example_enum", ("one", "two"))

    enum_type = bind._run_ddl_visitor.call_args.args[1]

    bind._run_ddl_visitor.assert_called_once()
    assert bind._run_ddl_visitor.call_args.kwargs["checkfirst"] is False
    assert enum_type.name == "example_enum"
    assert enum_type.enums == ["one", "two"]
