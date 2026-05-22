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

## 文件名处理

工具会自动处理文件名中的特殊字符和大小写问题：

- **特殊字符**：`<>:"/\|?*` 等字符会被替换为下划线
- **大小写不敏感**：Windows 系统上 `Foo.pdf` 和 `foo.pdf` 会被识别为碰撞
- **碰撞处理**：当多个源文件映射到同一输出文件名时，会自动添加 hash 后缀

示例：
- `report.pdf` → `report.md`
- `a?b.pdf` + `a*b.pdf` → `a_b_<hash1>.md` + `a_b_<hash2>.md`
- `Foo.pdf` + `foo.pdf` → `Foo_<hash1>.md` + `foo_<hash2>.md`

## 测试

运行单元测试：

```bash
python -m pytest test_parse.py -v
```

测试覆盖：
- 文件名清理和特殊字符处理
- 文件名碰撞检测（特殊字符、大小写）
- Markdown 表格格式化
- 换行符处理
