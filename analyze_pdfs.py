import fitz
import sys
import os

pdf_paths = [
    "docs/APOSTILA COMPLETA CEFS 2026.pdf",
    "docs/ilovepdf_merged_compressed.pdf"
]

for path in pdf_paths:
    print(f"--- Analyzing {path} ---")
    if not os.path.exists(path):
        print("File not found.")
        continue
    try:
        doc = fitz.open(path)
        print(f"Pages: {len(doc)}")
        # Check first few pages for selectable text
        has_text = False
        for i in range(min(5, len(doc))):
            text = doc[i].get_text()
            if text and len(text.strip()) > 50:
                has_text = True
                break
        
        print(f"Selectable text detected: {has_text}")
        print(f"OCR required: {not has_text}")
        # Just a rough check for TOC or structure
        toc = doc.get_toc()
        print(f"Structure/TOC detected: {len(toc) > 0} ({len(toc)} items)")
        doc.close()
    except Exception as e:
        print(f"Error: {e}")
    print()
