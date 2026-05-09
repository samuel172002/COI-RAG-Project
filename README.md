# COI-RAG-Project
This project is for COI Advising office to help perspective students to find information about degree plans.

Clone Repository

git clone https://github.com/samuel172002/COI-RAG-Project.git

cd COI-RAG-Project

Create Virtual Environment

python -m venv venv

Activate Virtual Environment
Windows

venv\Scripts\activate

pip install --upgrade pip

Install Dependencies

pip install -r requirements.txt

If the file is not available, do he following commands:

pip install chromadb
pip install sentence-transformers
pip install torch
pip install pymupdf

Build ChromaDB

python build_chroma_db.py

Run Retrieval System

python query_chroma.py

Example Query

What are the degree requirements for MS Data Science?