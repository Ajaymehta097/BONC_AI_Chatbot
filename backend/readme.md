# BONC B2B Network - AI Assistant

A highly accurate, hybrid Artificial Intelligence chatbot designed exclusively for the **BONC Network**. This bot uses advanced semantic vector search (FAISS) and NLP (Natural Language Processing) to help users find B2B products, verified suppliers, and categories from a database of 24 JSON files, while strictly rejecting non-business queries.

## 🚀 Key Features

* **Hybrid Architecture:** Combines a blazing-fast Rule-Based Engine (for greetings/support) with an advanced AI Vector Search Engine (for product discovery).
* **Semantic Search:** Understands the *meaning* behind queries instead of relying on exact keyword matches.
* **Auto-Language Detection:** Seamlessly detects whether the user is typing in English or Hinglish and responds in the appropriate tone.
* **Strict Accuracy Filter (Threshold 1.20):** Employs mathematical distance checking to ensure the bot strictly answers B2B queries and politely rejects irrelevant/random questions.
* **Hinglish Query Cleaner:** Automatically strips conversational Hinglish noise (e.g., "mujhe", "dikhao") before vectorizing to maintain high AI accuracy.
* **Smart Location Extractor (📍):** Dynamically hunts for geographical data (City, State, Pincode) inside complex JSON structures and highlights it for the user.
* **Auto-Formatter & SEO Cleaner:** Hides ugly system IDs, creation dates, and SEO metadata, converting raw JSON into a clean, human-readable response.

---

## 📂 Project Structure

    BONC-AI-CHATBOT/
    │
    ├── backend/
    │   ├── data/                 # Directory containing the original 24 MS SQL JSON files
    │   ├── b2b_index.faiss       # The compiled mathematical AI brain (Vector Database)
    │   ├── metadata.json         # The mapping file linking vectors to actual business text
    │   ├── chat.py               # 🌟 MAIN FILE: The Hybrid AI Chatbot Engine
    │   └── app.py                # Server file (Flask/FastAPI) to connect with the frontend

---

## 💻 Installation & Setup

**1. Prerequisites**
Ensure you have Python 3.8+ installed on your system.

**2. Install Required Libraries**
Open your terminal (VS Code) and run the following command to install the required AI and mathematical processing libraries:

    pip install sentence-transformers faiss-cpu numpy

*(Note: On the first run, the `sentence-transformers` library will download the `all-MiniLM-L6-v2` model (~80MB) for offline use.)*

---

## 🛠 How to Run (Testing Mode)

To test the chatbot locally in your terminal, navigate to the `backend` folder and execute the main Python script:

    cd backend
    python chat.py

Type your queries in the terminal. Type `exit` or `quit` to stop the program.

**Test Cases to Try:**
* *Rule Engine:* `Hello` or `I need support`
* *Semantic Match:* `I want outdoor audio systems` (Should find "Outdoor Speakers")
* *Hinglish Match:* `Karnal area ke medicine dealers dikhao`
* *Strict Reject:* `Tell me a joke` or `Order a pizza` (Should be rejected)

---

## ⚙️ Configuration & Tweaking

If you need to adjust the chatbot's behavior in the future, you can easily modify these variables inside `chat.py`:

* **`THRESHOLD = 1.20`**: Located in the `vector_search_engine` function. 
    * *Decrease* (e.g., `1.05`) to make the bot stricter (requires near-perfect matches).
    * *Increase* (e.g., `1.30`) to make the bot more relaxed (accepts looser matches and spelling errors).
* **`hinglish_noise`**: Add more conversational Hindi/Hinglish words to this list to ensure the AI ignores them and focuses only on the core search intent.
* **`ignore_keywords`**: Add any new technical database column names here that you want to hide from the end-user's screen.

---

## 🧠 Architecture Overview

1. **Input:** User types a message.
2. **Language Check:** Analyzes if the tone is English or Hinglish.
3. **Layer 1 (Rules):** Regex checks for greetings/support. If matched, returns O(1) fast response.
4. **Query Cleaning:** If passed to Layer 2, strips conversational stop-words.
5. **Vectorization:** `SentenceTransformer` converts the cleaned text into a 384-dimensional vector.
6. **FAISS Search:** Compares the vector against `b2b_index.faiss` using L2 Euclidean distance.
7. **Threshold Validation:** Rejects matches where the distance is > 1.20.
8. **Output Generation:** Fetches the matching ID from `metadata.json`, extracts locations, hides SEO data, and returns a formatted string to the user.