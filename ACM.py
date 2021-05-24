import getpass
import requests
import urllib.parse


class Session:
    def __init__(self):
        self.session = requests.Session()
        self.bearer = ""

    def login(self, username, password):
        self.session.get("https://go.oreilly.com/acm")
        url = "https://idp.acm.org/idp/profile/SAML2/Redirect/SSO?execution=e1s1"
        headers = {"content-type": "application/x-www-form-urlencoded"}
        data = f"j_username={username}&j_password={password}&_eventId_proceed=Sign+in"
        response = self.session.post(url, data=data, headers=headers)
        try:
            self.relay = urllib.parse.quote(
                str(response.content)
                .split('<input type="hidden" name="RelayState" value="')[1]
                .split('"/>')[0]
            )
            self.saml = urllib.parse.quote(
                str(response.content)
                .split('<input type="hidden" name="SAMLResponse" value="')[1]
                .split('"/>')[0]
            )
        except Exception:
            raise ConnectionError("Login failed")

        data = f"RelayState={self.relay}&SAMLResponse={self.saml}"
        response = self.session.post(
            url="https://safarijv.auth0.com/login/callback?connection=ACM",
            data=data,
            headers=headers,
        )
        self.bearer = "Success"

    def download_csv(self):
        url = "https://learning.oreilly.com/a/export/csv/"
        data = self.session.get(url)
        return data.content.decode("utf-8").split("\r\n")

    def match_highlights(self, rows, pattern):
        match = set()
        for row in rows.all:
            if pattern in row.title and row.h_url not in match:
                match.add(row)
        print("Question\tAnswer\tHighlight URL")
        for row in match:
            print(row)

    def interactive_login(self, user, password):
        while not self.bearer:
            while True:
                try:
                    password = getpass.getpass("Password: ")
                    break
                except KeyboardInterrupt:
                    print("")

            try:
                self.login(user, password)
            except ConnectionError:
                print("Login failed, try again")
                user = input("Username: ")
                continue
        print("Login successful!")

        self.headers = dict()
        self.bearer = ""
        self.session = requests.Session()