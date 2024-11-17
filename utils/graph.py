import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout
from pyqtgraph.Qt import QtGui
import networkx as nx
import numpy as np
from PyQt6.QtGui import QColor, QFont

from fsm.abs import Graph


class ComplexGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self, graph, web_fsm: Graph, k=1.5, iterations=500):
        super().__init__()
        self.plot = self.addPlot()  # Create the plot window
        self.plot.hideAxis('bottom')  # Hide the axes
        self.plot.hideAxis('left')
        self.plot.setAspectLocked()  # Lock the aspect ratio
        self.setBackground('w')

        # Generate layout using NetworkX
        # self.pos = nx.spring_layout(graph)  # Position nodes with layout algorithm
        self.graph = graph
        self.web_fsm = web_fsm

        self.k = k
        self.iterations = iterations
        self.pos = nx.spring_layout(self.graph, k=self.k, iterations=self.iterations)  # 弹性布局
        # self.pos = nx.shell_layout(self.graph)


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

        font = QFont()
        font.setPointSize(8)  # Set font size (e.g., 8)
        label_item.setFont(font)

        label_item.setPos(pos[0], pos[1] - 0.1)  # Adjust label position below the node
        self.plot.addItem(label_item)



    def add_edge(self, pos1, pos2, weight=1):
        line = pg.PlotDataItem(
            [pos1[0], pos2[0]], [pos1[1], pos2[1]],
            pen=pg.mkPen(color=(150, 150, 150, 100), width=weight)
        )
        self.plot.addItem(line)

    def update_layout(self, k=None, iterations=None):
        if k:
            self.k = k
        if iterations:
            self.iterations = iterations
        self.pos = nx.spring_layout(self.graph, k=self.k, iterations=self.iterations)
        self.draw_graph()


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
        # self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb())
        # self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb())

        self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb()[:3])
        self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb()[:3])

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
        dialog.resize(800, 800)  # Set initial size
        dialog.exec()  # Show as a modal dialog


# Usage example:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vgraph = VGraph()
    vgraph.add_node_pair('A', 'B', 'Node A', 'Node B', 'yellow', 'green')
    vgraph.add_node_pair('B', 'C', 'Node B', 'Node C', 'green', 'red')

    # To show as a popup
    vgraph.show_graph_popup()
