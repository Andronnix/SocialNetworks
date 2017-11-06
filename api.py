import json
from collections import namedtuple
from urllib.request import urlopen
from urllib.parse import urlencode

with open('config.json', 'r') as cfg:
    CONFIG = json.load(cfg)


def _build_url(method_name, params):
    params["access_token"] = CONFIG["ACCESS_TOKEN"]
    params["v"] = 5.69
    params = urlencode(params)


    return "https://api.vk.com/method/{}?{}".format(method_name, params)


def get_friends(user_id=None, list_id=None, fields=False):
    if user_id is None:
        user_id = CONFIG["USER_ID"]

    params = dict(
        user_id=user_id,
        # order="random",
    )

    if fields:
        params["fields"] = "name"

    if list_id is not None:
        params["list_id"] = list_id

    url = _build_url("friends.get", params)

    response = json.loads(urlopen(url).read().decode('utf8'))["response"]["items"]

    if fields:
        response = list(map(lambda x: User(x["id"], x["first_name"], x["last_name"]), response))
    else:
        response = list(map(User, response))

    return response


def get_friends_lists(user_id=None):
    if user_id is None:
        user_id = CONFIG["USER_ID"]

    params = dict(
        user_id=user_id,
        return_system=0,
    )

    url = _build_url("friends.getLists", params)

    response = json.loads(urlopen(url).read().decode('utf8'))
    response = response["response"]["items"]

    return response


UsersList = namedtuple('UsersList', ['id', 'name', 'users'])


class User:
    _users = dict()

    @staticmethod
    def me():
        return User(CONFIG["USER_ID"])

    def __new__(cls, *args, **kwargs):
        user_id = args[0]
        return User._users.setdefault(user_id, super().__new__(cls))

    def __init__(self, user_id, first_name=None, last_name=None):
        self.id = user_id
        self._first_name = first_name
        self._last_name = last_name
        self._friends = None
        self._lists = None

    def _get_friends(self):
        if self._friends is None:
            self._friends = get_friends(self.id, fields=True)

        return self._friends

    def _get_lists(self) -> [UsersList]:
        if self._lists is None:
            self._lists = []
            for lst in get_friends_lists(self.id):

                self._lists.append(UsersList(
                    id=lst["id"],
                    name=lst["name"],
                    users=get_friends(self.id, list_id=lst["id"])
                ))

        return self._lists

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return str(self.__dict__)

    friends = property(_get_friends)
    friend_lists = property(_get_lists)

