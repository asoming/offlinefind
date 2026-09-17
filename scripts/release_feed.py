"""Create a small public update feed from already-published GitHub releases."""

import json
import sys
from pathlib import Path


def main():
    source, target = map(Path, sys.argv[1:])
    releases = json.loads(source.read_text(encoding="utf-8"))
    feed = []
    for release in releases:
        if release.get("draft") or not release.get("published_at"):
            continue
        item = {key: release[key] for key in ("tag_name", "prerelease", "published_at")}
        item["body"] = (release.get("body") or "")[:16000]
        item["assets"] = [
            {
                key: asset.get(key)
                for key in ("name", "size", "state", "digest", "browser_download_url")
            }
            for asset in release.get("assets", [])
        ]
        feed.append(item)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
