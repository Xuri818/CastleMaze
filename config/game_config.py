class GameConfig:
    _game_mode = None
    _maze_size = None
    
    @classmethod
    def set_game_mode(cls, mode):
        """
    This function sets the game mode when the user clicks the mode or when it loads the game.
    If the game mode is not the only valid option (Classic or Solver), it raise a valueerror for that error.
    It does not return anything, it only sets the attribute. 
    
        """
        if mode is None or mode in ["Classic", "Solver"]:
            cls._game_mode = mode
        else:
            raise ValueError("Modo de juego no valido. Use 'Classic', 'Solver' o None")

    @classmethod
    def get_game_mode(cls):
        """
    This function sends the chosen game mode, Classic or Solver.
    If the game mode has not been set, raises a ValueError.
    Returns:
        str: The game mode.
        """

        if cls._game_mode is None:
            raise ValueError("Modo de juego no ha sido establecido")
        return cls._game_mode

    @classmethod
    def set_maze_size(cls, size):
        """
    This function sets the size of the maze when the user clicks the size or when it loads the game.
    If the size is not within the valid range, it raise a valueerror for that error.
    It does not return anything, it only sets the attribute. 

        """
        if size is None or (isinstance(size, int) and 3 <= size <= 50):
            cls._maze_size = size
        else:
            raise ValueError("Tamaño debe ser None o entero entre 3 y 50")

    @classmethod
    def get_maze_size(cls):
        """
    This function sends the configured maze size.
    If the maze size has not been set, raises a ValueError.
    
    Returns:
        int: The size of the maze.
        """

        if cls._maze_size is None:
            raise ValueError("Tamaño no ha sido establecido")
        return cls._maze_size

    @classmethod
    def reset(cls):
        """
        Resets the game configuration to its default state.
        This method sets the game mode and maze size to None, effectively
        discarding any previous configuration.
        """
        cls._game_mode = None
        cls._maze_size = None