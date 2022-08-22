#!/usr/bin/python3
# -*- coding: utf-8 -*-


from utils import fix_filename, get_mp3_url


class Audio:
    def __init__(self, obj):
        self.url = None
        self.artist = obj.get('artist')
        self.title = obj.get('title')
        self.is_hq = False
        self.is_explicit = False
        self.content_restricted = None
        self.song_name = self.artist + ' - ' + self.title

        self.__dict__.update(obj)

    def get_filename(self) -> str:
        return f'{fix_filename(self.song_name)}.mp3'

    def get_url(self):
        return get_mp3_url(self.url)

    def __str__(self):
        return self.song_name
    
    def __repr__(self):
        return f"Audio<artist={self.artist}, title={self.title}, url={self.url}>"
