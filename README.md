# ZDR 的笔记

用 Markdown 写，`build.py` 编成静态 HTML，GitHub Pages 发布。

- 站点：<https://3038665474qq.github.io/zdr-notes/>
- 仓库：<https://github.com/3038665474qq/zdr-notes>

> ⚠️ 仓库必须保持 **Public**。免费账号不支持私有仓库的 Pages，一旦改成 Private，站点会立刻变成
> “There isn't a GitHub Pages site here.”（Pages 设置也会被一并清掉，改回 Public 后要重新启用）。

## 结构

```
notes/                       笔记源文件（只有这里需要手写）
  <slug>/
    note.md                  front matter + 正文
    images/*.png             正文图片，md 里写 images/xxx.png
build.py                     生成器：notes/ → docs/
docs/                        产物（Pages 从这里发布，不要手改）
```

`note.md` 开头：

```yaml
---
title: 标题
date: 2026-11-26
tags: Antigravity, Gemini
summary: 一句话摘要，会显示在首页卡片上
cover: images/cover.png      # 可选
order: 0                     # 可选：大的排前面，负数沉底；同值按日期倒序
---
```

首页排序规则：`order` 降序 → `date` 降序 → 修改时间降序。所以默认最新在前，想置顶就填 `order: 10`，想让说明类沉底就填 `order: -1`。

## 新增一篇

```powershell
mkdir notes\my-note
# 写 notes\my-note\note.md，图片丢进 notes\my-note\images\
python build.py
git add -A; git commit -m "新增：my-note"; git push
```

推送后 Pages 约 30–60 秒重建。本地预览：`python build.py --serve` 起在 <http://127.0.0.1:8000>。

## 约定

- 一篇笔记一个目录，slug 就是 URL：`/notes/<slug>.html`
- 首页按 `date` 倒序，新笔记自动排前面，不需要手动改索引
- 图片按笔记分目录自动拷到 `docs/assets/<slug>/`，路径自动改写
- 正文支持：标题、段落、粗体、行内代码、代码块、表格、引用、列表、链接、图片 + 图注
