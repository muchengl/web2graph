import sys
import pygraphviz as pgv
import networkx as nx
import pyqtgraph as pg
from PIL.Image import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QTextEdit, QScrollArea, QWidget, QLabel, \
    QPushButton, QHBoxLayout
from PyQt6.QtGui import QColor, QFont, QPixmap
from loguru import logger


# from fsm import WebGraph


class ComplexGraphWidget(pg.GraphicsLayoutWidget):
    def __init__(self, graph, web_fsm):
        super().__init__()
        self.plot = self.addPlot()  # Create the plot window
        self.plot.hideAxis('bottom')  # Hide the axes
        self.plot.hideAxis('left')
        self.plot.setAspectLocked()  # Lock the aspect ratio
        self.setBackground('w')

        self.graph = graph
        self.web_fsm = web_fsm

        # Generate layout using PyGraphviz
        self.pos = self.generate_tree_layout()

        # Draw nodes and edges initially
        self.draw_graph()

    def generate_tree_layout(self):
        # Convert NetworkX graph to PyGraphviz AGraph
        ag = nx.nx_agraph.to_agraph(self.graph)

        # Use the dot layout for tree-like structures
        ag.layout(prog="dot")

        # Extract positions as a dictionary
        pos = {}
        for node in ag.nodes():
            x, y = map(float, node.attr["pos"].split(","))
            pos[node.name] = (x, -y)  # Flip y to match PyQtGraph's coordinate system
        return pos

    # def draw_graph(self):
    #     for node, (x, y) in self.pos.items():
    #         color = QColor(*self.graph.nodes[node]["color"])
    #         label = self.graph.nodes[node].get("label", "")
    #         self.add_node(node, (x, y), color, label)
    #
    #     for edge in self.graph.edges(data=True):
    #         self.add_edge(self.pos[edge[0]], self.pos[edge[1]], weight=edge[2].get("weight", 1))

    def draw_graph(self):
        self.plot.clear()

        for node, (x, y) in self.pos.items():
            color = QColor(*self.graph.nodes[node]["color"])
            label = self.graph.nodes[node].get("label", "")
            self.add_node(node, (x, y), color, label)

        for edge in self.graph.edges(data=True):
            color = edge[2].get("color", (150, 150, 150))
            width = edge[2].get("width", 1)
            self.add_edge(self.pos[edge[0]], self.pos[edge[1]], weight=width, color=color)

    def add_edge(self, pos1, pos2, weight=1, color=(150, 150, 150)):
        line = pg.PlotDataItem(
            [pos1[0], pos2[0]], [pos1[1], pos2[1]],
            pen=pg.mkPen(color=color, width=weight)
        )
        self.plot.addItem(line)


    def add_node(self, node_id, pos, color, label):
        node = pg.ScatterPlotItem(
            size=10,
            brush=pg.mkBrush(color),
            pen=pg.mkPen(width=0.5, color="k")  # Outline for node
        )
        node.addPoints([{"pos": pos, "data": node_id}])
        node.sigClicked.connect(self.on_node_click)
        self.plot.addItem(node)

        # Add label below the node
        label_item = pg.TextItem(text=label, color="k", anchor=(0.5, 1))

        font = QFont()
        font.setPointSize(8)  # Set font size (e.g., 8)
        label_item.setFont(font)

        label_item.setPos(pos[0], pos[1] - 0.1)  # Adjust label position below the node
        self.plot.addItem(label_item)

    # def add_edge(self, pos1, pos2, weight=1):
    #     line = pg.PlotDataItem(
    #         [pos1[0], pos2[0]], [pos1[1], pos2[1]],
    #         pen=pg.mkPen(color=(150, 150, 150, 100), width=weight)
    #     )
    #     self.plot.addItem(line)



    def on_node_click(self, plot, points):
        node_id = points[0].data()
        print(f"Clicked node ID: {node_id}")

        fsm = self.web_fsm

        state_name_edit, state_info_edit = None, None
        action_name_edit, action_info_edit = None, None

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Node Info: {node_id}")
        dialog_layout = QHBoxLayout(dialog)  # Use horizontal layout for left-right sections


        # Left section: Image display
        image_layout = QVBoxLayout()  # Vertical layout for image and toggle button
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Allow resizing of scroll content
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        if node_id in fsm.states:

            state = fsm.states[node_id]


            pixmap1 = QPixmap.fromImage(ImageQt(state.web_image))
            pixmap2 = QPixmap.fromImage(ImageQt(state.som_image))

            image_label = QLabel()
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center image in the scroll area
            image_label.setPixmap(pixmap1)

            def toggle_image():
                if image_label.pixmap() == pixmap1:
                    image_label.setPixmap(pixmap2)
                else:
                    image_label.setPixmap(pixmap1)

            toggle_button = QPushButton("Toggle Image")
            toggle_button.clicked.connect(toggle_image)



            # Add image and button to the scrollable area
            scroll_layout.addWidget(image_label)
            scroll_layout.addWidget(toggle_button)
            scroll_widget.setLayout(scroll_layout)
            scroll_area.setWidget(scroll_widget)
            scroll_area.setWidgetResizable(True)
            image_layout.addWidget(scroll_area)

        # Right section: Editable details
        edit_layout = QVBoxLayout()
        if node_id in fsm.states:
            state_name_edit = QLineEdit(state.state_name)
            state_info_edit = QTextEdit(state.state_info)

            move_button = QPushButton("Move to State")
            move_button.clicked.connect(lambda: fsm.move_to_state(node_id))

            edit_layout.addWidget(QLabel("State Name:"))
            edit_layout.addWidget(state_name_edit)
            edit_layout.addWidget(QLabel("State Info:"))
            edit_layout.addWidget(state_info_edit)
            edit_layout.addWidget(move_button)

        elif node_id in fsm.actions:
            action = fsm.actions[node_id]
            action_name_edit = QLineEdit(action.action_name)
            action_info_edit = QTextEdit(action.action_info)

            edit_layout.addWidget(QLabel("Action Name:"))
            edit_layout.addWidget(action_name_edit)
            edit_layout.addWidget(QLabel("Action Info:"))
            edit_layout.addWidget(action_info_edit)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(
            lambda: self.save_changes(node_id, state_name_edit, state_info_edit, action_name_edit, action_info_edit)
        )
        edit_layout.addWidget(save_button)

        # Add left and right layouts to the dialog
        dialog_layout.addLayout(image_layout)
        dialog_layout.addLayout(edit_layout)

        dialog.setLayout(dialog_layout)
        dialog.resize(800, 800)
        dialog.exec()



    def save_changes(self, node_id, state_name_edit=None, state_info_edit=None, action_name_edit=None, action_info_edit=None):
        fsm = self.web_fsm

        if node_id in fsm.states:
            state = fsm.states[node_id]
            state.state_name = state_name_edit.text()
            state.state_info = state_info_edit.toPlainText()
            print(f"Update state {node_id}: {state.state_name}, {state.state_info}")

        elif node_id in fsm.actions:
            action = fsm.actions[node_id]
            action.action_name = action_name_edit.text()
            action.action_info = action_info_edit.toPlainText()
            print(f"Update action {node_id}: {action.action_name}, {action.action_info}")





class VGraph:
    def __init__(self, graph):
        self.G = nx.DiGraph()
        self.web_fsm = graph

    def set_edge_style(self,
                       node1_id: str,
                       node2_id: str,
                       edge_color: str = "red",
                       edge_width: float = 2.0):
        """
        Sets the style (color, width) of an edge in the graph.

        Parameters:
            node1_id (str): The source node ID.
            node2_id (str): The destination node ID.
            edge_color (str): The color of the edge (e.g., "red", "blue").
            edge_width (float): The width of the edge line.
        """
        if self.G.has_edge(node1_id, node2_id):
            self.G[node1_id][node2_id]["color"] = QColor(edge_color).getRgb()[:3]
            self.G[node1_id][node2_id]["width"] = edge_width
            print(f"Edge style updated: {node1_id} -> {node2_id} with color {edge_color} and width {edge_width}")
        else:
            logger.warning(f"can't find {node1_id} to {node2_id}")



    def add_node_pair(self,
                      node1_id: str,
                      node2_id: str,
                      node1_label: str,
                      node2_label: str,
                      node1_color: str = "yellow",
                      node2_color: str = "green"):
        self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb()[:3])
        self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb()[:3])
        self.G.add_edge(node1_id, node2_id)


    def get_graph_widget(self):
        # Create a ComplexGraphWidget to be embedded
        return ComplexGraphWidget(self.G, self.web_fsm)

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

    def show_graph_popup_async(self, parent=None):
        # Create a dialog with the graph widget as a popup
        dialog = QDialog(parent)
        dialog.setWindowTitle("FSM Graph Visualization")
        layout = QVBoxLayout(dialog)

        # Add the graph widget to the layout
        graph_widget = self.get_graph_widget()
        layout.addWidget(graph_widget)

        dialog.setLayout(layout)
        dialog.resize(800, 800)  # Set initial size
        dialog.show()


# Usage example:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vgraph = VGraph(graph=None)  # Replace with your FSM graph object
    vgraph.add_node_pair("A", "B", "Node A", "Node B", "yellow", "green")
    vgraph.add_node_pair("B", "C", "Node B", "Node C", "green", "red")
    vgraph.add_node_pair("C", "A", "Node C", "Node A", "red", "yellow")  # Ancestor edge

    # To show as a popup
    vgraph.show_graph_popup()


# import sys
# import pyqtgraph as pg
# from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout
# from pyqtgraph.Qt import QtGui
# import networkx as nx
# import numpy as np
# from PyQt6.QtGui import QColor, QFont
#
# from fsm.abs import Graph
#
#
# class ComplexGraphWidget(pg.GraphicsLayoutWidget):
#     def __init__(self, graph, web_fsm: Graph, k=1.5, iterations=500):
#         super().__init__()
#         self.plot = self.addPlot()  # Create the plot window
#         self.plot.hideAxis('bottom')  # Hide the axes
#         self.plot.hideAxis('left')
#         self.plot.setAspectLocked()  # Lock the aspect ratio
#         self.setBackground('w')
#
#         # Generate layout using NetworkX
#         # self.pos = nx.spring_layout(graph)  # Position nodes with layout algorithm
#         self.graph = graph
#         self.web_fsm = web_fsm
#
#         self.k = k
#         self.iterations = iterations
#         self.pos = nx.spring_layout(self.graph, k=self.k, iterations=self.iterations)
#         # self.pos = nx.shell_layout(self.graph)
#
#
#         # Draw nodes and edges initially
#         self.draw_graph()
#
#     def draw_graph(self):
#         for node, (x, y) in self.pos.items():
#             color = QColor(*self.graph.nodes[node]['color'])
#             label = self.graph.nodes[node].get('label', '')
#             self.add_node(node, (x, y), color, label)
#
#         for edge in self.graph.edges(data=True):
#             self.add_edge(self.pos[edge[0]], self.pos[edge[1]], weight=edge[2].get('weight', 1))
#
#
#     def add_node(self, node_id, pos, color, label):
#         node = pg.ScatterPlotItem(
#             size=10,
#             brush=pg.mkBrush(color),
#             pen=pg.mkPen(width=0.5, color='k')  # Outline for node
#         )
#         node.addPoints([{'pos': pos, 'data': node_id}])
#         node.sigClicked.connect(self.on_node_click)
#         self.plot.addItem(node)
#
#         # Add label below the node
#         label_item = pg.TextItem(text=label, color='k', anchor=(0.5, 1))
#
#         font = QFont()
#         font.setPointSize(8)  # Set font size (e.g., 8)
#         label_item.setFont(font)
#
#         label_item.setPos(pos[0], pos[1] - 0.1)  # Adjust label position below the node
#         self.plot.addItem(label_item)
#
#
#
#     def add_edge(self, pos1, pos2, weight=1):
#         line = pg.PlotDataItem(
#             [pos1[0], pos2[0]], [pos1[1], pos2[1]],
#             pen=pg.mkPen(color=(150, 150, 150, 100), width=weight)
#         )
#         self.plot.addItem(line)
#
#     def update_layout(self, k=None, iterations=None):
#         if k:
#             self.k = k
#         if iterations:
#             self.iterations = iterations
#         self.pos = nx.spring_layout(self.graph, k=self.k, iterations=self.iterations)
#         self.draw_graph()
#
#
#     def on_node_click(self, plot, points):
#         node_id = points[0].data()
#         print(f"Clicked node ID: {node_id}")
#
#
#         fsm = self.web_fsm
#
#         fsm.move_to_state(node_id)
#
#
# class VGraph:
#     def __init__(self, graph: Graph):
#         self.G = nx.DiGraph()
#         self.graph = graph
#
#     def add_node_pair(self,
#                       node1_id: str,
#                       node2_id: str,
#                       node1_label: str,
#                       node2_label: str,
#                       node1_color: str = 'yellow',
#                       node2_color: str = 'green'):
#         # Add nodes with attributes
#         # self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb())
#         # self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb())
#
#         self.G.add_node(node1_id, label=node1_label, color=QColor(node1_color).getRgb()[:3])
#         self.G.add_node(node2_id, label=node2_label, color=QColor(node2_color).getRgb()[:3])
#
#         # Add edge between nodes
#         self.G.add_edge(node1_id, node2_id)
#
#     def get_graph_widget(self):
#         # Create a ComplexGraphWidget to be embedded
#         return ComplexGraphWidget(self.G, self.graph)
#
#     def show_graph_popup(self, parent=None):
#         # Create a dialog with the graph widget as a popup
#         dialog = QDialog(parent)
#         dialog.setWindowTitle("FSM Graph Visualization")
#         layout = QVBoxLayout(dialog)
#
#         # Add the graph widget to the layout
#         graph_widget = self.get_graph_widget()
#         layout.addWidget(graph_widget)
#
#         dialog.setLayout(layout)
#         dialog.resize(800, 800)  # Set initial size
#         dialog.exec()  # Show as a modal dialog
#
#
# # Usage example:
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     vgraph = VGraph()
#     vgraph.add_node_pair('A', 'B', 'Node A', 'Node B', 'yellow', 'green')
#     vgraph.add_node_pair('B', 'C', 'Node B', 'Node C', 'green', 'red')
#
#     # To show as a popup
#     vgraph.show_graph_popup()
