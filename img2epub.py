#!/usr/bin/env python3
"""
Turn a folder of images into an EPUB (or PDF).

Works two ways:

  - flat folder of images -> single-section book
        My Album/
            001.jpg
            002.jpg

  - folder of subfolders, each full of images -> one section per subfolder
        My Book/
            Part 1/
                001.jpg
            Part 2/
                001.jpg

Needs img2pdf + pillow for PDF output: pip install img2pdf pillow
"""

from __future__ import annotations

import argparse
import re
import tempfile
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
EPUB_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

    
def natural_key(name: str):
    # so "Part 10" doesn't sort before "Part 2"
    return [int(p) if p.isdigit() else p.casefold() for p in re.split(r"(\d+)", name)]


def list_images(folder: Path) -> list[Path]:
    return sorted(
        (p for p in folder.iterdir() if p.is_file() and p.suffix.casefold() in IMG_EXT),
        key=lambda p: natural_key(p.name),
    )


def find_sections(source: Path) -> list[tuple[str, list[Path]]]:
    
    subdirs = sorted(
        (p for p in source.iterdir() if p.is_dir() and not p.name.startswith(".")),
        key=lambda p: natural_key(p.name),
    )

    if subdirs:
        sections = []
        for d in subdirs:
            images = list_images(d)
            if images:
                sections.append((d.name, images))
        if not sections:
            raise ValueError(f"subfolders in {source} don't contain any images")
        return sections

    images = list_images(source)
    if not images:
        raise ValueError(f"no images found in {source}")
    return [(source.name, images)]


PAGE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, height=device-height"/>
    <link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body><img src="{img}" alt={title_attr}/></body>
</html>
"""

STYLE_CSS = """html, body { margin: 0; padding: 0; background: #000; }
body { text-align: center; }
img { display: block; width: 100%; height: auto; margin: 0 auto; }
"""


def build_epub(source: Path, out: Path | None = None, title: str | None = None, ltr: bool = True) -> Path:
    source = source.expanduser().resolve()
    title = title or source.name
    out = out or source.with_suffix(".epub")

    sections = find_sections(source)

    # work out ids/filenames up front, write the archive after
    book = []
    for sec_idx, (name, images) in enumerate(sections):
        pages = []
        for pg_num, img in enumerate(images, start=1):
            pid = f"s{sec_idx:04d}_p{pg_num:04d}"
            pages.append({"src": img, "id": pid, "xhtml": f"{pid}.xhtml", "num": pg_num})
        book.append({"name": name, "pages": pages})

    manifest, spine = [], []
    with tempfile.TemporaryDirectory(prefix="img2epub_") as tmp:
        tmp = Path(tmp)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("mimetype", "application/epub+zip", zipfile.ZIP_STORED)
            z.writestr(
                "META-INF/container.xml",
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                '  <rootfiles><rootfile full-path="OEBPS/content.opf" '
                'media-type="application/oebps-package+xml"/></rootfiles>\n</container>\n',
            )
            z.writestr("OEBPS/style.css", STYLE_CSS)

            for section in book:
                for page in section["pages"]:
                    src = page["src"]
                    ext = src.suffix.casefold()

                    if ext == ".bmp":
                        # epub readers don't reliably handle bmp, flatten to png
                        from PIL import Image
                        png_path = tmp / f"{page['id']}.png"
                        with Image.open(src) as im:
                            im.convert("RGB").save(png_path, "PNG")
                        ext, img_bytes = ".png", png_path.read_bytes()
                    else:
                        img_bytes = src.read_bytes()

                    img_name = f"images/{page['id']}{ext}"
                    z.writestr(f"OEBPS/{img_name}", img_bytes)

                    page_title = f"{section['name']} - {page['num']}"
                    z.writestr(
                        f"OEBPS/{page['xhtml']}",
                        PAGE_TEMPLATE.format(
                            title=escape(page_title),
                            img=escape(img_name),
                            title_attr=quoteattr(page_title),
                        ),
                    )

                    manifest.append(f'<item id="{page["id"]}" href="{img_name}" media-type="{EPUB_MIME[ext]}"/>')
                    manifest.append(
                        f'<item id="{page["id"]}_pg" href="{page["xhtml"]}" media-type="application/xhtml+xml"/>'
                    )
                    spine.append(f'<itemref idref="{page["id"]}_pg"/>')

            nav_links = "\n".join(
                f'<li><a href="{s["pages"][0]["xhtml"]}">{escape(s["name"])}</a></li>' for s in book
            )
            z.writestr(
                "OEBPS/nav.xhtml",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{escape(title)}</title></head>
<body>
<nav epub:type="toc" id="toc"><h1>{escape(title)}</h1><ol>
{nav_links}
</ol></nav>
</body>
</html>
""",
            )

            direction = "rtl" if not ltr else "ltr"
            z.writestr(
                "OEBPS/content.opf",
                f"""<?xml version="1.0" encoding="UTF-8"?>
                <package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">
                    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                        <dc:identifier id="book-id">urn:uuid:{uuid.uuid4()}</dc:identifier>
                        <dc:title>{escape(title)}</dc:title>
                        <dc:language>en</dc:language>
                    </metadata>
                    <manifest>
                        <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
                        <item id="css" href="style.css" media-type="text/css"/>
                        {chr(10).join(manifest)}
                    </manifest>
                    <spine page-progression-direction="{direction}">
                        {chr(10).join(spine)}
                    </spine>
                    </package>
                    """,
            )

    return out


def build_pdf(source: Path, out: Path | None = None) -> Path:
    import img2pdf
    from PIL import Image

    source = source.expanduser().resolve()
    out = out or source.with_suffix(".pdf")

    pages = [img for _, images in find_sections(source) for img in images]

    with tempfile.TemporaryDirectory(prefix="img2epub_pdf_") as tmp:
        tmp = Path(tmp)
        flattened = []
        for i, img in enumerate(pages):
            if img.suffix.casefold() in (".webp", ".bmp"):
                # img2pdf chokes on these, re-encode to png first
                converted = tmp / f"{i:06d}.png"
                with Image.open(img) as im:
                    im.convert("RGB").save(converted, "PNG")
                flattened.append(converted)
            else:
                flattened.append(img)

        out.write_bytes(img2pdf.convert([str(p) for p in flattened]))

    return out


def run_cli() -> None:
    ap = argparse.ArgumentParser(description="Turn a folder of images into an EPUB or PDF.")
    ap.add_argument("format", choices=("epub", "pdf"))
    ap.add_argument("folder", type=Path, help="flat folder of images, or a folder of subfolders")
    ap.add_argument("-o", "--output", type=Path)
    ap.add_argument("-t", "--title", help="EPUB only")
    args = ap.parse_args()

    if args.format == "epub":
        result = build_epub(args.folder, args.output, args.title, ltr=not args.rtl)
    else:
        result = build_pdf(args.folder, args.output)

    print(f"done -> {result}")

#GUI
def run_gui() -> None:

    import tkinter as tk
    from tkinter import filedialog, messagebox

    root = tk.Tk()
    root.title("Images to Ebook")
    root.resizable(False, False)

    folder_var = tk.StringVar()
    format_var = tk.StringVar(value="epub")
    title_var = tk.StringVar()
    rtl_var = tk.BooleanVar(value=False)

    frame = tk.Frame(root, padx=25, pady=20)
    frame.pack()

    tk.Label(frame, text="Images to Ebook", font=("Arial", 18, "bold")).pack(pady=(0, 12))
    tk.Label(
        frame,
        text="Pick a folder of images, or a folder of subfolders (one section each).",
        justify="center",
    ).pack(pady=(0, 12))

    folder_row = tk.Frame(frame)
    folder_row.pack(fill="x", pady=5)
    tk.Entry(folder_row, textvariable=folder_var, width=42).pack(side="left")
    tk.Button(
        folder_row,
        text="Browse...",
        command=lambda: folder_var.set(filedialog.askdirectory(title="Select folder") or folder_var.get()),
    ).pack(side="left", padx=(8, 0))

    title_row = tk.Frame(frame)
    title_row.pack(fill="x", pady=(10, 5))
    tk.Label(title_row, text="Title (optional):").pack(side="left")
    tk.Entry(title_row, textvariable=title_var, width=30).pack(side="left", padx=(8, 0))

    tk.Label(frame, text="Output format:").pack(anchor="w", pady=(10, 2))
    tk.Radiobutton(frame, text="EPUB", variable=format_var, value="epub").pack(anchor="w")
    tk.Radiobutton(frame, text="PDF", variable=format_var, value="pdf").pack(anchor="w")




    def convert():
        folder_text = folder_var.get().strip()
        if not folder_text:
            messagebox.showwarning("No folder selected", "Pick a folder first.")
            return

        folder = Path(folder_text)
        if not folder.is_dir():
            messagebox.showerror("Invalid folder", "That folder doesn't exist.")
            return

        try:
            if format_var.get() == "epub":
                result = build_epub(folder, title=title_var.get().strip() or None, ltr=not rtl_var.get())
            else:
                result = build_pdf(folder)
            messagebox.showinfo("Done", f"Created:\n{result}")
        except Exception as error:
            messagebox.showerror("Conversion failed", str(error))

    tk.Button(frame, text="Convert", command=convert, width=20, height=2).pack(pady=(18, 0))

    root.mainloop()


def main() -> None:
    import sys

    if len(sys.argv) == 1:
        run_gui()
    else:
        run_cli()


if __name__ == "__main__":
    main()