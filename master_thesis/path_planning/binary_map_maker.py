import cv2
import numpy as np

# Import image
im = cv2.imread("openseamap_oslofjord.png")
print("Original image shape:", im.shape)

# Coordinates at SW and NE of map
#SW: 5954.000, 1041.000
SW_lat = 5954.000
SW_lon = 1041.000
#NE: 5955.000, 1044.500
NE_lat = 5955.000
NE_lon = 1044.500
map_resolution = 0.01

# Make binary map
im = cv2.resize(im, ( int((NE_lon-SW_lon) / map_resolution), int((NE_lat-SW_lat) / map_resolution )) )

oslofjord_binary_map = np.ones([im.shape[0], im.shape[1]])
print("Binary map shape:", oslofjord_binary_map.shape)

# Fill binary map with ones where there is ocean
for i in range(im.shape[0]):
    for j in range(im.shape[1]):
        if im[i, j][0] == 223:
            if im[i, j][1] == 211:
                if im[i, j][2] == 170:
                    oslofjord_binary_map[i, j] = 0

#print(oslofjord_binary_map)

np.savetxt("oslofjord_binary_map.csv", oslofjord_binary_map)

temp = cv2.resize(oslofjord_binary_map, (350*2, 100*2))

cv2.imshow('Binary ocean map of the Oslo fjord', temp)
cv2.waitKey(0)
cv2.destroyAllWindows()
