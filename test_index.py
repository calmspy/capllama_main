from pprint import pprint

from llama_hub.confluence.base import ConfluenceReader
from llama_index.vector_stores import MilvusVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt

import os
pprint(dict(os.environ))

page_ids = ["464748589"]
space_key = "CAP"

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

base_url = "https://capspire.atlassian.net/wiki"

reader = ConfluenceReader(base_url=base_url)
print("loading base page")
# documents = reader.load_data(space_key=space_key, include_attachments=False, page_status="current")
# print(f"loading page ids {page_ids}")
documents = []
documents.extend(reader.load_data(page_ids=page_ids, include_children=False, include_attachments=False))
print("building index")
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)

# query_engine = index.as_query_engine()
# response = query_engine.query("What does crack spread mean?")
# print(response)

