"""Spotify login with Authorization Code + PKCE (no client secret)."""

import os

import spotipy
from dotenv import load_dotenv

SCOPES = " ".join(
    [
        "user-library-read",
        "playlist-read-private",
        "playlist-read-collaborative",
        "playlist-modify-private",
        "playlist-modify-public",
    ]
)


def create_spotify():
    """Return an authenticated spotipy client; the token is cached in .cache."""
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    if not client_id or not redirect_uri:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID or SPOTIFY_REDIRECT_URI in .env")

    auth = spotipy.SpotifyPKCE(
        client_id=client_id, redirect_uri=redirect_uri, scope=SCOPES
    )
    return spotipy.Spotify(auth_manager=auth)
