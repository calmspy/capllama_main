import os
from pprint import pprint

from atlassian import Confluence

api_token = os.getenv("CONFLUENCE_PASSWORD")
base_url = "https://capspire.atlassian.net/wiki"

pprint(api_token)

conf = Confluence(
    url=base_url, username="james.vogel@capspire.com", password=api_token, cloud=True
)

page_id = "464748589"
resp = conf.get_page_by_id(
    page_id=page_id,
    expand="body.storage.value",
)

pprint(resp)
