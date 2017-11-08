import json
import time
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


def _retry_request(url):
    retries = 10
    while retries:
        response = json.loads(urlopen(url).read().decode('utf8'))
        if not ("error" in response and response["error"]["error_code"] == 6):
            return response

        time.sleep(0.1 * (11 - retries))
        retries -= 1

    raise IOError("Can't get data from vk, {}".format(response))


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

    response = _retry_request(url)
    response = response.get("response", dict()).get("items", [])

    if fields:
        response = list(map(lambda x: User.create(x["id"], x["first_name"], x["last_name"]), response))
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

    response = _retry_request(url)
    response = response.get("response", dict()).get("items", [])

    return response


def get_subscriptions(user_id=None):
    if user_id is None:
        user_id = CONFIG["USER_ID"]

    params = dict(
        user_id=user_id,
        extended=0,
        count=200
    )

    url = _build_url("users.getSubscriptions", params)

    response = _retry_request(url)
    response = response.get("response", dict()).get("groups", dict()).get("items", [])

    return response


UsersList = namedtuple('UsersList', ['id', 'name', 'users'])


class User:
    _users = dict()

    @staticmethod
    def me():
        return User(CONFIG["USER_ID"], 'Андрей', 'Кокорев')

    @staticmethod
    def create(user_id, first_name=None, last_name=None):
        return User._users.setdefault(user_id, User(user_id, first_name, last_name))

    def __init__(self, user_id, first_name=None, last_name=None):
        self.id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self._friends = None
        self._lists = None
        self._subscriptions = None

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

    def _get_subscriptions(self) -> [int]:
        if self._subscriptions is None:
            self._subscriptions = get_subscriptions(self.id)

        return self._subscriptions

    def _get_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id

        return False

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "U(id={}, name={} {})".format(self.id, self.first_name, self.last_name)

    friends = property(_get_friends)
    friend_lists = property(_get_lists)
    name = property(_get_name)
    subscriptions = property(_get_subscriptions)

