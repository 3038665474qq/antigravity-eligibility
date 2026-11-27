# -*- coding: utf-8 -*-
"""3:4 covers for the Antigravity article — dark terminal + paper data."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "images"
F = r"C:\Windows\Fonts\msyh.ttc"
FB = r"C:\Windows\Fonts\msyhbd.ttc"
FM = r"C:\Windows\Fonts\consola.ttf"
FMB = r"C:\Windows\Fonts\consolab.ttf"

W, H = 1242, 1656


def font(path, size):
    return ImageFont.truetype(path, size)


def text(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def gradient(top, bottom):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line((0, y, W, y), fill=c)
    return im, d


def cover_dark():
    im, d = gradient((8, 20, 32), (17, 42, 60))
    for x in range(0, W, 62):
        d.line((x, 0, x, H), fill=(20, 42, 60), width=1)

    text(d, (96, 118), "GOOGLE ANTIGRAVITY", font(FMB, 30), (94, 214, 197))
    text(d, (96, 166), "资格报错的三道门", font(F, 34), (128, 152, 176))

    text(d, (88, 268), "挡住你的", font(FB, 138), (255, 255, 255))
    text(d, (88, 438), "不是 IP", font(FB, 138), (110, 226, 208))
    text(d, (94, 636), "是账号的“国籍”", font(FB, 104), (240, 245, 250))

    d.line((96, 800, 1110, 800), fill=(34, 62, 86), width=2)

    # terminal card
    d.rounded_rectangle((84, 848, 1158, 1196), radius=26, fill=(9, 26, 41), outline=(30, 58, 82), width=2)
    d.rounded_rectangle((84, 848, 1158, 916), radius=26, fill=(16, 38, 56))
    d.rectangle((84, 896, 1158, 916), fill=(16, 38, 56))
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        d.ellipse((118 + i * 40, 866, 138 + i * 40, 886), fill=c)
    text(d, (268, 864), "antigravity — sign in", font(FM, 24), (120, 145, 168))

    text(d, (128, 962), "Sorry, this account is", font(FM, 36), (214, 226, 238))
    text(d, (128, 1016), "ineligible to use Antigravity", font(FM, 36), (240, 148, 148))
    text(d, (128, 1082), "// 它在看的不是 IP", font(F, 29), (108, 132, 156))
    text(d, (128, 1126), "// 是账号关联的那个国家", font(F, 29), (108, 132, 156))

    # three gates
    gates = [("①", "资格", "看账号", (110, 226, 208)),
             ("②", "后端", "看请求", (148, 190, 236)),
             ("③", "条款", "看客户端", (240, 176, 132))]
    x = 96
    for mark, name, look, color in gates:
        d.rounded_rectangle((x, 1252, x + 336, 1404), radius=20, fill=(13, 32, 48), outline=(34, 62, 86), width=2)
        text(d, (x + 28, 1276), mark, font(FB, 42), color)
        text(d, (x + 80, 1282), name, font(FB, 40), (245, 248, 251))
        text(d, (x + 82, 1344), look, font(F, 28), (140, 162, 184))
        x += 360

    text(d, (96, 1452), "能开界面 ≠ 能用", font(FB, 52), (255, 255, 255))
    text(d, (98, 1536), "一道门一道门地查", font(F, 34), (150, 172, 192))
    text(d, (98, 1592), "2026.11 · 本机实测", font(F, 26), (110, 138, 162))
    im.save(OUT / "cover-ag-dark.png")


def cover_paper():
    im = Image.new("RGB", (W, H), (244, 241, 233))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 18), fill=(11, 61, 107))

    text(d, (84, 92), "ANTIGRAVITY  /  ELIGIBILITY", font(FMB, 30), (11, 61, 107))

    text(d, (74, 176), "224", font(FB, 250), (11, 61, 107))
    text(d, (626, 268), "个国家和地区", font(FB, 48), (24, 32, 40))
    text(d, (630, 338), "在 FAQ 的支持列表里", font(F, 32), (108, 100, 88))
    text(d, (630, 384), "中国大陆、香港、俄罗斯", font(F, 32), (108, 100, 88))
    text(d, (630, 428), "不在其中（2026.10）", font(F, 32), (108, 100, 88))

    d.line((84, 540, 1158, 540), fill=(214, 208, 196), width=2)

    text(d, (78, 590), "挡住你的", font(FB, 120), (24, 32, 40))
    text(d, (78, 736), "不是 IP", font(FB, 120), (11, 61, 107))
    text(d, (84, 892), "是账号的“国籍”", font(FB, 102), (24, 32, 40))

    # three gate rows
    rows = [("门一", "资格检查", "看账号关联的国家", (11, 61, 107)),
            ("门二", "后端接口", "看请求从哪个出口出发", (32, 122, 112)),
            ("门三", "条款与滥用", "看你拿什么客户端在调它", (176, 92, 56))]
    y = 1064
    for no, title, desc, color in rows:
        d.rounded_rectangle((84, y, 1158, y + 112), radius=16, fill=(255, 255, 255), outline=(222, 216, 204), width=2)
        d.rounded_rectangle((88, y + 12, 100, y + 100), radius=6, fill=color)
        text(d, (128, y + 24), no, font(FB, 28), color)
        text(d, (208, y + 16), title, font(FB, 42), (24, 32, 40))
        text(d, (208, y + 68), desc, font(F, 28), (110, 100, 88))
        y += 130

    text(d, (84, 1580), "2026.11 · 本机实测记录", font(F, 28), (140, 132, 120))
    im.save(OUT / "cover-ag-paper.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    cover_dark()
    cover_paper()
    print("covers done")
