#!/usr/bin/env python3
"""CLI script to create API keys."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.services.api_key import APIKeyService


def create_key(
    name: str,
    tier: str = "free",
    description: str | None = None,
    rate_limit: int = 100,
    rate_window: int = 60,
) -> None:
    """Create a new API key.

    Args:
        name: Key name
        tier: Access tier
        description: Optional description
        rate_limit: Rate limit
        rate_window: Rate window in seconds
    """
    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Create API key
        api_key, full_key = APIKeyService.create_api_key(
            db=db,
            name=name,
            tier=tier,
            description=description,
            created_by="CLI",
            rate_limit=rate_limit,
            rate_window=rate_window,
        )

        print("\n" + "=" * 60)
        print("API Key Created Successfully!")
        print("=" * 60)
        print(f"ID:           {api_key.id}")
        print(f"Name:         {api_key.name}")
        print(f"Tier:         {api_key.tier}")
        print(f"Rate Limit:   {api_key.rate_limit} requests per {api_key.rate_window}s")
        print("\n" + "-" * 60)
        print("IMPORTANT: Save this API key - it won't be shown again!")
        print("-" * 60)
        print(f"\n{full_key}\n")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"Error creating API key: {e}")
        sys.exit(1)
    finally:
        db.close()


def list_keys(include_inactive: bool = False) -> None:
    """List all API keys.

    Args:
        include_inactive: Include inactive keys
    """
    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        keys = APIKeyService.list_api_keys(db, include_inactive)

        if not keys:
            print("\nNo API keys found.\n")
            return

        print("\n" + "=" * 80)
        print("API Keys")
        print("=" * 80)
        print(
            f"{'ID':<5} {'Name':<20} {'Prefix':<12} {'Tier':<10} {'Active':<8} {'Rate Limit':<15}"
        )
        print("-" * 80)

        for key in keys:
            active = "Yes" if key.is_active else "No"
            rate_info = f"{key.rate_limit}/{key.rate_window}s"
            print(
                f"{key.id:<5} {key.name:<20} {key.key_prefix:<12} {key.tier:<10} {active:<8} {rate_info:<15}"
            )

        print("=" * 80 + "\n")

    except Exception as e:
        print(f"Error listing API keys: {e}")
        sys.exit(1)
    finally:
        db.close()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage API keys")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new API key")
    create_parser.add_argument("name", help="Name for the API key")
    create_parser.add_argument(
        "--tier",
        choices=["free", "premium", "admin"],
        default="free",
        help="Access tier (default: free)",
    )
    create_parser.add_argument("--description", help="Optional description")
    create_parser.add_argument(
        "--rate-limit", type=int, default=100, help="Rate limit (default: 100)"
    )
    create_parser.add_argument(
        "--rate-window",
        type=int,
        default=60,
        help="Rate window in seconds (default: 60)",
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List all API keys")
    list_parser.add_argument("--all", action="store_true", help="Include inactive keys")

    args = parser.parse_args()

    if args.command == "create":
        create_key(
            name=args.name,
            tier=args.tier,
            description=args.description,
            rate_limit=args.rate_limit,
            rate_window=args.rate_window,
        )
    elif args.command == "list":
        list_keys(include_inactive=args.all)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
