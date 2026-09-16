"""Create synthetic documents for screenshots and manual QA; never touch user files."""

import argparse
import os
import time
import zipfile
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen.canvas import Canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    folder = parser.parse_args().directory
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "客户沟通记录.md").write_text(
        "# 客户沟通记录\n\n2026 年 9 月 14 日 · 需求确认\n\n"
        "本次会议主要讨论资料检索的使用场景，以及企业内网中的交付要求。\n\n"
        "客户希望优先评估离线部署的成本，并确认断网后是否仍然支持全文搜索。\n\n"
        "下一步：整理测试文档，确认搜索结果的准确性，再安排小范围试用。",
        encoding="utf-8",
    )
    (folder / "周末阅读清单.md").write_text(
        "# 周末阅读清单\n\n给阅读留一点安静的时间。\n\n"
        "整理关于信息架构、排版设计与城市散步的文章。好用的工具，应该让复杂的事情变得简单。",
        encoding="utf-8",
    )
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    canvas = Canvas(str(folder / "产品部署方案.pdf"))
    canvas.setFont("STSong-Light", 22)
    canvas.drawString(64, 750, "产品部署方案")
    canvas.setFont("STSong-Light", 12)
    for y, line in enumerate(
        [
            "技术方案 · 2026 年 9 月",
            "",
            "03 / 部署方式",
            "",
            "为适应不同网络环境，系统提供灵活的部署方式。",
            "支持在企业内网进行离线部署，无需连接外部服务。",
            "所有文档与索引均保存在本地设备，数据由用户自主掌控。",
            "",
            "部署完成后，可按文件夹设置检索范围。",
            "文档更新时，只处理发生变化的内容，减少对日常工作的影响。",
        ]
    ):
        canvas.drawString(64, 710 - y * 25, line)
    canvas.save()
    xml = (
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>知识库建设规划</w:t></w:r></w:p>"
        "<w:p><w:r><w:t>第一阶段采用离线部署，支持 PDF、Markdown 和 Word 文档的全文检索。"
        "</w:t></w:r></w:p><w:p><w:r><w:t>搜索结果直接展示关键词所在的段落。"
        "</w:t></w:r></w:p></w:body></w:document>"
    )
    with zipfile.ZipFile(folder / "知识库建设规划.docx", "w") as archive:
        archive.writestr("word/document.xml", xml)
        archive.writestr(
            "[Content_Types].xml",
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'wordprocessingml.document.main+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "_rels/.rels",
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
            'officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            "</Relationships>",
        )
    for path in folder.iterdir():
        os.utime(path, (time.time() - 5, time.time() - 5))
    print(f"Created 4 synthetic documents in {folder}")


if __name__ == "__main__":
    main()
