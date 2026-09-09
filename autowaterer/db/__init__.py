from quart_sqlalchemy import AsyncBindConfig, SQLAlchemyConfig
from quart_sqlalchemy.framework import QuartSQLAlchemy

db = QuartSQLAlchemy(
    SQLAlchemyConfig(
        binds={
            "default": AsyncBindConfig(
                engine={"url": "sqlite+aiosqlite:///autowaterer.db"},
            )
        }
    )
)
