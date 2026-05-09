import chromadb
from sentence_transformers import SentenceTransformer
import os

persist_dir = os.path.abspath("chroma_db")

client = chromadb.PersistentClient(path=persist_dir)

print("\nAvailable Collections:")
print(client.list_collections())

collection = client.get_collection(name="unt_rag")

model = SentenceTransformer("all-MiniLM-L6-v2")

def search(query, top_k=5, distance_threshold=1.5):

    print(f"\n🔍 Query: {query}")

    # Generate query embedding
    query_embedding = model.encode([query]).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    filtered_results = []

    for i in range(len(documents)):

        doc = documents[i]
        meta = metadatas[i]
        distance = distances[i]

        # Smaller distance = better semantic similarity
        if (
            len(doc.strip()) > 50
            and distance < distance_threshold
        ):

            filtered_results.append({
                "document": doc,
                "metadata": meta,
                "distance": distance
            })


    if not filtered_results:
        print("\n❌ No relevant chunks found.")
        return []

    print("\n================ RETRIEVED CHUNKS ================\n")

    for idx, result in enumerate(filtered_results):

        doc = result["document"]
        meta = result["metadata"]
        distance = result["distance"]

        source = meta.get("source", "unknown")
        chunk_type = meta.get("type", "unknown")

        print(f"Result {idx + 1}")
        print("=" * 70)

        print(f"Type      : {chunk_type}")
        print(f"Source    : {source}")
        print(f"Distance  : {distance:.4f}")

        if "slide_number" in meta:
            print(f"Slide No  : {meta['slide_number']}")

        print("\nRetrieved Chunk:\n")
        print(doc)

        print("\n" + "-" * 70 + "\n")

    return filtered_results


if __name__ == "__main__":

    while True:

        query = input("\nEnter your question (or 'exit'): ")

        if query.lower() == "exit":
            print("\n👋 Exiting retrieval system.")
            break

        search(query)