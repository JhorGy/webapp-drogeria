from flask import template_rendered
#from farmaciaCJJJ import create_app
from app import create_app
import app
import pytest

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def test_client(app):
    return app.test_client()


@pytest.fixture()
def test_runner(app):
    return app.test_cli_runner()

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)
