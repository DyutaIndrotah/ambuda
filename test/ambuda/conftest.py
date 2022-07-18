import pytest
from flask_login import FlaskLoginClient

import ambuda.database as db
from ambuda import create_app
from ambuda.queries import get_engine, get_session


def initialize_test_db():
    engine = get_engine()
    assert ":memory:" in engine.url

    db.Base.metadata.drop_all(engine)
    db.Base.metadata.create_all(engine)

    session = get_session()

    # Text and parse data
    text = db.Text(slug="pariksha", title="parIkSA")
    session.add(text)
    session.flush()

    section = db.TextSection(text_id=text.id, slug="1", title="adhyAyaH 1")
    session.add(section)
    session.flush()

    block = db.TextBlock(
        text_id=text.id, section_id=section.id, slug="1.1", xml="<div>agniH</div>", n=1
    )
    session.add(block)
    session.flush()

    parse = db.BlockParse(
        text_id=text.id, block_id=block.id, data="agniH\tagni\tpos=n,g=m,c=1,n=s"
    )
    session.add(parse)

    # Dictionaries
    dictionary = db.Dictionary(slug="test-dict", title="Test Dictionary")
    session.add(dictionary)
    session.flush()

    dictionary_entry = db.DictionaryEntry(
        dictionary_id=dictionary.id, key="agni", value="<div>fire</div>"
    )
    session.add(dictionary_entry)

    # Auth
    user = db.User(username="rama", email="rama@ayodhya.com")
    user.set_password("sita")
    session.add(user)
    session.flush()

    # Proofreading
    project = db.Project(slug="test-project", title="Test Project")
    session.add(project)
    session.flush()

    page = db.Page(project_id=project.id, slug="1", order=1)
    session.add(page)

    session.commit()


@pytest.fixture(scope="session")
def flask_app():
    app = create_app("testing")
    app.config.update({"TESTING": True})
    app.test_client_class = FlaskLoginClient

    with app.app_context():
        initialize_test_db()

    yield app


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


@pytest.fixture()
def rama_client(flask_app):
    session = get_session()
    user = session.query(db.User).filter_by(username="rama").first()
    with flask_app.test_client(user=user) as client:
        yield client
