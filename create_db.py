import chromadb
from pathlib import Path
import uuid

# chroma_client = chromadb.HttpClient(host="localhost", port=8000)
# # # chroma_client.delete_collection(name="my_collection")
# # collection = chroma_client.create_collection(name="my_collection")

# collection = chroma_client.get_or_create_collection(name="gdpr")

class Tools:
    def __init__(self):
        pass

    def query_collection(self, query_texts: list[str]):
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        collection = chroma_client.get_collection(name="gdpr")
        results = collection.query(query_texts=query_texts, n_results=5)
        return results

# with open("notes/resume.txt", "r", encoding="utf-8") as f:
#     text = f.read()
#     collection.upsert(
#         ids=[str(uuid.uuid4())], 
#         documents=[text],
#         metadatas=[{"source": "resume.txt"}]
#         )

query_texts = ["This is a query about the supervisory authority of the GDPR."]
tool = Tools()
results = tool.query_collection(query_texts=query_texts)
print(results)