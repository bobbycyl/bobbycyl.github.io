from clayutil.futil import OsuPlaylist

oauth = "../osu.properties"
normal_playlists = [
    "./playlists/2000pp过关.properties"
]
match_playlists = [
    "./playlists/HSC3S1R1.properties"
]
o0 = OsuPlaylist(oauth)
font_difficulty = "../Kodchasan-Medium.ttf"
font_title = "../AlibabaPuHuiTi-3-75-SemiBold.ttf"
font_artist = "../AlibabaPuHuiTi-3-55-Regular.ttf"
font_mapped_by = "../Kodchasan-Italic.ttf"
font_mapper = "../Kodchasan-SemiBold.ttf"
font_mono = "../HackNerdFontMono-Bold.ttf"
for playlist in normal_playlists:
    o0.draw_target = True
    o0.draw_difficulty_table = False
    o0.generate(playlist, font_difficulty, font_title, font_artist, font_mapped_by, font_mapper, font_mono)
for playlist in match_playlists:
    o0.draw_target = False
    o0.draw_difficulty_table = True
    o0.generate(playlist, font_difficulty, font_title, font_artist, font_mapped_by, font_mapper, font_mono)
