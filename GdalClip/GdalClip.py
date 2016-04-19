import os, shutil

def imageToArray(i):
    a = gdalnumeric.fromstring(i.tobytes(),'b')
    a.shape=i.im.size[1], i.im.size[0]
    return a

def arrayToImage(a):
    i=Image.frombytes('L',(a.shape[1],a.shape[0]),(a.astype('b')).tostring())
    return i

def world2Pixel(geoMatrix,x,y):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel,line)

def OpenArray(array, prototype_ds = None, xoff = 0, yoff = 0):
    ds  = gdal.Open(gdalnumeric.GetArrayFilename(array))
    
    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdal.Open(prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo(prototype_ds,ds,xoff=xoff,yoff=yoff)
    return ds


def main( shapefile_path, raster_path,output_path ):
    # Load the source data as a gdalnumeric array
    srcArray = gdalnumeric.LoadFile(raster_path)

    # Also load as a gdal image to get geotransform
    # (world file) info
    srcImage = gdal.Open(raster_path)
    geoTrans = srcImage.GetGeoTransform()

    # Create an OGR layer from a boundary shapefile
    shapef = ogr.Open(shapefile_path)
    lyr = shapef.GetLayer()
    poly = lyr.GetNextFeature()

    # Convert the layer extent to image pixel coordinates
    minX, maxX, minY, maxY = lyr.GetExtent()
    ulX, ulY = world2Pixel(geoTrans, minX, maxY)
    lrX, lrY = world2Pixel(geoTrans, maxX, minY)

    # Calculate the pixel size of the new image
    pxWidth = int(lrX - ulX)
    pxHeight = int(lrY - ulY)
    clip = srcArray[ulY:lrY, ulX:lrX]

    #
    # EDIT: create pixel offset to pass to new image Projection info
    #
    xoffset =  ulX
    yoffset =  ulY

    # Create a new geomatrix for the image
    geoTrans = list(geoTrans)
    geoTrans[0] = minX
    geoTrans[3] = maxY

    # Map points to pixels for drawing the
    # boundary on a blank 8-bit,
    # black and white, mask image.
    points = []
    pixels = []
    geom = poly.GetGeometryRef()
    pts = geom.GetGeometryRef(0)
    for p in range(pts.GetPointCount()):
      points.append((pts.GetX(p), pts.GetY(p)))
    for p in points:
      pixels.append(world2Pixel(geoTrans, p[0], p[1]))
    rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
    rasterize = ImageDraw.Draw(rasterPoly)
    rasterize.polygon(pixels, 0)
    mask = imageToArray(rasterPoly)

    # Clip the image using the mask
    clip = gdalnumeric.choose(mask, \
        (clip, 0))
    

    # Save new tiff
    #
    #  EDIT: instead of SaveArray, let's break all the
    #  SaveArray steps out more explicity so
    #  we can overwrite the offset of the destination
    #  raster
    #
    ### the old way using SaveArray
    #
    # gdalnumeric.SaveArray(clip, "OUTPUT.tif", format="GTiff", prototype=raster_path)
    #
    ###
    #
    gtiffDriver = gdal.GetDriverByName( 'GTiff' )
    if gtiffDriver is None:
        raise ValueError("Can't find GeoTiff Driver")
    gtiffDriver.CreateCopy( output_path,
        OpenArray( clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset )
    )

    gdal.ErrorReset()


    
    
