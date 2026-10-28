import numpy as np
from PIL import Image
from vectorcraft.core.binarizer import binarize_image, compute_otsu_threshold


def test_compute_otsu_threshold():
    # Create bimodal distribution: dark foreground (values ~30), bright background (values ~220)
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[:50, :] = 30
    arr[50:, :] = 220
    
    thresh = compute_otsu_threshold(arr)
    # Threshold should separate 30 and 220, typically around 125
    assert 50 <= thresh <= 200


def test_binarize_rectangular_image():
    # Test non-square image to ensure border pixel concatenation handles differing dimensions
    arr = np.full((120, 240), 255, dtype=np.uint8)
    arr[30:90, 60:180] = 20
    binary = binarize_image(arr)
    assert binary.shape == (120, 240)
    assert binary[60, 120] == True
    assert binary[5, 5] == False
    img = Image.new("L", (80, 80), color=255) # white bg
    # Draw dark square in center
    arr = np.array(img)
    arr[20:60, 20:60] = 10
    img = Image.fromarray(arr)

    binary = binarize_image(img)
    assert isinstance(binary, np.ndarray)
    assert binary.dtype == bool
    # Center should be foreground (True)
    assert binary[40, 40] == True
    # Corner should be background (False)
    assert binary[5, 5] == False
