import requests, csv, time, os.path, urllib, urllib2
from lxml import html
from os.path import expanduser

home = expanduser("~")
DIR =  home + "/TecDigital"
CRED_FILE = DIR+ "/creds.csv"
INFO_FILE = "/info.csv"
HOME_URL = "http://tecdigital.tec.ac.cr"
LOGIN_URL = "http://tecdigital.tec.ac.cr/register/"
DOCS = "http://tecdigital.tec.ac.cr/dotlrn/?page_num=2"
NOMBRE = 0
URL = 1;
LAST_MODIFIED = 2;

def main():
    session_requests = requests.session()

    login(session_requests)

    mainFolders(session_requests)




def login(session_requests):
    if (os.path.isfile(CRED_FILE)):
        with open(CRED_FILE) as file:
            reader = csv.reader(file)
            for row in reader:
                username = row[0]
                password = row[1]
            file.close()


    else:
        username = input("What's your username?")
        password = input("What's your pin?")
        if not os.path.exists(DIR):
            os.makedirs(DIR)
        with open(CRED_FILE, 'w') as file:
            writer = csv.writer(file)
            data = [username,password]
            writer.writerow(data)
            file.close()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='token_id']/@value")))[0]
    hashcode = list(set(tree.xpath("//input[@name='hash']/@value")))[0]

    # Create payload
    payload = {
        "username": username,
        "password": password,
        "token_id": authenticity_token,
        "hash": hashcode,
        "time": str(int(time.time())),
        "return_url": "/dotlrn/index",
        "formbutton:style": "Entrar",
        "form:id": "login",
        "from:mode": "edit"
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))

def mainFolders(session_requests):
    # Scrape url
    result = session_requests.get(DOCS, headers = dict(referer = DOCS))
    tree = html.fromstring(result.content)
    hrefs = tree.xpath("//td[@headers='folders_name']/a")

    folders  = []
    for href in hrefs:
        folder = [href.text,href.attrib['href']]
        folders.append(folder)
    for folder in folders:
        updateFolder(DIR + "/" + folder[NOMBRE],"")
        subfolder(session_requests, DIR + "/" + folder[NOMBRE], HOME_URL + folder[URL])

def subfolder(session_requests, path, url):
    result = session_requests.get(url, headers=dict(referer=url))
    tree = html.fromstring(result.content)

    types = tree.xpath("//td[contains(@headers,'type')]/img")
    hrefs = tree.xpath("//td[contains(@headers,'name')]/a")
    dates = tree.xpath("//td[contains(@headers,'last_modified')]/text()")
    downloadLinks = tree.xpath("//td[contains(@headers,'download_link')]/a")

    subs = []
    i = 0
    for href in hrefs:
        if (types[i].attrib['alt']== "Carpeta"):
            sub = [href.text, href.attrib['href'], dates[i]]
            subs.append(sub)
        else:
            link = downloadLinks[i].attrib['href']
            file = urllib2.urlopen(HOME_URL + link)
            out = path + "/" + href.text + urllib.unquote(link.split("/")[-1]).decode('utf8')
            with open(out, 'wb') as output:
                output.write(file.read())
        i += 1
    for sub in subs:
        if (updateFolder(path + "/" + sub[NOMBRE], sub[LAST_MODIFIED]) ):
            subfolder(session_requests, path + "/" + sub[NOMBRE], HOME_URL + sub[URL])

#Returns need to update
def updateFolder (path, date ):
    if not os.path.exists(path):
        os.makedirs(path)
        with open(path + INFO_FILE, 'w') as file:
            writer = csv.writer(file)
            data = [date]
            writer.writerow(data)
            file.close()
        return True;
    else:
        with open(path + INFO_FILE) as file:
            reader = csv.reader(file)
            for row in reader:
                flag =  (date != row[0])
            file.close()
        if flag:
            os.remove(path + INFO_FILE)
            with open(path + INFO_FILE, 'w') as f:
                writer = csv.writer(f)
                data = [date]
                writer.writerow(data)
                f.close()
            return True;
    return False;



if __name__ == '__main__':
    main()