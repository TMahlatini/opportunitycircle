import shutil
from pathlib import Path

from app import create_app, load_content

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
STATIC_FILES = (
    "css/main.css",
    "js/main.js",
    "img/favicon.svg",
    "img/og-image.png",
)
PAGES = (
    ("/", "index.html", 0),
    ("/about", "about/index.html", 1),
    ("/does-not-exist", "404.html", "404"),
)


def freeze(app=None, destination=DOCS):
    app = app or create_app()
    client = app.test_client()
    if destination.exists():
        shutil.rmtree(destination)

    for route, relative, depth in PAGES:
        app.config["EXPORT_DEPTH"] = depth
        response = client.get(route)
        expected = 404 if depth == "404" else 200
        if response.status_code != expected:
            raise RuntimeError(f"{route} returned {response.status_code}")
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(response.get_data(as_text=True), encoding="utf-8")

    static_out = destination / "static"
    for name in STATIC_FILES:
        source = ROOT / "static" / name
        dest = static_out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    for member in load_content("team"):
        photo = member["photo"]
        if not photo:
            continue
        source = ROOT / "static" / "img" / "team" / photo
        if not source.is_file():
            raise RuntimeError(f"missing headshot {source.name}")
        dest = static_out / "img" / "team" / photo
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    (destination / ".nojekyll").write_text("", encoding="utf-8")
    return destination


if __name__ == "__main__":
    freeze()
