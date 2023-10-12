import gc
from pprint import pprint
from time import sleep

from llama_hub.confluence.base import ConfluenceReader
from loguru import logger
from slack_bolt.adapter.socket_mode import SocketModeHandler

from builders import build_write_index, build_read_index, reset, build_service_context
from slack_bolt import App


def load_confluence_data(include_attachments=False):
    space_keys = ["CAP", "RA", "TRAIN", "AL"]
    base_url = "https://capspire.atlassian.net/wiki"
    reader = ConfluenceReader(base_url=base_url)
    logger.info("loading space page")
    documents = []
    for key in space_keys:
        logger.info(f"loading space {key}")
        new_documents = reader.load_data(
            space_key=key,
            include_attachments=include_attachments,
            page_status="current",
        )
        logger.info(f"loaded {len(new_documents)} documents")
        documents.extend(new_documents)
    logger.info("building index")
    build_write_index(documents)


def ask(question: str) -> str:
    question = question.strip()
    if question.startswith("dbg"):
        # remove dbg from the question process it normally
        # then return the response plus some new lines and the links to the relevant documents
        # in metadata
        question = question[3:].strip()

    index = build_read_index()
    query_engine = index.as_query_engine()
    response = query_engine.query(question)

    return f"{response.response }\n\nI used these sources:\n" + "\n".join(
        [
            f"<{page_info['url']}|{page_info['title']}>"
            for _, page_info in (response.metadata or {}).items()
        ]
    )


app = App(token=bot_token)


@app.event("app_mention")
def handle_mention(client, event, logger):
    text = event.get("text", "")
    question = text.split(" ", 1)[1]
    if question.strip() == "rebuild":
        client.chat_postMessage(
            channel=event["channel"],
            text="Starting Rebuild Dont ask Questions or stuff will probably break",
        )
        reset()
        gc.collect()
        load_confluence_data(include_attachments=False)
        reset()
        gc.collect()
        logger.info("sleeping for 5 seconds")
        sleep(5)
        build_service_context()
        client.chat_postMessage(
            channel=event["channel"], text="Completed Rebuild, go off and play again"
        )
    else:
        response = ask(question)
        client.chat_postMessage(channel=event["channel"], text=response)


if __name__ == "__main__":
    # build_service_context()
    # load_confluence_data()
    handler = SocketModeHandler(app, app_token)
    handler.start()
