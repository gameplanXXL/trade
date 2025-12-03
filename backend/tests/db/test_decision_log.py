"""Tests for Decision Audit Log - Story 003-04."""

from sqlalchemy import JSON

from src.db.models import AgentDecisionLog


class TestAgentDecisionLogModel:
    """Tests for AgentDecisionLog SQLAlchemy model."""

    def test_model_has_required_columns(self) -> None:
        """Test that model has all required columns."""
        # Check table name
        assert AgentDecisionLog.__tablename__ == "agent_decisions"

        # Check columns exist
        columns = {c.name for c in AgentDecisionLog.__table__.columns}
        expected_columns = {
            "id",
            "team_instance_id",
            "agent_name",
            "decision_type",
            "data",
            "confidence",
            "created_at",
        }
        assert expected_columns.issubset(columns)

    def test_id_is_primary_key(self) -> None:
        """Test that id is primary key."""
        pk_columns = [c.name for c in AgentDecisionLog.__table__.primary_key.columns]
        assert "id" in pk_columns

    def test_team_instance_id_column(self) -> None:
        """Test team_instance_id column configuration."""
        column = AgentDecisionLog.__table__.c.team_instance_id
        assert column is not None
        # Has foreign key to team_instances
        fks = list(column.foreign_keys)
        assert len(fks) == 1
        assert "team_instances.id" in str(fks[0])

    def test_agent_name_column(self) -> None:
        """Test agent_name column configuration."""
        column = AgentDecisionLog.__table__.c.agent_name
        assert column is not None
        assert column.type.length == 50

    def test_decision_type_column(self) -> None:
        """Test decision_type column configuration."""
        column = AgentDecisionLog.__table__.c.decision_type
        assert column is not None
        assert column.type.length == 20

    def test_data_column_is_json(self) -> None:
        """Test data column is JSON type."""
        column = AgentDecisionLog.__table__.c.data
        assert column is not None
        assert isinstance(column.type, JSON)

    def test_confidence_column_nullable(self) -> None:
        """Test confidence column is nullable."""
        column = AgentDecisionLog.__table__.c.confidence
        assert column is not None
        assert column.nullable is True

    def test_created_at_has_default(self) -> None:
        """Test created_at column has server default."""
        column = AgentDecisionLog.__table__.c.created_at
        assert column is not None
        assert column.server_default is not None

    def test_model_instantiation(self) -> None:
        """Test model can be instantiated."""
        log_entry = AgentDecisionLog(
            team_instance_id=1,
            agent_name="crash_detector",
            decision_type="warning",
            data={"crash_probability": 0.75},
            confidence=0.75,
        )

        assert log_entry.team_instance_id == 1
        assert log_entry.agent_name == "crash_detector"
        assert log_entry.decision_type == "warning"
        assert log_entry.data == {"crash_probability": 0.75}
        assert log_entry.confidence == 0.75

    def test_model_without_confidence(self) -> None:
        """Test model can be created without confidence."""
        log_entry = AgentDecisionLog(
            team_instance_id=1,
            agent_name="trader",
            decision_type="action",
            data={"order": {"symbol": "EURUSD", "side": "BUY"}},
        )

        assert log_entry.confidence is None

    def test_decision_types(self) -> None:
        """Test various decision types."""
        for decision_type in ["signal", "warning", "rejection", "override", "action"]:
            log_entry = AgentDecisionLog(
                team_instance_id=1,
                agent_name="test_agent",
                decision_type=decision_type,
                data={},
            )
            assert log_entry.decision_type == decision_type


class TestAgentDecisionLogIndexes:
    """Tests for database indexes."""

    def test_has_team_instance_id_index(self) -> None:
        """Test index on team_instance_id column."""
        indexes = list(AgentDecisionLog.__table__.indexes)
        index_columns = []
        for idx in indexes:
            index_columns.extend([c.name for c in idx.columns])
        assert "team_instance_id" in index_columns

    def test_has_created_at_index(self) -> None:
        """Test index on created_at column."""
        indexes = list(AgentDecisionLog.__table__.indexes)
        index_columns = []
        for idx in indexes:
            index_columns.extend([c.name for c in idx.columns])
        assert "created_at" in index_columns
