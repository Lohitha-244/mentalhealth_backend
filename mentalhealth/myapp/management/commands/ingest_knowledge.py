import os
from django.core.management.base import BaseCommand
from pypdf import PdfReader

from myapp.rag import build_index


def chunk_text(text: str, chunk_size=900, overlap=150):
    words = (text or "").split()
    chunks = []
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + chunk_size]))
        i += (chunk_size - overlap)
    return chunks


class Command(BaseCommand):
    help = "Ingest a TXT/PDF file and build the FAISS RAG index"

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True)
        parser.add_argument("--source", type=str, default="kb")

    def handle(self, *args, **opts):
        path = opts["file"]
        source = opts["source"]

        if not os.path.exists(path):
            self.stdout.write(self.style.ERROR(f"File not found: {path}"))
            return

        # Read file content
        text = ""
        if path.lower().endswith(".pdf"):
            reader = PdfReader(path)
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
        else:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

        raw_chunks = chunk_text(text)

        chunks = [
            {"source": source, "title": f"chunk-{i+1}", "content": c}
            for i, c in enumerate(raw_chunks)
        ]

        build_index(chunks)

        self.stdout.write(self.style.SUCCESS(f"✅ Indexed {len(chunks)} chunks from {path}"))