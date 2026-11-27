# -*- coding: utf-8 -*-
"""16:9 cover for Zhihu (1600x900)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "images"
F = r"C:\Windows\Fonts\msyh.ttc"
FB = r"C:\Windows\Fonts\msyhbd.ttc"
FM = r"C:\Windows\Fonts\consola.ttf"
FMB = r"C:\Windows\Fonts\consolab.ttf"

W, H = 1600, 900
WHITE = (255, 255, 255)
TEAL = (110, 226, 208)
MUTE = (150, 172, 192)
BLUE = (148, 190, 236)
ORANGE = (240, 176, 132)


def font(path, size):
    return ImageFont.truetype(path, size)


def text(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def main():
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(a + (b - a) * t) for a, b in zip((8, 20, 32), (17, 42, 60)))
        d.line((0, y, W, y), fill=c)
    for x in range(0, W, 56):
        d.line((x, 0, x, H), fill=(20, 43, 61), width=1)

    text(d, (76, 66), "GOOGLE ANTIGRAVITY", font(FMB, 24), TEAL)
    text(d, (78, 104), "资格报错的三道门", font(F, 26), MUTE)

    text(d, (72, 170), "挡住你的", font(FB, 104), WHITE)
    text(d, (72, 292), "不是 IP", font(FB, 104), TEAL)
    text(d, (76, 424), "是账号的“国籍”", font(FB, 86), WHITE)

    d.line((80, 570, 860, 570), fill=(34, 62, 86), width=2)
    text(d, (78, 600), "能开界面 ≠ 能用", font(FB, 40), (240, 246, 251))
    text(d, (80, 664), "Antigravity 说你不符合资格，它看的不是网络", font(F, 27), MUTE)
    text(d, (80, 720), "2026.11 · 本机实测", font(F, 23), (116, 140, 164))

    # right: three gates
    gates = [
        ("①", "资格检查", "看账号关联的那个国家", BLUE),
        ("②", "后端接口", "看请求从哪个出口出发", TEAL),
        ("③", "条款与滥用", "看你拿什么客户端在调它", ORANGE),
    ]
    y = 138
    for mark, name, desc, color in gates:
        d.rounded_rectangle((940, y, 1530, y + 158), radius=18, fill=(12, 30, 46),
                            outline=(33, 60, 84), width=2)
        d.rounded_rectangle((956, y + 18, 966, y + 140), radius=5, fill=color)
        text(d, (990, y + 26), mark, font(FB, 34), color)
        text(d, (1040, y + 28), name, font(FB, 38), (245, 248, 251))
        text(d, (1042, y + 96), desc, font(F, 26), MUTE)
        y += 190

    text(d, (940, 744), "三道门各管各的：修错一道，白折腾一下午。", font(F, 24), (128, 152, 176))

    im.save(OUT / "cover-ag-wide.png")
    print("saved", im.size)


if __name__ == "__main__":
    main()
