"""Non-destructive additive upgrade for existing local demo databases."""
from sqlalchemy import inspect, text


def upgrade_outcome_schema(engine):
    columns = {c["name"] for c in inspect(engine).get_columns("employment_records")}
    if "non_placement_reason" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE employment_records ADD COLUMN non_placement_reason VARCHAR(255)"
            ))