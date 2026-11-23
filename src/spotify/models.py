"""Data classes for Spotify objects and parsing of API responses."""

from dataclasses import dataclass

COVER_SIZE = 300  # preferred cover width (px)


@dataclass(frozen=True)
class Track:
    """A usable track: it has a cover and belongs to an album."""

    id: str
    uri: str
    name: str
    artists: tuple[str, ...]
    album_id: str
    album_name: str
    image_url: str  # cover closest to COVER_SIZE


@dataclass(frozen=True)
class Playlist:
    """A playlist from the user's library."""

    id: str
    name: str
    owner_id: str
    collaborative: bool
    track_count: int
    image_url: str | None
    snapshot_id: str

    def can_modify(self, user_id: str) -> bool:
        """True if the user owns the playlist or it is collaborative."""
        return self.owner_id == user_id or self.collaborative


def pick_image_url(images: list[dict] | None, size: int = COVER_SIZE) -> str | None:
    """Return the URL of the image whose width is closest to size, or None."""
    if not images:
        return None
    best = min(images, key=lambda image: abs((image.get("width") or 0) - size))
    return best["url"]


def parse_track(entry: dict | None) -> Track | None:
    """Build a Track from a Liked Songs or playlist item; None if unusable.

    Skips null items, podcast episodes, local files, unavailable tracks
    and tracks without a cover.
    """
    if not entry:
        return None
    track = entry.get("item") or entry.get("track")  # playlists use "item" since 2026
    if not track or track.get("type") != "track" or track.get("is_local"):
        return None
    if track.get("is_playable") is False:
        return None

    album = track.get("album") or {}
    image_url = pick_image_url(album.get("images"))
    if not image_url or not album.get("id"):
        return None

    return Track(
        id=track["id"],
        uri=track["uri"],
        name=track["name"],
        artists=tuple(artist["name"] for artist in track["artists"]),
        album_id=album["id"],
        album_name=album["name"],
        image_url=image_url,
    )
