import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml


def parse_pdf(file_path: str) -> dict:
    import pdfplumber

    texts = []
    tables = []

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                texts.append(f"<!-- Page {i+1} -->\n{text}")

            page_tables = page.extract_tables()
            for table in page_tables:
                if table:
                    md_table = format_table_as_markdown(table)
                    tables.append(md_table)

    return {
        "title": Path(file_path).stem,
        "content": "\n\n".join(texts),
        "tables": tables,
    }


def parse_docx(file_path: str) -> dict:
    import docx

    doc = docx.Document(file_path)
    texts = []
    tables = []

    for para in doc.paragraphs:
        if para.text.strip():
            texts.append(para.text)

    for table in doc.tables:
        rows = []
        for row in table.rows:
            rows.append([cell.text for cell in row.cells])
        tables.append(format_table_as_markdown(rows))

    return {
        "title": Path(file_path).stem,
        "content": "\n\n".join(texts),
        "tables": tables,
    }


def parse_image(file_path: str) -> dict:
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    result = ocr.ocr(file_path, cls=True)

    texts = []
    for line in result:
        if line:
            for word_info in line:
                texts.append(word_info[1][0])

    return {
        "title": Path(file_path).stem,
        "content": "\n".join(texts),
        "tables": [],
    }


def format_table_as_markdown(table: list) -> str:
    if not table:
        return ""

    rows = []
    for row in table:
        cells = [str(cell).replace("\n", " ").strip() if cell else "" for cell in row]
        rows.append("| " + " | ".join(cells) + " |")

    if len(rows) < 2:
        return rows[0] if rows else ""

    header = rows[0]
    separator = "| " + " | ".join(["---"] * len(table[0])) + " |"
    body = rows[1:]

    return "\n".join([header, separator] + body)


def build_markdown(title: str, content: str, tables: list, source_file: str) -> str:
    frontmatter = {
        "标题": title,
        "来源": source_file,
        "日期": datetime.now().strftime("%Y-%m-%d"),
        "解析工具": "deepdoc-toolkit",
    }

    frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False).strip()

    parts = [f"---\n{frontmatter_str}\n---\n"]

    if content.strip():
        parts.append(content.strip())

    if tables:
        parts.append("\n\n## 表格\n")
        for i, table in enumerate(tables, 1):
            parts.append(f"\n### 表格 {i}\n\n{table}\n")

    return "\n\n".join(parts)


def parse_single_file(file_path: str, output_dir: str = None) -> str:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        result = parse_pdf(file_path)
    elif ext in (".docx", ".doc"):
        result = parse_docx(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        result = parse_image(file_path)
    else:
        print(f"Unsupported format: {ext}")
        return None

    md_content = build_markdown(
        title=result["title"],
        content=result["content"],
        tables=result["tables"],
        source_file=path.name,
    )

    if output_dir:
        out_path = Path(output_dir) / f"{path.stem}.md"
    else:
        out_path = path.parent / f"{path.stem}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md_content, encoding="utf-8")

    return str(out_path)


def batch_parse(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    supported = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    files = [f for f in input_path.rglob("*") if f.suffix.lower() in supported]

    if not files:
        print(f"No supported files found in {input_dir}")
        return

    print(f"Found {len(files)} files to parse")

    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Parsing: {file.name}")
        try:
            result = parse_single_file(str(file), str(output_path))
            if result:
                print(f"  -> {result}")
        except Exception as e:
            print(f"  -> Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="DeepDoc Toolkit - Document parser for game-kb")
    parser.add_argument("input", nargs="?", help="Single file to parse")
    parser.add_argument("--input", dest="input_dir", help="Input directory for batch parsing")
    parser.add_argument("--output", dest="output_dir", default="./output", help="Output directory (default: ./output)")

    args = parser.parse_args()

    if args.input_dir:
        batch_parse(args.input_dir, args.output_dir)
    elif args.input:
        result = parse_single_file(args.input, args.output_dir)
        if result:
            print(f"Output: {result}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
