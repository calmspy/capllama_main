from llama_index.vector_stores import MilvusVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt
from llama_index import download_loader
import os

vector_store = MilvusVectorStore(dim=1024, overwrite=True)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

model_path = "./llama-2-13b-chat.Q4_0.gguf"
llm = LlamaCPP(
    model_url=None,
    model_path=model_path,
    temperature=0.1,
    max_new_tokens=256,
    context_window=3900,
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": 1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=True,
)

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")
service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embed_model,
)

NotionPageReader = download_loader("NotionPageReader")

# page_ids = ["<page_id>"]
reader = NotionPageReader(integration_token=integration_token)
documents = reader.load_data(page_ids=["d288a93e0fa64d4fb0ab58fc23a7017f"])
print("building index")
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, service_context=service_context
)

# query_engine = index.as_query_engine()
# response = query_engine.query("What does crack spread mean?")
# print(response)
