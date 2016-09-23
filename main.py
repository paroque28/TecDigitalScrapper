import requests, csv, time, os.path
from lxml import html
from os.path import expanduser

home = expanduser("~")
DIR =  home + "/TecDigital"
CRED_FILE = DIR+ "/creds.csv"
LOGIN_URL = "http://tecdigital.tec.ac.cr/register/"
URL = "http://tecdigital.tec.ac.cr/dotlrn/?page_num=2"


def main():
    session_requests = requests.session()

    #Login
    login(session_requests)

    # Scrape url
    result = session_requests.get(URL, headers = dict(referer = URL))
    tree = html.fromstring(result.content)
    bucket_names = tree.xpath("//td[@headers='folders_name']")

    print(bucket_names)


def login(session_requests):
    if (os.path.isfile(CRED_FILE)):
        with open(CRED_FILE) as file:
            reader = csv.reader(file)
            for row in reader:
                username = row[0]
                password = row[1]


    else:
        username = input("What's your username?")
        password = input("What's your pin?")
        if not os.path.exists(DIR):
            os.makedirs(DIR)
        with open(CRED_FILE, 'w') as file:
            writer = csv.writer(file)
            data = [username,password]
            writer.writerow(data)

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


if __name__ == '__main__':
    main()