# -*- coding: utf-8 -*-
"""Cover (1600x900) for the GPT purchase note."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"C:\Users\30386\Desktop\文章\zdr-notes\notes\gpt-purchase\images")
F = r"C:\Windows\Fonts\msyh.ttc"
FB = r"C:\Windows\Fonts\msyhbd.ttc"
FM = r"C:\Windows\Fonts\consola.ttf"
FMB = r"C:\Windows\Fonts\consolab.ttf"
W, H = 1600, 900


def font(path, size):
    return ImageFont.truetype(path, size)


def text(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def main():
    im = Image.new("RGB", (W, H), (244, 241, 233))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 16), fill=(11, 61, 107))

    text(d, (72, 62), "CHATGPT  /  SUBSCRIPTION", font(FMB, 24), (11, 61, 107))
    text(d, (74, 100), "订阅路上的三层对齐", font(F, 26), (108, 100, 88))

    text(d, (68, 168), "付款被拒", font(FB, 118), (24, 32, 40))
    text(d, (68, 300), "不是卡里没钱", font(FB, 118), (11, 61, 107))

    d.line((74, 470, 900, 470), fill=(214, 208, 196), width=2)
    text(d, (72, 500), "钱一直在。被拒的是「这一笔不像当地用户」。", font(F, 30), (90, 82, 70))
    text(d, (72, 552), "出口 IP、浏览器指纹、卡的 BIN 与账单地址——", font(F, 30), (90, 82, 70))
    text(d, (72, 604), "三层指向同一个国家，它才像真的。", font(FB, 32), (24, 32, 40))

    chips = [("①", "出口 IP", "家宽还是机房"), ("②", "浏览器", "时区语言指纹"), ("③", "卡", "BIN 与账单地址")]
    y = 176
    for mark, name, desc in chips:
        d.rounded_rectangle((980, y, 1530, y + 150), radius=18, fill=(255, 255, 255), outline=(222, 216, 204), width=2)
        text(d, (1010, y + 26), mark, font(FB, 32), (11, 61, 107))
        text(d, (1058, y + 26), name, font(FB, 38), (24, 32, 40))
        text(d, (1060, y + 92), desc, font(F, 25), (110, 100, 88))
        y += 178

    text(d, (72, 742), "2026.11 · 实测记录", font(F, 24), (140, 132, 120))
    im.save(OUT / "cover.png")
    print("cover ok", im.size)


if __name__ == "__main__":
    main()
