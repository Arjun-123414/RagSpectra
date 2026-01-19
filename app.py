import streamlit as st
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Configuration
FAISS_DB_FOLDER = "./faiss_db"
embeddings = OpenAIEmbeddings()
llm = ChatOpenAI(temperature=0, api_key=os.getenv("OPENAI_API_KEY"))

# RAG Prompt Template
rag_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a construction bid analysis expert. Analyze the bid documents carefully and provide accurate comparisons.

Context from bid documents:
{context}

User's Question: {question}

IMPORTANT INSTRUCTIONS:
1. EXTRACT exact numbers from EACH file separately
2. If comparing bids, create a clear comparison table like:
   | Item | File 1 (name) | File 2 (name) |
   |------|---------------|---------------|
   | Price | $X | $Y |
   
3. ALWAYS identify which bid is CHEAPER/BETTER with exact price difference
4. If prices differ, calculate: "File X is $Z cheaper than File Y"
5. Include ALL relevant details: tonnage, system type, PO breakdowns
6. If data is unclear or missing, say exactly what's missing
7. DO NOT make assumptions - only use data from context

ANSWER FORMAT:
1. Data from each file (with file name)
2. Side-by-side comparison (if applicable)
3. Clear recommendation with reasoning
4. Price difference calculation

Answer:
"""
)


def get_available_categories():
    """Get list of categories from faiss_db folder"""
    if not os.path.exists(FAISS_DB_FOLDER):
        return []
    
    categories = [f for f in os.listdir(FAISS_DB_FOLDER) 
                  if os.path.isdir(os.path.join(FAISS_DB_FOLDER, f))]
    return categories


def get_files_in_category(category):
    """Get list of files within a category"""
    category_path = os.path.join(FAISS_DB_FOLDER, category)
    if not os.path.exists(category_path):
        return []
    
    files = [f for f in os.listdir(category_path) 
             if os.path.isdir(os.path.join(category_path, f))]
    return files


def load_faiss_index(category, file_name):
    """Load FAISS index for a specific file within a category"""
    path = os.path.join(FAISS_DB_FOLDER, category, file_name)
    try:
        db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        st.error(f"Error loading {file_name} index: {e}")
        return None


def search_across_all_files(category, query, chunks_per_file=3):
    """Search across all files in a category and get top chunks from each"""
    files = get_files_in_category(category)
    all_results = []
    
    for file_name in files:
        db = load_faiss_index(category, file_name)
        if db:
            results = db.similarity_search_with_score(query, k=chunks_per_file)
            for doc, score in results:
                doc.metadata["source_file"] = file_name  # Ensure source is set
                all_results.append((doc, score, file_name))
    
    # Sort by score (lower is better for FAISS L2 distance)
    all_results.sort(key=lambda x: x[1])
    
    return all_results


def format_context(results):
    """Format retrieved chunks into context string with clear file separation"""
    # Group chunks by file first
    chunks_by_file = {}
    for doc, score, file_name in results:
        if file_name not in chunks_by_file:
            chunks_by_file[file_name] = []
        chunks_by_file[file_name].append((doc, score))
    
    context_parts = []
    for file_name, chunks in chunks_by_file.items():
        context_parts.append(f"\n{'='*60}")
        context_parts.append(f"FILE: {file_name}")
        context_parts.append(f"{'='*60}")
        
        for i, (doc, score) in enumerate(chunks, 1):
            context_parts.append(f"\n[Chunk {i}]")
            context_parts.append(doc.page_content)
        
        context_parts.append("")
    
    return "\n".join(context_parts)


def get_llm_response(context, question):
    """Get response from LLM using RAG"""
    prompt = rag_prompt.format(context=context, question=question)
    response = llm.invoke(prompt)
    return response.content


# ===================== STREAMLIT UI =====================

st.set_page_config(
    page_title="Bid Document Q&A",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Bid Document Q&A System")
st.markdown("---")

# Sidebar - Category Selection
with st.sidebar:
    st.header("⚙️ Settings")
    
    categories = get_available_categories()
    
    if not categories:
        st.error("❌ No categories found! Run main.py first to classify documents.")
        st.stop()
    
    selected_category = st.selectbox(
        "Select Category:",
        options=categories,
        help="Choose the bid category to search in"
    )
    
    st.markdown("---")
    
    # Show files in selected category
    files_in_category = get_files_in_category(selected_category)
    st.markdown(f"**📁 Files in {selected_category}:**")
    for f in files_in_category:
        st.markdown(f"- {f}")
    
    st.markdown("---")
    
    # Number of chunks per file to retrieve
    chunks_per_file = st.slider(
        "Chunks per file:",
        min_value=1,
        max_value=5,
        value=3,
        help="Number of chunks to retrieve from each file"
    )
    
    st.markdown("---")
    st.info(f"Will search across {len(files_in_category)} files, retrieving {chunks_per_file} chunks each")

# Main Area
col1, col2 = st.columns([1, 1])

with col1:
    st.header(f"💬 Ask about {selected_category} Bids")
    
    # Chat input
    user_question = st.text_area(
        "Enter your question:",
        placeholder="e.g., Which bid has the lowest price for plan 4101? Compare the warranties offered.",
        height=100
    )
    
    ask_button = st.button("🔍 Ask Question", type="primary", use_container_width=True)

with col2:
    st.header("📋 Retrieved Context")
    context_placeholder = st.empty()

# Process question
if ask_button and user_question:
    with st.spinner("🔍 Searching across all files..."):
        # Get relevant chunks from ALL files in category
        results = search_across_all_files(selected_category, user_question, chunks_per_file)
        
        if not results:
            st.error("No results found!")
            st.stop()
        
        # Format context
        context = format_context(results)
        
        # Display retrieved chunks grouped by file
        with context_placeholder.container():
            st.markdown("**Chunks retrieved from each file:**")
            
            # Group by file
            chunks_by_file = {}
            for doc, score, file_name in results:
                if file_name not in chunks_by_file:
                    chunks_by_file[file_name] = []
                chunks_by_file[file_name].append((doc, score))
            
            for file_name, chunks in chunks_by_file.items():
                st.markdown(f"**📄 {file_name}**")
                for i, (doc, score) in enumerate(chunks, 1):
                    with st.expander(f"Chunk {i} (Score: {1-score:.2f})"):
                        st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
    
    with st.spinner("🤖 Generating answer..."):
        # Get LLM response
        answer = get_llm_response(context, user_question)
    
    # Display answer
    st.markdown("---")
    st.header("✅ Answer")
    st.markdown(answer)
    
    # Show sources summary
    st.markdown("---")
    st.subheader("📚 Sources Used")
    for file_name in chunks_by_file.keys():
        st.markdown(f"- {file_name} ({len(chunks_by_file[file_name])} chunks)")

elif ask_button and not user_question:
    st.warning("⚠️ Please enter a question first!")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit + LangChain + FAISS + OpenAI*")