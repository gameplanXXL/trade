"""Test script for performance aggregation functionality."""

import asyncio
import sys
from pathlib import Path

# Add backend src to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir / "src"))

from sqlalchemy import select

from src.db.models import PerformanceMetric, TeamInstance
from src.db.session import async_session_factory
from src.services.analytics import AnalyticsService


async def test_aggregation():
    """Test performance aggregation for all teams."""
    print("\n=== Testing Performance Aggregation ===\n")

    async with async_session_factory() as session:
        # Get all team instances
        stmt = select(TeamInstance)
        result = await session.execute(stmt)
        teams = result.scalars().all()

        print(f"Found {len(teams)} team instances\n")

        if not teams:
            print("No teams found. Create a team first.")
            return

        for team in teams:
            print(f"\nTeam: {team.name} (ID: {team.id})")
            print(f"  Status: {team.status.value}")
            print(f"  Mode: {team.mode.value}")
            print(f"  Budget: {team.current_budget}")
            print(f"  Realized P/L: {team.realized_pnl}")

            try:
                # Test aggregation
                analytics = AnalyticsService(session)
                metric = await analytics.aggregate_performance(
                    team_id=team.id, period="hourly"
                )

                print(f"\n  ✓ Aggregation successful!")
                print(f"    Metric ID: {metric.id}")
                print(f"    Timestamp: {metric.timestamp}")
                print(f"    Period: {metric.period}")
                print(f"    P/L: {metric.pnl}")
                print(f"    P/L %: {metric.pnl_percent:.2f}%")
                print(f"    Win Rate: {metric.win_rate:.2f}")
                print(f"    Sharpe Ratio: {metric.sharpe_ratio}")
                print(f"    Max Drawdown: {metric.max_drawdown:.2f}")
                print(f"    Trade Count: {metric.trade_count}")

                # Check if metric was saved
                check_stmt = select(PerformanceMetric).where(
                    PerformanceMetric.id == metric.id
                )
                check_result = await session.execute(check_stmt)
                saved_metric = check_result.scalar_one_or_none()

                if saved_metric:
                    print(f"\n  ✓ Metric saved to database")
                else:
                    print(f"\n  ✗ Metric NOT found in database")

            except Exception as e:
                print(f"\n  ✗ Aggregation failed: {e}")
                import traceback

                traceback.print_exc()

        # Show total metrics in database
        count_stmt = select(PerformanceMetric)
        count_result = await session.execute(count_stmt)
        all_metrics = count_result.scalars().all()

        print(f"\n=== Summary ===")
        print(f"Total performance metrics in database: {len(all_metrics)}")

        if all_metrics:
            print("\nRecent metrics:")
            for metric in all_metrics[-5:]:  # Show last 5
                print(
                    f"  - Team {metric.team_instance_id}, {metric.period}, "
                    f"{metric.timestamp}, P/L: {metric.pnl}"
                )


if __name__ == "__main__":
    asyncio.run(test_aggregation())
