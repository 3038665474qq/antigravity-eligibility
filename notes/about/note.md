---
title: 关于这个笔记库
date: 2026-11-27
tags: 说明, 工程
summary: 一篇笔记一个目录，Markdown 写完跑一行 build.py，GitHub Pages 直接发布。新增笔记不需要动索引，也不用装任何依赖。
cover: 
---

这里的笔记都长一个样：`notes/<slug>/note.md` 加一个 `images/` 目录，`build.py` 把 `notes/` 编译成 `docs/`，GitHub Pages 从 `docs/` 发布。

## 为什么不用现成的静态博客

试过 Hexo 和 Hugo，最后都停在一件事上：为了写一篇两千字的文章，得先理解一套主题系统、一堆插件和一个版本可能对不上的 Node 环境。而这里真正需要的功能只有三个——把 Markdown 变成 HTML、把图片搬对位置、按时间倒序列出来。

`build.py` 就是这三件事，三百多行，只用标准库。改样式直接翻到文件里的 `CSS` 常量，不用找主题目录。

## 新增一篇要做什么

```bash
mkdir notes/my-note
# 写 note.md，图片丢进 notes/my-note/images/
python build.py
git add -A && git commit -m "新增：my-note" && git push
```

推送之后两条流水线各管一段：`build-notes` 重新编译 `docs/`，Pages 再把它发出去。所以如果直接在网页上上传一个 `note.md`，站点也会自己更新。

## 一条原则

内容归内容，样式归样式。笔记里只有 Markdown，没有一行 HTML；改版式只动 `build.py`，不会碰到任何一篇旧文。
