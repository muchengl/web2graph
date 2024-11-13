import networkx as nx
import matplotlib.pyplot as plt


def visualize_graph(G: nx.DiGraph):
    pos = nx.spring_layout(G)

    node_colors = [data['color'] for _, data in G.nodes(data=True)]
    labels = nx.get_node_attributes(G, 'label')

    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=False, node_color=node_colors, node_size=500, font_size=10)

    for node, (x, y) in pos.items():
        plt.text(x, y - 0.1, labels[node], ha='center', fontsize=8)

    plt.title("WebGraph Visualization")
    plt.show()