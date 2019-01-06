Author: Chris Mitchell
Last updated: 1/5/19

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
 the final point by the same amount. For simplicity, this code assumes c = 0.

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
	Default is True

Verbose:
	Boolean. For verbose outputs. Default is False

RAS:
	Boolean. SITK uses LPS coordinates. However, some programs, to include Slicer, use RAS.
	If True, converts the transformation matrix into LPS coordinates. Default is False

FileIn:
	Image file to be read in

FileOut:
	Image file to be read out

A11 to A33:
	For the A matrix, A = [[A11, A12, A13],
							[A21, A22, A23],
							[A31, A32, A33]]
Tx, Ty, Tz:
	The translational vector t = [Tx, Ty, Tz]^T

Using Slicer to align images:

First off, DO NOT MODIFY ANY IMAGE PROPERTIES. This code makes assumptions on origin position, 
	directions, and spacing in order to simplify computation. This also means you shouldn't use
	the "Center Volume" button.

Load two images (or the entire folder if you want) into Slicer by clicking the "Data" folder
button on the top left and following the prompts. Next to the red header of the "right" image,
click the button that looks like a pin, and then click the down arrow to cause the menu to drop down.
Click the button which looks like two interlocked circles (so this way what you do applys to all views).
Then use the drop down menus to select which images you want to use, and either the slider or the 
box to the left of the image to control transparency.

From here, go to the transforms menu. Under "Active Transform," click "Create new LinearTransform." 
I'd recommend renaming the transform by clicking "Rename Current Node" in the same drop-down 
menu while having the desired transform selected.

Under this same "Transforms" menu, under "Apply Transforms," select which image(s) you wish to apply
a transform to (AKA the moving image) and click the right pointing arrow. Use the sliders above under
"Edit Transform" to translate and rotate images until they are aligned.