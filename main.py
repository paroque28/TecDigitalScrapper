import requests
import  time
from lxml import html

USERNAME = "2014084649"
PASSWORD = "6381"

LOGIN_URL = "http://tecdigital.tec.ac.cr/register/"
URL = "http://tecdigital.tec.ac.cr/dotlrn/?page_num=2"

def main():
    session_requests = requests.session()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='token_id']/@value")))[0]
    hashcode = list(set(tree.xpath("//input[@name='hash']/@value")))[0]

    # Create payload
    payload = {
        "username": USERNAME, 
        "password": PASSWORD, 
        "token_id": authenticity_token,
        "hash" : hashcode,
        "time" : str (int(time.time())),
        "return_url": "/dotlrn/index",
        "formbutton:style" : "Entrar",
        "form:id" : "login",
        "from:mode" : "edit"
    }

    # Perform login
    result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL))

    # Scrape url
    result = session_requests.get(URL, headers = dict(referer = URL))
    tree = html.fromstring(result.content)
    bucket_names = tree.xpath("//td[@headers='folders_name']/a/text()")

    print(bucket_names)

if __name__ == '__main__':
    main()