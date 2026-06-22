import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, 
    QToolBar, QDockWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, 
    QGraphicsLineItem, QGraphicsTextItem, QInputDialog, QPlainTextEdit,
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit
)
from PyQt6.QtGui import QAction, QKeySequence, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF

import network_helper
import lumped

class Terminal(QGraphicsEllipseItem):
    def __init__(self, parent, x, y, is_ground=False):
        super().__init__(-4, -4, 8, 8, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(Qt.GlobalColor.red))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.is_ground = is_ground
        self.wires = []

class ComponentItem(QGraphicsRectItem):
    def __init__(self, comp_type, pos, scene_ref):
        super().__init__(0, 0, 60, 30)
        self.comp_type = comp_type
        self.scene_ref = scene_ref
        self.setPos(pos)
        
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Label
        self.label = QGraphicsTextItem(self.comp_type, self)
        self.label.setPos(20, 5)
        
        # Default Params based on component type
        self.params = self.get_default_params(comp_type)
        
        # Terminals
        self.t1 = Terminal(self, 0, 15)
        self.t2 = Terminal(self, 60, 15)
        scene_ref.terminals.extend([self.t1, self.t2])
        
    def get_default_params(self, comp_type):
        defaults = {
            'V': "5, V1",
            'I': "1, I1",
            'R': "1000, R1",
            'C': "0.001, 0, C1",  # C, V_init, Name
            'L': "1, 0, L1",      # L, I_init, Name
            'D': "D1"
        }
        return defaults.get(comp_type, "Params")

    def mouseDoubleClickEvent(self, event):
        new_params, ok = QInputDialog.getText(None, f"Edit {self.comp_type}", "Parameters (val, [init], name):", text=self.params)
        if ok and new_params:
            self.params = new_params
            
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for t in [self.t1, self.t2]:
                for w in t.wires:
                    w.update_position()
        return super().itemChange(change, value)

class GroundItem(QGraphicsRectItem):
    def __init__(self, pos, scene_ref):
        super().__init__(0, 0, 20, 20)
        self.setPos(pos)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Draw Ground Symbol Lines (handled in simple paint override ideally, but text is fine here)
        self.label = QGraphicsTextItem("GND", self)
        self.label.setPos(-5, 5)
        
        self.t1 = Terminal(self, 10, 0, is_ground=True)
        scene_ref.terminals.append(self.t1)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for w in self.t1.wires:
                w.update_position()
        return super().itemChange(change, value)

class WireItem(QGraphicsLineItem):
    def __init__(self, start_terminal):
        super().__init__()
        self.setPen(QPen(Qt.GlobalColor.blue, 3))
        self.setZValue(1)
        self.start_terminal = start_terminal
        self.end_terminal = None
        self.start_terminal.wires.append(self)

    def update_position(self):
        if self.start_terminal and self.end_terminal:
            p1 = self.start_terminal.scenePos()
            p2 = self.end_terminal.scenePos()
            self.setLine(QLineF(p1, p2))

class SchematicScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(0, 0, 1000, 800)
        self.current_mode = None 
        
        self.components = []
        self.terminals = []
        self.wires = []
        
        self.is_wiring = False
        self.current_wire = None

    def set_mode(self, mode):
        self.current_mode = mode
        self.is_wiring = False
        if self.current_wire:
            self.removeItem(self.current_wire)
            self.current_wire.start_terminal.wires.remove(self.current_wire)
            self.current_wire = None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        click_pos = event.scenePos()
        item = self.itemAt(click_pos, self.views()[0].transform())

        # Start Wire
        if self.current_mode == "Wire" and isinstance(item, Terminal):
            self.is_wiring = True
            self.current_wire = WireItem(item)
            self.addItem(self.current_wire)
            self.wires.append(self.current_wire)
            return

        # Place Component
        if self.current_mode in ["Voltage Source", "Current Source", "Resistor", "Capacitor", "Inductor", "Diode"]:
            comp_type = self.current_mode[0] 
            comp = ComponentItem(comp_type, click_pos, self)
            self.addItem(comp)
            self.components.append(comp)
            self.set_mode(None) # Reset mode after drop
            
        # Place Ground
        elif self.current_mode == "Ground":
            gnd = GroundItem(click_pos, self)
            self.addItem(gnd)
            self.components.append(gnd)
            self.set_mode(None)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_wiring and self.current_wire:
            p1 = self.current_wire.start_terminal.scenePos()
            self.current_wire.setLine(QLineF(p1, event.scenePos()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_wiring and self.current_wire:
            self.is_wiring = False

            self.current_wire.hide()
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            self.current_wire.show()

            if isinstance(item, Terminal) and item != self.current_wire.start_terminal:
                self.current_wire.end_terminal = item
                item.wires.append(self.current_wire)
                self.current_wire.update_position()
            else:
                self.removeItem(self.current_wire)
                self.current_wire.start_terminal.wires.remove(self.current_wire)
                self.wires.remove(self.current_wire)
            
            self.current_wire = None
            self.set_mode(None)
            
        super().mouseReleaseEvent(event)

    def generate_netlist(self):
        # 1. Resolve Nodes using Union-Find on Terminals
        parent = {t: t for t in self.terminals}
        
        def find(i):
            if parent[i] == i: return i
            parent[i] = find(parent[i])
            return parent[i]
            
        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_i] = root_j

        for w in self.wires:
            if w.start_terminal and w.end_terminal:
                union(w.start_terminal, w.end_terminal)

        # 2. Group and Name Nodes
        groups = {}
        for t in self.terminals:
            groups.setdefault(find(t), []).append(t)

        node_names = {}
        node_idx = 1
        for root, terms in groups.items():
            is_gnd = any(t.is_ground for t in terms)
            name = '0' if is_gnd else f"N{node_idx}"
            if not is_gnd: node_idx += 1
            for t in terms:
                node_names[t] = name

        # 3. Build String
        netlist = []
        for comp in self.components:
            if isinstance(comp, ComponentItem):
                n1 = node_names[comp.t1]
                n2 = node_names[comp.t2]
                netlist.append(f"{comp.comp_type}, {n1}, {n2}, {comp.params}")
                
        return "\n".join(netlist)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MNA Visualizer")
        self.resize(1400, 900)

        # Schematic Canvas
        self.scene = SchematicScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints().Antialiasing)
        self.setCentralWidget(self.view)

        # Plotting Dock
        self.plot_dock = QDockWidget("Transient Analysis", self)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_dock.setWidget(self.plot_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.plot_dock)

        # Netlist Editor Dock
        self.netlist_dock = QDockWidget("Netlist", self)
        
        netlist_container = QWidget()
        layout = QVBoxLayout()
        self.text_editor = QPlainTextEdit()
        btn_layout = QHBoxLayout()
        
        self.btn_compile = QPushButton("Compile from Canvas")
        self.btn_compile.clicked.connect(self.compile_canvas)
        
        self.btn_run_tran = QPushButton("Run Transient")
        self.btn_run_tran.clicked.connect(self.run_transient)
        
        self.dt_input = QLineEdit("0.001")
        self.end_time_input = QLineEdit("5.0")
        
        btn_layout.addWidget(QLabel("dt:"))
        btn_layout.addWidget(self.dt_input)
        btn_layout.addWidget(QLabel("t_end:"))
        btn_layout.addWidget(self.end_time_input)
        
        layout.addWidget(self.text_editor)
        layout.addWidget(self.btn_compile)
        layout.addLayout(btn_layout)
        layout.addWidget(self.btn_run_tran)
        
        netlist_container.setLayout(layout)
        self.netlist_dock.setWidget(netlist_container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.netlist_dock)

        self.setup_toolbar()

    def setup_toolbar(self):
        toolbar = QToolBar("Components")
        self.addToolBar(toolbar)

        tools = {
            "Voltage Source": "V",
            "Current Source": "I",
            "Resistor": "R",
            "Capacitor": "C",
            "Inductor": "L",
            "Diode": "D",
            "Ground": "G",
            "Wire": "W"
        }

        for name, key in tools.items():
            action = QAction(f"{name} ({key})", self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(lambda checked, n=name: self.scene.set_mode(n))
            toolbar.addAction(action)

    def compile_canvas(self):
        netlist_str = self.scene.generate_netlist()
        self.text_editor.setPlainText(netlist_str)

    def run_transient(self):
        self.plot_widget.clear()
        self.plot_widget.addLegend()
        
        text = self.text_editor.toPlainText()
        if not text.strip():
            return
            
        try:
            dt = float(self.dt_input.text())
            end_time = float(self.end_time_input.text())
            
            components = network_helper.parse_network(text)
            graph, component_list = network_helper.assemble_network_graph(components)
            
            # Run simulation with plot_voltage=False so it doesn't block with Matplotlib
            voltage_history = lumped.MNA_time(graph, component_list, dt, end_time, plot_voltage=False)
            
            num_steps = len(next(iter(voltage_history.values())))
            time_axis = np.arange(num_steps) * dt

            colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
            
            for i, (node, history) in enumerate(voltage_history.items()):
                if node != '0':  # Skip plotting ground
                    color = colors[i % len(colors)]
                    self.plot_widget.plot(time_axis, history, pen=pg.mkPen(color, width=2), name=f"V({node})")
                    
        except Exception as e:
            print(f"Simulation Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())