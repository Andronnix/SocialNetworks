from api import User

TISCHENKO = User(48075937)
OVSIANNIKOVA = User(25445578)
VESELKOVA = User(134158269)
ME = User.me()

template = "{:>5}, {:>10}, {:>10}, {:>10}"

print(template.format("", "Tischenko", "Ovsiannikova", "Veselkova"))

for lst in ME.friend_lists:
    print(template.format(lst.name, TISCHENKO in lst.users, OVSIANNIKOVA in lst.users, VESELKOVA in lst.users))
