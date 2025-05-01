from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QSpacerItem, 
    QSizePolicy
)
from PyQt6.QtGui import QPixmap, QPalette
from config.game_config import GameConfig

class SizeSelectWidget(QWidget):
    start_game_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        This init method sets up the parent window (the window it cames from, which is the main window),
        and sets up the Ui for the size selection screen, like the background, buttons, etc.
        """
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
    
    def _setup_ui(self):
        # Configurar imagen de fondo
        """
        This method sets up the UI for the size selection screen, like the background, buttons, etc.
        It also connects the buttons to function with their respective parameters. 
        If the difficult is Easy, the size is 10x10, if it's Standard, the size is 15x15, 
        if it's Hard, the size is 20x20 and if it's Extreme, the size is 25x25
        """
        self._set_background()
        self.setFixedSize(1000, 800)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título del modo de juego (obtenido de GameConfig)
        try:
            mode = GameConfig.get_game_mode()
            mode_title = QLabel(f"{mode} - Select Difficulty", self)
        except ValueError:
            mode_title = QLabel("Select Difficulty", self)
            
        mode_title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #e0e0e0;
                margin-bottom: 30px;
            }
        """)
        mode_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Layout para los botones de dificultad
        difficulty_layout = QVBoxLayout()
        difficulty_layout.setSpacing(20)
        difficulty_layout.setContentsMargins(50, 50, 50, 50)
        
        # Crear botones de dificultad
        self.easy_button = self._create_difficulty_button("Easy", "#4a7c59")
        self.standard_button = self._create_difficulty_button("Standard", "#4a6c9c")
        self.hard_button = self._create_difficulty_button("Hard", "#9c6c4a")
        self.extreme_button = self._create_difficulty_button("Extreme", "#9c4a4a")
        
        # Añadir botones al layout
        difficulty_layout.addWidget(self.easy_button)
        difficulty_layout.addWidget(self.standard_button)
        difficulty_layout.addWidget(self.hard_button)
        difficulty_layout.addWidget(self.extreme_button)
        
        # Botón de regresar
        self.back_button = QPushButton("Back", self)
        self.back_button.setFixedSize(150, 50)
        
        # Añadir widgets al layout principal
        main_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addWidget(mode_title)
        main_layout.addLayout(difficulty_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Estilos
        self._style_buttons()
        
        # Conexión de señales
        self.back_button.clicked.connect(self._go_back)
        self.easy_button.clicked.connect(lambda: self._start_game_with_size(11))      # 10x10
        self.standard_button.clicked.connect(lambda: self._start_game_with_size(17))  # 15x15
        self.hard_button.clicked.connect(lambda: self._start_game_with_size(21))      # 20x20
        self.extreme_button.clicked.connect(lambda: self._start_game_with_size(27))   # 25x25
    
    def _set_background(self):
        
        """
        This method sets up the background for the window size widget. It tries to
        load the image bg_game_mode.png from the assets folder and manages it to
        fit the window size while maintaining its aspect. If the image is not
        found or an error occurs during loading, a solid dark gray color is used
        instead. The background is then sent to the back of the window.
        """

        self.background = QLabel(self)
        try:
            pixmap = QPixmap("assets/bg_game_mode.png")
            if pixmap.isNull():
                raise FileNotFoundError
            pixmap = pixmap.scaled(
                1000, 800, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, 1000, 800)
            self.background.lower()
        except (FileNotFoundError, AttributeError):
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.darkGray)
            self.setPalette(palette)
    
    def _create_difficulty_button(self, text, color):
        
        """
        This method creates a button with a specific text and color, and styles it
        with a specific font size, weight, background color, text color, border
        radius, and border color. The button is also given a style.
        The method returns the created button.
        """

        button = QPushButton(text, self)
        button.setFixedSize(300, 80)
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 24px;
                font-weight: bold;
                background-color: {color};
                color: white;
                border-radius: 10px;
                border: 3px solid {self._darken_color(color)};
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(color)};
                border: 3px solid {self._lighten_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color)};
            }}
        """)
        return button
    
    def _lighten_color(self, hex_color, percent=10):
        """
    This method lightens a given hex color by a specified percentage.
    It returns the lightened color. The method uses a simplified implementation.

        """

        return hex_color  # Retornamos el mismo color por simplicidad
    
    def _darken_color(self, hex_color, percent=20):
       
        # Implementación simplificada - en producción usa QColor para manipulación de colores
        """
        This method darkens a given hex color by a specified percentage.
        It returns the darkened color. The method uses a simplified implementation.
        """
        return hex_color  # Retornamos el mismo color por simplicidad
    
    def _style_buttons(self):
        
        """
        This method styles the buttons in the window size widget, specifically the Back button.
        It sets the font size, background color, text color, border radius, and border color for the button.
        It also sets the hover and pressed styles for the button.
        """
        
        self.back_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: rgba(90, 90, 90, 0.8);
                color: white;
                border-radius: 8px;
                border: 1px solid #7a7a7a;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(106, 106, 106, 0.9);
                border: 1px solid #8a8a8a;
            }
            QPushButton:pressed {
                background-color: rgba(74, 74, 74, 0.8);
            }
        """)
    
    def _start_game_with_size(self, size):
        """
        This method sets the maze size to the given size and emits the start game signal.
        It is called when a difficulty button is clicked.
        When the user clicks the difficult, automatically starts the game and shows the MazeWidget window, which is not an index it is a signal.
        It does not directly change the current index of the parent window.
        """
        
        GameConfig.set_maze_size(size)
        self.start_game_signal.emit()  # Emitir señal en lugar de cambiar directamente
    
    def _go_back(self):
        """
        This method is called when the Back button is clicked.
        It changes the current widget to the Game selection widget (index 2).
        """
        if self.parent_window:
            self.parent_window.setCurrentIndex(2)  # Volver a la selección de juego