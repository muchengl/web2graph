import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go


class VGraph:

    def __init__(self):
        self.G = nx.DiGraph()

    def add_node_pair(self,
                       node1_id: str,
                       node2_id: str,
                       node1_label: str,
                       node2_label: str,
                       node1_color: str = 'yellow',
                       node2_color: str = 'green'):

        self.G.add_node(node1_id, label=node1_label, color=node1_color)
        self.G.add_node(node2_id, label=node2_label, color=node2_color)

        self.G.add_edge(node1_id, node2_id)

    def visualize_graph_plotly(self):
        pos = nx.spring_layout(self.G)
        edge_x = []
        edge_y = []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        node_x = []
        node_y = []
        node_text = []
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(self.G.nodes[node].get("label", ""))

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=10,
                color=[self.G.nodes[node].get("color", "blue") for node in self.G.nodes()],
                colorbar=dict(thickness=15, title="Node Color"),
            ),
            textposition="top center"
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title="WebGraph Visualization",
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                        ))

        fig.show()

    def visualize_graph_pyplot(self):
        pos = nx.spring_layout(self.G)

        node_colors = [data['color'] for _, data in self.G.nodes(data=True)]
        labels = nx.get_node_attributes(self.G, 'label')

        plt.figure(figsize=(12, 8))
        nx.draw(self.G, pos, with_labels=False, node_color=node_colors, node_size=500, font_size=10)

        for node, (x, y) in pos.items():
            plt.text(x, y - 0.1, labels[node], ha='center', fontsize=8)

        plt.title("WebGraph Visualization")
        plt.show()
