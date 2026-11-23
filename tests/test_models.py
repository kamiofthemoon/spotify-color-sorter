from dataclasses import FrozenInstanceError

import pytest

from src.spotify.models import (
    Playlist,
    Track,
    pick_image_url,
    parse_track,
    parse_playlist,
)


def make_track(**changes) -> Track:
    """A valid Track; keyword arguments override fields."""
    fields = {
        "id": "t1",
        "uri": "spotify:track:t1",
        "name": "Song",
        "artists": ("Artist A", "Artist B"),
        "album_id": "a1",
        "album_name": "Album",
        "image_url": "https://i.scdn.co/image/x",
    }
    fields.update(changes)
    return Track(**fields)


def make_playlist(**changes) -> Playlist:
    """A valid Playlist; keyword arguments override fields."""
    fields = {
        "id": "p1",
        "name": "My playlist",
        "owner_id": "me",
        "collaborative": False,
        "track_count": 10,
        "image_url": None,
        "snapshot_id": "snap1",
    }
    fields.update(changes)
    return Playlist(**fields)


# Track


def test_track_keeps_its_fields():
    track = make_track()
    assert track.name == "Song"
    assert track.artists == ("Artist A", "Artist B")


def test_track_is_immutable():
    track = make_track()
    with pytest.raises(FrozenInstanceError):
        track.name = "Other"


def test_tracks_with_same_fields_are_equal():
    assert make_track() == make_track()
    assert make_track() != make_track(id="t2")


# Playlist


def test_owner_can_modify():
    assert make_playlist(owner_id="me").can_modify("me")


def test_other_owner_cannot_modify():
    assert not make_playlist(owner_id="someone").can_modify("me")


def test_collaborative_can_be_modified_by_others():
    playlist = make_playlist(owner_id="someone", collaborative=True)
    assert playlist.can_modify("me")


# pick_image_url

SPOTIFY_IMAGES = [
    {"url": "big", "width": 640},
    {"url": "medium", "width": 300},
    {"url": "small", "width": 64},
]


def test_pick_image_url_prefers_300px():
    assert pick_image_url(SPOTIFY_IMAGES) == "medium"


def test_pick_image_url_without_images():
    assert pick_image_url([]) is None
    assert pick_image_url(None) is None


def test_pick_image_url_with_missing_width():
    assert pick_image_url([{"url": "mosaic", "width": None}]) == "mosaic"


# parse_track


def api_track(**changes) -> dict:
    """A track object shaped like the real API response."""
    track = {
        "type": "track",
        "id": "t1",
        "uri": "spotify:track:t1",
        "name": "Song",
        "is_local": False,
        "is_playable": True,
        "artists": [{"name": "Artist A"}, {"name": "Artist B"}],
        "album": {"id": "a1", "name": "Album", "images": SPOTIFY_IMAGES},
    }
    track.update(changes)
    return track


def test_parse_liked_songs_item():
    track = parse_track({"added_at": "2026-01-01", "track": api_track()})
    assert track == make_track(image_url="medium")


def test_parse_playlist_item_uses_item_key():
    track = parse_track({"added_at": "2026-01-01", "item": api_track()})
    assert track.id == "t1"


def test_parse_track_skips_unusable_items():
    no_cover = {"id": "a1", "name": "Album", "images": []}
    assert parse_track(None) is None
    assert parse_track({"item": api_track(type="episode")}) is None
    assert parse_track({"item": api_track(is_local=True)}) is None
    assert parse_track({"item": api_track(is_playable=False)}) is None
    assert parse_track({"item": api_track(album=no_cover)}) is None


def test_parse_track_keeps_track_without_is_playable():
    track = api_track()
    del track["is_playable"]
    assert parse_track({"track": track}) is not None


# parse_playlist


def api_playlist(**changes) -> dict:
    """A playlist object shaped like the real API response."""
    playlist = {
        "id": "p1",
        "name": "My playlist",
        "owner": {"id": "me", "display_name": "Me"},
        "collaborative": False,
        "items": {"href": "https://api.spotify.com/v1/playlists/p1/items", "total": 10},
        "images": [],
        "snapshot_id": "snap1",
    }
    playlist.update(changes)
    return playlist


def test_parse_playlist():
    assert parse_playlist(api_playlist()) == make_playlist()


def test_parse_playlist_with_cover():
    playlist = parse_playlist(api_playlist(images=SPOTIFY_IMAGES))
    assert playlist.image_url == "medium"


def test_parse_playlist_reads_old_tracks_field():
    old = api_playlist(tracks={"total": 7})
    del old["items"]
    assert parse_playlist(old).track_count == 7


def test_parse_playlist_skips_null():
    assert parse_playlist(None) is None
