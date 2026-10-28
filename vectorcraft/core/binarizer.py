import numpy as np
from PIL import Image, ImageFilter


def binarize_image(image_input, threshold=None, invert=False, denoise=True):
    """
    Convert an image (path or PIL.Image) to a binary boolean numpy array (foreground = True).
    If threshold is None, applies Otsu's optimal thresholding algorithm.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, np.ndarray):
        img = Image.fromarray(image_input)
    else:
        raise TypeError(f"Unsupported image input type: {type(image_input)}")

    # Convert to Grayscale
    img = img.convert("L")

    # Optional slight Gaussian blur to suppress fine raster noise
    if denoise:
        img = img.filter(ImageFilter.GaussianBlur(radius=0.7))

    arr = np.array(img, dtype=np.uint8)

    # Compute threshold via Otsu if not provided
    if threshold is None:
        threshold = compute_otsu_threshold(arr)

    # In typical logo artwork on white background, foreground is darker than background
    # We want foreground (ink/lines) to be True (1)
    border_pixels = np.concatenate([arr[0, :], arr[-1, :], arr[:, 0], arr[:, -1]])
    mean_border = np.mean(border_pixels)
    if mean_border > 128:
        # White/bright background -> foreground is darker
        binary = arr < threshold
    else:
        # Dark background -> foreground is brighter
        binary = arr >= threshold

    if invert:
        binary = ~binary

    return binary


def compute_otsu_threshold(grayscale_arr):
    """Calculates Otsu's threshold for bimodal image histograms in pure NumPy."""
    hist, _ = np.histogram(grayscale_arr.ravel(), bins=256, range=(0, 256))
    total_pixels = grayscale_arr.size
    
    sum_total = np.dot(np.arange(256), hist)
    weight_background = 0
    sum_background = 0.0
    
    variances = np.zeros(256, dtype=np.float64)
    
    for t in range(256):
        weight_background += hist[t]
        if weight_background == 0:
            continue
        weight_foreground = total_pixels - weight_background
        if weight_foreground == 0:
            break
            
        sum_background += t * hist[t]
        mean_background = sum_background / weight_background
        mean_foreground = (sum_total - sum_background) / weight_foreground
        
        # Inter-class variance
        var_between = weight_background * weight_foreground * ((mean_background - mean_foreground) ** 2)
        variances[t] = var_between
        
    max_val = np.max(variances)
    if max_val == 0:
        return 128
        
    plateau = np.where(variances == max_val)[0]
    return int(plateau[len(plateau) // 2])
