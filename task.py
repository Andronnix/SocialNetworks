from api import User
import networkx as nx
import matplotlib.pyplot as plt


def calculate_multiplexity(u1, u2):
    s1 = set(u1.subscriptions)
    s2 = set(u2.subscriptions)
    s = s1.intersection(s2)
    return 1 + len(s)


ME = User.me()

social = nx.Graph()
social.add_nodes_from(ME.friends)

labels = dict()
labels[ME] = ME.name

multiplexity = dict()
max_multiplexity = -1
max_multiplexity_friend = None
for friend in ME.friends:
    multiplexity[friend] = calculate_multiplexity(ME, friend)
    labels[friend] = "{}, {}".format(friend.name, multiplexity[friend])
    print(labels[friend])

    if multiplexity[friend] > max_multiplexity:
        max_multiplexity = multiplexity[friend]
        max_multiplexity_friend = friend

    social.add_edge(ME, friend, weight=multiplexity[friend], color='limegreen')
    for friend2 in friend.friends:
        if friend2 in ME.friends:
            social.add_edge(friend2, friend, weight=calculate_multiplexity(friend2, friend), color='lightgray')

print("My maximal multiplexity = {}, with {}".format(max_multiplexity, max_multiplexity_friend.name))

plt.subplot(111)
edges = social.edges()
ecolors = [social[u][v]['color'] for u, v in edges]
weights = [social[u][v]['weight'] for u, v in edges]

nodes = social.nodes()
nsizes = [(200 if user == ME else 10*multiplexity[user]) for user in nodes]
ncolors = [('red' if user == ME else 'gray') for user in nodes]

nx.draw(social,
        pos=nx.spring_layout(social, weight='weight'),
        edges=edges,
        nodes=nodes,
        # node_color=ncolors,
        node_size=nsizes,
        width=weights,
        edge_color=ecolors,
        font_size=8,
        labels=labels,
        figsize=(20, 10),
        dpi=200
)
plt.show()

