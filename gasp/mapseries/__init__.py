"""
Mass production of Cartographic layouts
"""

def change_color_on_map(inFile, inRGB, outRGB, outFile):
    """
    Replace a certain color in one image for another color and write
    a new file
    
    inRGB  = (255, 255, 255)
    outRGB = (0, 0, 0)
    """
    
    import numpy
    from PIL import image
    
    img = Image.open(imagePath)
    
    imgArray = numpy.array(img)
    
    r1, g1, b1 = inRGB
    
    red, green, blue = imgArray[:, :, 0], imgArray[:, :, 1], imgArray[:, :, 2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    
    imgArray[:, :, :3][mask] = list(outRGB)
    
    outImg = Image.fromarray(imgArray)
    
    outImg.save(outFile)
    
    return outFile

