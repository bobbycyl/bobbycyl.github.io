import os
import re
import shutil
import zipfile

import pandas as pd
import rosu_pp_py as rosu
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, UnidentifiedImageError
from clayutil.futil import Downloader, Properties
from ossapi import Ossapi


class OsuPlaylist(object):
    headers = {
        "Referer": "https://bobbycyl.github.io/playlists/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    }
    split_pattern = re.compile(r"(.*) \[(.*)] \((.*)\)")
    mod_color = {"NM": "#1050eb", "HD": "#ebb910", "HR": "#eb4040", "EZ": "#40b940", "DT": "#b910eb", "FM": "#40507f", "TB": "#7f4050"}
    target_color = [("brown", "orange"), ("gray", "silver"), ("gold", "yellow")]
    mods = {"NM": 0, "HD": 8, "HR": 16, "EZ": 2, "DT": 64}

    def __init__(self, oauth_filename: str, draw_target: bool = False, draw_difficulty_table: bool = True):
        p = Properties(oauth_filename)
        p.load()
        self.__api = Ossapi(p["client_id"], p["client_secret"])
        self.draw_target: bool = draw_target
        self.draw_difficulty_table: bool = draw_difficulty_table

    def _draw_mod_tags(self, mods, draw, font):
        for i in range(len(mods)):
            draw.rounded_rectangle((1774 - 118 * i, 34, 1874 - 118 * i, 95.8), 12, fill="#303030", width=0)
            draw.rounded_rectangle((1772 - 118 * i, 32, 1872 - 118 * i, 93.8), 12, fill=self.mod_color[mods[len(mods) - i - 1]], width=0)
            draw.text((1802 - 118 * i, 39), mods[len(mods) - i - 1], font=ImageFont.truetype(font=font, size=48), fill="#1f1f1f")
            draw.text((1797 - 118 * i, 36), mods[len(mods) - i - 1], font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((1798 - 118 * i, 36), mods[len(mods) - i - 1], font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((1799 - 118 * i, 36), mods[len(mods) - i - 1], font=ImageFont.truetype(font=font, size=48), fill="white")

    def _draw_target_badges(self, targets, draw, font):
        for i in range(len(targets)):
            draw.rounded_rectangle((1860, 278 - 74 * i, 1871, 334 - 74 * i), 36, fill=self.target_color[i][0], width=0)
            draw.rounded_rectangle((1859, 276 - 74 * i, 1869, 332 - 74 * i), 36, fill=self.target_color[i][1], width=0)
            draw.text((1590, 282 - 74 * i), targets[i], font=ImageFont.truetype(font=font, size=44), fill=(40, 40, 40))
            draw.text((1589, 280 - 74 * i), targets[i], font=ImageFont.truetype(font=font, size=44), fill="white")
            draw.text((1588, 280 - 74 * i), targets[i], font=ImageFont.truetype(font=font, size=44), fill="white")

    def _calc_difficulty(self, osu, mods):
        if "EZ" in mods and "HR" in mods:
            raise ValueError("EZ and HR are mutually exclusive")
        if "NM" in mods and len(mods) > 1:
            raise ValueError("NM is mutually exclusive with other mods")
        if "FM" in mods and len(mods) > 1:
            raise ValueError("FM is mutually exclusive with other mods")
        if "TB" in mods and len(mods) > 1:
            raise ValueError("TB is mutually exclusive with other mods")

        map = rosu.Beatmap(path=osu)
        res: dict[str, float | int | str] = {
            "CS": map.cs,
            "HP": map.hp,
            "OD": map.od,
            "AR": map.ar,
            "BPM": map.bpm,
        }
        if "HR" in mods:
            res["CS"] *= 1.3
        if "DT" in mods:
            res["BPM"] *= 1.5
        if "EZ" in mods:
            res["CS"] += 0.5
        res["CS"] = round(res["CS"], 2)
        res["BPM"] = round(res["BPM"], 2)

        diff = rosu.Difficulty(mods=sum(self.mods.get(i, 0) for i in mods))
        diff_attr = diff.calculate(map)
        if diff_attr.hp is not None:
            res["HP"] = round(diff_attr.hp, 2)
        if diff_attr.od is not None:
            res["OD"] = round(diff_attr.od, 2)
        if diff_attr.ar is not None:
            res["AR"] = round(diff_attr.ar, 2)
        res["Max Combo"] = diff_attr.max_combo
        res["Stars"] = round(diff_attr.stars, 2)
        
        if "FM" in mods:
            extra = self._calc_difficulty(osu, ["HR"])
            res["Stars"] = "%s(%s)" % (res["Stars"], extra["Stars"])

        return res

    def generate(self, playlist_filename: str, font, suffix: str = ""):
        """生成课题

        :param playlist_filename: 课题源文件
        :param font: 字体
        :param suffix: 标题前缀
        """
        p = Properties(playlist_filename)
        p.load()
        playlist_raw = [int(x) for x in (p.keys())]
        beatmap_list = self.__api.beatmaps(playlist_raw)

        playlist: list[dict] = []

        output_dir = playlist_filename.replace(".properties", "") + ".covers"
        tmp_dir = playlist_filename.replace(".properties", "") + ".osus"
        d = Downloader(output_dir)
        tmp_d = Downloader(tmp_dir)
        for b in beatmap_list:
            i = playlist_raw.index(b.id) + 1
            t0, t1, t2, t3 = b.version, b.beatmapset().title_unicode, b.beatmapset().artist_unicode, b.beatmapset().creator
            m = self.split_pattern.match(str(p[str(b.id)]))
            notes = m.group(3)

            cover_filename = "%d-%d.jpg" % (i, b.id)
            cover = d.start(b.beatmapset().covers.slimcover, cover_filename)
            try:
                im = Image.open(cover)
            except UnidentifiedImageError:
                try:
                    im = Image.open(d.start(b.beatmapset().covers.cover, cover_filename))
                except UnidentifiedImageError:
                    im = Image.open("./bg1.jpg")  # 使用默认图片
                    im = im.filter(ImageFilter.BLUR)
                im = im.resize((1920, int(im.height * 1920 / im.width)), Image.LANCZOS)  # 缩放到宽为1920
                im = im.crop((im.width // 2 - 960, 0, im.width // 2 + 960, 360))  # 从中间裁剪到1920x360

            be = ImageEnhance.Brightness(im)
            im = be.enhance(0.25)
            draw = ImageDraw.Draw(im)
            title_len = draw.textlength(t1, font=ImageFont.truetype(font=font, size=72))
            if title_len > 1416:
                cut_length = -1
                while True:
                    t1_cut = t1[:cut_length] + "..."
                    title_len = draw.textlength(t1_cut, font=ImageFont.truetype(font=font, size=72))
                    if title_len <= 1416:
                        break
                    cut_length -= 1
                t1 = t1_cut
            draw.text((42, 19), t0, font=ImageFont.truetype(font=font, size=48), fill="#1f1f1f")
            draw.text((40, 16), t0, font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((41, 16), t0, font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((40, 17), t0, font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((41, 17), t0, font=ImageFont.truetype(font=font, size=48), fill="white")
            draw.text((42, 132), t1, font=ImageFont.truetype(font=font, size=72), fill="#1f1f1f")
            draw.text((42, 131), t1, font=ImageFont.truetype(font=font, size=72), fill="#1f1f1f")
            draw.text((40, 129), t1, font=ImageFont.truetype(font=font, size=72), fill="white")
            draw.text((41, 129), t1, font=ImageFont.truetype(font=font, size=72), fill="white")
            draw.text((40, 130), t1, font=ImageFont.truetype(font=font, size=72), fill="white")
            draw.text((41, 130), t1, font=ImageFont.truetype(font=font, size=72), fill="white")
            draw.text((41, 218), t2, font=ImageFont.truetype(font=font, size=44), fill="#1f1f1f")
            draw.text((40, 216), t2, font=ImageFont.truetype(font=font, size=44), fill="white")
            draw.text((41, 292), "mapped by", font=ImageFont.truetype(font=font, size=36), fill="#1f1f1f")
            draw.text((40, 290), "mapped by", font=ImageFont.truetype(font=font, size=36), fill="white")
            draw.text((221, 292), t3, font=ImageFont.truetype(font=font, size=36), fill="#1f1f2a")
            draw.text((220, 290), t3, font=ImageFont.truetype(font=font, size=36), fill=(180, 235, 250))
            draw.text((219, 290), t3, font=ImageFont.truetype(font=font, size=36), fill=(180, 235, 250))
            if len(m.group(1)):
                self._draw_mod_tags(m.group(1).split(" "), draw, font)
            original_beatmap_info = """
+---------------------------+
|    Original Difficulty    |
+---------------------------+
| Star  %-19.2f |
| CS  %-8.2f HP  %-8.2f |
| AR  %-8.2f OD  %-8.2f |
| BPM %-8.2f LEN %-8d |
+---------------------------+
""" % (
                b.difficulty_rating,
                b.cs,
                b.drain,
                b.ar,
                b.accuracy,
                b.bpm,
                b.hit_length,
            )
            if self.draw_target:
                targets = m.group(2).split("/")
                self._draw_target_badges(targets, draw, font)
            if self.draw_difficulty_table:
                draw.multiline_text((1470, 82), original_beatmap_info, font=ImageFont.truetype(font=font, size=28), fill="#1f1f1f")
                draw.multiline_text((1469, 80), original_beatmap_info, font=ImageFont.truetype(font=font, size=28), fill=(235, 235, 235))
                draw.multiline_text((1468, 80), original_beatmap_info, font=ImageFont.truetype(font=font, size=28), fill=(235, 235, 235))
            im.save(cover)

            img_src = "./" + (os.path.relpath(os.path.join(output_dir, cover_filename), os.path.split(playlist_filename)[0])).replace("\\", "/")
            img_link = "https://osu.ppy.sh/beatmapsets/%d#%s/%d" % (b.beatmapset_id, b.mode.value, b.id)

            beatmapset_filename = tmp_d.start("https://dl.sayobot.cn/beatmaps/download/mini/%s" % b.beatmapset_id)
            beatmapset_dir = os.path.join(tmp_dir, str(b.beatmapset_id))
            with zipfile.ZipFile(beatmapset_filename, "r") as zipf:
                zipf.extractall(beatmapset_dir)
            if os.path.exists(os.path.join(beatmapset_dir, "mini/")):
                beatmapset_dir = os.path.join(beatmapset_dir, "mini/")
            if os.path.exists(os.path.join(beatmapset_dir, str(b.beatmapset_id))):
                beatmapset_dir = os.path.join(beatmapset_dir, str(b.beatmapset_id))
            found_beatmap_filename = ""
            if "%s - %s (%s) [%s].osu" % (b.beatmapset().artist, b.beatmapset().title, t3, t0) in os.listdir(beatmapset_dir):
                found_beatmap_filename = "%s - %s (%s) [%s].osu" % (b.beatmapset().artist, b.beatmapset().title, t3, t0)
            for beatmap_filename in os.listdir(beatmapset_dir):
                try:
                    with open(os.path.join(beatmapset_dir, beatmap_filename)) as osuf:
                        for line in osuf:
                            if line[:9] == "BeatmapID":
                                if line.lstrip("BeatmapID:").rstrip("\n") == str(b.id):
                                    found_beatmap_filename = beatmap_filename
                                    break
                except UnicodeDecodeError:
                    continue
            if found_beatmap_filename == "":
                raise ValueError("beatmap %s not found" % b.id)
            if len(m.group(1)):
                diff_with_mods = self._calc_difficulty(os.path.join(beatmapset_dir, found_beatmap_filename), m.group(1).split(" "))
            song_len_in_sec =  b.hit_length
            if "DT" in m.group(1).split(" "):
                song_len_in_sec /= 1.5
            song_len_m, song_len_s = divmod(song_len_in_sec, 60)

            playlist.append(
                {
                    "#": i,
                    "BID": b.id,
                    # "MODE": b.mode.value,
                    # "SID": b.beatmapset_id,
                    "Beatmap Info": '<a href="%s"><img src="%s" alt="%s" height="118"/></a>' % (img_link, img_src, cover_filename),
                    "CS": diff_with_mods["CS"],
                    "HP": diff_with_mods["HP"],
                    "OD": diff_with_mods["OD"],
                    "AR": diff_with_mods["AR"],
                    "Hit Length": "%2d:%02d (%dx)" % (song_len_m, song_len_s, diff_with_mods["Max Combo"]),
                    "BPM": diff_with_mods["BPM"],
                    "Stars": diff_with_mods["Stars"],
                    "Notes": notes,
                }
            )

        df = pd.DataFrame(playlist)
        df.sort_values(by=["#"], inplace=True)
        pd.set_option("colheader_justify", "center")
        html_string = """<html>
  <head><meta charset="utf-8"><title>%s%s</title></head>
  <link rel="stylesheet" type="text/css" href="style.css"/>
  <body bgcolor="#1f1f1f">
    {table}
  </body>
</html>
""" % (
            os.path.splitext(os.path.split(playlist_filename)[1])[0],
            suffix,
        )
        with open(playlist_filename.replace(".properties", ".html"), "w", encoding="utf-8") as fi:
            fi.write(html_string.format(table=df.to_html(index=False, escape=False, classes="pd")))
        shutil.rmtree(tmp_dir)


fast_gen = True
oauth = "../../../osu.properties"
original_playlist_pattern = re.compile(r"O\.(.*)\.properties")
match_playlist_pattern = re.compile(r"M\.(.*)\.properties")
skill_practice_pattern = re.compile(r"SP\.(.*)\.properties")
o0 = OsuPlaylist(oauth)
font = "../unifont-15.1.05.otf"
for i in os.listdir("./"):
    if m := original_playlist_pattern.match(i):
        o0.draw_target = True
        o0.draw_difficulty_table = False
        suffix = " — original playlist"
    elif m := match_playlist_pattern.match(i):
        suffix = " — match playlist"
        o0.draw_target = False
        o0.draw_difficulty_table = False
    elif m := skill_practice_pattern.match(i):
        suffix = " — original skill practice playlist"
        o0.draw_target = False
        o0.draw_difficulty_table = False
    else:
        continue
    if os.path.exists("../%s.html" % m.group(1)) and fast_gen:
        print("skipped %s" % m.group(1))
        continue
    try:
        shutil.copyfile("./%s" % m.group(0), "../%s.properties" % m.group(1))
        o0.generate("../%s.properties" % m.group(1), font, suffix)
    except:
        raise
    else:
        print("generated %s" % m.group(1))
    finally:
        os.remove("../%s.properties" % m.group(1))
