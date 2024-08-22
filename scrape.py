from bs4 import BeautifulSoup
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.request import urlretrieve
from os import makedirs
import os.path, time, re
from urllib.error import URLError
import ssl



sugi_files = {}

def enum_links(html, base):
	soup = BeautifulSoup(html, "html.parser")
	links = soup.select("link[rel='stylesheet']")
	links += soup.select("a[href]")
	result = []

	for a in links:
		href = a.attrs['href']
		url = urljoin(base, href)
		result.append(url)
	return result

# Set your desired timeout value in seconds
TIMEOUT = 10

# Create an unverified SSL context to bypass certificate verification
ssl_context = ssl._create_unverified_context()

def download_file(url):
    o = urlparse(url)
    savepath = "./" + o.netloc + o.path
    if re.search(r"/$", savepath):
        savepath += "index.html"
    savedir = os.path.dirname(savepath)

    if os.path.exists(savepath): 
        return savepath

    if not os.path.exists(savedir):
        print("mkdir=", savedir)
        makedirs(savedir)

    try:
        print("download=", url)
        # Open the URL with a timeout and bypass SSL verification
        with urllib.request.urlopen(url, context=ssl_context, timeout=TIMEOUT) as response:
            content = response.read()

            # Write the content to a file
            with open(savepath, "wb") as f:
                f.write(content)

        time.sleep(1)
        return savepath

    except URLError as e:
        print("ダウンロード失敗:", url)
        print("エラー:", e.reason)
        return None

def analize_html(url, root_url):
	savepath = download_file(url)
	if savepath is None: return
	if savepath in sugi_files: return
	sugi_files[savepath] = True
	print("analize_html=", url)

	html = open(savepath, "r", encoding="utf-8").read()
	links = enum_links(html, url)
	for link_url in links:
		if link_url.find(root_url) != 0:
			if not re.search(r".css$", link_url): continue

		if re.search(r".(html|htm)$", link_url):
			analize_html(link_url, root_url)
			continue

		download_file(link_url)

if __name__ == "__main__":
	url = "https://morriscapital.net/en/"
	analize_html(url, url)