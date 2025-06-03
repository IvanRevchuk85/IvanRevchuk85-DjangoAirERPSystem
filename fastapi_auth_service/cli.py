from sqlalchemy import create_engine
from fastapi_auth_service.app.database import Base
from dotenv import load_dotenv
import typer
from fastapi_auth_service.app.core.settings import settings


# Create a Typer Application
app = typer.Typer()

# Loading environment variables
load_dotenv()

# Building a Synchronous URL for the CLI
SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# Synchronous Engine for CLI
sync_engine = create_engine(SYNC_DATABASE_URL)


@app.command("create-db")
def create_db():
    """
    Create all tables in the database.
    """
    try:
        # Create all tables according to Base.metadate
        Base.metadata.create_all(bind=sync_engine)
        typer.echo("✅ The database has been successfully created..")
    except Exception as e:
        typer.echo(f"❌ Error creating database: {e}")


@app.command("drop-db")
def drop_db():
    """
    💣 Removing all tables from the database.
    """
    try:
        # Delete all tables
        Base.metadata.drop_all(bind=sync_engine)
        typer.echo("✅ The database has been deleted successfully..")
    except Exception as e:
        typer.echo(f"❌ Database deletion error: {e}")


# Сwe start the application if we launched this file directly
if __name__ == "__main__":
    app()
