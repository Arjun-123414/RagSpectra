# 📄 Bid Document Classification & Q&A System

This project analyzes vendor bid documents (PDF / Excel), automatically classifies them into construction categories (HVAC, Electricity, Roofing, etc.), stores structured chunks using FAISS embeddings, and provides a Streamlit-based chat interface to compare and query bids using an LLM.

The system is designed to be transparent, structured, and easy to inspect at every stage.

---

## 🛠️ Initial Cleanup (Very Important)

Before running the project, **delete old generated data** to avoid conflicts:

1. Delete the `faiss_db` folder (if it exists)
2. Delete the `chunk_output.txt` file (if it exists)

This ensures embeddings and chunks are rebuilt from scratch.

---

## ▶️ Core Processing Pipeline

Run the following command:

python main.py

---

## 🔍 What `main.py` Does (Step-by-Step)

### 1. File Loading
- Reads all files from the `./data` folder
- Supports PDF and Excel vendor bid documents

### 2. Chunk Creation
- Each document is split into multiple meaningful text chunks
- Chunking logic is handled in `chunker.py`

### 3. Category Classification (Key Logic)
- **Only the FIRST chunk of each file** is sent to the LLM
- This chunk is used to determine the bid category:
  - HVAC
  - Electricity
  - Roofing
- This avoids unnecessary LLM calls and keeps classification cost-effective

### 4. Metadata Attachment
Each chunk is enriched with metadata:
- `category` → Determined by the LLM
- `source_file` → Original file name

### 5. FAISS Storage Structure

All chunks are stored as embeddings inside the `faiss_db` folder using this folder hierarchy:

```text
faiss_db/
├── HVAC/
│   ├── file_1/
│   ├── file_2/
├── Electricity/
│   ├── file_3/
├── Roofing/
│   ├── file_4/
```

Each **file has its own FAISS index** inside its category.

### 6. Chunk Visibility Output
- The file `chunk_output.txt` is generated
- For each file, it shows:
  - File name
  - First 3 chunks (truncated for readability)
- This helps visually verify chunk quality

### 7. Console Transparency
After execution, the terminal clearly shows:
- Which chunk was sent to the LLM
- Which category was determined
- Total chunks generated per file

This makes the classification process fully auditable.

---

## 📂 Inspecting FAISS Storage (Recommended)

After running `main.py`, execute:

python view_faiss.py

---

## 🔎 What `view_faiss.py` Shows

- Complete FAISS folder hierarchy
- Category-wise file organization
- Number of chunks stored per file
- Total chunks per category
- Grand total chunks across all categories

This is useful to understand:
- How embeddings are structured
- How many chunks exist per file
- How retrieval will work internally

---

## 💬 Running the Chat Application (Streamlit)

Launch the interactive chat interface:

streamlit run app.py

---

## 🧠 How the Chat System Works

### 1. Category Selection
- User selects a category (HVAC / Electricity / Roofing) from the sidebar
- Only files belonging to that category are searched

### 2. Chunk Retrieval Strategy
- The system searches **ALL files** inside the selected category
- From **each file**, it retrieves up to **N chunks** (default = 3)
- This ensures:
  - Fair representation of every file
  - No single bid dominates the context

### 3. Context Formatting
Retrieved chunks are grouped clearly like:

============================================================
FILE: vendor_bid_1.pdf
============================================================
[Chunk 1]
[Chunk 2]
[Chunk 3]

This structured context is sent to the LLM.

### 4. LLM Answering Rules
The LLM is strictly instructed to:
- Extract exact numbers per file
- Compare bids side-by-side
- Calculate price differences
- Identify cheaper / better bids
- Avoid assumptions
- Clearly mention missing data if any

---

## 🧪 Example Questions You Can Ask

- Which bid is best for plan 4101?
- Compare pricing between Vendor A and Vendor B
- Which bid offers better warranty terms?
- What is the price difference between the two HVAC bids?

---

## 📌 Design Highlights

- Only ONE chunk is used for classification (cost-efficient)
- Multiple chunks per file are used for answering (accuracy-focused)
- Category-based isolation for clean retrieval
- Full transparency via logs and inspection scripts
- Modular, scalable, and easy to extend

---

## ✅ Execution Summary

1. Delete `faiss_db` and `chunk_output.txt`
2. Run `python main.py`
3. (Optional) Run `python view_faiss.py`
4. Run `streamlit run app.py`
5. Select category → Ask questions → Get structured answers

---

Built with ❤️ using Python, Streamlit, LangChain, FAISS, and OpenAI
