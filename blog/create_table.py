import click
from flask.cli import with_appcontext

from . import db
from models import Entry


@click.command(name="create_tables")
@with_appcontext
def create_tables():
    db.create_all()