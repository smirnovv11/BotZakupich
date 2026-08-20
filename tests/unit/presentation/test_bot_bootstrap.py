import importlib

from app.presentation.bot.router import bot_router


def test_app_main_import_does_not_load_runtime_settings() -> None:
    module = importlib.import_module("app.main")

    assert callable(module.main)
    assert callable(module.run_polling)


def test_bot_router_includes_start_router() -> None:
    assert bot_router.name == "bot"
    assert [router.name for router in bot_router.sub_routers] == ["start", "items"]
