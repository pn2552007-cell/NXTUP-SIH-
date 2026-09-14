"""Persist optional non-placement reasons without deleting existing data."""
from alembic import op
import sqlalchemy as sa

revision = "20260913_outcome_reason"
down_revision = "7519609ba247"
branch_labels = None
depends_on = None


def upgrade():
    columns = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("employment_records")}
    if "non_placement_reason" not in columns:
        op.add_column("employment_records", sa.Column("non_placement_reason", sa.String(255), nullable=True))


def downgrade():
    op.drop_column("employment_records", "non_placement_reason")