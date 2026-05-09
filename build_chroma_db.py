import chromadb
from sentence_transformers import SentenceTransformer
import json
import os

persist_dir = os.path.abspath("chroma_db")

client = chromadb.PersistentClient(path=persist_dir)

collection = client.get_or_create_collection(
    name="unt_rag"
)

model = SentenceTransformer("all-MiniLM-L6-v2")

documents = []
embeddings = []
ids = []
metadatas = []


with open("rag_output/unt_faq_chunks.json", "r", encoding="utf-8") as f:

    faq_data = json.load(f)

    for i, item in enumerate(faq_data):

        question = item.get("question", "")
        answer = item.get("answer", "")
        source = item.get("source", "")

        text = f"""
[TYPE]: FAQ

[QUESTION]:
{question}

[ANSWER]:
{answer}
""".strip()

        documents.append(text)

        ids.append(f"faq_{i}")

        metadatas.append({
            "type": "faq",
            "source": source
        })



with open("rag_output/unt_pdf_chunks.json", "r", encoding="utf-8") as f:

    pdf_data = json.load(f)

    for item in pdf_data:

        chunk_id = item.get("chunk_id", "")
        title = item.get("title", "")
        content = item.get("content", "")
        slide_number = item.get("slide_number", "")
        source = item.get("source", "")
        keywords = item.get("keywords", [])

        text = f"""
[TYPE]: PDF_SLIDE

[TITLE]:
{title}

[CONTENT]:
{content}
""".strip()

        documents.append(text)

        ids.append(chunk_id)

        metadatas.append({
            "type": "pdf_slide",
            "slide_number": slide_number,
            "source": source,
            "keywords": ", ".join(keywords)
        })


print("Generating embeddings...")

embeddings = model.encode(
    documents,
    show_progress_bar=True
).tolist()


collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)

print(f"\n✅ Stored {len(documents)} chunks in ChromaDB")