"""Quick check of the Spotify Web API access (Development Mode).

Checks: login (PKCE), reading Liked Songs with covers, listing playlists
and creating a private playlist.

Run from the project root:
    python scripts/smoke_test.py
"""

import os
import sys

import spotipy
from dotenv import load_dotenv

SCOPES = "user-library-read playlist-read-private playlist-modify-private"


def main():
    """Run the checks one after another."""
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    if not client_id or not redirect_uri:
        sys.exit("Missing SPOTIFY_CLIENT_ID or SPOTIFY_REDIRECT_URI in .env")

    auth = spotipy.SpotifyPKCE(
        client_id=client_id, redirect_uri=redirect_uri, scope=SCOPES
    )
    sp = spotipy.Spotify(auth_manager=auth)

    me = sp.current_user()
    print(f"Logged in as: {me['display_name']} ({me['id']})")

    saved = sp.current_user_saved_tracks(limit=5)
    print(f"Liked Songs: {saved['total']} tracks")
    for entry in saved["items"]:
        track = entry["track"]
        images = track["album"]["images"]
        url = images[0]["url"] if images else "no cover"
        artists = ", ".join(a["name"] for a in track["artists"])
        print(f"  - {track['name']} | {artists} | {url}")

    playlists = sp.current_user_playlists(limit=5)
    print(f"Playlists: {playlists['total']}")

    # spotipy still uses the removed POST /users/{id}/playlists
    created = sp._post(  # pylint: disable=protected-access
        "me/playlists",
        payload={"name": "smoke test - can be deleted", "public": False},
    )
    print(f"Created playlist: {created['external_urls']['spotify']}")


if __name__ == "__main__":
    try:
        main()
        print("OK: Spotify connection works.")
    except spotipy.SpotifyException as err:
        # 401: bad token, 403: user not in the allowlist or missing scope
        sys.exit(f"Spotify error {err.http_status}: {err.msg}")
