import sys
import requests
import subprocess
import config

proc = subprocess.run(["pbpaste"], capture_output=True)
print(proc.stdout)
resp = requests.get("https://api.github.com/repos/MikeiLL/Playground/contents/ansi_colours",
             headers={
  "Accept": "application/vnd.github.object",
  "Authorization": "Bearer " + config.githubtoken,
  "X-GitHub-Api-Version": "2022-11-28",
})

resp.raise_for_status()
print(resp.content)
