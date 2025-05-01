import json
from PyQt6.QtGui import QPixmap
from pathlib import Path

class AtlasLoader:
    def __init__(self, assets_dir="assets"):
        """
    This function initializes the AtlasLoader with the specified assets directory.
    Also it uses the directory where the atlas assets are located. 
                      Defaults to "assets".
        """

        self.assets_dir = Path(assets_dir)
        self.atlas_data = {}
        self.load_atlas_data()
    
    def load_atlas_data(self):
        """
    This function loads the atlas data from a JSON file into the atlas_data attribute, it is loading all those textures and images characteristics for the maze.
    This function is used in the maze to load all the textures and images.
    The method tries to open the "atlas.json" file located in the assets directory.
    In case of an error like file not found or JSON decode error, an error message is sent,
    and the atlas_data attribute is set to an empty dictionary.
        """

        atlas_file = self.assets_dir / "atlas.json"
        try:
            with open(atlas_file, 'r') as f:
                self.atlas_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading atlas data: {e}")
            self.atlas_data = {}
    
    def get_frame(self, atlas_name, frame_name):
        
        """
    This function  recuperates a specific frame from the given atlas by name, recieving them as parameters.
    This function is useful when you want to access a specific frame from an atlas.
    This method recuperates the frame information for the specified frame name using / and with the provided atlas name. 
    It then loads the associated image file, takes that specific frame region, and returns it as a QPixmap object.

    Returns:
    QPixmap: The pixmap of the specified frame, or None if the atlas/frame is not found, 
    or if the image file cannot be loaded.
        """

        atlas = self.atlas_data.get(atlas_name)
        if not atlas:
            print(f"Atlas '{atlas_name}' not found")
            return None
        
        frame_info = atlas["frames"].get(frame_name)
        if not frame_info:
            print(f"Frame '{frame_name}' not found in atlas '{atlas_name}'")
            return None
        
        # Cargar la imagen principal
        image_path = self.assets_dir / atlas["image_path"]
        if not image_path.exists():
            print(f"Image file not found: {image_path}")
            return None
        
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            print(f"Failed to load image: {image_path}")
            return None
        
        # Extraer la región específica
        return pixmap.copy(
            frame_info["x"],
            frame_info["y"],
            frame_info["width"],
            frame_info["height"]
        )
    
    def get_all_frames(self, atlas_name):
        """
    This function returns all frames from the specified atlas, recieving the atlas as parameter.
    It looks up the atlas data in the atlas_data attribute, and returns a dictionary containing all frames from that atlas.
    This method is useful for cases where you want to access all frames in an atlas without having to know their names.

    Returns:
        dict: A dictionary containing all frames from the specified atlas.
        """
        atlas = self.atlas_data.get(atlas_name)
        if not atlas:
            return {}
        
        frames = {}
        for frame_name, frame_info in atlas["frames"].items():
            pixmap = self.get_frame(atlas_name, frame_name)
            if pixmap:
                frames[frame_name] = pixmap
        
        return frames