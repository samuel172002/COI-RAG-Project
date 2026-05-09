from flask import Flask, request, jsonify
import chromadb
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)

# =========================
# Setup Chroma
# =========================
persist_dir = os.path.abspath("chroma_db")
client = chromadb.PersistentClient(path=persist_dir)

collection = client.get_collection(name="unt_rag")

# =========================
# Load embedding model
# =========================
model = SentenceTransformer("all-MiniLM-L6-v2")


# =========================
# 🔍 Search Function
# =========================
def search(query, top_k=5):
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0]

    filtered = []

    for i, doc in enumerate(documents):
        if len(doc.strip()) > 50:
            filtered.append({
                "text": doc,
                "source": metadatas[i].get("source", "unknown")
            })

    return filtered


# =========================
# 🧠 Answer Generator
# =========================
def generate_answer(results):
    context = "\n\n".join([r["text"] for r in results[:3]])

    return f"Based on the retrieved information:\n\n{context}"

@app.route("/", methods=["GET"])
def home():
    return "✅ RAG API is running. Use POST /ask"

# =========================
# 🚀 API Route
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request must be JSON. Example: { 'query': 'your question' }"
        }), 400

    query = data.get("query")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    results = search(query)
    answer = generate_answer(results)

    return jsonify({
        "query": query,
        "answer": answer,
        "sources": results
    })


# =========================
# Run server
# =========================
if __name__ == "__main__":
    app.run(debug=True)