# -*- coding: utf-8 -*-
"""Anonymise the article screenshots straight from the notes repo.

Every shipped picture must be free of: project names, conversation titles,
assistant names, chat content, local user paths, screen-recorder watermarks.
Reads the originals from Notes/AI (never modified), writes images/*.png here,
so it is safe to run again.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(r"C:\Users\30386\Desktop\Notes\AI\images\download\attachments\261416316")
IMG = Path(__file__).resolve().parent.parent / "images"
MONO = r"C:\Windows\Fonts\consola.ttf"

ORIG = {
    "port": SRC / "image2026-11-25_10-37-21-version-1-modificationdate-1795574241000-api-v2.png",
    "doctor": SRC / "image2026-11-25_11-1-54-version-1-modificationdate-1795575714000-api-v2.png",
    "ok": SRC / "image2026-11-25_10-42-27-version-1-modificationdate-1795574547000-api-v2.png",
    "gif": SRC / "image2026-11-25_10-58-19-version-1-modificationdate-1795575499000-api-v2.png",
}


def save(im, name):
    im.save(IMG / name, optimize=True)
    print(f"{name}: {im.size[0]}x{im.size[1]}")


# 1. 报错界面（录屏 GIF 第 40 帧）：只留报错卡片与输入框
gif = Image.open(ORIG["gif"])
gif.seek(40)
save(gif.convert("RGB").crop((660, 770, 1520, 985)), "ag-tls.png")

# 2. 体检输出：只留「修复后复核 → 结论」，切掉含路径的头部与落款提示符
im = Image.open(ORIG["doctor"]).convert("RGB").crop((0, 272, 1763, 534))
save(im, "ag-doctor.png")

# 3. 端口诊断：路径里的用户名替换为 ***
im = Image.open(ORIG["port"]).convert("RGB")
d = ImageDraw.Draw(im)
box = (100, 251, 568, 275)
path = r"C:\Users\***\AppData\Local\Programs\Antigravity\config.json"
d.rounded_rectangle(box, radius=5, fill=(41, 41, 41))
size = 12.5
f = ImageFont.truetype(MONO, size)
while d.textlength(path, font=f) > box[2] - box[0] - 10 and size > 8:
    size -= 0.5
    f = ImageFont.truetype(MONO, size)
d.text((box[0] + 5, (box[1] + box[3]) / 2), path, font=f, fill=(240, 242, 245), anchor="lm")
save(im, "ag-port.png")

# 4. 对话界面：只留输入框（模型已加载），项目、对话、助手名都不进画面
im = Image.open(ORIG["ok"]).convert("RGB").crop((430, 770, 1225, 905))
save(im, "ag-ok.png")
