import os
from langchain_core.documents import Document

PDF_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pdfs")
def _extract_text_pypdf(pdf_path: str) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    pages  = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({"page_number": i, "text": text})
    return pages


def _chunk_pages(
    pages:      list[dict],
    chunk_size: int = 800,
    overlap:    int = 100,
) -> list[str]:
    full_text = "\n\n".join(p["text"] for p in pages)
    chunks    = []
    start     = 0

    while start < len(full_text):
        end   = min(start + chunk_size, len(full_text))
        chunk = full_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap   # slide forward, keeping overlap

    return chunks


def build_documents(pdf_path: str) -> list[Document]:
    filename  = os.path.basename(pdf_path)
    label     = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
    file_url  = f"file://data/pdfs/{filename}"

    print(f"  Reading: {filename}")

    try:
        pages = _extract_text_pypdf(pdf_path)
    except Exception as e:
        print(f"    ✗ Failed to read {filename}: {e}")
        return []

    if not pages:
        print(f"    ✗ No text extracted from {filename} (scanned/image PDF?)")
        return []

    print(f"    → {len(pages)} page(s) extracted")
    chunks = _chunk_pages(pages)
    print(f"    → {len(chunks)} chunk(s) created")

    docs = []
    for i, chunk in enumerate(chunks):
        # Prepend a header so the LLM always knows where this text came from
        content = f"[From {label} — chunk {i+1}/{len(chunks)}]\n\n{chunk}"
        docs.append(Document(
            page_content=content,
            metadata={
                "source":      file_url,
                "source_type": "pdf",
                "filename":    filename,
                "label":       label,
                "chunk":       i + 1,
                "total_chunks": len(chunks),
            },
        ))

    return docs


def scrape_all_pdfs() -> list[Document]:
    
    if not os.path.isdir(PDF_DIR):
        print(f"  ℹ PDF directory not found ({PDF_DIR}) — skipping")
        return []

    pdf_files = sorted(
        f for f in os.listdir(PDF_DIR) if f.lower().endswith(".pdf")
    )

    if not pdf_files:
        print(f"  ℹ No PDF files found in {PDF_DIR} — skipping")
        return []

    all_docs = []
    for filename in pdf_files:
        path = os.path.join(PDF_DIR, filename)
        all_docs.extend(build_documents(path))

    return all_docs


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json

    docs = scrape_all_pdfs()
    print(f"\nTotal documents: {len(docs)}")

    if docs:
        print(f"First chunk preview")
        print(docs[0].page_content[:500])
        print("...")
        print("\nMetadata:", json.dumps(docs[0].metadata, indent=2))
