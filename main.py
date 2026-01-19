import os
from loader import load_document
from chunker import chunk_docs
from classifier import classify_chunk
from vector_store import store_chunks

DATA_FOLDER = "./data"
OUTPUT_FILE = "./chunk_output.txt"

def write_chunks_output(all_files_data):
    """Write chunks from all files to a formatted text file (just chunks, no classification info)"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for file_data in all_files_data:
            file_name = file_data["file_name"]
            chunks = file_data["chunks"]
            
            # File name header with nice formatting
            f.write("-" * 80 + "\n")
            f.write("-" * 80 + "\n")
            f.write(f"{file_name}:\n")
            f.write("-" * 80 + "\n")
            f.write("-" * 80 + "\n\n")
            
            # Show first 3 chunks (or less if fewer available)
            num_chunks_to_show = min(3, len(chunks))
            
            for i in range(num_chunks_to_show):
                f.write(f"chunk {i + 1}:\n")
                chunk_text = chunks[i]["text"]
                # Truncate long chunks for readability
                display_text = chunk_text[:1500] + ("..." if len(chunk_text) > 1500 else "")
                f.write(display_text + "\n")
                f.write("----\n\n")
            
            f.write("\n")
    
    print(f"\n✅ Chunk output written to: {OUTPUT_FILE}")

def main():
    all_files_data = []
    
    for file in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, file)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue

        docs = load_document(file_path)
        chunks = chunk_docs(docs)

        # 🔑 classify only FIRST chunk
        first_chunk_text = chunks[0]["text"]
        category = classify_chunk(first_chunk_text)

        print(f"{file} → classified as {category}")

        # attach metadata
        for chunk in chunks:
            chunk["metadata"]["category"] = category
            chunk["metadata"]["source_file"] = file

        # store ALL chunks under category/filename
        store_chunks(category, file, chunks)
        
        # Collect data for output file
        all_files_data.append({
            "file_name": file,
            "chunks": chunks,
            "category": category,
            "classification_chunk": first_chunk_text
        })
    
    # Write chunks to output file
    write_chunks_output(all_files_data)
    
    # Print classification details to console
    print("\n" + "=" * 70)
    print("CLASSIFICATION DETAILS - CHUNK USED BY LLM")
    print("=" * 70)
    for file_data in all_files_data:
        print(f"\n📄 File: {file_data['file_name']}")
        print(f"📁 Category Determined: {file_data['category']}")
        print(f"📊 Total Chunks in File: {len(file_data['chunks'])}")
        print("-" * 50)
        print("Chunk given to LLM for classification:")
        print("-" * 50)
        # Show first 500 chars of the chunk used
        chunk_preview = file_data['classification_chunk'][:500]
        print(chunk_preview)
        if len(file_data['classification_chunk']) > 500:
            print("...")
        print("-" * 50)
        print(f"✅ LLM read this chunk and determined it belongs to: {file_data['category']}")
        print("=" * 70)

if __name__ == "__main__":
    main()