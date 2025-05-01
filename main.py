import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon  # Importar QIcon
from ui.window_intro import IntroWidget
from ui.window_game_mode import GameModeWidget
from ui.window_game_select import GameSelectWidget
from ui.window_size import SizeSelectWidget
from ui.window_maze import MazeWidget
from config.game_config import GameConfig

class MainWindow(QStackedWidget):
    def __init__(self):
        """
    This function initializes the main window of the Castle Maze application, setting up
    the initial configuration, creating and adding the necessary widgets,
    and establishing signal connections.
Sets the window icon and title.
    - Fixes the window size to 1000x800.
    - Resets the game configuration.
    - Creates intro, game mode, game select, and size select widgets.
    - Connects the start game signal from the size select widget to create the maze widget.
    - Adds the widgets to the stacked widget and shows the intro screen initially.
        """

        super().__init__()
        
        # Configuración inicial
        self.setWindowIcon(QIcon('assets/icon.png'))
        self.setWindowTitle("Castle Maze")
        self.setFixedSize(1000, 800)
        GameConfig.reset()
        
        # Crear widgets
        self.intro_widget = IntroWidget(self)
        self.game_mode_widget = GameModeWidget(self)
        self.game_select_widget = GameSelectWidget(self)
        self.size_select_widget = SizeSelectWidget(self)
        self.maze_widget = None

        
        # Configurar conexión de señales ANTES de añadir widgets
        self.size_select_widget.start_game_signal.connect(self._create_maze_widget)
        
        # Añadir widgets
        self.addWidget(self.intro_widget)        # Índice 0
        self.addWidget(self.game_mode_widget)    # Índice 1
        self.addWidget(self.game_select_widget)  # Índice 2
        self.addWidget(self.size_select_widget)  # Índice 3
       

        
        # Mostrar pantalla inicial
        self.setCurrentWidget(self.intro_widget)
    
    def handle_maze_widget_cleanup(self):
        """
    This method cleans up the maze widget by removing it from the stack (if it exists) and deleting it.
    
    - Checks if the maze widget exists and is a valid widget type.
    - Removes the widget from the stack and deletes it.
    - Ignores RuntimeError if the widget is already deleted.
    - Resets the maze_widget instance variable to None.
        """

        if hasattr(self, 'maze_widget') and self.maze_widget is not None:
            try:
                # Verificar si el widget aún existe
                if self.maze_widget.isWidgetType():
                    # Eliminar el widget y quitarlo de la pila
                    self.removeWidget(self.maze_widget)
                    self.maze_widget.deleteLater()
            except RuntimeError:
                # Ignorar el error si el widget ya fue eliminado
                pass  
            finally:
                # Establecer la variable de instancia en None
                self.maze_widget = None

    def _create_maze_widget(self):
        """
    This method creates and displays a new MazeWidget instance, it means the user clicked the maze size so it starts the game for him. 
    It is a connection between wndow_size and window_maze.

    - Cleans up any existing maze widget instance before creating a new one.
    - Ensures that game mode and maze size are configured before proceeding.
    - Initializes a new MazeWidget and adds it to the stacked widget.
    - Handles ValueError exceptions by displaying the intro screen.
        """

        try:
            # Limpiar primero cualquier instancia previa
            self.handle_maze_widget_cleanup()
            
            # Verificar configuración
            # - El modo de juego debe estar establecido
            # - El tamaño del laberinto debe estar establecido
            GameConfig.get_game_mode()
            GameConfig.get_maze_size()
            
            # Crear nueva instancia
            self.maze_widget = MazeWidget(self)
            self.addWidget(self.maze_widget)
            self.setCurrentIndex(4)
            
        except ValueError as e:
            # Mostrar pantalla de inicio si hay un error de configuración
            print(f"Error de configuración: {e}")
            self.setCurrentIndex(0)

    def load_saved_maze(self, maze_data):
        """
    This method loads and displays a saved maze configuration.

    - Cleans up any existing maze widget instance before loading a new one.
    - Sets the maze size using data from the provided maze configuration.
    - Initializes a new MazeWidget with the loaded maze data and adds it to the stacked widget.
    - Handles exceptions by displaying an error message and returning to the intro screen.
    
    Parameters:
    maze_data (dict): A dictionary containing the maze configuration, including rows.
        """

        try:
            self.handle_maze_widget_cleanup()
        
            # Aquí no necesitas pedir modo o tamaño: ya viene dado.
            GameConfig.set_maze_size(maze_data['rows'])
            self.maze_widget = MazeWidget(self, loaded_maze=maze_data)

            self.addWidget(self.maze_widget)
            self.setCurrentIndex(4)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize maze: {e}")
            self.setCurrentIndex(0)


def main():
    """
    Entry point of the application.

    - Creates a new QApplication instance with the provided command line arguments.
    - Creates a new MainWindow instance.
    - Shows the main window.
    - Starts the application event loop and waits for it to finish.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()