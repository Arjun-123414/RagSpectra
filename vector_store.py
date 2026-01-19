from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import os

embeddings = OpenAIEmbeddings()

def store_chunks(category, file_name, chunks):
    """Store chunks for a specific file within a category"""
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    # Create path: faiss_db/CATEGORY/FILENAME/
    path = f"faiss_db/{category}/{file_name}"

    if os.path.exists(path):
        db = FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        db.add_texts(texts, metadatas)
    else:
        os.makedirs(path, exist_ok=True)
        db = FAISS.from_texts(texts, embeddings, metadatas)

    db.save_local(path)