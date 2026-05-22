# DeepDoc Toolkit

独立的文档解析工具，用于批量将 PDF/Word/图片解析为结构化 Markdown。

## 安装

```bash
python install.py
```

要求 Python 3.10+，首次运行会自动下载 PaddleOCR 模型。

## 使用

单文件解析：

```bash
python parse.py input.pdf
```

批量解析：

```bash
python parse.py --input ./pdfs --output ./parsed
```

启用详细日志：

```bash
python parse.py --input ./pdfs --output ./parsed --verbose
```

支持格式：PDF、Word (.docx)、图片 (.png/.jpg/.jpeg/.tiff/.bmp)

## 输出格式

输出 Markdown 包含 YAML frontmatter，兼容 game-kb 的 `parse_frontmatter()` 和 `ingest_article()`：

```yaml
---
标题: 文档标题
来源: input.pdf
日期: 2025-01-01
解析工具: deepdoc-toolkit
---

文档正文内容...

## 表格

### 表格 1

| 列1 | 列2 |
| --- | --- |
| 数据1 | 数据2 |
```
