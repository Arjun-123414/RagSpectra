def chunk_docs(docs):
    chunks = []
    for doc in docs:
        chunks.append({
            "text": doc.page_content,
            "metadata": doc.metadata
        })
    return chunks
