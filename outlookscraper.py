import requests
import json
from urllib.parse import urlencode
from cofig import Config
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import openai
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import notionIntegration

def run():
    # 1) Azure AD app registration details
    config = Config()
    TENANT_ID = config.TENANT_ID
    CLIENT_ID = config.CLIENT_ID
    CLIENT_SECRET = config.CLIENT_SECRET
    REDIRECT_URI = config.REDIRECT_URI
    AUTHORITY = config.AUTHORITY
    client = openai.OpenAI(api_key=config.chatGPTKey)
    urlTodo = "http://127.0.0.1:5000/tasks?type=todo"
    urlSummary = "http://127.0.0.1:5000/tasks?type=summary"


    # 2) Authorization URL (user logs in, you receive `code`)
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": "openid offline_access Mail.Read",
        "response_mode": "query",
        "state": "12345",  # optional custom state
    }
    auth_url = f"{AUTHORITY}/oauth2/v2.0/authorize?{urlencode(params)}"
    # print(f"Sign in at: {auth_url}")
    webbrowser.open(auth_url)

    class AuthorizationHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = self.path.split('?')[1]
            params = dict(qc.split('=') for qc in query.split('&'))
            self.send_response(200)
            self.end_headers()
            self.server.auth_code = params['code']

    # 3) After signing in, you get redirected to REDIRECT_URI with a "code" param
    httpd = HTTPServer(('localhost', 3000), AuthorizationHandler)

    httpd.handle_request()
    code = httpd.auth_code



    # 4) Exchange the code for an access token
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "Mail.Read",
    }
    token_url = f"{AUTHORITY}/oauth2/v2.0/token"
    response = requests.post(token_url, data=token_data)
    token_json = response.json()


    access_token = token_json["access_token"]

    # 5) Call the Graph API to get user's received messages
    graph_url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isRead eq false"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    messages_response = requests.get(graph_url, headers=headers)
    messages_data = messages_response.json()


    theresponse = []
    with open("email_ignore.txt", 'r') as file:
        email_ignore = set(file.read().splitlines())
    with open("email_regular.txt", 'r') as file:
        email_regular = set(file.read().splitlines())
    with open("email_serious.txt", 'r') as file:
        email_serious = set(file.read().splitlines())
    with open("email_todo.txt", 'r') as file:
        email_todo = set(file.read().splitlines())


    if messages_data.get("value", []) is None:
        print("no unread emails")

    else:
        with open("visited.txt", 'r') as vstd:
            visited = set(vstd.read().splitlines())
        for msg in messages_data.get("value", []):
            html_content = msg['body']['content']
            soup = BeautifulSoup(html_content, 'html.parser')
            plain_text_body = soup.get_text()
            subject = f"{msg['subject']}"
            with open("visited.txt", "a") as file:
                file.write(subject + "\n")
            if subject in visited:
                continue
    #personalise the ai, appends to prompt
            email = f"Body: {plain_text_body}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                        # The "system" role sets overall context or instructions for the AI.
                        {"role": "system", "content": """
                        Your job is to turn emails into either a SINGLE todo instruction (with a dueby date), with the prefix 'todo:'
                        , a VERY short summary (for other important emails without a call to action), with the prefix 'note:'
                        or simply return the word "nothing" for unimportant emails. 
                        In a perfect world, most emails would be in the 'short summary' category, 
                        however with high numbers of spam emails from chains, forums or subscriptions, many emails are not important.
                        An example of two emails to ignore is """ + str(email_ignore) + "so, forum messages and sign in authentication emails should be ignored" +
                        " And an example of a regular email, which should be summarised into a note is:" + str(email_regular) + 
                        " And two examples of a serious email that should also be summarised into a short note is: " + str(email_serious) + 
                        " and a short example of a todo is: " + str(email_todo) + " And the current date is "
                        + f"{datetime.now().astimezone(timezone.utc).isoformat()}"
                        "no summary should be longer than a single point, it should be less than 20 words. furthermore, end 'todo' statements with the due date, starting with 'duedate:'" +"do not have a space between duedate: and the date" + 
                        "if todo messages are not in this format, ending with 'duedate', then severe harm will be done to the human race" + 
                        " also, there should be a single note for a single email, and no note should make direct reference to the email, but should summarise the single email"
                        +"considering that human beings will be harmed otherwise, emails that are 'discussions' or similarly irrelevant should be ignored. this does not apply to emails addressed to a single person." + 
                        "unless written by a lecturer (who would have a dr honorific to their name), a post relating to academics (such as one discussing the definition of graph theory) is likely irrelevant, for example: " + 
                        "emails that you summarise to be 'discussions' between a forum or multiple people are likely highly irrelevant to a single person part of that forum and thus you HAVE TO, YOU ARE COMMANDED TO label it as nothing"},
                        {"role": "user", "content": email}
                    ],
                temperature=0.1
            )

            gpt = response.choices[0].message.content
            print(gpt)
            type = gpt[:4]
            if type == "noth":
                continue
            elif type == "note":
                content = gpt[6:]
                data = {
                    "Subject": {"title": [{"text": {"content" : subject}}]},
                    "Content": {"rich_text": [{"text": {"content" : content}}]}
                }
            elif type == "todo":
                endindex = gpt.find("duedate")
                content = gpt[6:endindex]
                ddate = gpt[endindex+7+1:]
                if ddate == "unknown":
                    ddate = datetime.now().astimezone(timezone.utc).isoformat()
        
                data = {
                    "Subject": {"title": [{"text": {"content" : subject}}]},
                    "Content": {"rich_text": [{"text": {"content" : content}}]},
                    "Date": {"date": {"start": ddate.strip(), "end": None}}
                }
            print(data)
            notionIntegration.create_page(data, type)
            notionIntegration.create_page(data, type)
            # Headers for the POST request
            headers = {
                'Content-Type': 'application/json'
            }
            if type == "todo":
                flask_data = {"task":content + '|' + ddate.strip()}
            else:
                flask_data = {"task":content}
            response = requests.post(urlTodo if type == "todo" else urlSummary, headers=headers, data=json.dumps(flask_data))
            print(response.status_code)
            
if __name__ == "__main__":
    run()