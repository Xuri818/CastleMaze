from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QSpacerItem, 
    QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPalette, QBrush
from config.atlas_loader import AtlasLoader
from config.game_config import GameConfig

class GameModeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.atlas_loader = AtlasLoader()
        self._setup_ui()
    
    def _setup_ui(self):
        # Configurar imagen de fondo primero
        self._set_background()
        
        # Configurar el tamaño fijo del widget
        self.setFixedSize(1000, 800)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Layout horizontal para los botones de modo
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(30)
        modes_layout.setContentsMargins(20, 20, 20, 20)
        
        # Crear botones con imágenes
        self.classic_button = self._create_image_button("pj", "down_standing", "Classic")
        self.solver_button = self._create_book_button("Solver")
        
        # Añadir botones al layout horizontal
        modes_layout.addWidget(self.classic_button)
        modes_layout.addWidget(self.solver_button)
        
        # Espaciado
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(modes_layout)
        
        # Botón de regresar
        self.back_button = QPushButton("Back to Menu")
        self.back_button.setFixedSize(200, 50)
        
        # Espacio y botón
        main_layout.addSpacerItem(QSpacerItem(20, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        main_layout.addWidget(self.back_button, 0, Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # Estilos
        self._style_buttons()
        
        # Conexión de señales
        self.back_button.clicked.connect(self._go_back)
    
    def _set_background(self):
        """Configura la imagen de fondo bg_game_mode.png"""
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
    
    def _create_image_button(self, atlas_name, frame_name, text):
        """Crea un botón con imagen del atlas y texto"""
        button = QPushButton(self)  # Ahora con parent self
        button.setFixedSize(250, 180)
        
        # Layout vertical para la imagen y el texto
        layout = QVBoxLayout(button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Cargar imagen del atlas
        pixmap = self.atlas_loader.get_frame(atlas_name, frame_name)
        if pixmap and not pixmap.isNull():
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
    
    def _create_book_button(self, text):
        """Crea un botón con la imagen del libro y texto"""
        button = QPushButton(self)  # Ahora con parent self
        button.setFixedSize(250, 180)
        
        # Layout vertical para la imagen y el texto
        layout = QVBoxLayout(button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        # Cargar imagen del libro
        book_pixmap = QPixmap("assets/book.png")
        if not book_pixmap.isNull():
            image_label = QLabel(button)
            scaled_pixmap = book_pixmap.scaled(
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
        # Estilo para los botones de modo
        button_style = """
            QPushButton {
                background-color: rgba(58, 92, 140, 0.8);
                border-radius: 15px;
                border: 3px solid #5a7cac;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(74, 108, 156, 0.9);
                border: 3px solid #6a9ccc;
            }
            QPushButton:pressed {
                background-color: rgba(42, 76, 124, 0.8);
            }
        """
        self.classic_button.setStyleSheet(button_style)
        self.solver_button.setStyleSheet(button_style)
        
        # Conectar señales de los botones de modo
        self.classic_button.clicked.connect(lambda: self._go_to_game_select("Classic"))
        self.solver_button.clicked.connect(lambda: self._go_to_game_select("Solver"))
        
        # Estilo para el botón de regresar
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
    
    def _go_to_game_select(self, game_mode):
        GameConfig.set_game_mode(game_mode)
        self.parent_window.setCurrentIndex(2)
        
    def _go_back(self):
        if self.parent_window:
            self.parent_window.setCurrentIndex(0)  # Volver al menú principal