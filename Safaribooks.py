import requests
from requests.auth import HTTPBasicAuth

import getpass


class Session:
    def __init__(self,):
        self.client_id = "532409"
        self.client_secret = "ce1e4a0d4f726a27a6dbad88e4732c5f7dee15e36e15899971b5d5e7"
        self.auth = HTTPBasicAuth(self.client_id, self.client_secret)
        self.login_url = "https://api.oreilly.com/api/v1/auth/login/"
        self.base_url = "https://learning.oreilly.com"
        self.headers = dict()
        self.bearer = ""
        self.session = requests.Session()

    def login(self, email, password):
        """
        Login to Safaribooks using provided credentials

        :param credentials: username/password
        :type credentials: dict
        :return: Bearer Token
        :rtype: str
        """
        credentials = {
            "email": email,
            "password": password,
        }
        response = self.session.post(
            url=self.login_url, json=credentials, auth=self.auth
        )
        data = response.json()
        self.bearer = data.get("id_token")
        self.headers["Authorization"] = f"Bearer {self.bearer}"
        if not self.bearer:
            raise ConnectionError("Login failed")
        return self.bearer

    def download_csv(self):
        url = f"{self.base_url}/api/v1/annotations/export-csv/"
        data = self.session.get(url, headers=self.headers)
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
                    password = password or getpass.getpass("Password: ")
                    break
                except KeyboardInterrupt:
                    print("")

            try:
                self.login(user, password)
            except ConnectionError:
                print("Login failed, try again")
                password = ""
                user = input("Username: ")
                continue
        print("Login successful!")

    def get_collections(self):
        url = f"{self.base_url}/api/v2/collections/"
        data = self.session.get(url, headers=self.headers)
        return {
            pl["name"]: [book["api_url"] for book in pl["content"]]
            for pl in data.json()
        }

    def delete_highlight(self, highlight, pattern=""):
        if pattern in highlight.title:
            url = highlight.h_url.replace(
                "https://learning.oreilly.com/library/view/-/",
                "https://learning.oreilly.com/api/v1/annotations/",
            ).replace("#", "/")
            print(url)
            self.headers[
                "x-csrftoken"
            ] = "mk0PD4En0Xx0G2k1FGrFxqFvwpjuFU01yuqpibzVdGBvVs4qw8eS1S6yq1Y5SnhM"
            self.headers["referer"] = url
            cookies = {"csrfsafari": self.headers["x-csrftoken"]}
            response = self.session.delete(url, headers=self.headers, cookies=cookies)
            if response.status_code in range(400, 600):
                print(response)
            return response

    def download_metadata(self, rows):
        metadata = dict()
        for row in rows:
            if row.isbn not in metadata:
                url = f"{self.base_url}/api/v1/book/{row.isbn}"
                metadata[row.isbn] = self.session.get(url, headers=self.headers).json()
        return metadata
