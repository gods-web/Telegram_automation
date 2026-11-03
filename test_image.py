
import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

output = os.path.exists(".env")
print("output:", output)
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

print(POLLINATIONS_API_KEY)

print(os.getenv("POLLINATIONS_API_KEY"))
print(os.environ.get("POLLINATIONS_API_KEY"))

if not POLLINATIONS_API_KEY:
    raise ValueError("Pollinations API key was not found in .env")

prompt = "A beautiful blue holographic AI robot named Nexi"

url = (
    "https://gen.pollinations.ai/image/"
    + quote(prompt)
    + "?model=black-forest-labs/flux.1-schnell"
)

response = requests.get(
    url,
    headers={"Authorization": f"Bearer {POLLINATIONS_API_KEY}"},
    timeout=120,
)

if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("image/"):
    with open("nexi_test.png", "wb") as image_file:
        image_file.write(response.content)

    print("Image generated successfully!")
    print("Check your project folder for nexi_test.png")
else:
    print("Request failed:", response.status_code)
    print(response.text[:500])