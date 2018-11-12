#! /usr/bin/env python3

"""This program will read the butterfly png and generate a list of triangles."""

import os
import json
import pickle
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay
from sklearn.cluster import KMeans
from PIL import Image

def filtered(simplices, points, bitmask):
	retval = []
	for idx1, idx2, idx3 in simplices:
		point1 = points[idx1]
		point2 = points[idx2]
		point3 = points[idx3]
		y, x = ((point1 + point2 + point3) / 3.0).astype(np.int32)
		if bitmask[y, x] != 2:
			retval.append([idx1, idx2, idx3])

	return np.array(retval)

def dump_colors(fname, simplices, colors, points, scaled):
	retval = []
	# Rotate the points 180 degrees.
	rot180 = np.array([
		[-1, 0],
		[0, -1]
	])
	scaled = np.matmul(scaled, rot180)
	
	for idx1, idx2, idx3 in simplices:
		point1 = points[idx1]
		point2 = points[idx2]
		point3 = points[idx3]
		y, x = ((point1 + point2 + point3) / 3.0).astype(np.int32)
		red, green, blue, alpha = colors[y, x]
		retval.append((
			[float(scaled[idx1, 0]), float(scaled[idx1, 1])],
			[float(scaled[idx2, 0]), float(scaled[idx2, 1])],
			[float(scaled[idx3, 0]), float(scaled[idx3, 1])],
			[int(red), int(green), int(blue), 128]
		))

	with open(fname, "wt") as jsfp:
		json.dump(retval, jsfp, indent=4, sort_keys=True)

def main():
	img = Image.open("butterfly-template.png")
	npimg = np.array(img)
	img.close()

	rawcolors = Image.open("butterfly-colored.png")
	colors = np.array(rawcolors)
	rawcolors.close()

	black = np.array([[[0,0,0]]])
	green = np.array([[[0,255,0]]])
	white = np.array([[[255,255,255]]])
	blackdist = np.exp(-np.linalg.norm(npimg - black, axis=2, keepdims=True)*1024)
	greendist = np.exp(-np.linalg.norm(npimg - green, axis=2, keepdims=True)*1024)
	whitedist = np.exp(-np.linalg.norm(npimg - white, axis=2, keepdims=True)*1024)
	combined = np.concatenate([blackdist, greendist, whitedist], axis=2)
	combined = combined / combined.sum(axis=2, keepdims=True)
	bitmask = (combined[:, :, 0] > 0.5) * 4 + (combined[:, :, 1] > 0.5) * 2 + (combined[:, :, 2] > 0.5) * 1
	points = np.vstack((bitmask == 4).nonzero()).transpose()
	ksz = 4096
	kfn = "butterfly-template-%d.pickle" % (ksz)
	if os.path.exists(kfn):
		with open(kfn, "rb") as pfp:
			kmeans = pickle.load(pfp)
	else:
		kmeans = KMeans(ksz, n_jobs=-1, verbose=True)
		kmeans.fit(points)
		with open(kfn, "wb") as pfp:
			pickle.dump(kmeans, pfp)
	points = kmeans.cluster_centers_
	triangles = Delaunay(points)
	simplices = filtered(triangles.simplices, points, bitmask) 
	plt.triplot(points[:, 1], points[:, 0], simplices)
	# plt.plot(points[:,1], points[:,0], 'o')
	plt.show()
	scaled = points[:]
	minx = points[:, 0].min()
	maxx = points[:, 0].max()
	miny = points[:, 1].min()
	maxy = points[:, 1].max()

	width = maxx - minx
	height = maxy - miny
	size = max(width, height)

	centerx = (minx + maxx) / 2.0
	centery = (miny + maxy) / 2.0

	scaled = (scaled - np.array([[centerx, centery]])) / size
	dump_colors("butterfly-%d.json" % (ksz), simplices, colors, points, scaled)

# For this to be used in processing, we need to make 
# a set of triangles and colors.

if __name__ == "__main__":
	main()
