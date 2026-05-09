# ============================================================
# UNT College of Information - RAG Data Extractor
# This script does 2 things:
#   1. Scrapes the FAQ webpage
#   2. Extracts text from the PDF slides
# Then saves everything as clean chunks for your RAG system
# ============================================================
# Install these first by running in your terminal:
#   pip install requests beautifulsoup4 pymupdf
# ============================================================

import json
import os
import fitz  # this is PyMuPDF - for reading PDFs (install with: pip install pymupdf)
import requests
from bs4 import BeautifulSoup

# ──────────────────────────────────────────────
# PART 1: SCRAPE THE FAQ WEBPAGE
# ──────────────────────────────────────────────

def scrape_faq_page(url):
    """
    Goes to the UNT FAQ webpage and pulls out all
    the questions and answers.
    Think of it like copy-pasting the page, but automatically.
    """
    print(f"🌐 Fetching FAQ page: {url}")

    headers = {
        # This makes our request look like a real browser
        # Some websites block "robots" - this helps avoid that
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != 200:
        print(f"❌ Failed to fetch page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # These are words/phrases we want to SKIP
    # They're navigation/footer stuff, not real content
    skip_phrases = [
        "Skip to", "Search", "MyUNT", "CANVAS", "Follow Us",
        "Apply to UNT", "University of North Texas. All Rights",
        "Disclaimer", "Privacy", "Accessibility"
    ]

    all_elements = soup.find_all(["h2", "h3", "h4", "p", "table"])

    faqs = []
    current_question = None
    current_answer_parts = []

    for el in all_elements:
        text = el.get_text(separator=" ", strip=True)

        # Skip short or navigation text
        if len(text) < 10:
            continue
        if any(skip in text for skip in skip_phrases):
            continue

        # Detect if this is a question (ends with ?)
        is_question = "?" in text and len(text) < 300

        if is_question:
            # Save the previous Q&A before starting a new one
            if current_question and current_answer_parts:
                faqs.append({
                    "question": current_question,
                    "answer": " ".join(current_answer_parts).strip(),
                    "source": "UNT COI Undergraduate FAQ Page",
                    "url": url
                })
            current_question = text
            current_answer_parts = []

        elif current_question:
            # This is answer text
            if el.name == "table":
                # Handle tables (like the GPA table, classification table)
                rows = []
                for row in el.find_all("tr"):
                    cols = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    if any(cols):
                        rows.append(" | ".join(cols))
                current_answer_parts.append(" | ".join(rows))
            elif text and len(text) > 5:
                current_answer_parts.append(text)

    # Don't forget the last Q&A!
    if current_question and current_answer_parts:
        faqs.append({
            "question": current_question,
            "answer": " ".join(current_answer_parts).strip(),
            "source": "UNT COI Undergraduate FAQ Page",
            "url": url
        })

    print(f"✅ Scraped {len(faqs)} FAQ entries from webpage")
    return faqs


# ──────────────────────────────────────────────
# PART 2: EXTRACT TEXT FROM THE PDF
# ──────────────────────────────────────────────

def extract_pdf_chunks(pdf_path):
    """
    Opens the PDF and reads each slide page by page.
    Each slide becomes one "chunk" of knowledge for your RAG system.
    Think of it like taking notes from each slide separately.
    """
    print(f"\n📄 Reading PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found at: {pdf_path}")
        print("   Make sure the PDF file is in the same folder as this script!")
        return []

    doc = fitz.open(pdf_path)
    chunks = []

    # Words/lines we want to skip (they appear on every slide but add no info)
    skip_lines = ["UNT | University of North Texas", "COLLEGE OF INFORMATION", "INFORMATION"]

    for page_num in range(len(doc)):
        page = doc[page_num]
        raw_text = page.get_text()

        # Clean up the text
        lines = raw_text.split("\n")
        clean_lines = []

        for line in lines:
            line = line.strip()
            if len(line) < 2:
                continue  # skip blank lines
            if any(skip in line for skip in skip_lines):
                continue  # skip repeated logo text
            clean_lines.append(line)

        page_text = "\n".join(clean_lines).strip()

        if len(page_text) < 20:
            continue  # skip basically empty slides (like title-only slides)

        # The first line is usually the slide title
        title = clean_lines[0] if clean_lines else f"Slide {page_num + 1}"

        chunks.append({
            "slide_number": page_num + 1,
            "title": title,
            "content": page_text,
            "source": "UNT COI Graduate Preview Slides (Nov 2025)",
            "file": os.path.basename(pdf_path)
        })

    doc.close()
    print(f"✅ Extracted {len(chunks)} slide chunks from PDF")
    return chunks


# ──────────────────────────────────────────────
# PART 3: SAVE EVERYTHING FOR YOUR RAG SYSTEM
# ──────────────────────────────────────────────

def save_for_rag(faq_chunks, pdf_chunks, output_folder="."):
    """
    Saves your data in two formats:
    - JSON: good for loading in Python code
    - TXT: plain text chunks, easy to paste into any RAG tool
    """
    os.makedirs(output_folder, exist_ok=True)

    # ── Save FAQ JSON ──
    faq_json_path = os.path.join(output_folder, "unt_faq_chunks.json")
    with open(faq_json_path, "w", encoding="utf-8") as f:
        json.dump(faq_chunks, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved FAQ JSON → {faq_json_path}")

    # ── Save PDF JSON ──
    pdf_json_path = os.path.join(output_folder, "unt_pdf_chunks.json")
    with open(pdf_json_path, "w", encoding="utf-8") as f:
        json.dump(pdf_chunks, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved PDF JSON → {pdf_json_path}")

    # ── Save combined TXT (this is the one you plug into RAG) ──
    combined_txt_path = os.path.join(output_folder, "unt_all_chunks_for_rag.txt")
    with open(combined_txt_path, "w", encoding="utf-8") as f:

        f.write("=" * 60 + "\n")
        f.write("SOURCE 1: UNT COI UNDERGRADUATE FAQ PAGE\n")
        f.write("=" * 60 + "\n\n")

        for i, chunk in enumerate(faq_chunks, 1):
            f.write(f"--- FAQ Chunk {i} ---\n")
            f.write(f"Source: {chunk['source']}\n")
            f.write(f"Q: {chunk['question']}\n")
            f.write(f"A: {chunk['answer']}\n\n")

        f.write("=" * 60 + "\n")
        f.write("SOURCE 2: UNT COI GRADUATE PREVIEW SLIDES\n")
        f.write("=" * 60 + "\n\n")

        for chunk in pdf_chunks:
            f.write(f"--- Slide {chunk['slide_number']}: {chunk['title']} ---\n")
            f.write(f"Source: {chunk['source']}\n")
            f.write(f"{chunk['content']}\n\n")

    print(f"💾 Saved combined RAG chunks → {combined_txt_path}")

    # Print a summary
    total = len(faq_chunks) + len(pdf_chunks)
    print(f"\n🎉 DONE! Total chunks ready for RAG: {total}")
    print(f"   📋 FAQ chunks:   {len(faq_chunks)}")
    print(f"   📊 Slide chunks: {len(pdf_chunks)}")
    print(f"\n📁 Output files saved in: {os.path.abspath(output_folder)}")


# ──────────────────────────────────────────────
# MAIN - Run everything
# ──────────────────────────────────────────────

if __name__ == "__main__":

    # ── Settings - change these if needed ──
    FAQ_URL = "https://ci.unt.edu/advising/undergraduate-faqs.html"

    # Put your PDF file path here!
    # If the PDF is in the same folder as this script, just use the filename:
    PDF_PATH = "/Users/samuelsibbirayanjerome/Documents/Docs/UNT/COI Project/1258_COI_GradPreview_Slides_11-05-2025.pdf"

    # Where to save the output files
    OUTPUT_FOLDER = "rag_output"

    # ── Run the scraper ──
    faq_data = scrape_faq_page(FAQ_URL)

    # ── Run the PDF extractor ──
    pdf_data = extract_pdf_chunks(PDF_PATH)

    # ── Save everything ──
    save_for_rag(faq_data, pdf_data, output_folder=OUTPUT_FOLDER)