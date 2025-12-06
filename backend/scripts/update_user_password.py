"""Script to check if user exists and update password."""

import asyncio
import sys
from pathlib import Path

# Add backend/src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from src.db.session import async_session_maker
from src.db.models import User
from src.services.auth import AuthService


async def main():
    username = "test@123login.de"
    new_password = "[A6z_`-!Pl)`G~["

    async with async_session_maker() as session:
        # Check if user exists
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if user is None:
            print(f"User '{username}' NOT FOUND in database.")
            print("\nExisting users:")
            all_users = await session.execute(select(User))
            users = all_users.scalars().all()
            if users:
                for u in users:
                    print(f"  - ID: {u.id}, Username: {u.username}")
            else:
                print("  (no users in database)")

            # Ask if we should create the user
            print(f"\nCreating user '{username}' with the specified password...")
            password_hash = AuthService.hash_password(new_password)
            new_user = User(username=username, password_hash=password_hash)
            session.add(new_user)
            await session.commit()
            print(f"User '{username}' created successfully!")
        else:
            print(f"User '{username}' FOUND (ID: {user.id})")
            print(f"Updating password...")

            # Update password
            password_hash = AuthService.hash_password(new_password)
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(password_hash=password_hash)
            )
            await session.commit()
            print(f"Password updated successfully for user '{username}'!")


if __name__ == "__main__":
    asyncio.run(main())
