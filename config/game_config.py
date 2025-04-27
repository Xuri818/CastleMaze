class GameConfig:
    _game_mode = None
    _maze_size = None
    
    @classmethod
    def set_game_mode(cls, mode):
        """Permite None para resetear, o 'Classic'/'Solver'"""
        if mode is None or mode in ["Classic", "Solver"]:
            cls._game_mode = mode
        else:
            raise ValueError("Modo de juego no válido. Use 'Classic', 'Solver' o None")

    @classmethod
    def get_game_mode(cls):
        if cls._game_mode is None:
            raise ValueError("Modo de juego no ha sido establecido")
        return cls._game_mode

    @classmethod
    def set_maze_size(cls, size):
        """Permite None para resetear, o enteros 3-50"""
        if size is None or (isinstance(size, int) and 3 <= size <= 50):
            cls._maze_size = size
        else:
            raise ValueError("Tamaño debe ser None o entero entre 3 y 50")

    @classmethod
    def get_maze_size(cls):
        if cls._maze_size is None:
            raise ValueError("Tamaño no ha sido establecido")
        return cls._maze_size

    @classmethod
    def reset(cls):
        """Resetea la configuración"""
        cls._game_mode = None
        cls._maze_size = None