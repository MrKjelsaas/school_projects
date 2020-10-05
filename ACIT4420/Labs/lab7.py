import numpy as np


# Read the header of the file and print the size of the picture (height, width)
file = open("oslomet.bmp", "rb")
imageSize = np.fromfile(file, dtype = np.uint32, offset = 18, count = 2)
imageHeight = imageSize[1]
imageWidth = imageSize[0]
print("Image width:", imageWidth, "\nImage height:", imageHeight)


# Read the pixels of the bitmap into a numpy 3D array containing the 3 color components (red, green, blue). First index: row, second index: column, third index: component
file = open("oslomet.bmp", "rb")
image = np.fromfile(file, dtype = np.uint8, offset = 54)
image = np.reshape(image, [imageHeight, imageWidth, 3])
image = image[::-1,:,::-1]


# Copy the 3D array and manipulate the pixels in a way that every pixel with higher byte value than 150 for each component should be total white. Save a new image with the name “oslomet_snow.bmp”
new_image = image.copy()

for i in range(imageHeight):
    for j in range(imageWidth):
        for k in range(3):
            if image[i, j, k] > 150:
                new_image[i, j, k] = 255

new_image = new_image[::-1,:,::-1]

file = open("oslomet.bmp", "rb")
header = np.fromfile(file, dtype = np.uint8, count = 54)
oslomet_snow = np.append(header, np.ndarray.flatten(new_image))
file2 = open("oslomet_snow.bmp", "wb")
oslomet_snow.astype("int8").tofile("oslomet_snow.bmp")


"""
Copy the 3D array and manipulate the pixels in a way that every pixel where both the red and the green component byte values are higher than 130 and the blue component byte value is less than 110 has to be modified:
The red and the green values has to be exchanged, the green value has to be increased with 50 (if possible) and the red values has to be decreased by 50 (if possible).
Save a new image with the name “oslomet_yellow.bmp”
"""
new_image = image.copy()

for i in range(imageHeight):
    for j in range(imageWidth):
        for k in range(3):
            if image[i, j, 0] > 130:
                if image[i, j, 1] > 130:
                    if image[i, j, 2] < 110:
                        new_image[i, j, 0] = image[i, j, 1]
                        new_image[i, j, 1] = image[i, j, 0]
                        new_image[i, j, 1] = min(new_image[i, j, 1]+50, 255)
                        new_image[i, j, 0] = max(new_image[i, j, 0]-50, 255)

new_image = new_image[::-1,:,::-1]

file = open("oslomet.bmp", "rb")
header = np.fromfile(file, dtype = np.uint8, count = 54)
oslomet_yellow = np.append(header, np.ndarray.flatten(new_image))
oslomet_yellow.astype("int8").tofile("oslomet_yellow.bmp")


# Cut the upper 200 pixels and 200 pixels from both edges. Modify the header accordingly. Save the new bitmap with the name “oslomet_small.bmp”
new_image = image[200:, 200:-200, :]
new_image = new_image[::-1,:,::-1]

file = open("oslomet.bmp", "rb")
startOfHeader = np.fromfile(file, dtype = np.uint8, count = 18)
header = np.append(startOfHeader, [32, 3, 0, 0, 174, 1, 0, 0])

file = open("oslomet.bmp", "rb")
endOfHeader = np.fromfile(file, dtype = np.uint8, offset = 26, count = 28)
header = np.append(header, endOfHeader)

oslomet_small = np.append(header, np.ndarray.flatten(new_image))
oslomet_small.astype("int8").tofile("oslomet_small.bmp")
