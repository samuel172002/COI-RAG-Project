import chromadb
import os

persist_dir = os.path.abspath("chroma_db")

client = chromadb.PersistentClient(path=persist_dir)

collection = client.get_collection(name="unt_rag")

data = collection.get()
print("\nTotal Chunks Stored:", len(data["ids"]))

for i in range(len(data["ids"])):

    print("\n" + "=" * 80)

    print(f"ID: {data['ids'][i]}")

    print("\nMETADATA:")
    print(data["metadatas"][i])

    print("\nDOCUMENT:")
    print(data["documents"][i][:1000])  # first 1000 chars

    print("\n" + "=" * 80)