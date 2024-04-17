from clayutil.futil import OsuPlaylist

oauth = "../osu.properties"
playlist = "./playlists/2000pp过关.properties"
o0 = OsuPlaylist(oauth)
font_difficulty = "../Kodchasan-Medium.ttf"
font_title = "../AlibabaPuHuiTi-3-65-Medium.ttf"
font_artist = "../AlibabaPuHuiTi-3-55-Regular.ttf"
font_mapped_by = "../Kodchasan-Italic.ttf"
font_mapper = "../Kodchasan-Medium.ttf"
o0.generate(playlist, font_difficulty, font_title, font_artist, font_mapped_by, font_mapper)
