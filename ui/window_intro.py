from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPalette, QBrush

class IntroWidget(QWidget):
    def __init__(self, parent=None):
        """
        This init method sets up the parent window (the window it cames from, which is the main window), 
        and sets up the Ui for the intro screen (the first screen you see when you start the game), like the background, buttons, etc.
        """
        super().__init__(parent)
        self.parent_window = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """
        This method sets up the Ui for the intro screen (the first screen you see when you start the game), like the background, buttons, etc.
        Also, it connects the buttons to their respective functions.
        """
        # Configurar imagen de fondo
        self._set_background()
        
        # Configurar el tamaño fijo del widget
        self.setFixedSize(1000, 800)
        
        # Crear y posicionar botones
        self._create_and_position_buttons()
        
        # Conectar señales
        self._connect_buttons()
    
    def _set_background(self):
        """
        This method sets up the background for the intro screen (the first screen you see when you start the game).
          Searching the image in the assets folder and loading the image intro.png and scaling it to fit the window size.
        """
        try:
            pixmap = QPixmap("assets/bg_intro.png")
            if pixmap.isNull():
                raise FileNotFoundError
            self.background = QLabel(self)
            pixmap = pixmap.scaled(1000, 800, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, 1000, 800)
            self.background.lower()
        except (FileNotFoundError, AttributeError):
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.darkGray)
            self.setPalette(palette)
    
    def _create_and_position_buttons(self):

        """
        This method creates the buttons for the intro screen (the first screen you see when you start the game). 
        It creates the Play, Options, and Credits buttons with fixed sizes and positions.
        """
        # Tamaños fijos
        play_width, play_height = 200, 80
        other_width, other_height = 150, 50
        
        # Posición vertical del botón Play (ajusta este valor)
        play_y = 480 # Más abajo que en la versión anterior
        
        # Posición horizontal del botón Play (centrado exacto)
        play_x = (1000 - play_width) // 2  # 800 es el ancho fijo de la ventana
        
        # Crear botón Play
        self.play_button = QPushButton("PLAY", self)
        self.play_button.setGeometry(play_x, play_y, play_width, play_height)
        
        # Espacio entre botones laterales y el central
        horizontal_spacing = 30  # Separación horizontal
        
        # Crear botón Options (a la izquierda de Play)
        options_x = play_x - other_width - horizontal_spacing
        options_y = play_y + 10  # 10px más abajo que Play
        self.options_button = QPushButton("Options", self)
        self.options_button.setGeometry(options_x, options_y, other_width, other_height)
        
        # Crear botón Credits (a la derecha de Play)
        credits_x = play_x + play_width + horizontal_spacing
        credits_y = play_y + 10  # 10px más abajo que Play
        self.credits_button = QPushButton("Credits", self)
        self.credits_button.setGeometry(credits_x, credits_y, other_width, other_height)
        
        # Estilizar botones
        self._style_buttons()
    
    def _style_buttons(self):

        """
        This method styles the buttons for the intro screen (the first screen you see when you start the game).
        It sets the font size, weight, background color, text color, border radius, and border color for the Play button.
        It also sets the font size, background color, text color, border radius, and border color for the Options and Credits buttons.  """
        # Botón PLAY (grande y naranja/marrón)
        self.play_button.setStyleSheet("""
            QPushButton {
                font-size: 24px;
                font-weight: bold;
                background-color: #c47345;
                color: white;
                border-radius: 10px;
                border: 2px solid #5a3120;
            }
            QPushButton:hover {
                background-color: #eebd86;
            }
            QPushButton:pressed {
                background-color: #c47345;
            }
        """)
        
        # Botones Options y Credits (verde oscuro)
        button_style = """
            QPushButton {
                font-size: 18px;
                background-color: #343b24;
                color: white;
                border-radius: 8px;
                border: 1px solid #100e0a;
            }
            QPushButton:hover {
                background-color: #6e7658;
            }
            QPushButton:pressed {
                background-color: #343b24;
            }
        """
        self.options_button.setStyleSheet(button_style)
        self.credits_button.setStyleSheet(button_style)
    
    def _connect_buttons(self):
        """
        This method connects the signals from the buttons for the intro screen (the first screen you see when you start the game).
        It connects the clicked signal from the Play, Options, and Credits buttons to their respective functions.
        Currentlt it connects them to the _on_play_clicked, _on_options_clicked, and _on_credits_clicked methods.
        Options and credits buttons are not implemented yet. 
        """
        self.play_button.clicked.connect(self._on_play_clicked)
        self.options_button.clicked.connect(self._on_options_clicked)
        self.credits_button.clicked.connect(self._on_credits_clicked)
    
    def _on_play_clicked(self):
        """
        This method is called when the Play button is clicked.
        It changes the current widget to the Game Mode selection widget (index 1).

        """
        print("Play button clicked")
        if self.parent_window:
            self.parent_window.setCurrentIndex(1)  # Cambiar al widget de Game Mode
    
    def _on_options_clicked(self):
        print("Options button clicked")
    
    def _on_credits_clicked(self):
        print("Credits button clicked")