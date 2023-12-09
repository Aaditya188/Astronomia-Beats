import random
from typing import Optional
from collections import deque

from discord import Embed

from config import config
from musicbot.utils import StrEnum
from musicbot.songinfo import Song


LoopMode = StrEnum("LoopMode", config.get_dict("LoopMode"))
LoopState = StrEnum("LoopState", config.get_dict("LoopState"))
PauseState = StrEnum("PauseState", config.get_dict("PauseState"))
PlaylistErrorText = StrEnum(
    "PlaylistErrorText", config.get_dict("PlaylistError")
)


class PlaylistError(Exception):
    pass


class Playlist:
    """Stores the youtube links of songs to be played and already played
    Offers basic operation on the queues"""

    def __init__(self):
        # Stores the links os the songs in queue and the ones already played
        self.playque: deque[Song] = deque()
        self.playhistory: deque[Song] = deque()

        # A seperate history that remembers
        # the names of the tracks that were played
        self.trackname_history: deque[str] = deque()

        self.loop = LoopMode.OFF

    def __len__(self):
        return len(self.playque)

    def add_name(self, trackname: str):
        self.trackname_history.append(trackname)
        if len(self.trackname_history) > config.MAX_TRACKNAME_HISTORY_LENGTH:
            self.trackname_history.popleft()

    def add(self, track: Song):
        self.playque.append(track)

    def has_next(self) -> bool:
        return len(self.playque) >= (2 if self.loop != LoopMode.ALL else 1)

    def has_prev(self) -> bool:
        return (
            len(
                self.playhistory if self.loop != LoopMode.ALL else self.playque
            )
            != 0
        )

    def next(self, ignore_single_loop=False) -> Optional[Song]:
        if len(self.playque) == 0:
            return None

        if self.loop == LoopMode.OFF or (
            ignore_single_loop and self.loop == LoopMode.SINGLE
        ):
            self.playhistory.append(self.playque.popleft())
            if len(self.playhistory) > config.MAX_HISTORY_LENGTH:
                self.playhistory.popleft()
            if len(self.playque) != 0:
                return self.playque[0]
            else:
                return None

        if self.loop == LoopMode.ALL:
            self.playque.rotate(-1)

        return self.playque[0]

    def prev(self) -> Optional[Song]:
        if self.loop != LoopMode.ALL:
            if len(self.playhistory) != 0:
                song = self.playhistory.pop()
                self.playque.appendleft(song)
                return song
            else:
                return None

        if len(self.playque) == 0:
            return None

        self.playque.rotate()

        return self.playque[0]

    def shuffle(self):
        first = self.playque.popleft()
        random.shuffle(self.playque)
        self.playque.appendleft(first)

    def clear(self):
        if self.playque:
            first = self.playque.popleft()
            self.playque.clear()
            self.playque.appendleft(first)

    def _check_and_get(self, index: int) -> Song:
        """Checks if song at `index` can be moved
        Returns the song or raises PlaylistError with description"""
        if index < 0:
            raise PlaylistError(PlaylistErrorText.NEGATIVE_INDEX)
        if index == 0:
            raise PlaylistError(PlaylistErrorText.ZERO_INDEX)
        try:
            return self.playque[index]
        except IndexError as e:
            raise PlaylistError(PlaylistErrorText.MISSING_INDEX) from e

    def remove(self, index: int) -> Song:
        song = self._check_and_get(index)
        del self.playque[index]
        return song

    def move(self, oldindex: int, newindex: int):
        song = self._check_and_get(oldindex)
        self._check_and_get(newindex)
        del self.playque[oldindex]
        self.playque.insert(newindex, song)

    def empty(self):
        self.playque.clear()
        self.playhistory.clear()

    def queue_embed(self) -> Embed:
        embed = Embed(
            title=config.QUEUE_TITLE.format(tracks_number=len(self.playque)),
            color=config.EMBED_COLOR,
        )

        for counter, song in enumerate(
            list(self.playque)[: config.MAX_SONG_PRELOAD], start=1
        ):
            embed.add_field(
                name="{}.".format(str(counter)),
                value="[{}]({})".format(
                    song.info.title
                    or song.info.webpage_url.partition("://")[2],
                    song.info.webpage_url,
                ),
                inline=False,
            )

        return embed
