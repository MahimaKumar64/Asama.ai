
from sqlalchemy import text
from app.database.session import engine


def upgrade():
    statements = [
        """
        ALTER TABLE routing_logs
        ALTER COLUMN rerank_score DROP NOT NULL
        """,
        """
        ALTER TABLE routing_logs
        ADD COLUMN IF NOT EXISTS hybrid_score FLOAT
        """,
        """
        ALTER TABLE routing_logs
        ADD COLUMN IF NOT EXISTS routing_decision VARCHAR(50)
        """,
        """
        ALTER TABLE routing_logs
        ADD COLUMN IF NOT EXISTS decision_reason TEXT
        """
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("Routing evaluation columns added successfully.")


if __name__ == "__main__":
    upgrade()
