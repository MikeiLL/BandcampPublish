import json
import sys
import requests
import subprocess
import config
from html.parser import HTMLParser
from base64 import b64encode

proc = subprocess.run(["pbpaste"], capture_output=True)
trackurl = proc.stdout
#trackurl = "https://chrisbutler1.bandcamp.com/track/impeachment-day"

ITEM_ID = 0
ITEM_TYPE = "t"

class ParseBandcamp(HTMLParser):

  def handle_starttag(self, tag, attrs):
    if tag == "meta":
      attrs = dict(attrs)
      if attrs.get("name") == "bc-page-properties":
        content = json.loads(attrs.get("content"))
        global ITEM_ID; ITEM_ID = content.get("item_id")
        global ITEM_TYPE; ITEM_TYPE = content.get("item_type")

pagerequest = requests.get(trackurl)

ParseBandcamp().feed(pagerequest.content.decode())

if not ITEM_ID:
  print("Something went wrong. No Item ID.")
  sys.exit()
resp = requests.put(F"https://api.github.com/repos/MikeiLL/Playground/contents/{ITEM_ID}",
    json={
        "message":f"add {"track" if ITEM_TYPE == 't' else "Album"}: {ITEM_ID}",
        "committer":{
          "name":"BC Publish Rosuav and Mike",
              "email":"mike@mzoo.org"
            },
        "content": b64encode(b"{'type': %s}" % ITEM_TYPE.encode()).decode()
    },
      headers={
  "Accept": "application/vnd.github.object",
  "Authorization": "Bearer " + config.githubtoken,
  "X-GitHub-Api-Version": "2022-11-28",
})
resp.raise_for_status()
print(resp.content)
