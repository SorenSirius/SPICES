import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QToolBar, QDockWidget, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QGraphicsTextItem, QInputDialog, QPlainTextEdit,
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QLineEdit,
    QDialog, QFormLayout, QDialogButtonBox, QGroupBox, QMessageBox,
    QStatusBar, QFrame, QSizePolicy
)
from PyQt6.QtGui import (
    QAction, QKeySequence, QPen, QBrush, QColor, QFont, QPainter,
    QLinearGradient, QTransform
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF, QTimer

import network_helper
import lumped


# ── Palette ──────────────────────────────────────────────────────────────────
CLR_BG          = "#1a1d23"
CLR_SURFACE     = "#22262f"
CLR_SURFACE2    = "#2a2f3a"
CLR_BORDER      = "#373c4a"
CLR_ACCENT      = "#4f8ef7"
CLR_ACCENT2     = "#7c5ef7"
CLR_GREEN       = "#3dd68c"
CLR_AMBER       = "#f7b731"
CLR_RED         = "#f74f4f"
CLR_TEXT        = "#e8eaf0"
CLR_TEXT_MUTED  = "#8b91a8"
CLR_WIRE        = "#4f8ef7"
CLR_TERMINAL    = "#f74f4f"
CLR_COMP_BG     = "#2a2f3a"
CLR_COMP_BORDER = "#4f8ef7"
CLR_GRID        = "#262b36"


COMP_COLORS = {
    'V': ("#1a3a2a", "#3dd68c"),
    'I': ("#1a2a3a", "#4f8ef7"),
    'R': ("#2a2a1a", "#f7b731"),
    'C': ("#2a1a3a", "#7c5ef7"),
    'L': ("#3a1a1a", "#f74f4f"),
    'D': ("#1a3a3a", "#3dd6d6"),
}

COMP_SYMBOLS = {
    'V': 'V',
    'I': 'I',
    'R': 'R',
    'C': 'C',
    'L': 'L',
    'D': 'D',
}


# ── Parameter dialog ──────────────────────────────────────────────────────────
class ComponentDialog(QDialog):
    def __init__(self, comp_type, current_params, parent=None):
        super().__init__(parent)
        self.comp_type = comp_type
        self.setWindowTitle(f"Edit {comp_type} Parameters")
        self.setMinimumWidth(340)
        self._apply_style()

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        parts = [p.strip() for p in current_params.split(',')]
        self.fields = {}

        if comp_type == 'V':
            self.fields['value'] = QLineEdit(parts[0] if len(parts) > 0 else "5")
            self.fields['name']  = QLineEdit(parts[1] if len(parts) > 1 else "V1")
            form.addRow("Voltage (V):", self.fields['value'])
            form.addRow("Name:",        self.fields['name'])
        elif comp_type == 'I':
            self.fields['value'] = QLineEdit(parts[0] if len(parts) > 0 else "1")
            self.fields['name']  = QLineEdit(parts[1] if len(parts) > 1 else "I1")
            form.addRow("Current (A):", self.fields['value'])
            form.addRow("Name:",        self.fields['name'])
        elif comp_type == 'R':
            self.fields['value'] = QLineEdit(parts[0] if len(parts) > 0 else "1000")
            self.fields['name']  = QLineEdit(parts[1] if len(parts) > 1 else "R1")
            form.addRow("Resistance (Ω):", self.fields['value'])
            form.addRow("Name:",           self.fields['name'])
        elif comp_type == 'C':
            self.fields['value']  = QLineEdit(parts[0] if len(parts) > 0 else "0.001")
            self.fields['v_init'] = QLineEdit(parts[1] if len(parts) > 1 else "0")
            self.fields['name']   = QLineEdit(parts[2] if len(parts) > 2 else "C1")
            form.addRow("Capacitance (F):",    self.fields['value'])
            form.addRow("Initial Voltage (V):", self.fields['v_init'])
            form.addRow("Name:",                self.fields['name'])
            self._add_hint(layout, "Initial voltage sets capacitor charge at t=0.")
        elif comp_type == 'L':
            self.fields['value']  = QLineEdit(parts[0] if len(parts) > 0 else "1")
            self.fields['i_init'] = QLineEdit(parts[1] if len(parts) > 1 else "0")
            self.fields['name']   = QLineEdit(parts[2] if len(parts) > 2 else "L1")
            form.addRow("Inductance (H):",      self.fields['value'])
            form.addRow("Initial Current (A):", self.fields['i_init'])
            form.addRow("Name:",                self.fields['name'])
            self._add_hint(layout, "Initial current sets inductor flux at t=0.")
        elif comp_type == 'D':
            self.fields['name'] = QLineEdit(parts[0] if len(parts) > 0 else "D1")
            form.addRow("Name:", self.fields['name'])

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_hint(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {CLR_TEXT_MUTED}; font-size: 11px; font-style: italic;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

    def _apply_style(self):
        self.setStyleSheet(f"""
            QDialog {{ background: {CLR_SURFACE}; color: {CLR_TEXT}; font-family: 'Segoe UI', system-ui, sans-serif; }}
            QLabel {{ color: {CLR_TEXT}; font-size: 13px; }}
            QLineEdit {{
                background: {CLR_BG}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 5px 8px; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {CLR_ACCENT}; }}
            QPushButton {{
                background: {CLR_ACCENT}; color: white; border: none;
                border-radius: 4px; padding: 6px 16px; font-size: 13px;
            }}
            QPushButton:hover {{ background: #6fa3f9; }}
        """)

    def get_params(self):
        ct = self.comp_type
        f  = self.fields
        if ct in ('V', 'I'):
            return f"{f['value'].text()}, {f['name'].text()}"
        if ct == 'R':
            return f"{f['value'].text()}, {f['name'].text()}"
        if ct == 'C':
            return f"{f['value'].text()}, {f['v_init'].text()}, {f['name'].text()}"
        if ct == 'L':
            return f"{f['value'].text()}, {f['i_init'].text()}, {f['name'].text()}"
        if ct == 'D':
            return f"{f['name'].text()}"
        return ""


# ── Terminal ──────────────────────────────────────────────────────────────────
class Terminal(QGraphicsEllipseItem):
    def __init__(self, parent, x, y, is_ground=False):
        super().__init__(-5, -5, 10, 10, parent)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor(CLR_TERMINAL)))
        self.setPen(QPen(QColor("#ff8888"), 1))
        self.setZValue(5)
        self.is_ground = is_ground
        self.wires = []

    def highlight(self, on: bool):
        if on:
            self.setBrush(QBrush(QColor(CLR_GREEN)))
            self.setPen(QPen(QColor(CLR_GREEN), 2))
        else:
            self.setBrush(QBrush(QColor(CLR_TERMINAL)))
            self.setPen(QPen(QColor("#ff8888"), 1))


# ── Component ─────────────────────────────────────────────────────────────────
class ComponentItem(QGraphicsRectItem):
    W, H = 70, 36

    def __init__(self, comp_type, pos, scene_ref):
        super().__init__(0, 0, self.W, self.H)
        self.comp_type  = comp_type
        self.scene_ref  = scene_ref
        # Cumulative rotation in degrees (multiples of 90)
        self._rot = 0
        self.setPos(pos)

        bg, border = COMP_COLORS.get(comp_type, (CLR_COMP_BG, CLR_COMP_BORDER))
        self.setBrush(QBrush(QColor(bg)))
        self.setPen(QPen(QColor(border), 1.5))

        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        symbol = COMP_SYMBOLS.get(comp_type, comp_type)
        self.sym_label = QGraphicsTextItem(symbol, self)
        self.sym_label.setDefaultTextColor(QColor(border))
        self.sym_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        sym_w = self.sym_label.boundingRect().width()
        self.sym_label.setPos((self.W - sym_w) / 2, 4)

        self.params = self._default_params(comp_type)

        # Terminals at left-centre and right-centre in LOCAL space
        self.t1 = Terminal(self, 0,      self.H / 2)
        self.t2 = Terminal(self, self.W, self.H / 2)
        scene_ref.terminals.extend([self.t1, self.t2])

    def _default_params(self, t):
        return {
            'V': "5, V1",
            'I': "1, I1",
            'R': "1000, R1",
            'C': "0.001, 0, C1",
            'L': "1, 0, L1",
            'D': "D1",
        }.get(t, "Params")

    def mouseDoubleClickEvent(self, event):
        dlg = ComponentDialog(self.comp_type, self.params)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.params = dlg.get_params()
        event.accept()

    def rotate_90(self):
        """
        Rotate 90° clockwise around the component's own centre.
        We use setTransformOriginPoint so Qt handles the pivot correctly
        and scenePos() of child Terminal items stays accurate.
        """
        self._rot = (self._rot + 90) % 360
        # Set the pivot to the visual centre of the rect
        self.setTransformOriginPoint(self.W / 2, self.H / 2)
        self.setRotation(self._rot)
        # Wire endpoints must be recalculated now that terminal scene-positions changed
        for t in (self.t1, self.t2):
            for w in t.wires:
                w.update_position()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for t in (self.t1, self.t2):
                for w in t.wires:
                    w.update_position()
        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            sel_pen = QPen(QColor(CLR_ACCENT), 2, Qt.PenStyle.DashLine)
            painter.setPen(sel_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(-3, -3, 3, 3), 5, 5)
        super().paint(painter, option, widget)


# ── Ground ────────────────────────────────────────────────────────────────────
class GroundItem(QGraphicsRectItem):
    def __init__(self, pos, scene_ref):
        super().__init__(0, 0, 28, 28)
        self.setPos(pos)
        self.setBrush(QBrush(QColor("#1a2a1a")))
        self.setPen(QPen(QColor(CLR_GREEN), 1.5))
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.label = QGraphicsTextItem("GND", self)
        self.label.setDefaultTextColor(QColor(CLR_GREEN))
        self.label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        lw = self.label.boundingRect().width()
        self.label.setPos((28 - lw) / 2, 6)

        self.t1 = Terminal(self, 14, 0, is_ground=True)
        scene_ref.terminals.append(self.t1)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for w in self.t1.wires:
                w.update_position()
        return super().itemChange(change, value)


# ── Wire ──────────────────────────────────────────────────────────────────────
class WireItem(QGraphicsLineItem):
    def __init__(self, start_terminal):
        super().__init__()
        pen = QPen(QColor(CLR_WIRE), 2, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        self.setPen(pen)
        self.setZValue(2)
        self.start_terminal = start_terminal
        self.end_terminal   = None
        self.start_terminal.wires.append(self)

    def update_position(self):
        if self.start_terminal and self.end_terminal:
            p1 = self.start_terminal.scenePos()
            p2 = self.end_terminal.scenePos()
            self.setLine(QLineF(p1, p2))


# ── Scene ─────────────────────────────────────────────────────────────────────
class SchematicScene(QGraphicsScene):
    SNAP = 10

    def __init__(self, status_callback=None):
        super().__init__()
        self.setSceneRect(0, 0, 1200, 900)
        self.setBackgroundBrush(QBrush(QColor(CLR_BG)))
        self.current_mode = None
        self.components   = []
        self.terminals    = []
        self.wires        = []
        self.is_wiring    = False
        self.current_wire = None
        self._status      = status_callback or (lambda msg: None)

    def _snap(self, pos):
        s = self.SNAP
        return QPointF(round(pos.x() / s) * s, round(pos.y() / s) * s)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        painter.setPen(QPen(QColor(CLR_GRID), 1))
        s = self.SNAP * 2
        left   = int(rect.left())  - (int(rect.left())  % s)
        top    = int(rect.top())   - (int(rect.top())   % s)
        right  = int(rect.right()) + s
        bottom = int(rect.bottom())+ s
        for x in range(left, right, s):
            for y in range(top, bottom, s):
                painter.drawPoint(x, y)

    def set_mode(self, mode):
        self.current_mode = mode
        self.is_wiring = False
        if self.current_wire:
            self._cancel_wire()
        if mode:
            self._status(f"Mode: {mode}  —  click canvas to place  |  Esc to cancel")
        else:
            self._status("Ready  —  select a tool from the toolbar")

    # ── key events come from the scene (not individual items) ──────────────
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_Escape:
            self.set_mode(None)
        elif key == Qt.Key.Key_Delete or key == Qt.Key.Key_Backspace:
            for item in list(self.selectedItems()):
                self._delete_item(item)
        elif key == Qt.Key.Key_R:
            # Rotate ALL selected ComponentItems
            rotated = 0
            for item in self.selectedItems():
                if isinstance(item, ComponentItem):
                    item.rotate_90()
                    rotated += 1
            if rotated:
                self._status(f"Rotated {rotated} component(s)  —  press R again to continue rotating")
        else:
            super().keyPressEvent(event)

    def _cancel_wire(self):
        if self.current_wire:
            self.removeItem(self.current_wire)
            if self.current_wire in self.current_wire.start_terminal.wires:
                self.current_wire.start_terminal.wires.remove(self.current_wire)
            if self.current_wire in self.wires:
                self.wires.remove(self.current_wire)
            self.current_wire = None

    def _terminal_at(self, pos, exclude=None):
        best, best_d = None, 16.0
        for item in self.items(QRectF(pos.x() - 16, pos.y() - 16, 32, 32)):
            if isinstance(item, Terminal) and item is not exclude:
                d = (item.scenePos() - pos).manhattanLength()
                if d < best_d:
                    best, best_d = item, d
        return best

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos  = event.scenePos()
        spos = self._snap(pos)

        if self.current_mode == "Wire":
            term = self._terminal_at(pos)
            if term:
                self.is_wiring    = True
                self.current_wire = WireItem(term)
                self.addItem(self.current_wire)
                self.wires.append(self.current_wire)
                term.highlight(True)
                self._status("Wiring — release on another terminal to connect  |  Esc to cancel")
            return

        type_map = {
            "Voltage Source": 'V', "Current Source": 'I',
            "Resistor": 'R', "Capacitor": 'C', "Inductor": 'L', "Diode": 'D',
        }
        if self.current_mode in type_map:
            comp = ComponentItem(type_map[self.current_mode], spos, self)
            self.addItem(comp)
            self.components.append(comp)
            self.set_mode(None)
            return

        if self.current_mode == "Ground":
            gnd = GroundItem(spos, self)
            self.addItem(gnd)
            self.components.append(gnd)
            self.set_mode(None)
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        if self.is_wiring and self.current_wire:
            p1 = self.current_wire.start_terminal.scenePos()
            self.current_wire.setLine(QLineF(p1, pos))
            near = self._terminal_at(pos, exclude=self.current_wire.start_terminal)
            for t in self.terminals:
                if t is not self.current_wire.start_terminal:
                    t.highlight(t is near)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.is_wiring and self.current_wire:
            self.is_wiring = False
            pos  = event.scenePos()
            term = self._terminal_at(pos, exclude=self.current_wire.start_terminal)

            for t in self.terminals:
                t.highlight(False)

            if term:
                self.current_wire.end_terminal = term
                term.wires.append(self.current_wire)
                self.current_wire.update_position()
                self._status("Wire connected ✓  —  click another terminal to draw next wire")
            else:
                self._cancel_wire()
                self._status("Wire dropped — no terminal found  |  try again")

            self.current_wire = None
            # Stay in Wire mode for rapid wiring
            self.current_mode = "Wire"

        super().mouseReleaseEvent(event)

    def _delete_item(self, item):
        if isinstance(item, ComponentItem):
            for t in (item.t1, item.t2):
                for w in list(t.wires):
                    other = w.end_terminal if w.start_terminal is t else w.start_terminal
                    if other and w in other.wires:
                        other.wires.remove(w)
                    if w in self.wires:
                        self.wires.remove(w)
                    self.removeItem(w)
                if t in self.terminals:
                    self.terminals.remove(t)
            if item in self.components:
                self.components.remove(item)
            self.removeItem(item)
        elif isinstance(item, GroundItem):
            for w in list(item.t1.wires):
                other = w.end_terminal if w.start_terminal is item.t1 else w.start_terminal
                if other and w in other.wires:
                    other.wires.remove(w)
                if w in self.wires:
                    self.wires.remove(w)
                self.removeItem(w)
            if item.t1 in self.terminals:
                self.terminals.remove(item.t1)
            if item in self.components:
                self.components.remove(item)
            self.removeItem(item)
        elif isinstance(item, WireItem):
            for t in (item.start_terminal, item.end_terminal):
                if t and item in t.wires:
                    t.wires.remove(item)
            if item in self.wires:
                self.wires.remove(item)
            self.removeItem(item)

    # ── netlist ────────────────────────────────────────────────────────────
    def generate_netlist(self):
        parent = {t: t for t in self.terminals}

        def find(i):
            if parent[i] is i: return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            ri, rj = find(i), find(j)
            if ri is not rj:
                parent[ri] = rj

        for w in self.wires:
            if w.start_terminal and w.end_terminal:
                union(w.start_terminal, w.end_terminal)

        groups = {}
        for t in self.terminals:
            groups.setdefault(find(t), []).append(t)

        node_names = {}
        node_idx   = 1
        for root, terms in groups.items():
            is_gnd = any(t.is_ground for t in terms)
            name   = '0' if is_gnd else f"N{node_idx}"
            if not is_gnd:
                node_idx += 1
            for t in terms:
                node_names[t] = name

        lines = []
        for comp in self.components:
            if isinstance(comp, ComponentItem):
                n1 = node_names.get(comp.t1, '?')
                n2 = node_names.get(comp.t2, '?')
                lines.append(f"{comp.comp_type}, {n1}, {n2}, {comp.params}")

        return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _lighten(hex_color, amt=20):
    c = QColor(hex_color)
    return QColor(min(c.red()+amt,255), min(c.green()+amt,255), min(c.blue()+amt,255)).name()

def _darken(hex_color, amt=20):
    c = QColor(hex_color)
    return QColor(max(c.red()-amt,0), max(c.green()-amt,0), max(c.blue()-amt,0)).name()

def make_button(text, color=CLR_ACCENT, text_color="white"):
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setMinimumHeight(32)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: {color}; color: {text_color};
            border: none; border-radius: 5px;
            padding: 0 14px; font-size: 12px; font-weight: 600;
            font-family: 'Segoe UI', system-ui, sans-serif;
        }}
        QPushButton:hover   {{ background: {_lighten(color)}; }}
        QPushButton:pressed {{ background: {_darken(color)};  }}
        QPushButton:disabled {{ background: {CLR_SURFACE2}; color: {CLR_TEXT_MUTED}; }}
    """)
    return btn


# ── Main Window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Circuit Sim")
        self.resize(1520, 960)
        self._apply_global_style()

        self.status = QStatusBar()
        self.status.setStyleSheet(f"""
            QStatusBar {{
                background: {CLR_SURFACE}; color: {CLR_TEXT_MUTED};
                border-top: 1px solid {CLR_BORDER};
                font-size: 12px; padding: 2px 8px;
            }}
        """)
        self.setStatusBar(self.status)
        self.status.showMessage("Ready  —  select a tool from the toolbar")

        self.scene = SchematicScene(status_callback=self.status.showMessage)
        self.view  = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setStyleSheet(f"background: {CLR_BG}; border: none;")
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Give the scene keyboard focus so keyPressEvent fires
        self.view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setCentralWidget(self.view)

        self._setup_toolbar()
        self._setup_right_panel()
        self._setup_plot_dock()

        self.view.wheelEvent = self._wheel_zoom

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{
                background: {CLR_BG}; color: {CLR_TEXT};
                font-family: 'Segoe UI', system-ui, sans-serif;
            }}
            QDockWidget {{ background: {CLR_SURFACE}; color: {CLR_TEXT}; }}
            QDockWidget::title {{
                background: {CLR_SURFACE2}; color: {CLR_TEXT};
                padding: 6px 10px; font-size: 12px; font-weight: 600;
                border-bottom: 1px solid {CLR_BORDER};
                text-transform: uppercase; letter-spacing: 0.5px;
            }}
            QPlainTextEdit {{
                background: {CLR_BG}; color: {CLR_GREEN};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                font-family: 'Cascadia Code','Fira Code','Consolas',monospace;
                font-size: 12px; padding: 6px;
                selection-background-color: {CLR_ACCENT};
            }}
            QLineEdit {{
                background: {CLR_BG}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 4px;
                padding: 4px 8px; font-size: 12px;
            }}
            QLineEdit:focus {{ border-color: {CLR_ACCENT}; }}
            QLabel {{ color: {CLR_TEXT_MUTED}; font-size: 12px; }}
            QToolBar {{
                background: {CLR_SURFACE}; border-bottom: 1px solid {CLR_BORDER};
                spacing: 4px; padding: 4px 8px;
            }}
            QToolButton {{
                background: {CLR_SURFACE2}; color: {CLR_TEXT};
                border: 1px solid {CLR_BORDER}; border-radius: 5px;
                padding: 5px 12px; font-size: 12px; font-weight: 500; min-width: 60px;
            }}
            QToolButton:hover   {{ background: {CLR_BORDER}; border-color: {CLR_ACCENT}; }}
            QToolButton:checked {{ background: {CLR_ACCENT}; color: white; border-color: {CLR_ACCENT}; }}
        """)

    def _setup_toolbar(self):
        tb = QToolBar("Components")
        tb.setMovable(False)
        self.addToolBar(tb)
        self._tool_actions = {}

        def sep(text):
            lbl = QLabel(f"  {text}  ")
            lbl.setStyleSheet(f"color: {CLR_TEXT_MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px;")
            tb.addWidget(lbl)

        sep("Sources")
        for name, key, mode in [("Voltage", "V", "Voltage Source"), ("Current", "I", "Current Source")]:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(lambda chk, m=mode: self._set_mode(m))
            tb.addAction(act)
            self._tool_actions[mode] = act

        tb.addSeparator(); sep("Passives")
        for name, key, mode in [("Resistor","R","Resistor"),("Capacitor","C","Capacitor"),("Inductor","L","Inductor")]:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(lambda chk, m=mode: self._set_mode(m))
            tb.addAction(act)
            self._tool_actions[mode] = act

        tb.addSeparator(); sep("Semi")
        for name, key, mode in [("Diode","D","Diode")]:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(lambda chk, m=mode: self._set_mode(m))
            tb.addAction(act)
            self._tool_actions[mode] = act

        tb.addSeparator(); sep("Wiring")
        for name, key, mode in [("Ground","G","Ground"),("Wire","W","Wire")]:
            act = QAction(name, self)
            act.setCheckable(True)
            act.setShortcut(QKeySequence(key))
            act.triggered.connect(lambda chk, m=mode: self._set_mode(m))
            tb.addAction(act)
            self._tool_actions[mode] = act

        tb.addSeparator()
        hint = QLabel("   R = rotate selected  |  Del = delete  |  Scroll = zoom")
        hint.setStyleSheet(f"color: {CLR_TEXT_MUTED}; font-size: 11px;")
        tb.addWidget(hint)

    def _set_mode(self, mode):
        for act in self._tool_actions.values():
            act.setChecked(False)
        if mode in self._tool_actions:
            self._tool_actions[mode].setChecked(True)
        # Rubber-band drag conflicts with click-to-place; disable it while a tool is active
        if mode in ("Wire",):
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif mode is None:
            self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        else:
            self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setFocus()          # ensure scene receives key events
        self.scene.set_mode(mode)

    def _setup_right_panel(self):
        dock = QDockWidget("Analysis & Netlist", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        container = QWidget()
        container.setStyleSheet(f"background: {CLR_SURFACE};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        def section(text):
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {CLR_TEXT_MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px; margin-top:4px;")
            layout.addWidget(lbl)

        section("NETLIST")
        self.text_editor = QPlainTextEdit()
        self.text_editor.setMinimumHeight(160)
        self.text_editor.setPlaceholderText("# Netlist appears here after compiling…\n# Or type manually.")
        layout.addWidget(self.text_editor)

        btn_compile = make_button("⟳  Compile from Canvas", CLR_SURFACE2, CLR_TEXT)
        btn_compile.clicked.connect(self.compile_canvas)
        layout.addWidget(btn_compile)

        layout.addWidget(self._divider())
        section("SIMULATION PARAMETERS")

        grid = QHBoxLayout()
        grid.setSpacing(6)
        for lbl_text, attr, default, width in [
            ("dt (s)",     "dt_input",       "0.001", 72),
            ("t_end (s)",  "end_time_input", "5.0",   72),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setFixedWidth(52)
            le  = QLineEdit(default)
            le.setFixedWidth(width)
            setattr(self, attr, le)
            grid.addWidget(lbl)
            grid.addWidget(le)
        grid.addStretch()
        layout.addLayout(grid)

        layout.addWidget(self._divider())
        section("RUN ANALYSIS")

        btn_tran = make_button("▶  Transient Analysis", CLR_ACCENT)
        btn_tran.clicked.connect(self.run_transient)
        layout.addWidget(btn_tran)

        btn_op = make_button("◉  Operating Point", CLR_SURFACE2, CLR_TEXT)
        btn_op.clicked.connect(self.run_operating_point)
        layout.addWidget(btn_op)

        btn_ac = make_button("〜  AC Analysis  (coming soon)", CLR_SURFACE2, CLR_TEXT_MUTED)
        btn_ac.setEnabled(False)
        btn_ac.setToolTip("AC frequency-domain analysis — not yet implemented")
        layout.addWidget(btn_ac)

        layout.addStretch()

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet(f"color: {CLR_GREEN}; font-size: 12px; font-family: monospace;")
        layout.addWidget(self.result_label)

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        dock.setMinimumWidth(290)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {CLR_BORDER};")
        return line

    def _setup_plot_dock(self):
        dock = QDockWidget("Waveform Viewer", self)
        dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                         QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(CLR_BG)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        for ax in ('left', 'bottom'):
            self.plot_widget.getAxis(ax).setTextPen(pg.mkPen(CLR_TEXT_MUTED))
            self.plot_widget.getAxis(ax).setPen(pg.mkPen(CLR_BORDER))
        self.plot_widget.setLabel('left',   'Voltage', units='V', color=CLR_TEXT_MUTED)
        self.plot_widget.setLabel('bottom', 'Time',    units='s', color=CLR_TEXT_MUTED)

        dock.setWidget(self.plot_widget)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        dock.setMinimumHeight(220)

    def _wheel_zoom(self, event):
        factor = 1.12 if event.angleDelta().y() > 0 else 1 / 1.12
        self.view.scale(factor, factor)

    # ── actions ────────────────────────────────────────────────────────────
    def compile_canvas(self):
        nl = self.scene.generate_netlist()
        self.text_editor.setPlainText(nl)
        self.status.showMessage(f"Netlist compiled — {len(nl.splitlines())} component(s)")

    def run_transient(self):
        self.plot_widget.clear()
        text = self.text_editor.toPlainText().strip()
        if not text:
            self.status.showMessage("⚠  Netlist is empty — compile first or type manually")
            return
        try:
            dt       = float(self.dt_input.text())
            end_time = float(self.end_time_input.text())

            self.status.showMessage("Running transient simulation…")
            QApplication.processEvents()

            components      = network_helper.parse_network(text)
            graph, clist    = network_helper.assemble_network_graph(components)
            voltage_history = lumped.MNA_time(graph, clist, dt, end_time, plot_voltage=False)

            n_steps   = len(next(iter(voltage_history.values())))
            time_axis = np.arange(n_steps) * dt

            colors = [CLR_ACCENT, CLR_GREEN, CLR_AMBER, CLR_RED, CLR_ACCENT2,
                      "#3dd6d6", "#f79231", "#d63d8c"]

            self.plot_widget.addLegend(
                offset=(10, 10),
                brush=pg.mkBrush(CLR_SURFACE + "cc"),
                pen=pg.mkPen(CLR_BORDER),
                labelTextColor=CLR_TEXT,
            )
            for i, (node, history) in enumerate(voltage_history.items()):
                if node != '0':
                    self.plot_widget.plot(
                        time_axis, history,
                        pen=pg.mkPen(colors[i % len(colors)], width=2),
                        name=f"V({node})",
                    )

            self.status.showMessage(
                f"Transient done — {n_steps} steps, dt={dt} s, t_end={end_time} s"
            )
            self.result_label.setText("")

        except Exception as e:
            self.status.showMessage(f"Simulation error: {e}")
            self.result_label.setText(f"Error:\n{e}")
            self.result_label.setStyleSheet(f"color: {CLR_RED}; font-size: 12px; font-family: monospace;")

    def run_operating_point(self):
        """
        Calls lumped.MNA() which prints node voltages and currents to stdout.
        We capture those results by monkey-patching print, then display them
        in the result panel.  MNA() replaces caps→open and inductors→short
        before solving, which is the correct DC operating-point treatment.
        """
        text = self.text_editor.toPlainText().strip()
        if not text:
            self.status.showMessage("⚠  Netlist is empty — compile first")
            return
        try:
            self.status.showMessage("Running operating point…")
            QApplication.processEvents()

            components   = network_helper.parse_network(text)
            graph, clist = network_helper.assemble_network_graph(components)

            # Capture printed output from lumped.MNA
            captured = []
            import builtins
            _orig_print = builtins.print
            def _capture(*args, **kwargs):
                captured.append(" ".join(str(a) for a in args))
            builtins.print = _capture
            try:
                lumped.MNA(graph, clist)
            finally:
                builtins.print = _orig_print

            out = "\n".join(captured) if captured else "(no output)"
            self.result_label.setText(out)
            self.result_label.setStyleSheet(
                f"color: {CLR_GREEN}; font-size: 12px; font-family: monospace;"
            )
            self.status.showMessage("Operating point solved ✓")

        except Exception as e:
            self.result_label.setText(f"Error:\n{e}")
            self.result_label.setStyleSheet(
                f"color: {CLR_RED}; font-size: 12px; font-family: monospace;"
            )
            self.status.showMessage(f"Operating point error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())