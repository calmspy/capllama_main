from llama_index.llms import LlamaCPP
from llama_index.llms.llama_utils import messages_to_prompt, completion_to_prompt

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

if __name__ == '__main__':
    response = llm.complete("Hello! Can you tell me a poem about cats and dogs?")
    print(response.text)
    from pprint import pprint
    pprint([x for x in dir(response) if not x.startswith("_")])
