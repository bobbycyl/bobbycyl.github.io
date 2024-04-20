import os
import re
import shutil

from clayutil.futil import OsuPlaylist


oauth = "../osu.properties"
original_playlist_pattern = re.compile(r"O\.(.*\.properties)")
match_playlist_pattern = re.compile(r"M\.(.*\.properties)")
o0 = OsuPlaylist(oauth)
font = "../unifont-15.1.05.otf"
for i in os.listdir("./playlists"):
    if m := original_playlist_pattern.match(i):
        shutil.copyfile("./playlists/%s" % m.group(0), "./playlists/%s" % m.group(1))
        o0.draw_target = True
        o0.draw_difficulty_table = False
        o0.generate("./playlists/%s" % m.group(1), font, " — original playlist")
        os.remove("./playlists/%s" % m.group(1))
    if m := match_playlist_pattern.match(i):
        shutil.copyfile("./playlists/%s" % m.group(0), "./playlists/%s" % m.group(1))
        o0.draw_target = False
        o0.draw_difficulty_table = True
        o0.generate("./playlists/%s" % m.group(1), font, " — match playlist")
        os.remove("./playlists/%s" % m.group(1))
