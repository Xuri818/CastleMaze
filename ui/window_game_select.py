from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect,
    QFrame, QLabel, QPushButton, QGraphicsView, QApplication,
    QGraphicsScene, QGraphicsPixmapItem, QMessageBox
)
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QSpacerItem, 
    QSizePolicy
)

from PyQt6.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPalette, QTransform, QPainter, QKeyEvent
from ui.window_maze import MazeWidget
from PyQt6.QtWidgets import QFileDialog
import os
import json
from config.game_config import GameConfig
from PyQt6.QtWidgets import QFileDialog

class GameSelectWidget(QWidget):
    def __init__(self, parent=None):
        """
This init method initializes the GameSelectWidget, which is part of the UI for selecting a game.
It sets the parent window and calls the method to set up the user interface components.
        """

        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
     
    def _setup_ui(self):
        # Configurar imagen de fondo
        """
    This method sets up the UI for the game selection widget. It includes
    setting the background, fixing the size of the widget, and arranging the
    buttons in a horizontal layout. It creates buttons for starting a new game
    and loading an existing maze, and a back button to return to the game mode
    selection screen. Additionally, it applies styles to the buttons and
    connects the back button to its respective function.
        """

        self._set_background()
        
        # Configurar el tamaño fijo del widget
        self.setFixedSize(1000, 800)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
      
        # Layout horizontal para los botones principales
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        
        # Crear botones con imágenes
        self.new_game_button = self._create_image_button("parchment.png", "New Game")
        self.load_maze_button = self._create_image_button("books.png", "Load Maze")
        
        # Añadir botones al layout horizontal
        buttons_layout.addWidget(self.new_game_button)
        buttons_layout.addWidget(self.load_maze_button)
        
        # Botón de regresar
        self.back_button = QPushButton("Back to Select Game", self)
        self.back_button.setFixedSize(200, 50)
        
        # Añadir widgets al layout principal
        main_layout.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(buttons_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Estilos
        self._style_buttons()
        
        # Conexión de señales
        self.back_button.clicked.connect(self._go_back)
    
    def _set_background(self):
        
        """
        This method sets up the background for the game selection widget. It tries to
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
            # Escalar la imagen al tamaño de la ventana
            pixmap = pixmap.scaled(
                1000, 800, 
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, 1000, 800)
            self.background.lower()  # Enviar al fondo
        except (FileNotFoundError, AttributeError):
            # Si no se encuentra la imagen, usar un color sólido
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.darkGray)
            self.setPalette(palette)
    
    def _create_image_button(self, image_path, text):
        
        """
        This method creates a button with an image from the assets folder and a text label below it.
        It gets a specific image from the assets folder using the image_path parameter.
        It returns a QPushButton object with the image and text.
        """
        
        button = QPushButton(self)
        button.setFixedSize(250, 180)
        
        # Layout vertical para la imagen y el texto
        layout = QVBoxLayout(button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Cargar imagen
        pixmap = QPixmap(f"assets/{image_path}")
        if not pixmap.isNull():
            image_label = QLabel(button)
            scaled_pixmap = pixmap.scaled(
                100, 100, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(image_label)
        
        # Añadir texto
        text_label = QLabel(text, button)
        text_label.setStyleSheet("""
            QLabel {
                font-size: 28px; 
                font-weight: bold; 
                color: white;
                margin-top: 10px;
            }
        """)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)
        
        return button
    
    def _style_buttons(self):
        # Estilo para los botones principales (verde musgo)
        """
        This method styles the buttons in the game selection screen, including the New Game, Load Maze, and Back buttons.
        It sets the background color, border radius, border color, and pressed styles for the main buttons.
        It also sets the font size, background color, text color, border radius, and border color for the Back button.
        Additionally, it connects the New Game and Load Maze buttons to their respective slots.
        """
        main_button_style = """
            QPushButton {
                background-color: rgba(67, 93, 56, 0.8);
                border-radius: 15px;
                border: 3px solid #8a9c7d;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(87, 113, 76, 0.9);
                border: 3px solid #aabcaf;
            }
            QPushButton:pressed {
                background-color: rgba(47, 73, 36, 0.8);
            }
        """
        self.new_game_button.setStyleSheet(main_button_style)
        self.load_maze_button.setStyleSheet(main_button_style)
        
        # Conectar señal del botón New Game
        self.new_game_button.clicked.connect(self._start_new_game)
        self.load_maze_button.clicked.connect(self._load_game)
        
        # Estilo para el botón de regresar (gris)
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
    
    def _start_new_game(self):
        """
        This method is called when the New Game button is clicked.
        It changes the current widget to the size selection screen (index 3).
        """

        self.parent_window.setCurrentIndex(3)    # Ve a selección de tamaño

    def _load_game(self):
        
        """
        This method is called when the Load Maze button is clicked.
        It opens a file dialog for the user to select a JSON file containing a maze configuration.
        If a file is selected, it tries to load the maze configuration from the file and tell the parent window to load it.
        If the file cannot be loaded, it shows an error message box.
        """

        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Seleccionar archivo de mapa", 
            "", 
            "Archivos JSON (*.json);;Todos los archivos (*)", 
            options=options
        )


        if file_path:
            try:
                with open(file_path, "r") as file:
                    # Cargar el laberinto: es una lista de listas de enteros
                    import json
                    maze_data = json.load(file)
            
                #  a la ventana principal que cargue el laberinto
                if self.parent_window:
                    self.parent_window.load_saved_maze(maze_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load maze: {e}")

            
    def _go_back(self):
        """
        This method is called when the Back button is clicked.
        It changes the current widget to the game mode selection screen (index 1).
        """
        if self.parent_window:
            self.parent_window.setCurrentIndex(1)  # Volver a la selección de modo