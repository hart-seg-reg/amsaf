import os
import SimpleITK as sitk
import amsaf

# Paths. Change these as needed for different subjects, parameter maps, and segmentations.
BASE_DIR = os.path.join(os.sep, 'srv', 'ultrasound_data')
SEG_PATH = os.path.join(BASE_DIR, '30deg', 'trial8_30_fs_seg_ak5_lh4_TRANS.nii')
SEG_IMG_PATH = os.path.join(BASE_DIR, '30deg', 'trial8_30_fs_volume_TRANS.nii')
SUBJECT_DIR = os.path.join(BASE_DIR, 'sub1', 'slices')
PARAMETER_MAP_DIR = os.path.join(os.sep, 'home', 'ian', 'amsaf_results', 'result-0')
OUTPUT_DIR = os.path.join(SUBJECT_DIR, 'seg')


def get_parameter_maps(pmap_dir):
    parameter_maps = []
    for filename in os.listdir(pmap_dir):
        if filename.startswith('parameter') and filename.endswith('.txt'):
            filepath = os.path.join(pmap_dir, filename)
            parameter_map = sitk.ReadParameterFile(filepath)
            parameter_maps.append(parameter_map)

    return parameter_maps


def main():
    parameter_maps = get_parameter_maps(PARAMETER_MAP_DIR)
    seg = amsaf.read_image(SEG_PATH, ultrasound_slice=True)
    seg_image = amsaf.read_image(SEG_IMG_PATH, ultrasound_slice=True)

    for filename in os.listdir(SUBJECT_DIR):
        if filename.endswith('.nii'):
            filepath = os.path.join(SUBJECT_DIR, filename)
            image_slice = amsaf.read_image(filepath, ultrasound_slice=True)
            mapped_seg = amsaf.segment(image_slice, seg_image, seg, parameter_maps=parameter_maps, verbose=True)
            amsaf.write_image(mapped_seg, os.path.join(OUTPUT_DIR, filename))


if __name__ == '__main__':
    main()
