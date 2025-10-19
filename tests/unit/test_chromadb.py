import chromadb

# Initialize a ChromaDB client (e.g., PersistentClient for disk-based storage)
client = chromadb.PersistentClient(path="./chroma_db")

# Get or create a collection named "my_collection"
# You can also pass optional metadata when creating a new collection
collection = client.get_or_create_collection(
    name="my_collection",
    metadata={"hnsw:space": "cosine"} # Example: set distance metric for HNSW index
)

# Now you can interact with the 'collection' object
# For example, adding documents:
collection.add(
    documents=["This is a document.", "Another document for the collection."],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)