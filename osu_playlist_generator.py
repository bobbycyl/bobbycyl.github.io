from clayutil.futil import OsuPlaylist

oauth = "../osu.properties"
normal_playlists = [
    "./playlists/2000pp过关.properties",
]
match_playlists = [
    "./playlists/HSC3S1R1.properties",
]
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
