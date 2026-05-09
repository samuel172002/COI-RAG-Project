import fitz  # PyMuPDF
import json
import re
from collections import Counter
from pathlib import Path

PDF_PATH = "1258_COI_GradPreview_Slides_11-05-2025.pdf"

SOURCE_NAME = "UNT COI Graduate Preview Slides (Nov 2025)"

OUTPUT_JSON = "unt_pdf_chunks.json"

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace("\u00a0", " ")
    return text.strip()


def extract_title(text):
    lines = text.split(". ")

    if len(lines) > 0:
        title = lines[0][:120]
        return title.strip()

    return "Untitled Section"


def extract_keywords(text, top_n=6):
    stopwords = {
        "the", "and", "for", "with", "that", "this",
        "from", "are", "was", "have", "has", "into",
        "their", "will", "your", "about", "through",
        "there", "they", "them", "than", "only",
        "application", "applications", "students"
    }

    words = re.findall(r'\b[A-Za-z]{4,}\b', text.lower())

    filtered = [
        word for word in words
        if word not in stopwords
    ]

    freq = Counter(filtered)

    keywords = [word.title() for word, _ in freq.most_common(top_n)]

    return keywords


doc = fitz.open(PDF_PATH)

chunks = []

pdf_name = Path(PDF_PATH).name
pdf_stem = Path(PDF_PATH).stem

for page_num in range(len(doc)):

    page = doc[page_num]

    raw_text = page.get_text()

    cleaned_text = clean_text(raw_text)

    # Skip empty pages
    if len(cleaned_text) < 20:
        continue

    title = extract_title(cleaned_text)

    keywords = extract_keywords(cleaned_text)

    chunk = {
        "chunk_id": f"{pdf_stem.lower()}_slide_{page_num + 1}",

        "document_type": "pdf_slide",

        "slide_number": page_num + 1,

        "title": title,

        "content": cleaned_text,

        "keywords": keywords,

        "source": SOURCE_NAME,

        "file_name": pdf_name,

        "embedding_ready": True
    }

    chunks.append(chunk)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"\nTotal Chunks Created: {len(chunks)}")
print(f"JSON Saved To: {OUTPUT_JSON}")

print(json.dumps(chunks[0], indent=2))