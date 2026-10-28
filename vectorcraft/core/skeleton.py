import numpy as np


def zhang_suen_thinning(binary_mask):
    """
    Applies the Zhang-Suen morphological thinning algorithm to a 2D boolean array.
    Reduces connected shapes down to 1-pixel wide skeleton centerlines.
    
    Args:
        binary_mask: 2D numpy boolean array (True for foreground).
        
    Returns:
        2D numpy boolean array containing the medial axis skeleton.
    """
    # Pad image by 1 pixel of background to avoid boundary index errors
    image = np.pad(binary_mask.astype(np.uint8), 1, mode='constant', constant_values=0)
    
    changed = True
    while changed:
        changed = False
        
        # Sub-iteration 1
        to_delete = _thinning_iteration(image, step=1)
        if len(to_delete[0]) > 0:
            image[to_delete] = 0
            changed = True
            
        # Sub-iteration 2
        to_delete = _thinning_iteration(image, step=2)
        if len(to_delete[0]) > 0:
            image[to_delete] = 0
            changed = True

    # Remove padding and return boolean mask
    return image[1:-1, 1:-1].astype(bool)


def _thinning_iteration(im, step=1):
    """Helper vectorized kernel check for Zhang-Suen conditions."""
    # Neighbors:
    # P9 P2 P3
    # P8 P1 P4
    # P7 P6 P5
    p2 = im[:-2, 1:-1]
    p3 = im[:-2, 2:]
    p4 = im[1:-1, 2:]
    p5 = im[2:, 2:]
    p6 = im[2:, 1:-1]
    p7 = im[2:, :-2]
    p8 = im[1:-1, :-2]
    p9 = im[:-2, :-2]
    p1 = im[1:-1, 1:-1]
    
    # Condition 1: Pixel must be foreground (1)
    c1 = (p1 == 1)
    
    # Condition 2: 2 <= B(P1) <= 6 (Number of non-zero neighbors)
    b = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
    c2 = (b >= 2) & (b <= 6)
    
    # Condition 3: A(P1) == 1 (Number of 0->1 transitions in clockwise order: P2, P3, P4, P5, P6, P7, P8, P9, P2)
    a = ((p2 == 0) & (p3 == 1)).astype(np.uint8) + \
        ((p3 == 0) & (p4 == 1)).astype(np.uint8) + \
        ((p4 == 0) & (p5 == 1)).astype(np.uint8) + \
        ((p5 == 0) & (p6 == 1)).astype(np.uint8) + \
        ((p6 == 0) & (p7 == 1)).astype(np.uint8) + \
        ((p7 == 0) & (p8 == 1)).astype(np.uint8) + \
        ((p8 == 0) & (p9 == 1)).astype(np.uint8) + \
        ((p9 == 0) & (p2 == 1)).astype(np.uint8)
    c3 = (a == 1)
    
    if step == 1:
        # Condition 4: P2 * P4 * P6 == 0
        c4 = (p2 * p4 * p6 == 0)
        # Condition 5: P4 * P6 * P8 == 0
        c5 = (p4 * p6 * p8 == 0)
    else:
        # Condition 4: P2 * P4 * P8 == 0
        c4 = (p2 * p4 * p8 == 0)
        # Condition 5: P2 * P6 * P8 == 0
        c5 = (p2 * p6 * p8 == 0)
        
    mask = c1 & c2 & c3 & c4 & c5
    indices = np.where(mask)
    # Offset by 1 because im is padded
    return (indices[0] + 1, indices[1] + 1)
