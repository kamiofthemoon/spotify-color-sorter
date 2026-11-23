"""Save real Spotify API responses as JSON samples for parsing and tests.

Run from the project root:
    python -m scripts.dump_samples
"""

import json
from pathlib import Path

from src.spotify.auth import create_spotify

OUT_DIR = Path("data/samples")
SAMPLE_PLAYLIST = "samples"  # playlist with edge cases (podcast, local file)


def save(name, data):
    """Write data to data/samples/<name>.json."""
    path = OUT_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {path}")


def main():
    """Dump Liked Songs, playlists and the items of one owned playlist."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sp = create_spotify()
    user_id = sp.current_user()["id"]

    save("liked_tracks", sp.current_user_saved_tracks(limit=5))

    playlists = sp.current_user_playlists(limit=20)
    save("playlists", playlists)

    owned = [p for p in playlists["items"] if p and p["owner"]["id"] == user_id]
    sample = [p for p in owned if p["name"] == SAMPLE_PLAYLIST] or owned[:1]
    if sample:
        save("playlist_items", sp.playlist_items(sample[0]["id"], limit=20))


if __name__ == "__main__":
    main()
