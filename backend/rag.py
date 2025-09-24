import os

class VectorStore:
    def __init__(self, index_dir: str):
        self.index_dir = index_dir
        os.makedirs(index_dir, exist_ok=True)
        print(f"[DEBUG] VectorStore initialized with index dir: {self.index_dir}")

    def ingest_folder(self, folder: str):
        print(f"[DEBUG] Ingesting folder: {folder}")

        if not os.path.exists(folder):
            print(f"[ERROR] Folder does not exist: {folder}")
            return []

        files = os.listdir(folder)
        print(f"[DEBUG] Found files: {files}")

        chunks = []
        for file in files:
            path = os.path.join(folder, file)

            # Skip non-txt files for now
            if not file.lower().endswith(".txt"):
                print(f"[DEBUG] Skipping non-text file: {file}")
                continue

            print(f"[DEBUG] Reading file: {path}")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read().strip()

                if text:
                    chunks.append(text)
                    print(f"[DEBUG] Added chunk from {file}: {text[:50]}...")
                else:
                    print(f"[WARN] File {file} was empty.")
            except Exception as e:
                print(f"[ERROR] Could not read {file}: {e}")

        print(f"[DEBUG] Total chunks created: {len(chunks)}")
        return chunks

    def search(self, query: str, k: int = 5):
        # For now, just return all stored chunks (placeholder)
        print(f"[DEBUG] Performing search for: {query}")
        return [(f"Dummy result for '{query}'", 1.0)]
