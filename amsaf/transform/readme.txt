Author: Chris Mitchell
Last updated: 12/29/18

This is the readme for the SITK-based affine Transform package.

Dependencies: SITK, numpy, xlrd, and any version of Python should work

Overview:

Affine transforms are any tranforms that can be written in the following format:

x' = Ax' + t

with A being a 3x3 matrix and t being a 3x1 translation vector. In SITK, this is modified to the following:

x' = A(x'-c) + t + c

Notice that this indeed is still a transform, just with a new t' = t + c - Ac. 
This also means that the rotation and stretching of the image will be the same regardless of c.
 "c" here functions as the center of rotation by translating both the initial point and 
 the final point by the same amount.

How to run transforms:
	There are two options to running transforms:
		Edit the main function with the necessary variables. Run through CLI with no arguments.
			This only runs for a single image at a time.
		Copy and fill in the transform_formatting.xlsx spreadsheet.
			Run through CLI with a single filename argument.
			This allows for numerous files to be ran at once

Parameters:

Ultrasound:
	Boolean. If True, a necessary float casting will take place when any images are read in.

Verbose:
	Boolean. For verbose outputs

RAS:
	Boolean. SITK uses LPS coordinates. However, some programs, to include Slicer, use RAS.
	If True, converts the transformation matrix into LPS coordinates

FileIn:
	Img file to be read in

FileOut:
	Img file to be read out

A11 to A33:
	For the A matrix, A = [[A11, A12, A13],
							[A21, A22, A23],
							[A31, A32, A33]]
Tx, Ty, Tz:
	The translational vector t = [Tx, Ty, Tz]^T

Cx, Cy, Cz;
	The center of rotation vector c = [Cx, Cy, Cz]^T
	If Cx == "origin", the origin is used. the origin is used
	If Cx == "none" or is blank, the center of the image is used
	Note that origin is not default (0, 0, 0)

Ox, Oy, Oz:
	The origin of the image
	This parameter is only needed if the origin was shifted at all when finding the transform,
		eg. if the "Center Volume" function was used in Slicer
	If Ox == "none" or is blank, the default origin (which is Slicer's default origin) is used
	Note that origin is not default (0, 0, 0)

Using Slicer to align images:
