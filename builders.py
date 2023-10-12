from llama_index import StorageContext, ServiceContext, VectorStoreIndex
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt
from llama_index.vector_stores import MilvusVectorStore
import requests
from pathlib import Path
from functools import lru_cache
from loguru import logger


@lru_cache(maxsize=1)
def build_llama_2_llm():
    model_path = Path("./llama-2-13b-chat.Q4_0.gguf")

    if not model_path.exists():
        logger.info("Downloading Llama model from huggingface...")
        url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_0.gguf"

        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with model_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

    return LlamaCPP(
        model_url=None,
        model_path=str(model_path),
        temperature=0.1,
        max_new_tokens=1024,
        context_window=3900,
        generate_kwargs={},
        model_kwargs={"n_gpu_layers": 43},
        messages_to_prompt=messages_to_prompt,
        completion_to_prompt=completion_to_prompt,
        verbose=True,
    )


@lru_cache(maxsize=1)
def build_embed_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")


@lru_cache(maxsize=1)
def build_read_vector_store():
    return MilvusVectorStore(dim=1024, overwrite=False)


@lru_cache(maxsize=1)
def build_write_vector_store():
    return MilvusVectorStore(dim=1024, overwrite=True)


def build_storage_context(vector_store):
    return StorageContext.from_defaults(vector_store=vector_store)


def build_service_context():
    return ServiceContext.from_defaults(
        llm=build_llama_2_llm(),
        embed_model=build_embed_model(),
    )


@lru_cache(maxsize=1)
def build_read_index():
    return VectorStoreIndex.from_vector_store(
        build_read_vector_store(),
        storage_context=build_storage_context(vector_store=build_read_vector_store()),
        service_context=build_service_context(),
    )


def build_write_index(documents):
    return VectorStoreIndex.from_documents(
        documents,
        storage_context=build_storage_context(vector_store=build_write_vector_store()),
        service_context=ServiceContext.from_defaults(
            llm=None,
            embed_model=build_embed_model(),
        ),
    )


def reset():
    build_llama_2_llm.cache_clear()
    build_embed_model.cache_clear()
    build_read_vector_store.cache_clear()
    build_write_vector_store.cache_clear()
    build_read_index.cache_clear()
    logger.info("Caches cleared")
