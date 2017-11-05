import json
from urllib.request import urlopen
from urllib.parse import urlencode

with open('config.json', 'r') as cfg:
    CONFIG = json.load(cfg)


def _build_url(method_name, params):
    params["access_token"] = CONFIG["ACCESS_TOKEN"]
    params = urlencode(params)

    return "https://api.vk.com/method/{}?{}".format(method_name, params)


def get_friends(user_id=None):
    if user_id is None:
        user_id = CONFIG["USER_ID"]

    params = dict(
        order="random",
    )

    url = _build_url("friends.get", params)

    response = json.loads(urlopen(url).read().decode('utf8'))

    return response["response"]


class User:
    _users = dict()

    @staticmethod
    def me():
        return User(CONFIG["USER_ID"])

    def __new__(cls, *args, **kwargs):
        user_id = args[0]
        return User._users.setdefault(user_id, super().__new__(cls))

    def __init__(self, user_id):
        self.id = user_id
        self._friends = None

    def _get_friends(self):
        if self._friends is None:
            self._friends = list(map(User, get_friends(self.id)))

        return self._friends

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "U{id={}}".format(self.id)

    friends = property(_get_friends)


me = User.me()
me1 = User.me()
me2 = User.me()
