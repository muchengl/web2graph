import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout
from pyqtgraph.Qt import QtGui
import networkx as nx
import numpy as np
from PyQt6.QtGui import QColor

from fsm.abs import Graph


class ComplexGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self, graph, web_fsm: Graph):
        super().__init__()
        self.plot = self.addPlot()  # Create the plot window
        self.plot.hideAxis('bottom')  # Hide the axes
        self.plot.hideAxis('left')
        self.plot.setAspectLocked()  # Lock the aspect ratio
        self.setBackground('w')

        # Generate layout using NetworkX
        self.pos = nx.spring_layout(graph)  # Position nodes with layout algorithm
        self.graph = graph
        self.web_fsm = web_fsm

        # Draw nodes and edges initially
        self.draw_graph()

    def draw_graph(self):
        for node, (x, y) in self.pos.items():
            color = QColor(*self.graph.nodes[node]['color'])
            label = self.graph.nodes[node].get('label', '')
            self.add_node(node, (x, y), color, label)

        for edge in self.graph.edges(data=True):
            self.add_edge(self.pos[edge[0]], self.pos[edge[1]], weight=edge[2].get('weight', 1))


    def add_node(self, node_id, pos, color, label):
        node = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(color),
            pen=pg.mkPen(width=0.5, color='k')  # Outline for node
        )
        node.addPoints([{'pos': pos, 'data': node_id}])
        node.sigClicked.connect(self.on_node_click)
        self.plot.addItem(node)

        # Add label below the node
        label_item = pg.TextItem(text=label, color='k', anchor=(0.5, 1))
        label_item.setPos(pos[0], pos[1] - 0.1)  # Adjust label position below the node
        self.plot.addItem(label_item)



    def add_edge(self, pos1, pos2, weight=1):
        line = pg.PlotDataItem(
            [pos1[0], pos2[0]], [pos1[1], pos2[1]],
            pen=pg.mkPen(color=(150, 150, 150, 100), width=weight)
        )
        self.plot.addItem(line)



    def on_node_click(self, plot, points):
        node_id = points[0].data()
        print(f"Clicked node ID: {node_id}")

        fsm = self.web_fsm

        fsm.move_to_state(node_id)


class VGraph:
    def __init__(self, graph: Graph):
        self.G = nx.DiGraph()
        self.graph = graph

    def add_node_pair(self,
                      node1_id: str,
                      node2_id: str,
                      node1_label: str,
                      node2_label: str,
                      node1_color: str = 'yellow',
                      node2_color: str = 'green'):
        # Add nodes with attributes
        self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb())
        self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb())
        # Add edge between nodes
        self.G.add_edge(node1_id, node2_id)

    def get_graph_widget(self):
        # Create a ComplexGraphWidget to be embedded
        return ComplexGraphWidget(self.G, self.graph)

    def show_graph_popup(self, parent=None):
        # Create a dialog with the graph widget as a popup
        dialog = QDialog(parent)
        dialog.setWindowTitle("FSM Graph Visualization")
        layout = QVBoxLayout(dialog)

        # Add the graph widget to the layout
        graph_widget = self.get_graph_widget()
        layout.addWidget(graph_widget)

        dialog.setLayout(layout)
        dialog.resize(600, 600)  # Set initial size
        dialog.exec()  # Show as a modal dialog


# Usage example:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vgraph = VGraph()
    vgraph.add_node_pair('A', 'B', 'Node A', 'Node B', 'yellow', 'green')
    vgraph.add_node_pair('B', 'C', 'Node B', 'Node C', 'green', 'red')

    # To show as a popup
    vgraph.show_graph_popup()




# import networkx as nx
# import matplotlib.pyplot as plt
# import plotly.graph_objects as go
#
#
# class VGraph:
#
#     def __init__(self):
#         self.G = nx.DiGraph()
#
#     def add_node_pair(self,
#                        node1_id: str,
#                        node2_id: str,
#                        node1_label: str,
#                        node2_label: str,
#                        node1_color: str = 'yellow',
#                        node2_color: str = 'green'):
#
#         self.G.add_node(node1_id, label=node1_label, color=node1_color)
#         self.G.add_node(node2_id, label=node2_label, color=node2_color)
#
#         self.G.add_edge(node1_id, node2_id)
#
#     def visualize_graph_plotly(self):
#         pos = nx.spring_layout(self.G)
#         edge_x = []
#         edge_y = []
#         for edge in self.G.edges():
#             x0, y0 = pos[edge[0]]
#             x1, y1 = pos[edge[1]]
#             edge_x += [x0, x1, None]
#             edge_y += [y0, y1, None]
#
#         edge_trace = go.Scatter(
#             x=edge_x, y=edge_y,
#             line=dict(width=0.5, color='#888'),
#             hoverinfo='none',
#             mode='lines'
#         )
#
#         node_x = []
#         node_y = []
#         node_text = []
#         for node in self.G.nodes():
#             x, y = pos[node]
#             node_x.append(x)
#             node_y.append(y)
#             node_text.append(self.G.nodes[node].get("label", ""))
#
#         node_trace = go.Scatter(
#             x=node_x, y=node_y,
#             mode='markers+text',
#             text=node_text,
#             marker=dict(
#                 showscale=True,
#                 colorscale='YlGnBu',
#                 size=10,
#                 color=[self.G.nodes[node].get("color", "blue") for node in self.G.nodes()],
#                 colorbar=dict(thickness=15, title="Node Color"),
#             ),
#             textposition="top center"
#         )
#
#         fig = go.Figure(data=[edge_trace, node_trace],
#                         layout=go.Layout(
#                             title="WebGraph Visualization",
#                             showlegend=False,
#                             hovermode='closest',
#                             margin=dict(b=20, l=5, r=5, t=40),
#                             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#                             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
#                         ))
#
#         fig.show()
#
#     def visualize_graph_pyplot(self):
#         pos = nx.spring_layout(self.G)
#
#         node_colors = [data['color'] for _, data in self.G.nodes(data=True)]
#         labels = nx.get_node_attributes(self.G, 'label')
#
#         plt.figure(figsize=(12, 8))
#         nx.draw(self.G, pos, with_labels=False, node_color=node_colors, node_size=500, font_size=10)
#
#         for node, (x, y) in pos.items():
#             plt.text(x, y - 0.1, labels[node], ha='center', fontsize=8)
#
#         plt.title("WebGraph Visualization")
#         plt.show()
