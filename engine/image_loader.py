"""Image loader with caching for efficient frame rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

import numpy as np
from PIL import Image


class ImageLoader:
    """Loads and caches images for rendering."""
    
    def __init__(self):
        """Initialize image loader with empty cache."""
        self._cache: Dict[Path, np.ndarray] = {}
    
    def load(self, path: Union[str, Path]) -> np.ndarray:
        """
        Load an image file and convert to RGB numpy array.
        
        Args:
            path: Path to image file
            
        Returns:
            HxWx3 numpy array in RGB format
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            Exception: If image is corrupted or invalid
        """
        path = Path(path)
        
        # Check cache
        if path in self._cache:
            return self._cache[path]
        
        # Validate file exists
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        
        try:
            # Load and convert to RGB
            pil_image = Image.open(path)
            pil_image = pil_image.convert('RGB')
            array = np.array(pil_image)
            
            # Cache and return
            self._cache[path] = array
            return array
            
        except Exception as e:
            raise Exception(f"Failed to load image {path}: {e}")
    
    def clear_cache(self):
        """Clear the image cache to free memory."""
        self._cache.clear()
