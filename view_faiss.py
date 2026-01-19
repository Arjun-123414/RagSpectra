import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

FAISS_DB_FOLDER = "./faiss_db"
embeddings = OpenAIEmbeddings()

def view_faiss_contents():
    """View all chunks stored in each FAISS category/file folder"""
    
    # Check if faiss_db folder exists
    if not os.path.exists(FAISS_DB_FOLDER):
        print("❌ No faiss_db folder found. Run main.py first to classify and store documents.")
        return
    
    # Get all category folders
    categories = [f for f in os.listdir(FAISS_DB_FOLDER) if os.path.isdir(os.path.join(FAISS_DB_FOLDER, f))]
    
    if not categories:
        print("❌ No categories found in faiss_db folder.")
        return
    
    print("\n" + "=" * 70)
    print("FAISS VECTOR STORE STRUCTURE")
    print("=" * 70)
    
    for category in categories:
        category_path = os.path.join(FAISS_DB_FOLDER, category)
        
        # Get all file folders within this category
        file_folders = [f for f in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, f))]
        
        print(f"\n📁 {category}/")
        
        for file_idx, file_name in enumerate(file_folders):
            is_last_file = (file_idx == len(file_folders) - 1)
            file_prefix = "└──" if is_last_file else "├──"
            
            print(f"{file_prefix} 📄 {file_name}/")
            
            # Load FAISS index for this file
            file_path = os.path.join(category_path, file_name)
            try:
                db = FAISS.load_local(file_path, embeddings, allow_dangerous_deserialization=True)
                
                # Get chunk count
                docstore = db.docstore
                index_to_id = db.index_to_docstore_id
                chunk_count = len(index_to_id)
                
                # Print chunks
                for chunk_idx in range(chunk_count):
                    is_last_chunk = (chunk_idx == chunk_count - 1)
                    
                    if is_last_file:
                        chunk_prefix = "    └──" if is_last_chunk else "    ├──"
                    else:
                        chunk_prefix = "│   └──" if is_last_chunk else "│   ├──"
                    
                    print(f"{chunk_prefix} Chunk {chunk_idx + 1}")
                
                print(f"{'    ' if is_last_file else '│   '}📊 Total: {chunk_count} chunks")
                
            except Exception as e:
                print(f"    ❌ Error loading: {e}")
        
        print("-" * 50)
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_chunks = 0
    for category in categories:
        category_path = os.path.join(FAISS_DB_FOLDER, category)
        file_folders = [f for f in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, f))]
        
        category_chunks = 0
        for file_name in file_folders:
            file_path = os.path.join(category_path, file_name)
            try:
                db = FAISS.load_local(file_path, embeddings, allow_dangerous_deserialization=True)
                category_chunks += len(db.index_to_docstore_id)
            except:
                pass
        
        print(f"{category}: {len(file_folders)} files, {category_chunks} total chunks")
        total_chunks += category_chunks
    
    print(f"\n🎯 Grand Total: {total_chunks} chunks across all categories")
    print("=" * 70)

if __name__ == "__main__":
    view_faiss_contents()