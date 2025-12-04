import os, time
import requests
from datetime import datetime
import chromadb


class Tools:
    def __init__(self):
        pass

    def _embed(self, text: str):
        start = time.time()
        resp = requests.post(
            "http://localhost:8001/embeddings", json={"text": text}, timeout=20
        )

        elapsed = time.time() - start
        print(f"RESPONSE TIME: {elapsed:.3f}s")
        print("STATUS:", resp.status_code)
        return resp.json()["embedding"]

    def _rerank(self, query_text: str, results: dict):
        start = time.time()
        items = [
            {"id": id_, "text": result["document"]} for id_, result in results.items()
        ]

        request_payload = {"query": query_text, "items": items, "top_n": len(items)}
        resp = requests.post(
            "http://localhost:8001/reranking", json=request_payload, timeout=20
        )
        elapsed = time.time() - start
        print(f"RESPONSE TIME: {elapsed:.3f}s")
        print(f"RERANK STATUS: {resp.status_code}")
        return resp.json()

    def query_collection(self, query_text: str, collection: str):
        """
        This is a simple tool to send a query to a ChromaDB database. Calling it is
        easy.

        Arguments:
            - query_text, a string, the text of the query you want to send
            - collection, a string, the name of the collection you want to search.

            results = Tools().query_collection("<This is where the query goes>", "<the name of the collection to search>")

        ... then process the results to answer the question asked by the user.

        the collections available for query are: gdpr
        """
        emb = self._embed(query_text)
        chroma_client = chromadb.HttpClient(host="localhost", port=8000)
        col = chroma_client.get_collection(name=collection)
        raw = col.query(query_embeddings=[emb], n_results=10)

        results = {}

        ids = raw.get("ids", [[]])[0]
        docs = raw.get("documents", [[]])[0]
        metas = raw.get("metadatas", [[]])[0]
        dists = raw.get("distances", [[]])[0]

        for i in range(len(ids)):
            results[ids[i]] = {
                "document": docs[i],
                "metadata": metas[i],
                "distance": dists[i],
            }

        reranked = self._rerank(query_text=query_text, results=results)
        final = [
            {
                "id": item["id"],
                "score": item["score"],
                "document": results[item["id"]]["document"],
                "metadata": results[item["id"]]["metadata"],
                "distance": results[item["id"]]["distance"],
            }
            for item in reranked["results"]
        ]
        print(f"response type: {type(final)}")
        return final