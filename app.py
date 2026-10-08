import json
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, url_for

from config import CAT, Config

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"

def countdown_remaining(now, end):
    remaining = max(end - now, timedelta(0))
    return {
        "end": end,
        "is_complete": now >= end,
        "days": remaining.days,
        "hours": remaining.seconds // 3600,
        "minutes": (remaining.seconds % 3600) // 60,
        "seconds": remaining.seconds % 60,
    }


def parse_member_markdown(text, source):
    if not text.startswith("---"):
        raise ValueError(f"{source} must start with a --- front matter block")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{source} is missing a closing --- for its front matter")

    fields = {}
    for line_number, line in enumerate(parts[1].splitlines(), start=2):
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise ValueError(f"{source}:{line_number} needs a key: value line")
        key, value = stripped.split(":", 1)
        fields[key.strip()] = value.strip()

    if "name" not in fields:
        raise ValueError(f"{source} needs a name")
    if "order" not in fields:
        raise ValueError(f"{source} needs an order")
    try:
        order = int(fields["order"])
    except ValueError as error:
        raise ValueError(f"{source} order must be a whole number") from error

    paragraphs = []
    for block in parts[2].strip().split("\n\n"):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if lines:
            paragraphs.append(" ".join(lines))
    bio = " ".join(paragraphs)
    if not bio:
        raise ValueError(f"{source} needs a bio under the front matter")

    return {
        "name": fields["name"],
        "role": fields.get("role", ""),
        "affiliation": fields.get("affiliation", ""),
        "bio": bio,
        "photo": fields.get("photo", ""),
        "linkedin": fields.get("linkedin", ""),
        "order": order,
    }


def load_markdown_collection(directory):
    members = []
    for path in directory.glob("*.md"):
        member = parse_member_markdown(path.read_text(encoding="utf-8"), path.name)
        members.append((member.pop("order"), path.name, member))
    members.sort()
    return [member for _, _, member in members]


def load_content(name):
    directory = CONTENT_DIR / name
    if directory.is_dir():
        return load_markdown_collection(directory)
    with open(CONTENT_DIR / f"{name}.json", encoding="utf-8") as handle:
        return json.load(handle)


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    @app.context_processor
    def inject_globals():
        export_depth = app.config.get("EXPORT_DEPTH")

        def asset(filename):
            path = Path(app.static_folder) / filename
            version = int(path.stat().st_mtime) if path.exists() else 0
            if export_depth is None:
                return url_for("static", filename=filename, v=version)
            prefix = "../" if export_depth == 1 else ""
            return f"{prefix}static/{filename}?v={version}"

        def href_for(endpoint):
            if export_depth is None:
                return url_for(endpoint)
            if export_depth == 1:
                return "../" if endpoint == "index" else "./"
            return "./" if endpoint == "index" else "about/"

        site_url = app.config["SITE_URL"] or request.url_root.rstrip("/")
        return {
            "asset": asset,
            "href_for": href_for,
            "export_depth": export_depth,
            "site_url": site_url,
            "config": app.config,
            "current_year": datetime.now(CAT).year,
        }

    @app.route("/")
    def index():
        countdown = countdown_remaining(datetime.now(CAT), app.config["COUNTDOWN_END"])
        return render_template("index.html", countdown=countdown)

    @app.route("/about")
    def about():
        return render_template("about.html", team=load_content("team"))

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    return app


app = create_app()
