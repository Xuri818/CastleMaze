import json
from PyQt6.QtGui import QPixmap
from pathlib import Path

class AtlasLoader:
    def __init__(self, assets_dir="assets"):
        self.assets_dir = Path(assets_dir)
        self.atlas_data = {}
        self.load_atlas_data()
    
    def load_atlas_data(self):
        """Carga los datos del archivo atlas.json"""
        atlas_file = self.assets_dir / "atlas.json"
        try:
            with open(atlas_file, 'r') as f:
                self.atlas_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading atlas data: {e}")
            self.atlas_data = {}
    
    def get_frame(self, atlas_name, frame_name):
        """
        Obtiene un frame específico de un atlas
        Returns: QPixmap or None
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
        """Obtiene todos los frames de un atlas específico"""
        atlas = self.atlas_data.get(atlas_name)
        if not atlas:
            return {}
        
        frames = {}
        for frame_name, frame_info in atlas["frames"].items():
            pixmap = self.get_frame(atlas_name, frame_name)
            if pixmap:
                frames[frame_name] = pixmap
        
        return frames