"""Database URL helpers shared by runtime and migrations."""

from typing import Any

from sqlalchemy.engine import make_url


def normalize_asyncpg_url(database_url: str) -> tuple[str, dict[str, Any]]:
    """Return an asyncpg-compatible SQLAlchemy URL and connect args."""

    parsed_url = make_url(database_url)
    query = dict(parsed_url.query)
    ssl_mode = query.pop("sslmode", None)

    if parsed_url.drivername != "postgresql+asyncpg" or ssl_mode is None:
        return database_url, {}

    connect_args: dict[str, Any] = {}
    normalized_ssl_mode = str(ssl_mode).lower()

    if normalized_ssl_mode == "disable":
        connect_args["ssl"] = False
    else:
        connect_args["ssl"] = True

    return parsed_url.set(query=query).render_as_string(
        hide_password=False
    ), connect_args
