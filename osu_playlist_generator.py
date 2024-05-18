import os
import re
import shutil

from clayutil.futil import OsuPlaylist


fast_gen = True
oauth = "../osu.properties"
original_playlist_pattern = re.compile(r"O\.(.*)\.properties")
match_playlist_pattern = re.compile(r"M\.(.*)\.properties")
skill_practice_pattern = re.compile(r"SP\.(.*)\.properties")
o0 = OsuPlaylist(oauth)
font = "../unifont-15.1.05.otf"
for i in os.listdir("./playlists"):
    if m := original_playlist_pattern.match(i):
        o0.draw_target = True
        o0.draw_difficulty_table = False
        suffix = " — original playlist"
    elif m := match_playlist_pattern.match(i):
        suffix = " — match playlist"
        o0.draw_target = False
        o0.draw_difficulty_table = True
    elif m := skill_practice_pattern.match(i):
        suffix = " — original skill practice playlist"
        o0.draw_target = False
        o0.draw_difficulty_table = True
    else:
        continue
    if os.path.exists("./playlists/%s.html" % m.group(1)) and fast_gen:
        print("skipped %s" % m.group(1))
        continue
    try:
        shutil.copyfile("./playlists/%s" % m.group(0), "./playlists/%s.properties" % m.group(1))
        o0.generate("./playlists/%s.properties" % m.group(1), font, suffix)
    except:
        raise
    else:
        print("generated %s" % m.group(1))
    finally:
        os.remove("./playlists/%s.properties" % m.group(1))
