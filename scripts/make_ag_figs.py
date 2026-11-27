# -*- coding: utf-8 -*-
"""Figures for the Antigravity eligibility article (Pillow only)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "images"
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"
MONO_B = r"C:\Windows\Fonts\consolab.ttf"

INK = (34, 40, 46)
MUTED = (108, 116, 124)
FAINT = (150, 158, 166)
GRID = (229, 233, 238)
PANEL = (248, 250, 252)

BLUE = (11, 61, 107)
BLUE_L = (74, 140, 196)
BLUE_PALE = (234, 242, 250)
TEAL = (32, 122, 112)
TEAL_PALE = (234, 246, 243)
ORANGE = (176, 92, 56)
ORANGE_PALE = (251, 240, 234)
GREY = (152, 166, 180)
WHITE = (255, 255, 255)


def f(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def mono(size, bold=False):
    return ImageFont.truetype(MONO_B if bold else MONO, size)


def text(d, xy, s, size=30, color=INK, bold=False, anchor="la", font=None):
    d.text(xy, s, font=font or f(size, bold), fill=color, anchor=anchor)


def wrap(d, s, font, max_w):
    lines, cur = [], ""
    for ch in s:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        if d.textlength(cur + ch, font=font) > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def canvas(w, h):
    im = Image.new("RGB", (w, h), WHITE)
    return im, ImageDraw.Draw(im)


def header(d, title, sub, w=2100):
    text(d, (110, 76), title, 58, INK, True)
    text(d, (112, 168), sub, 31, MUTED)
    d.line((110, 232, w, 232), fill=GRID, width=2)


def footer(d, im, s):
    text(d, (110, im.height - 46), s, 24, FAINT)


def note(d, box, s, color=TEAL, fill=TEAL_PALE, size=28, pad=28):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=fill)
    text(d, (x0 + pad, (y0 + y1) / 2), s, size, color, True, "lm")


def arrow(d, x0, y, x1, color=GREY, width=3):
    d.line((x0, y, x1 - 14, y), fill=color, width=width)
    d.polygon([(x1, y), (x1 - 18, y - 9), (x1 - 18, y + 9)], fill=color)


# ---------------------------------------------------------------- figure 1
def fig_doors():
    im, d = canvas(2200, 1300)
    header(d, "三道门，各管各的", "报错看起来都差不多，对应的修法完全不搭界")

    cards = [
        (110, BLUE, BLUE_PALE, "1", "门 一", "资格检查", "看账号挂在哪",
         ["账号在 Google 服务条款页上\n显示的国家", "不看 IP、不看 Play 国家、\n不看账单地址"],
         'Sorry, this account is\nineligible to use Antigravity',
         "修法：更正国家关联 / 过年龄验证 / 换个人账号"),
        (783, TEAL, TEAL_PALE, "2", "门 二", "后端接口", "看请求从哪来",
         ["真正干活的是云端接口，\n不在客户端里", "它在服务器那一侧，\n再按请求的出口判一次"],
         'PERMISSION_DENIED (403)\nUNSUPPORTED_LOCATION',
         "修法：把目标进程的流量接进隧道"),
        (1456, ORANGE, ORANGE_PALE, "3", "门 三", "条款与滥用", "看你拿什么在调它",
         ["共享后端做滥用检查，\n三个产品共用一个标记", "用第三方客户端套 OAuth，\n是最常见的一种"],
         'Gemini has been disabled\nin this account ...',
         "修法：停用并移除授权，按邮件里的表单申诉"),
    ]

    for x0, color, pale, dig, no, title, big, lines, sample, fix in cards:
        x1 = x0 + 633
        d.rounded_rectangle((x0, 282, x1, 1046), radius=18, fill=WHITE, outline=GRID, width=2)
        d.rounded_rectangle((x0, 282, x1, 288), radius=3, fill=color)
        # number badge
        d.ellipse((x0 + 38, 320, x0 + 38 + 56, 320 + 56), fill=pale, outline=color, width=2)
        text(d, (x0 + 66, 348), dig, 28, color, True, "mm", font=mono(26, True))
        text(d, (x0 + 108, 322), no, 24, color, True)
        text(d, (x0 + 108, 354), title, 34, INK, True)

        text(d, (x0 + 38, 418), big, 42, color, True)
        d.line((x0 + 38, 488, x1 - 38, 488), fill=GRID, width=2)

        y = 516
        for ln in lines:
            for seg in ln.split("\n"):
                text(d, (x0 + 38, y), seg, 27, INK)
                y += 44
            y += 14

        text(d, (x0 + 38, y), "报错长这样", 22, FAINT, True)
        box_top = y + 32
        d.rounded_rectangle((x0 + 30, box_top, x1 - 30, box_top + 100), radius=10,
                            fill=(250, 251, 252), outline=GRID, width=2)
        for i, seg in enumerate(sample.split("\n")):
            text(d, (x0 + 48, box_top + 20 + i * 36), seg, 22, (120, 128, 136), font=mono(21))

        bx0, by0, bx1, by1 = x0 + 28, 880, x1 - 28, 1006
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=12, fill=pale)
        for i, seg in enumerate(wrap(d, fix, f(24, True), bx1 - bx0 - 40)):
            text(d, (bx0 + 20, by0 + 22 + i * 36), seg, 24, color, True)

    # gating order
    for xa in (110, 783):
        arrow(d, xa + 633 + 6, 660, xa + 633 + 34)
    text(d, (110, 1078), "顺序是：先过门一，再被门二判一次。门三不拦你进门，它管的是哪天把账号收走。", 30, INK, True)

    note(d, (110, 1136, 2090, 1216),
         "门一看账号，门二看请求。这两件事不重叠，所以“能打开界面、却问不了一句话”是必然会出现的一种状态。",
         color=INK, fill=PANEL)
    footer(d, im, "图：作者整理｜依据 Antigravity FAQ、附加条款第 6 条与 2026 年 10 月的官方回复")
    im.save(OUT / "ag-doors.png")


# ---------------------------------------------------------------- figure 2
def fig_chain():
    im, d = canvas(2200, 1080)
    header(d, "代理不是 VPN：它只改这几个进程的出口", "装一个 version.dll，进程启动时加载，把连接改写到本机端口")

    # left: processes
    d.rounded_rectangle((110, 300, 690, 800), radius=18, fill=PANEL, outline=GRID, width=2)
    text(d, (140, 322), "Antigravity 安装目录", 28, FAINT)
    for i, (name, tag) in enumerate([
        ("Antigravity.exe", "界面"),
        ("language_server.exe", "真正发请求的后端"),
        ("node.exe", ""),
        ("agy.exe", "命令行"),
    ]):
        y = 380 + i * 100
        d.rounded_rectangle((140, y, 660, y + 76), radius=12, fill=WHITE, outline=GRID, width=2)
        text(d, (162, y + 14), name, 27, INK, font=mono(26))
        if tag:
            text(d, (162, y + 44), tag, 22, MUTED)

    # middle: dll
    d.rounded_rectangle((736, 380, 1036, 700), radius=18, fill=BLUE_PALE, outline=BLUE_L, width=2)
    text(d, (886, 406), "version.dll", 30, BLUE, True, "ma", font=mono(28, True))
    for i, s in enumerate(["随进程启动", "读同目录的 config.json", "改写连接的目标", "进程本身无感"]):
        text(d, (886, 466 + i * 44), s, 23, BLUE, anchor="ma")

    # right: tunnel
    d.rounded_rectangle((1080, 300, 1560, 800), radius=18, fill=TEAL_PALE, outline=TEAL, width=2)
    text(d, (1320, 322), "本机代理端口", 26, TEAL, True, "ma")
    text(d, (1320, 356), "127.0.0.1:18787", 30, TEAL, True, "ma", font=mono(28, True))
    text(d, (1320, 424), "type 必须对上", 24, TEAL, anchor="ma")
    for i, s in enumerate(["socks5 → 握手走 SOCKS5", "http → 握手走 CONNECT", "填错：连接一直被关闭"]):
        text(d, (1112, 470 + i * 44), s, 23, INK)
    text(d, (1320, 640), "FakeIP 198.18.0.0/15", 24, TEAL, anchor="ma", font=mono(22))
    text(d, (1320, 676), "应用看到的是假地址，实际由本地接管", 22, MUTED, anchor="ma")

    # far right
    d.rounded_rectangle((1630, 380, 2090, 720), radius=18, fill=WHITE, outline=GRID, width=2)
    text(d, (1860, 404), "出口节点 → Google 后端", 26, INK, anchor="ma")
    text(d, (1860, 452), "cloudaicompanion", 24, MUTED, anchor="ma", font=mono(22))
    text(d, (1860, 486), "googleapis.com", 24, MUTED, anchor="ma", font=mono(22))
    text(d, (1860, 546), "这一跳在外面，", 22, MUTED, anchor="ma")
    text(d, (1860, 578), "本地看不到健康度", 22, MUTED, anchor="ma")

    arrow(d, 690 + 8, 550, 756)
    arrow(d, 1040, 550, 1076, TEAL)
    arrow(d, 1564, 550, 1626, TEAL)

    # untouched traffic
    d.rounded_rectangle((110, 840, 2090, 916), radius=14, fill=(250, 250, 250), outline=GRID, width=2)
    text(d, (138, 864), "系统的其他流量、浏览器的流量，一概不动——它只认名单里的进程名。", 26, MUTED)

    note(d, (110, 946, 2090, 1024),
         "所以“装完没生效”多半不是节点坏，而是名单里少了一个 language_server.exe。",
         color=ORANGE, fill=ORANGE_PALE)
    footer(d, im, "图：作者整理｜依据 antigravity-proxy 的部署方式与 doctor.ps1 的检查项")
    im.save(OUT / "ag-chain.png")


# ---------------------------------------------------------------- figure 3
def fig_triage():
    im, d = canvas(2200, 1160)
    header(d, "分层体检：一层不通，上面全白查",
           "四层坏哪一层，用户看到的都是同一句——“连不上”")

    # 从下往上：L1 端口 → L2 配置 → L3 补丁 → L4 名单
    layers = [
        ("端口可达", "ProxyPortReachable", "127.0.0.1:18787 能不能握手", "代理软件没开 / 端口填错", TEAL),
        ("配置能读", "ConfigParsed", "config.json 里的 type 与 port", "改完没重启；socks5 填给了 HTTP 端口", TEAL),
        ("补丁在位", "PatchPresent / ArchMatched", "version.dll 在不在，架构对不对", "应用更新顺手把补丁删了", ORANGE),
        ("进程覆盖", "TargetProcessesCovered", "名单里有没有 language_server.exe", "后端绕过代理直连", ORANGE),
    ]

    top, step = 296, 174
    x0, x1 = 110, 2090
    for i, (name, code, what, bad, color) in enumerate(reversed(layers)):
        y = top + i * step
        d.rounded_rectangle((x0, y, x1, y + 152), radius=16, fill=WHITE, outline=GRID, width=2)
        d.rounded_rectangle((x0, y, x0 + 10, y + 152), radius=5, fill=color)
        d.rounded_rectangle((x0 + 32, y + 46, x0 + 104, y + 100), radius=10, fill=PANEL, outline=GRID, width=2)
        text(d, (x0 + 68, y + 73), f"L{len(layers) - i}", 24, color, True, "mm", font=mono(23, True))
        text(d, (x0 + 130, y + 22), name, 34, INK, True)
        text(d, (x0 + 130, y + 76), code, 24, color, font=mono(23))
        text(d, (x0 + 130, y + 108), what, 24, MUTED)
        text(d, (x1 - 40, y + 28), "坏在这儿会看到", 22, FAINT, anchor="ra")
        text(d, (x1 - 40, y + 64), bad, 26, INK, anchor="ra")

    note(d, (110, 1014, 2090, 1090),
         "从 L1 往上查。退出码只有四种：0 健康、1 需修复、2 修复未完成、3 环境问题——看到 3 就别再动配置了。",
         color=INK, fill=PANEL, size=26)
    footer(d, im, "图：作者整理｜依据 doctor.ps1 的输出项与 -Action Setup / Repair 的语义")
    im.save(OUT / "ag-triage.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    fig_doors()
    fig_chain()
    fig_triage()
    print("figures done")
