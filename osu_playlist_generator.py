import os
import re

from clayutil.futil import OsuPlaylist


oauth = "../osu.properties"
original_playlist_pattern = re.compile(r"o\..*\.properties")
match_playlist_pattern = re.compile(r"m\..*\.properties")
normal_playlists = []
match_playlists = []
for i in os.listdir("./playlists"):
    if original_playlist_pattern.match(i):
        normal_playlists.append("./playlists/%s" % i)
    if match_playlist_pattern.match(i):
        match_playlists.append("./playlists/%s" % i)
o0 = OsuPlaylist(oauth)
font = "../unifont-15.1.05.otf"
for playlist in normal_playlists:
    o0.draw_target = True
    o0.draw_difficulty_table = False
    o0.generate(playlist, font)
for playlist in match_playlists:
    o0.draw_target = False
    o0.draw_difficulty_table = True
    o0.generate(playlist, font)
