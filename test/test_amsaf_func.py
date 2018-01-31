import SimpleITK as sitk

import pytest
from amsaf import amsaf_func as af

fixed_image = sitk.ReadImage("/srv/hart_mri/mri_data/SUBJECT_3/2-forearm/crops/sub3_forearm_cropped_for_ITK-SNAP_biascorr.nii")
moving_image = sitk.ReadImage("/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_for_ITK-SNAP_biascorr.nii")
PQ_forearm_combined = sitk.ReadImage("/srv/hart_mri/mri_data/PQ_Full/crops/forearm/PQ_forearm_cropped_combined.nii")

def test_score_maps():
    pass

def test_segment():
    pass

def test_register():
    pmaps = [sitk.GetDefaultParameterMap(t) for t in ['translation', 'affine', 'bspline']]
    _, parameter_maps = af.register(fixed_image, moving_image, parameter_maps=pmaps, verbose=True)
    for i, pm in enumerate(parameter_maps):
        sitk.WriteParameterFile(pm, "./test_transform_%s" % i)

def test_transform():
    def get_transform_pmaps():
        result = []
        for i in range(3):
            result.append(sitk.ReadParameterFile('./test_data/TransformParameters.%s.txt' % i))
        return result

    af.transform(PQ_forearm_combined, get_transform_pmaps())

if __name__ == '__main__':
    pytest.main()
