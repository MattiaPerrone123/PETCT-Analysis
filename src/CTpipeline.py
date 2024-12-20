import os
import numpy as np
import SimpleITK as sitk
import torch
import nibabel as nib 
from .io_utils import load_dicom_volume, copy_dicom_files, setup_input_ts_folder, check_target_series_in_folder
from .image_processing import reorient_and_rotate_images
from .totalsegmentator_integration import run_totalsegmentator

class CTProcessingPipeline:
    def __init__(self, source_path, target_study, target_number, new_spacing=[1,1,1], temp_file="temp_dict.pkl"):
        """Handles loading, segmentation, and reorientation of CT volumes"""
        self.source_path=source_path
        self.target_study=target_study
        self.target_number=target_number
        self.new_spacing=new_spacing
        self.temp_file=temp_file
        self.device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def load_and_resample_volume(self):
        """Loads and converts a DICOM volume to a NumPy array"""
        volume=load_dicom_volume(self.source_path,self.target_study,self.target_number)
        np_volume=sitk.GetArrayFromImage(volume)
        return np_volume

    def prepare_and_segment(self):
        """Prepares input folders, copies DICOM files, and runs totalsegmentator"""
        input_ts_path=setup_input_ts_folder()
        destination_path=os.path.join(os.getcwd(),'input_ts')
        copy_dicom_files(self.source_path,destination_path,self.target_study,self.target_number)
        
        if not os.listdir(destination_path):
            self.target_number="5"
            copy_dicom_files(self.source_path,destination_path,self.target_study,self.target_number)

        if check_target_series_in_folder(self.source_path,"iMAR"):
            input_ts_path=setup_input_ts_folder()
            self.target_number="4"
            copy_dicom_files(self.source_path,destination_path,self.target_study,self.target_number)

        run_totalsegmentator(input_ts_path,"segmentations_totalsegmentator_")

    def combine_and_reorient_segmentations(self):
        """Combines vertebrae segmentations into a single mask and reorients the images"""
        vertebrae_lumbar=["T12","L1","L2","L3","L4","L5","S1"]
        combined_mask=None

        for idx,vert in enumerate(vertebrae_lumbar,start=1):
            path_image=os.path.join(os.getcwd(),f'segmentations_totalsegmentator_/vertebrae_{vert}.nii.gz')
            nifti_img=nib.load(path_image)
            mask_data=nifti_img.get_fdata()
            if combined_mask is None:
                combined_mask=np.zeros_like(mask_data)
            combined_mask[mask_data>0]=idx

        loaded_volume=self.load_and_resample_volume()
        rotated_array,rotated_mask=reorient_and_rotate_images(loaded_volume,combined_mask)
        return rotated_array,rotated_mask

    def process(self):
        """Runs segmentation and reorientation pipeline"""
        self.prepare_and_segment()
        rotated_array,rotated_mask=self.combine_and_reorient_segmentations()
        return rotated_array,rotated_mask
