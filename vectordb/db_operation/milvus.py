
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

connections.connect("default", host="localhost", port="19530")


# Define your Milvus collection name and dimension
MILVUS_COLLECTION_NAME = "PDF_VECTOR"
VECTOR_DIMENSION = 768  # Change this to the dimension of your vectors

def pdf_vectorstore(text_chunks):
    # Compute the knowledge base
    start_time = time.time()
    embeddings = HuggingFaceEmbeddings()
    knowledge_base = embeddings.encode(text_chunks)  # Encode your text_chunks into vectors
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Computed knowledge_base in:", elapsed_time)

    # Create a Milvus collection and insert the vectors
    collection = Collection(MILVUS_COLLECTION_NAME)
    if not collection.exists:
        collection_schema = CollectionSchema(
            fields=[
                FieldSchema(name="vector", data_type=DataType.FLOAT_VECTOR, dim=VECTOR_DIMENSION)
            ]
        )
        collection.create_collection(collection_schema)
        collection.load()
        print(f"Milvus collection '{MILVUS_COLLECTION_NAME}' created")

    # Insert the vectors into the Milvus collection
    collection.insert([knowledge_base])

fields = [
    FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=False),
    FieldSchema(name="random", dtype=DataType.DOUBLE),
    FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=8)
]
schema = CollectionSchema(fields, "hello_milvus is the simplest demo to introduce the APIs")
hello_milvus = Collection("hello_milvus", schema)

import random
entities = [
    [i for i in range(3000)],  # field pk
    [float(random.randrange(-20, -10)) for _ in range(3000)],  # field random
    [[random.random() for _ in range(8)] for _ in range(3000)],  # field embeddings
]
insert_result = hello_milvus.insert(entities)
# After final entity is inserted, it is best to call flush to have no growing segments left in memory
hello_milvus.flush()  

