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
