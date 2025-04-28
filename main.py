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
        """Maneja la limpieza segura del maze widget"""
        if hasattr(self, 'maze_widget') and self.maze_widget is not None:
            try:
                # Verificar si el widget aún existe
                if self.maze_widget.isWidgetType():
                    self.removeWidget(self.maze_widget)
                    self.maze_widget.deleteLater()
            except RuntimeError:
                pass  # El widget ya fue eliminado
            finally:
                self.maze_widget = None

    def _create_maze_widget(self):
        """Crea una nueva instancia del maze widget"""
        try:
            # Limpiar primero cualquier instancia previa
            self.handle_maze_widget_cleanup()
            
            # Verificar configuración
            GameConfig.get_game_mode()
            GameConfig.get_maze_size()
            
            # Crear nueva instancia
            self.maze_widget = MazeWidget(self, loaded_maze=None)
            self.addWidget(self.maze_widget)
            self.setCurrentIndex(4)
            
        except ValueError as e:
            print(f"Error de configuración: {e}")
            self.setCurrentIndex(0)

    def load_saved_maze(self, maze_data):
        """Carga un laberinto guardado y muestra MazeWidget"""
        try:
            self.handle_maze_widget_cleanup()
        
            # Aquí no necesitas pedir modo o tamaño: ya viene dado.
            GameConfig.set_game_mode(maze_data['game_mode'])
            GameConfig.set_maze_size(maze_data['rows'])
            self.maze_widget = MazeWidget(self, loaded_maze=maze_data)

            self.addWidget(self.maze_widget)
            self.setCurrentIndex(4)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize maze: {e}")
            self.setCurrentIndex(0)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()