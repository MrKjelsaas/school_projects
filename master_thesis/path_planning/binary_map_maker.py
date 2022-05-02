import cv2
import numpy as np
import pymap3d as pm

# Import image
im = cv2.imread("openseamap_oslofjord.png")
print("Original image shape:", im.shape)

# Coordinates at SW and NE corners of map
#SW: 5954.000, 1041.000
SW_lat = 59 + (54/60)
SW_lon = 10 + (41/60)
#NE: 5955.000, 1044.500
NE_lat = 59 + (55/60)
NE_lon = 10 + (44.5/60)
e, n, u = pm.geodetic2enu(NE_lat, NE_lon, 0, SW_lat, SW_lon, 0)

# Make binary map
#im = cv2.resize(im, ( int((NE_lon-SW_lon) / map_resolution), int((NE_lat-SW_lat) / map_resolution )) )
im = cv2.resize(im, (int(e), int(n) ))

oslofjord_binary_map = np.ones([im.shape[1], im.shape[0]])
print("Binary map shape:", oslofjord_binary_map.shape)

# Fill binary map with zeros where there is ocean
for i in range(im.shape[0]):
    for j in range(im.shape[1]):
        if im[i, j][0] == 223:
            if im[i, j][1] == 211:
                if im[i, j][2] == 170:
                    oslofjord_binary_map[j, -i] = 0

#print(oslofjord_binary_map)

np.savetxt("oslofjord_binary_map.csv", oslofjord_binary_map)

temp = cv2.resize(oslofjord_binary_map, None, fx=0.4, fy=0.4)
cv2.imshow('Binary ocean map of the Oslo fjord', temp)
cv2.waitKey(0)
cv2.destroyAllWindows()
