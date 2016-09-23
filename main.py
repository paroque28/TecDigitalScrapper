import getpass, requests, csv, time, os.path, urllib
from lxml import html
from os.path import expanduser

home = expanduser("~")
DIR =  home + "/TecDigital"
CRED_FILE = DIR+ "/creds.csv"
INFO_FILE = "/info.csv"
HOME_URL = "http://tecdigital.tec.ac.cr"
LOGIN_URL = "http://tecdigital.tec.ac.cr/register/"
REFERER = "http://tecdigital.tec.ac.cr/register/?return%5furl=%2fdotlrn%2findex"
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
        username = input("Usuario/Carne?\n")
        password = getpass.getpass('Contrasena/pin?\n:')
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
        "from:mode": "edit",
        "_confirmed_p":"0",
        "_refreshing_p": "0",
        "_submit_button_name":"",
        "_submit_button_value": ""
    }

    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:48.0) Gecko/20100101 Firefox/48.0',
               'Referer' : REFERER
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data=payload, headers=headers)

def mainFolders(session_requests):
    # Scrape url
    result = session_requests.get(DOCS, headers = dict(referer = DOCS))
    tree = html.fromstring(result.content)
    hrefs = tree.xpath("//td[@headers='folders_name']/a")

    folders  = []
    for href in hrefs:
        if (raw_input('Do you want '+href.text + '? (y/n)\n')=="y"):
            folder = [href.text,href.attrib['href']]
            folders.append(folder)
        else:
            updateFolder(DIR + "/" + href.text, "n")
    for folder in folders:
        updateFolder(DIR + "/" + folder[NOMBRE],"y")
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
            out = path + "/" + href.text + urllib.unquote(link.split("/")[-1]).decode('utf8')
            downloadFile(session_requests,HOME_URL + link,out)
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
                flag = (date != row[0] or row[0] == "y")
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


def downloadFile(sessions_requests,url,path):
    local_filename = url.split('/')[-1]
    r = sessions_requests.get(url)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return

if __name__ == '__main__':
    main()