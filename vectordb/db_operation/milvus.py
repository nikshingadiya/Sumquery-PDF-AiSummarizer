import time
import hashlib
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from pymilvus import utility
class MilvusTextVectorStore:
    def __init__(self, uri, token, collection_name, vector_dimension):
        self.uri = uri
        self.token = token
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        self.collection = None
        self.collection_schema = CollectionSchema(
                    fields=[
                        FieldSchema(name="text_id", dtype=DataType.INT64,is_primary=True),
                        FieldSchema(name="pdf_name", dtype=DataType.VARCHAR,max_length=256),
                        FieldSchema(name="pdf_unique_id", dtype=DataType.INT64),
                        FieldSchema(name="text", dtype=DataType.VARCHAR,max_length=65535),
                        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.vector_dimension)
                    ],
                   enable_dynamic_field=True
                )

        # Connect to Milvus
        self.connect_to_milvus()

        # Define Milvus collection, create if not exists
        self.define_milvus_collection()

    def connect_to_milvus(self):
        connections.connect(uri=self.uri, token=self.token)
        print(f"Connecting to Milvus DB: {self.uri}")

    def define_milvus_collection(self):
     
        # Check if the collection exists
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            print(f"Milvus collection '{self.collection_name}' already exists.")
        else:
            index_params = {
            "metric_type":"L2",
            "index_type":"IVF_FLAT",
            "params":{"nlist":1024}
            }
            self.collection = Collection(name=self.collection_name, schema=self.collection_schema)
            self.collection.create_index(
            field_name="vector", 
            index_params=index_params,
            index_name="vec_index"
            )


            print(f"Milvus collection '{self.collection_name}' created")
     

    def generate_unique_id(self, pdf_name):
        # Generate a unique identifier based on the PDF name using a hash function
        hash_object = hashlib.md5(pdf_name.encode())
        unique_id = int(hash_object.hexdigest(), 16) % (10 ** 18)  # Limit to 18 digits
        return unique_id
    
    def row_query(self):
        pdf_unique_id=234
        self.collection.load()
        existing_entities = self.collection.query(expr=f"pdf_unique_id=={pdf_unique_id}")
        max_text_id = 0
        res =self.collection.query(
        expr="text_id>=0",
        output_fields = ["text_id"],
        )# Sorting by 'text_id' in descending order
        sorted_res = sorted(res, key=lambda k: k['text_id'])
        print("sorted_res",res)
        return sorted_res

    def pdf_vectorstore_with_text_and_auto_increment(self, pdf_name, texts):
        start_time = time.time()
        embeddings = HuggingFaceEmbeddings()

        # Generate a unique identifier for the PDF name
        pdf_unique_id = self.generate_unique_id(pdf_name)

        # Check if the PDF with the same unique identifier already exists in the collection
        self.collection.load()
        existing_entities = self.collection.query(expr=f"pdf_unique_id=={pdf_unique_id}")
        if len(existing_entities)>0:
            print(f"PDF with name '{pdf_name}' and unique identifier '{pdf_unique_id}' already exists. Skipping insertion.")
            return
        else:

            # Determine the current maximum text ID in the collection
            max_text_id = 0
            res =self.collection.query(
            expr="text_id>=0",
            output_fields = ["text_id"],
            )# Sorting by 'text_id' in descending order
            sorted_res = sorted(res, key=lambda k: k['text_id'])
            print("sorted_res",res)
    
            if len(sorted_res)>0:
                entities = sorted_res[0]
                max_text_id = entities

            # Process texts and auto-increment text IDs
            for text in texts:
                max_text_id += 1
                embedding = embeddings.embed_documents(text)[0]

                # Insert the vector along with the text, text ID, PDF name, and unique PDF identifier
                vector_data = {
                    "text_id": max_text_id,
                    "pdf_name": pdf_name,
                    "pdf_unique_id": pdf_unique_id,
                    "text": text,
                    "vector": embedding
                }
                self.collection.insert([vector_data])

            end_time = time.time()
            elapsed_time = end_time - start_time
            print("Computed and stored knowledge_base in:", elapsed_time)
