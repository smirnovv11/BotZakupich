from app.infrastructure.db.url import normalize_asyncpg_url


def test_normalize_asyncpg_url_moves_sslmode_to_connect_args() -> None:
    database_url = (
        "postgresql+asyncpg://user:password@example.com:5432/app?sslmode=require"
    )

    normalized_url, connect_args = normalize_asyncpg_url(database_url)

    assert normalized_url == "postgresql+asyncpg://user:password@example.com:5432/app"
    assert connect_args == {"ssl": True}


def test_normalize_asyncpg_url_keeps_regular_asyncpg_url() -> None:
    database_url = "postgresql+asyncpg://user:password@example.com:5432/app"

    normalized_url, connect_args = normalize_asyncpg_url(database_url)

    assert normalized_url == database_url
    assert connect_args == {}
