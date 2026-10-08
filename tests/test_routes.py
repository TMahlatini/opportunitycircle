from datetime import datetime

import pytest

from app import create_app, load_content, parse_member_markdown
from config import CAT, Config


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_index_renders_countdown(client):
    response = client.get("/")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert Config.COUNTDOWN_END.isoformat() in html
    assert 'id="verify"' in html
    assert 'data-countdown' in html
    assert "11 Dec 2026" in html
    assert 'action="https://buttondown.com/api/emails/embed-subscribe/opportunitycircle"' in html
    assert 'id="bd-email"' in html
    assert "one time newsletter detailing our findings and solution" in html


def test_about_renders_six_team_cards(client):
    response = client.get("/about")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert html.count('class="photo"') == 6


def test_unknown_route_returns_custom_404(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert "outside the circle" in response.get_data(as_text=True)


def test_countdown_runs_through_11_dec():
    assert Config.LAUNCH_DAY == datetime(2026, 12, 11, tzinfo=CAT)
    assert Config.COUNTDOWN_END == datetime(2026, 12, 12, tzinfo=CAT)


def test_content_files_are_complete():
    team = load_content("team")
    assert [member["name"] for member in team] == [
        "Terence Mahlatini",
        "Woopi Takarasima",
        "Ruvarashe Mbizvo",
        "Gerald Munetsi",
        "Fidelity Ndali",
        "Candace Tariro Hunzwi",
    ]
    assert all({"name", "role", "bio", "photo", "linkedin"} <= member.keys() for member in team)
    assert all("order" not in member for member in team)
    assert team[0]["linkedin"] == "https://www.linkedin.com/in/terence-mahlatini"
    assert "Whitman College" in team[0]["bio"]


def test_member_markdown_joins_wrapped_lines():
    member = parse_member_markdown(
        """---
name: Ada Lovelace
role: Role to be announced
photo:
linkedin: https://www.linkedin.com/in/ada
order: 4
---

First line
still the same paragraph.

Second paragraph.
""",
        "ada.md",
    )
    assert member["linkedin"] == "https://www.linkedin.com/in/ada"
    assert member["photo"] == ""
    assert member["affiliation"] == ""
    assert member["bio"] == "First line still the same paragraph. Second paragraph."
    assert member["order"] == 4
