import sys

import matplotlib
import networkx as nx
import pyqtgraph as pg
from PIL.ImageQt import ImageQt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLineEdit, QTextEdit, QScrollArea, QWidget, QLabel, \
    QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPixmap
import matplotlib.pyplot as plt



class PyQtGraphWidget(QWidget):
    def __init__(self, graph, web_fsm):
        super().__init__()
        self.graph = graph
        self.web_fsm = web_fsm

        # Set layout
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.widget = self.init_pyqtgraph_widget()
        self.layout.addWidget(self.widget)

    """
    Pyqtgraph mode
    """

    def init_pyqtgraph_widget(self):
        # Initialize the pyqtgraph-based visualization
        plot_widget = pg.GraphicsLayoutWidget()
        plot_widget.setBackground("w")
        plot = plot_widget.addPlot()
        plot.hideAxis('bottom')
        plot.hideAxis('left')
        plot.setAspectLocked()

        self.plot = plot
        self.generate_tree_layout_pyqtgraph()
        self.draw_graph_pyqtgraph()
        return plot_widget

    def generate_tree_layout_pyqtgraph(self):
        # Generate layout using NetworkX and PyGraphviz
        ag = nx.nx_agraph.to_agraph(self.graph)
        ag.layout(prog="dot")
        self.pos = {node: (float(node.attr["pos"].split(",")[0]),
                           -float(node.attr["pos"].split(",")[1]))
                    for node in ag.nodes()}

    def draw_graph_pyqtgraph(self):
        self.plot.clear()
        self.scatter_items = {}  # Store scatter plot items for click detection
        for node, (x, y) in self.pos.items():
            color = QColor(self.graph.nodes[node]["color"])
            label = self.graph.nodes[node].get("label", "")
            self.add_node_pyqtgraph(node, (x, y), color, label)
        for edge in self.graph.edges(data=True):
            color = edge[2].get("color", (150, 150, 150))
            width = edge[2].get("width", 1)
            self.add_edge_pyqtgraph(self.pos[edge[0]], self.pos[edge[1]], width, color)

    def add_node_pyqtgraph(self, node_id, pos, color, label):
        # Create a scatter plot item for the node
        node_item = pg.ScatterPlotItem(
            size=10, brush=pg.mkBrush(color), pen=pg.mkPen(width=0.5, color="k")
        )
        node_item.addPoints([{"pos": pos, "data": node_id}])
        node_item.sigClicked.connect(self.on_node_click)  # Connect click signal
        self.plot.addItem(node_item)

        # Store the scatter plot item for click detection
        self.scatter_items[node_id] = node_item

        # Add a text label for the node
        label_item = pg.TextItem(text=label, anchor=(0.5, 1))
        font = QFont()
        font.setPointSize(8)
        label_item.setFont(font)
        label_item.setPos(pos[0], pos[1] - 0.1)
        self.plot.addItem(label_item)

    def add_edge_pyqtgraph(self, pos1, pos2, weight, color):
        line = pg.PlotDataItem(
            [pos1[0], pos2[0]], [pos1[1], pos2[1]],
            pen=pg.mkPen(color=color, width=weight)
        )
        self.plot.addItem(line)

    """
    Actions
    """

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


class MatplotlibGraphDisplay:
    def __init__(self, graph, web_fsm):
        self.graph = graph
        self.web_fsm = web_fsm
        self.fig = None
        self.ax = None
        matplotlib.use('Qt5Agg')

    def show(self):
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            plt.ion()  # Turn on interactive mode
            self.fig, self.ax = plt.subplots(figsize=(8, 6))
            self.fig.canvas.mpl_connect('pick_event', self.on_pick)
            self.generate_tree_layout()
            self.draw_graph()

            # self.fig.subplots_adjust(top=0.95, bottom=0.15, left=0.15, right=0.95)
            fig_manager = plt.get_current_fig_manager()
            # fig_manager.window.setGeometry(100, 100, 800, 600)
            # fig, ax = plt.subplots()
            # fig_width, fig_height = fig.get_size_inches()  # Get width and height in inches
            # dpi = fig.dpi  # Get the DPI (dots per inch) of the figure
            # window_width = fig_width * dpi  # Convert inches to pixels
            # window_height = fig_height * dpi
            fig_manager.window.setGeometry(1000, 100, int(600), int(800))

            plt.show(block=False)  # Non-blocking show


        else:
            self.ax.clear()
            self.generate_tree_layout()
            self.draw_graph()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def generate_tree_layout(self):
        self.pos = nx.nx_agraph.graphviz_layout(self.graph, prog="dot")

    def draw_graph(self):
        self.ax.clear()
        labels = {node: self.graph.nodes[node].get("label", "") for node in self.graph.nodes}

        nx.draw(
            self.graph,
            pos=self.pos,
            ax=self.ax,
            with_labels=True,
            labels=labels,
            node_color=[self.graph.nodes[node].get("color", "#ffffff") for node in self.graph.nodes],
            edge_color=[self.graph.edges[edge].get("color", "#aaaaaa") for edge in self.graph.edges],
            node_size=30,
            font_size=5,
            font_color="black",
            width=[self.graph.edges[edge].get("width", 1) for edge in self.graph.edges],
            arrows=True
        )

    def on_pick(self, event):
        node_ind = event.ind[0]
        node_id = list(self.graph.nodes())[node_ind]
        print(f"Clicked node ID: {node_id}")


class VGraph:
    def __init__(self, graph):
        self.G = nx.DiGraph()
        self.web_fsm = graph
        self.matplotlib_display = None

    def set_edge_style(self,
                       node1_id: str,
                       node2_id: str,
                       edge_color: str = "red",
                       edge_width: float = 2.0):
        if self.G.has_edge(node1_id, node2_id):
            self.G[node1_id][node2_id]["color"] = edge_color
            self.G[node1_id][node2_id]["width"] = edge_width
        else:
            print(f"Edge {node1_id} -> {node2_id} does not exist.")

    def add_node_pair(self,
                      node1_id: str,
                      node2_id: str,
                      node1_label: str,
                      node2_label: str,
                      node1_color: str = "yellow",
                      node2_color: str = "green"):
        self.G.add_node(node1_id, label=node1_label, color=node1_color)
        self.G.add_node(node2_id, label=node2_label, color=node2_color)
        self.G.add_edge(node1_id, node2_id)

    def get_graph_widget(self, mode="pyqtgraph"):
        if mode.lower() == "pyqtgraph":
            return PyQtGraphWidget(self.G, self.web_fsm)
        elif mode.lower() == "matplotlib":
            if self.matplotlib_display is None:
                self.matplotlib_display = MatplotlibGraphDisplay(self.G, self.web_fsm)
            else:
                self.matplotlib_display.graph = self.G  # Update the graph data
            return self.matplotlib_display
        else:
            raise ValueError("Invalid mode. Choose 'pyqtgraph' or 'matplotlib'.")

    def show_graph_popup(self, mode="pyqtgraph", parent=None):
        if mode.lower() == "pyqtgraph":
            dialog = QDialog(parent)
            dialog.setWindowTitle("FSM Graph Visualization")
            layout = QVBoxLayout(dialog)

            graph_widget = self.get_graph_widget(mode=mode)
            layout.addWidget(graph_widget)

            dialog.setLayout(layout)
            dialog.resize(800, 800)
            dialog.exec()
        elif mode.lower() == "matplotlib":
            graph_display = self.get_graph_widget(mode=mode)
            graph_display.show()
        else:
            raise ValueError("Invalid mode. Choose 'pyqtgraph' or 'matplotlib'.")



# Usage example:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    vgraph = VGraph(graph=None)  # Replace with your FSM graph object
    vgraph.add_node_pair("A", "B", "Node A", "Node B", "yellow", "green")
    vgraph.add_node_pair("B", "C", "Node B", "Node C", "green", "red")
    vgraph.add_node_pair("C", "A", "Node C", "Node A", "red", "yellow")  # Ancestor edge

    # To show as a popup
    vgraph.show_graph_popup()


