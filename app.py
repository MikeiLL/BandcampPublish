import json
import re
import sys
import requests
import subprocess
import config
from html.parser import HTMLParser
from base64 import b64encode

proc = subprocess.run(["pbpaste"], capture_output=True, encoding="UTF-8")
trackurl = proc.stdout

if not re.match("https://.*bandcamp.*[track|album]", trackurl):
  print(f"""\x1b[1;31mHey! You must copy a bandcamp track or album link\x1b[0m
        eg: https://chrisbutler1.bandcamp.com/track/impeachment-day
        \x1b[1;31mYou gave us {trackurl[:30]}\x1b[0m
""")
  sys.exit()

ITEM_ID = 0
ITEM_TYPE = "t"
ITEM_TITLE = ""

class ParseBandcamp(HTMLParser):

  def handle_starttag(self, tag, attrs):
    if tag == "meta":
      attrs = dict(attrs)
      if attrs.get("name") == "bc-page-properties":
        content = json.loads(attrs.get("content"))
        global ITEM_ID; ITEM_ID = content.get("item_id")
        global ITEM_TYPE; ITEM_TYPE = content.get("item_type")
      if attrs.get("name") == "title":
        global ITEM_TITLE; ITEM_TITLE = attrs["content"]
pagerequest = requests.get(trackurl)

ParseBandcamp().feed(pagerequest.content.decode())

ITEM_TYPE_DISPLAY = {"t": "track", "a": "album"}.get(ITEM_TYPE, ITEM_TYPE)

if not ITEM_ID:
  print("Something went wrong. No Item ID.")
  sys.exit()

print(f"""Okay great! We got the data from Bandcamp.
Looks like the {ITEM_TYPE_DISPLAY},  {ITEM_TITLE}.
Publishing the player now...
""")

content = {
  "type": ITEM_TYPE,
  "title": ITEM_TITLE,
}
resp = requests.put(F"https://api.github.com/repos/MikeiLL/futurefossilmusicsite/contents/_data/bandcamptracks/{ITEM_ID}.json",
    json={
        "message":f"add {"track" if ITEM_TYPE == 't' else "Album"}: {ITEM_ID}",
        "committer":{
          "name":"BC Publish Rosuav and Mike",
              "email":"mike@mzoo.org"
            },
        "content": b64encode(json.dumps(content).encode()).decode(),
    },
      headers={
  "Accept": "application/vnd.github.object",
  "Authorization": "Bearer " + config.githubtoken,
  "X-GitHub-Api-Version": "2022-11-28",
})
if resp.status_code == 422:
  print(f"\x1b[1;33mHmmm. Is that {ITEM_TYPE_DISPLAY} already posted?\x1b[0m")
  sys.exit()
resp.raise_for_status()
print("\x1b[1;32mSuccess. The new bandcamp player is publishing this very moment. It could take up to 15 minutes.\x1b[0m")
