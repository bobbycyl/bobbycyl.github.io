from clayutil.futil import OsuPlaylist

oauth = "../osu.properties"
playlist = "./playlists/2000pp过关.properties"
o0 = OsuPlaylist(oauth, True, False)
font_difficulty = "../Kodchasan-Medium.ttf"
font_title = "../AlibabaPuHuiTi-3-75-SemiBold.ttf"
font_artist = "../AlibabaPuHuiTi-3-55-Regular.ttf"
font_mapped_by = "../Kodchasan-Italic.ttf"
font_mapper = "../Kodchasan-SemiBold.ttf"
font_mono = "../HackNerdFontMono-Bold.ttf"
o0.generate(playlist, font_difficulty, font_title, font_artist, font_mapped_by, font_mapper, font_mono)
