"""
Command Line Interface

CLI tool for OneTimeSecret management.
"""

import asyncio
from typing import Optional

import click


@click.group()
@click.version_option(version="3.0.0")
def main():
    """OneTimeSecret CLI - Manage secrets from the command line."""
    pass


@main.command()
@click.option(
    "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
)
@click.option("--port", default=8000, type=int, help="Port to bind to (default: 8000)")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option("--workers", default=4, type=int, help="Number of worker processes (default: 4)")
def serve(host: str, port: int, reload: bool, workers: int):
    """Start the OneTimeSecret server."""
    import uvicorn

    click.echo(f"Starting OneTimeSecret server on {host}:{port}")

    uvicorn.run(
        "onetimesecret.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
    )


@main.command()
def generate_key():
    """Generate a new secret key for configuration."""
    import secrets

    key = secrets.token_hex(32)
    click.echo("\nGenerated secret key:")
    click.echo(f"SECRET_KEY={key}")
    click.echo("\nAdd this to your .env file")


@main.command()
@click.option("--db-url", help="Database URL (optional, uses config if not provided)")
def init_db(db_url: Optional[str]):
    """Initialize the database schema."""
    from onetimesecret.db import init_db as _init_db

    if db_url:
        # Override database URL temporarily
        import os

        os.environ["DATABASE_URL"] = db_url

    click.echo("Initializing database...")
    asyncio.run(_init_db())
    click.echo("Database initialized successfully!")


@main.command()
def create_migration():
    """Create a new database migration."""
    import subprocess

    click.echo("Creating new migration...")
    subprocess.run(["alembic", "revision", "--autogenerate"])


@main.command()
def migrate():
    """Run database migrations."""
    import subprocess

    click.echo("Running migrations...")
    subprocess.run(["alembic", "upgrade", "head"])


if __name__ == "__main__":
    main()
