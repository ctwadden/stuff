"""
Unreal Engine 5 - Game AI Buddy Panel
Shows a Qt-based dialog window inside the Unreal editor.
Call show_buddy_panel() from the Python console or menu.
"""
import unreal

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    QT_AVAILABLE = True
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        QT_AVAILABLE = True
    except ImportError:
        QT_AVAILABLE = False

import buddy_client as client
import terrain_controller as tc

_panel_instance = None

class BuddyPanel(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game AI Buddy - Unreal Engine 5")
        self.setMinimumSize(420, 580)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self._build_ui()
        self._check_server()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Header
        title = QtWidgets.QLabel("Game AI Buddy")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4fc3f7;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        sub = QtWidgets.QLabel("Unreal Engine 5 AI Assistant")
        sub.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(sub)

        # Server status
        self.status_label = QtWidgets.QLabel("Checking server...")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addWidget(self._separator())

        # Quick actions
        quick_group = QtWidgets.QGroupBox("Quick Actions")
        quick_layout = QtWidgets.QGridLayout()

        actions = [
            ("Create Landscape", self.quick_create_landscape),
            ("Add Mountain", self.quick_add_mountain),
            ("Add Lake", self.quick_add_lake),
            ("World Summary", self.quick_world_summary),
            ("Scatter Trees", self.quick_scatter_trees),
            ("Scatter Rocks", self.quick_scatter_rocks),
        ]
        for i, (label, fn) in enumerate(actions):
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(fn)
            quick_layout.addWidget(btn, i // 3, i % 3)

        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)

        layout.addWidget(self._separator())

        # Prompt
        layout.addWidget(QtWidgets.QLabel("Ask AI Buddy:"))
        self.prompt_input = QtWidgets.QPlainTextEdit()
        self.prompt_input.setPlaceholderText(
            "Examples:\n"
            "- Create a mountain range in the northwest corner\n"
            "- Swap all pine trees with oak trees\n"
            "- Scatter 300 boulders on steep slopes\n"
            "- Add a river running east to west\n"
            "- How do I set up a PCG foliage graph?"
        )
        self.prompt_input.setFixedHeight(100)
        layout.addWidget(self.prompt_input)

        self.screenshot_cb = QtWidgets.QCheckBox("Include screenshot")
        layout.addWidget(self.screenshot_cb)

        btn_row = QtWidgets.QHBoxLayout()
        self.ask_btn = QtWidgets.QPushButton("Ask Buddy")
        self.ask_btn.setStyleSheet("background-color: #1565c0; color: white; font-weight: bold; padding: 8px;")
        self.ask_btn.clicked.connect(self.ask_ai)
        btn_row.addWidget(self.ask_btn)

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.setFixedWidth(70)
        clear_btn.clicked.connect(self.clear_all)
        btn_row.addWidget(clear_btn)
        layout.addLayout(btn_row)

        layout.addWidget(self._separator())

        # Reply
        layout.addWidget(QtWidgets.QLabel("Buddy says:"))
        self.reply_box = QtWidgets.QPlainTextEdit()
        self.reply_box.setReadOnly(True)
        self.reply_box.setFixedHeight(140)
        layout.addWidget(self.reply_box)

        # Code block
        layout.addWidget(QtWidgets.QLabel("Generated Code:"))
        self.code_box = QtWidgets.QPlainTextEdit()
        self.code_box.setReadOnly(True)
        self.code_box.setFixedHeight(100)
        self.code_box.setStyleSheet("font-family: monospace; font-size: 11px;")
        layout.addWidget(self.code_box)

        exec_btn = QtWidgets.QPushButton("Execute Code in Unreal")
        exec_btn.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        exec_btn.clicked.connect(self.execute_code)
        layout.addWidget(exec_btn)

        self.exec_status = QtWidgets.QLabel("")
        layout.addWidget(self.exec_status)

    def _separator(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    def _check_server(self):
        online = client.check_online()
        if online:
            self.status_label.setText("Server Online")
            self.status_label.setStyleSheet("color: #4caf50; font-weight: bold;")
        else:
            self.status_label.setText("Server Offline - run: python server/main.py")
            self.status_label.setStyleSheet("color: #f44336; font-weight: bold;")

    def ask_ai(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.ask_btn.setEnabled(False)
        self.ask_btn.setText("Thinking...")
        self.reply_box.setPlainText("Waiting for AI...")
        QtWidgets.QApplication.processEvents()

        try:
            response = client.ask(prompt, self.screenshot_cb.isChecked())
            self.reply_box.setPlainText(response["reply"])
            code = client.extract_python_code(response["reply"])
            self.code_box.setPlainText(code if code else "")
        except ConnectionError as e:
            self.reply_box.setPlainText(str(e))
        except Exception as e:
            self.reply_box.setPlainText(f"Error: {e}")

        self.ask_btn.setEnabled(True)
        self.ask_btn.setText("Ask Buddy")

    def execute_code(self):
        code = self.code_box.toPlainText().strip()
        if not code:
            self.exec_status.setText("No code to execute.")
            return

        try:
            exec(compile(code, "<buddy_ai>", "exec"), {
                "unreal": unreal,
                "tc": tc,
                "client": client,
            })
            self.exec_status.setText("Code executed successfully.")
            self.exec_status.setStyleSheet("color: #4caf50;")
        except Exception as e:
            self.exec_status.setText(f"Error: {e}")
            self.exec_status.setStyleSheet("color: #f44336;")

    def clear_all(self):
        self.prompt_input.clear()
        self.reply_box.clear()
        self.code_box.clear()
        self.exec_status.clear()

    # --- Quick action helpers ---
    def quick_create_landscape(self):
        self.prompt_input.setPlainText("Create a new 2017x2017 landscape for an open world game")
        self.ask_ai()

    def quick_add_mountain(self):
        self.prompt_input.setPlainText("Add a mountain range to the landscape")
        self.ask_ai()

    def quick_add_lake(self):
        self.prompt_input.setPlainText("Add a lake in the center of the map at ground level")
        self.ask_ai()

    def quick_world_summary(self):
        summary = tc.get_world_summary()
        self.reply_box.setPlainText(summary)

    def quick_scatter_trees(self):
        self.prompt_input.setPlainText("Scatter 200 trees across the landscape on flat ground (slope < 20 degrees)")
        self.ask_ai()

    def quick_scatter_rocks(self):
        self.prompt_input.setPlainText("Scatter 150 rocks and boulders on steep slopes (slope > 30 degrees)")
        self.ask_ai()


def show_buddy_panel():
    global _panel_instance
    if not QT_AVAILABLE:
        unreal.log_error("[Buddy] PySide2/PySide6 not available. Cannot show panel.")
        return

    if _panel_instance is None or not _panel_instance.isVisible():
        _panel_instance = BuddyPanel()
    _panel_instance.show()
    _panel_instance.raise_()
    _panel_instance.activateWindow()
