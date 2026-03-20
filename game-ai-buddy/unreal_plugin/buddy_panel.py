"""
Unreal Engine 5 - Game AI Buddy Panel (v2)
Features: Do / Teach mode | Vision | PCG Biome builder | Asset swap | World summary
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
import pcg_builder as pcg

_panel_instance = None

DARK_STYLE = """
QDialog { background-color: #1e1e2e; color: #cdd6f4; font-size: 13px; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 8px; padding: 6px; color: #cdd6f4; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; color: #89b4fa; font-weight: bold; }
QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 6px 10px; }
QPushButton:hover { background-color: #45475a; }
QPushButton#primary { background-color: #1e66f5; color: white; font-weight: bold; border: none; }
QPushButton#primary:hover { background-color: #3579f6; }
QPushButton#success { background-color: #40a02b; color: white; font-weight: bold; border: none; }
QPushButton#success:hover { background-color: #52b33b; }
QPushButton#vision { background-color: #8839ef; color: white; font-weight: bold; border: none; }
QPlainTextEdit, QTextEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; font-family: monospace; }
QLabel { color: #cdd6f4; }
QLabel#title { color: #89b4fa; font-size: 18px; font-weight: bold; }
QLabel#online { color: #40a02b; font-weight: bold; }
QLabel#offline { color: #d20f39; font-weight: bold; }
QComboBox { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 4px; padding: 4px; }
QTabWidget::pane { border: 1px solid #45475a; }
QTabBar::tab { background: #313244; color: #cdd6f4; padding: 6px 14px; border-radius: 4px 4px 0 0; }
QTabBar::tab:selected { background: #45475a; color: #89b4fa; font-weight: bold; }
QCheckBox { color: #cdd6f4; }
QSlider::groove:horizontal { background: #45475a; height: 4px; border-radius: 2px; }
QSlider::handle:horizontal { background: #89b4fa; width: 14px; height: 14px; border-radius: 7px; margin: -5px 0; }
"""

class BuddyPanel(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Game AI Buddy - Unreal Engine 5")
        self.setMinimumSize(460, 680)
        self.setStyleSheet(DARK_STYLE)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self._build_ui()
        self._check_server()

    # -----------------------------------------------------------------------
    #  UI
    # -----------------------------------------------------------------------

    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(6)

        # Header
        title = QtWidgets.QLabel("Game AI Buddy")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(title)

        sub = QtWidgets.QLabel("Unreal Engine 5")
        sub.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(sub)

        self.status_label = QtWidgets.QLabel("Checking server...")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(self.status_label)

        # Mode selector
        mode_row = QtWidgets.QHBoxLayout()
        mode_row.addWidget(QtWidgets.QLabel("Mode:"))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Do It (generate code)", "Teach Me (step-by-step)"])
        mode_row.addWidget(self.mode_combo)
        root.addLayout(mode_row)

        root.addWidget(self._separator())

        # Tabs
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_chat_tab(), "Chat")
        tabs.addTab(self._build_biome_tab(), "Biome / PCG")
        tabs.addTab(self._build_terrain_tab(), "Terrain")
        tabs.addTab(self._build_assets_tab(), "Assets")
        root.addWidget(tabs)

        root.addWidget(self._separator())

        # Reply
        root.addWidget(QtWidgets.QLabel("Buddy says:"))
        self.reply_box = QtWidgets.QPlainTextEdit()
        self.reply_box.setReadOnly(True)
        self.reply_box.setFixedHeight(130)
        root.addWidget(self.reply_box)

        # Code
        root.addWidget(QtWidgets.QLabel("Generated Code:"))
        self.code_box = QtWidgets.QPlainTextEdit()
        self.code_box.setReadOnly(True)
        self.code_box.setFixedHeight(90)
        root.addWidget(self.code_box)

        exec_btn = QtWidgets.QPushButton("Execute Code in Unreal")
        exec_btn.setObjectName("success")
        exec_btn.clicked.connect(self.execute_code)
        root.addWidget(exec_btn)

        self.exec_status = QtWidgets.QLabel("")
        root.addWidget(self.exec_status)

    def _build_chat_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        layout.addWidget(QtWidgets.QLabel("Ask AI Buddy anything:"))
        self.prompt_input = QtWidgets.QPlainTextEdit()
        self.prompt_input.setPlaceholderText(
            "Examples:\n"
            "- How do I set up a PCG foliage graph?\n"
            "- Create a mountain with river in the valley\n"
            "- Swap all oak trees with pine trees\n"
            "- Teach me how to use the Landscape tool\n"
            "- How do I add lumen global illumination?"
        )
        self.prompt_input.setFixedHeight(100)
        layout.addWidget(self.prompt_input)

        self.screenshot_cb = QtWidgets.QCheckBox("Include screenshot (Buddy sees your screen)")
        layout.addWidget(self.screenshot_cb)

        row = QtWidgets.QHBoxLayout()
        self.ask_btn = QtWidgets.QPushButton("Ask Buddy")
        self.ask_btn.setObjectName("primary")
        self.ask_btn.clicked.connect(self.ask_ai)
        row.addWidget(self.ask_btn)

        see_btn = QtWidgets.QPushButton("See My Screen")
        see_btn.setObjectName("vision")
        see_btn.clicked.connect(self.see_screen)
        row.addWidget(see_btn)

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.setFixedWidth(60)
        clear_btn.clicked.connect(self.clear_all)
        row.addWidget(clear_btn)
        layout.addLayout(row)

        layout.addStretch()
        return w

    def _build_biome_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        info = QtWidgets.QLabel(
            "Populate your level with a complete biome.\n"
            "Update asset paths in pcg_builder.py to match your downloaded assets."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QtWidgets.QFormLayout()
        self.biome_combo = QtWidgets.QComboBox()
        self.biome_combo.addItems(["forest", "desert", "mountain", "swamp", "coastal", "tundra"])
        form.addRow("Biome:", self.biome_combo)

        self.density_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.density_slider.setRange(10, 300)
        self.density_slider.setValue(100)
        self.density_label = QtWidgets.QLabel("1.0x")
        self.density_slider.valueChanged.connect(lambda v: self.density_label.setText(f"{v/100:.1f}x"))
        density_row = QtWidgets.QHBoxLayout()
        density_row.addWidget(self.density_slider)
        density_row.addWidget(self.density_label)
        form.addRow("Density:", density_row)

        self.area_spin = QtWidgets.QSpinBox()
        self.area_spin.setRange(1000, 100000)
        self.area_spin.setValue(10000)
        self.area_spin.setSuffix(" cm")
        form.addRow("Area Size:", self.area_spin)

        self.clear_existing_cb = QtWidgets.QCheckBox("Clear previous buddy actors first")
        self.clear_existing_cb.setChecked(True)
        form.addRow("", self.clear_existing_cb)

        layout.addLayout(form)

        populate_btn = QtWidgets.QPushButton("Populate Biome")
        populate_btn.setObjectName("primary")
        populate_btn.clicked.connect(self.populate_biome)
        layout.addWidget(populate_btn)

        clear_btn = QtWidgets.QPushButton("Clear All Buddy Actors")
        clear_btn.clicked.connect(lambda: [pcg.clear_buddy_actors(), self.exec_status.setText("Cleared all buddy actors.")])
        layout.addWidget(clear_btn)

        layout.addWidget(self._separator())

        # Biome mix
        mix_group = QtWidgets.QGroupBox("Mix Two Biomes")
        mix_layout = QtWidgets.QFormLayout()
        self.mix_a = QtWidgets.QComboBox()
        self.mix_a.addItems(pcg.list_biomes())
        self.mix_b = QtWidgets.QComboBox()
        self.mix_b.addItems(pcg.list_biomes())
        self.mix_b.setCurrentIndex(1)
        self.mix_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mix_slider.setRange(0, 100)
        self.mix_slider.setValue(50)
        mix_layout.addRow("Biome A:", self.mix_a)
        mix_layout.addRow("Biome B:", self.mix_b)
        mix_layout.addRow("Blend A→B:", self.mix_slider)
        mix_group.setLayout(mix_layout)
        layout.addWidget(mix_group)

        mix_btn = QtWidgets.QPushButton("Mix Biomes")
        mix_btn.clicked.connect(self.mix_biomes)
        layout.addWidget(mix_btn)

        layout.addStretch()
        return w

    def _build_terrain_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        layout.addWidget(QtWidgets.QLabel("Terrain Quick Actions:"))

        actions = [
            ("Create Landscape (2017x2017)", self.quick_create_landscape),
            ("Add Mountain (center)", self.quick_mountain),
            ("Add Lake (center)", self.quick_lake),
            ("Add River (E→W)", self.quick_river),
            ("World Summary", self.quick_summary),
        ]
        for label, fn in actions:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(fn)
            layout.addWidget(btn)

        layout.addWidget(self._separator())
        layout.addWidget(QtWidgets.QLabel("Or describe terrain changes:"))
        self.terrain_prompt = QtWidgets.QLineEdit()
        self.terrain_prompt.setPlaceholderText("e.g. Add a volcano in the northeast corner")
        layout.addWidget(self.terrain_prompt)

        ask_terrain = QtWidgets.QPushButton("Ask AI for Terrain Code")
        ask_terrain.setObjectName("primary")
        ask_terrain.clicked.connect(self.ask_terrain_ai)
        layout.addWidget(ask_terrain)

        layout.addStretch()
        return w

    def _build_assets_tab(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        layout.addWidget(QtWidgets.QLabel("Asset Swap:"))
        form = QtWidgets.QFormLayout()
        self.old_asset = QtWidgets.QLineEdit("/Game/OldAsset/SM_Old")
        self.new_asset = QtWidgets.QLineEdit("/Game/NewAsset/SM_New")
        form.addRow("Old Asset Path:", self.old_asset)
        form.addRow("New Asset Path:", self.new_asset)
        layout.addLayout(form)

        swap_btn = QtWidgets.QPushButton("Swap All Matching Actors")
        swap_btn.clicked.connect(self.swap_assets)
        layout.addWidget(swap_btn)

        layout.addWidget(self._separator())
        layout.addWidget(QtWidgets.QLabel("Custom scatter:"))
        self.scatter_prompt = QtWidgets.QLineEdit()
        self.scatter_prompt.setPlaceholderText("e.g. Scatter 300 pine trees on slopes below 30 degrees")
        layout.addWidget(self.scatter_prompt)

        scatter_btn = QtWidgets.QPushButton("Ask AI for Scatter Code")
        scatter_btn.setObjectName("primary")
        scatter_btn.clicked.connect(self.ask_scatter_ai)
        layout.addWidget(scatter_btn)

        layout.addStretch()
        return w

    def _separator(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        return line

    # -----------------------------------------------------------------------
    #  Actions
    # -----------------------------------------------------------------------

    def _get_mode(self):
        return "teach" if self.mode_combo.currentIndex() == 1 else "do"

    def _check_server(self):
        online = client.check_online()
        if online:
            self.status_label.setText("Server Online")
            self.status_label.setObjectName("online")
        else:
            self.status_label.setText("Server Offline — run start_server.bat / start_server.sh")
            self.status_label.setObjectName("offline")
        self.status_label.setStyleSheet(
            "color: #40a02b; font-weight: bold;" if online else "color: #d20f39; font-weight: bold;"
        )

    def _ask(self, prompt: str, screenshot: bool = False):
        self.ask_btn.setEnabled(False)
        self.ask_btn.setText("Thinking...")
        self.reply_box.setPlainText("Waiting for AI...")
        QtWidgets.QApplication.processEvents()

        try:
            response = client.ask(prompt, include_screenshot=screenshot, mode=self._get_mode())
            self.reply_box.setPlainText(response["reply"])
            code = client.extract_python_code(response["reply"])
            self.code_box.setPlainText(code or "")
        except ConnectionError as e:
            self.reply_box.setPlainText(str(e))
        except Exception as e:
            self.reply_box.setPlainText(f"Error: {e}")

        self.ask_btn.setEnabled(True)
        self.ask_btn.setText("Ask Buddy")

    def ask_ai(self):
        prompt = self.prompt_input.toPlainText().strip()
        if prompt:
            self._ask(prompt, self.screenshot_cb.isChecked())

    def see_screen(self):
        prompt = self.prompt_input.toPlainText().strip() or \
            "Look at my Unreal Editor screen. What am I working on and what should I do next?"
        self._ask(prompt, screenshot=True)

    def populate_biome(self):
        biome = self.biome_combo.currentText()
        density = self.density_slider.value() / 100
        area = self.area_spin.value()
        clear = self.clear_existing_cb.isChecked()
        self.exec_status.setText(f"Populating {biome} biome...")
        QtWidgets.QApplication.processEvents()
        count = pcg.populate_biome(biome, area, density, clear)
        self.exec_status.setText(f"Done — placed {count} actors.")

    def mix_biomes(self):
        a = self.mix_a.currentText()
        b = self.mix_b.currentText()
        blend = self.mix_slider.value() / 100
        self.exec_status.setText(f"Mixing {a} + {b}...")
        QtWidgets.QApplication.processEvents()
        pcg.mix_biomes(a, b, blend, self.area_spin.value())
        self.exec_status.setText("Biome mix complete.")

    def swap_assets(self):
        tc.swap_all_actors(self.old_asset.text(), self.new_asset.text())
        self.exec_status.setText("Asset swap complete — check Unreal output log.")

    def ask_terrain_ai(self):
        p = self.terrain_prompt.text().strip()
        if p:
            self._ask(p)

    def ask_scatter_ai(self):
        p = self.scatter_prompt.text().strip()
        if p:
            self._ask(p)

    def execute_code(self):
        code = self.code_box.toPlainText().strip()
        if not code:
            self.exec_status.setText("No code to execute.")
            return
        try:
            exec(compile(code, "<buddy_ai>", "exec"), {
                "unreal": unreal, "tc": tc, "pcg": pcg, "client": client
            })
            self.exec_status.setText("Executed successfully.")
            self.exec_status.setStyleSheet("color: #40a02b;")
        except Exception as e:
            self.exec_status.setText(f"Error: {e}")
            self.exec_status.setStyleSheet("color: #d20f39;")

    def clear_all(self):
        self.prompt_input.clear()
        self.reply_box.clear()
        self.code_box.clear()
        self.exec_status.clear()

    # Quick terrain actions
    def quick_create_landscape(self):
        self._ask("Create a new landscape actor (2017x2017 resolution) in the current level")
    def quick_mountain(self):
        self._ask("Add a mountain to the center of the landscape using Python")
    def quick_lake(self):
        self._ask("Add a lake water body at the center of the map at z=-50")
    def quick_river(self):
        self._ask("Add a river water body running from the east side of the map to the west")
    def quick_summary(self):
        summary = tc.get_world_summary()
        self.reply_box.setPlainText(summary)


def show_buddy_panel():
    global _panel_instance
    if not QT_AVAILABLE:
        unreal.log_error("[Buddy] PySide2/PySide6 not available.")
        return
    if _panel_instance is None or not _panel_instance.isVisible():
        _panel_instance = BuddyPanel()
    _panel_instance.show()
    _panel_instance.raise_()
    _panel_instance.activateWindow()
