from dataclasses import FrozenInstanceError

import pytest

from src.spotify.models import Playlist, Track, pick_image_url


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
