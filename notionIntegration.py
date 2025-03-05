import requests
from datetime import datetime, timezone

NOTION_TOKEN = config.NOTION_TOKEN
DATABASE_ID_TODO = config.DATABASE_ID_TODO
DATABASE_ID_SUMMARY = config.DATABASE_ID_SUMMARY



headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def create_page(data: dict, type):
    if type == "todo":
        DATABASE_ID = DATABASE_ID_TODO
    elif type == "note":
        DATABASE_ID = DATABASE_ID_SUMMARY
    else:
        return
    
    create_url = "https://api.notion.com/v1/pages"
    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)
    print(res.status_code)
    return res

# type = "note"
# content = "create this"
# ddate = datetime.now().astimezone(timezone.utc).isoformat()

# data = {
#     "Type": {"title": [{"text": {"content" : type}}]},
#     "Content": {"rich_text": [{"text": {"content" : content}}]},

# }
# print(data)
# create_page(data, type)
