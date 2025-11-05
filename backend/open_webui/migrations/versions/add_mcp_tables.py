"""Add MCP (Model Context Protocol) tables

Revision ID: mcp_001_initial
Revises: d31026856c01
Create Date: 2025-11-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "mcp_001_initial"
down_revision: Union[str, None] = "d31026856c01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create mcp_server table
    op.create_table(
        "mcp_server",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.Text(), nullable=False),  # stdio, sse, streamable_http
        sa.Column("command", sa.Text(), nullable=True),
        sa.Column("args", sa.JSON(), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("env", sa.JSON(), nullable=True),
        sa.Column("auth_type", sa.Text(), nullable=True),
        sa.Column("auth_config", sa.JSON(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_global", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("health_status", sa.Text(), nullable=True),
        sa.Column("last_health_check", sa.BigInteger(), nullable=True),
        sa.Column("server_info", sa.JSON(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.Column("updated_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
    )

    # Create indexes for mcp_server
    op.create_index("idx_mcp_server_user_id", "mcp_server", ["user_id"])
    op.create_index("idx_mcp_server_enabled", "mcp_server", ["enabled"])
    op.create_index("idx_mcp_server_is_global", "mcp_server", ["is_global"])
    op.create_index("idx_mcp_server_type", "mcp_server", ["type"])

    # Create mcp_resource table
    op.create_table(
        "mcp_resource",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("server_id", sa.Text(), nullable=False),
        sa.Column("uri", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.Text(), nullable=True),
        sa.Column("cached_content", sa.Text(), nullable=True),
        sa.Column("cached_at", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["mcp_server.id"], ondelete="CASCADE"),
    )

    # Create indexes for mcp_resource
    op.create_index("idx_mcp_resource_server_id", "mcp_resource", ["server_id"])
    op.create_index("idx_mcp_resource_uri", "mcp_resource", ["uri"])
    op.create_index(
        "idx_mcp_resource_server_uri",
        "mcp_resource",
        ["server_id", "uri"],
        unique=True,
    )

    # Create mcp_tool table
    op.create_table(
        "mcp_tool",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("server_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("input_schema", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["server_id"], ["mcp_server.id"], ondelete="CASCADE"),
    )

    # Create indexes for mcp_tool
    op.create_index("idx_mcp_tool_server_id", "mcp_tool", ["server_id"])
    op.create_index("idx_mcp_tool_name", "mcp_tool", ["name"])
    op.create_index(
        "idx_mcp_tool_server_name",
        "mcp_tool",
        ["server_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    # Drop mcp_tool table and indexes
    op.drop_index("idx_mcp_tool_server_name", table_name="mcp_tool")
    op.drop_index("idx_mcp_tool_name", table_name="mcp_tool")
    op.drop_index("idx_mcp_tool_server_id", table_name="mcp_tool")
    op.drop_table("mcp_tool")

    # Drop mcp_resource table and indexes
    op.drop_index("idx_mcp_resource_server_uri", table_name="mcp_resource")
    op.drop_index("idx_mcp_resource_uri", table_name="mcp_resource")
    op.drop_index("idx_mcp_resource_server_id", table_name="mcp_resource")
    op.drop_table("mcp_resource")

    # Drop mcp_server table and indexes
    op.drop_index("idx_mcp_server_type", table_name="mcp_server")
    op.drop_index("idx_mcp_server_is_global", table_name="mcp_server")
    op.drop_index("idx_mcp_server_enabled", table_name="mcp_server")
    op.drop_index("idx_mcp_server_user_id", table_name="mcp_server")
    op.drop_table("mcp_server")
