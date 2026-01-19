# 📄 Project Setup & Usage Guide

This project processes vendor bid documents using chunking, categorization, embeddings (FAISS), and an LLM-powered chat interface to determine which category (HVAC, Electricity, Roofing, etc.) a bid belongs to and to answer user questions with proper context.

---

## 🛠️ Initial Setup (Important)

Before running the project, make sure to clean any previously generated data:

1. Delete the `faiss_db` folder (if it exists)
2. Delete the `chunk_output.txt` file (if it exists)

This ensures the system starts fresh and avoids mixing old chunks or embeddings.

---

## ▶️ Running the Core Pipeline

After cleanup, run the following command:

python main.py

### What `main.py` does:

- Reads vendor bid files (PDF / Excel)
- Splits each file into meaningful chunks
- Categorizes chunks into domains such as:
  - HVAC
  - Electricity
  - Roofing
- Stores chunks category-wise
- Generates embeddings and saves them into FAISS vector stores
- Writes chunk information into `chunk_output.txt` for visibility

1. After you run this code `faiss_db` folder will be created
2. `chunk_output.txt` file will be created
You can checkout both

### Category Classification Logic

Only the most relevant chunks are sent to the LLM.  
Using these chunks, the LLM determines which category (HVAC, Electricity, or Roofing) the bid file belongs to.

---

## 🔍 Viewing FAISS Structure (Optional)

After `main.py` finishes execution, you can inspect how chunks and embeddings are stored.

Run:

python view_faiss.py

### What this helps you understand:

- How chunks are organized inside FAISS
- The order of embeddings
- Category-wise folder and file structure
- Overall internal data organization

---

## 💬 Running the Chat Interface (Streamlit)

Start the Streamlit chat application using:

streamlit run app.py

### Chat Interface Features:

- Select a category (HVAC / Electricity / Roofing)
- Ask questions such as:
  - Which bid is best for plan 4101?
- The system:
  - Retrieves the most relevant chunks
  - Sends them as context to the LLM
  - Displays a clear answer
  - Shows the supporting context chunks on the side

---

## 🧠 Context Selection Strategy

- For each file within a selected category:
  - Up to 3 relevant chunks are selected
- This design ensures:
  - Balanced context across files
  - No single file dominates the answer
  - More accurate and reliable LLM responses

---

## ✅ Workflow Summary

1. Delete `faiss_db` and `chunk_output.txt`
2. Run `main.py` to process and categorize files
3. (Optional) Run `view_faiss.py` to inspect FAISS structure
4. Run `streamlit run app.py` to launch the chat interface
5. Select a category and ask questions using natural language

## app interface:
<img width="1912" height="960" alt="image" src="https://github.com/user-attachments/assets/665b9e16-3d04-422f-9421-15e28ec160e6" />

