import json

faq_file = "rag_output/unt_faq_chunks.json"
pdf_file = "rag_output/unt_pdf_chunks.json"
output_file = "rag_output/unt_all_chunks_for_rag.txt"

all_chunks = []

# =========================================================
# LOAD FAQ CHUNKS
# =========================================================

with open(faq_file, "r", encoding="utf-8") as f:
    faq_data = json.load(f)

    print(f"FAQ entries found: {len(faq_data)}")

    for item in faq_data:

        question = item.get("question", "").strip()
        answer = item.get("answer", "").strip()
        source = item.get("source", "").strip()

        text = f"""
==================================================
[TYPE]: FAQ
[SOURCE]: {source}

[QUESTION]:
{question}

[ANSWER]:
{answer}
""".strip()

        if text:
            all_chunks.append(text)

# =========================================================
# LOAD PDF CHUNKS
# =========================================================

with open(pdf_file, "r", encoding="utf-8") as f:
    pdf_data = json.load(f)

    print(f"PDF entries found: {len(pdf_data)}")

    for item in pdf_data:

        if not isinstance(item, dict):
            continue

        chunk_id = item.get("chunk_id", "")
        slide_number = item.get("slide_number", "")
        title = item.get("title", "").strip()
        content = item.get("content", "").strip()
        source = item.get("source", "").strip()
        keywords = item.get("keywords", [])

        keywords_text = ", ".join(keywords)

        text = f"""
==================================================
[TYPE]: PDF_SLIDE
[CHUNK_ID]: {chunk_id}
[SLIDE_NUMBER]: {slide_number}
[SOURCE]: {source}

[TITLE]:
{title}

[KEYWORDS]:
{keywords_text}

[CONTENT]:
{content}
""".strip()

        if text:
            all_chunks.append(text)

# =========================================================
# WRITE FINAL CORPUS
# =========================================================

with open(output_file, "w", encoding="utf-8") as f:

    for chunk in all_chunks:

        f.write(chunk)
        f.write("\n\n")

print(f"\n✅ Combined {len(all_chunks)} chunks")
print(f"✅ Saved to: {output_file}")