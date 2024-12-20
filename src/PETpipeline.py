import os
import numpy as np
import SimpleITK as sitk
from .io_utils import check_target_series_in_folder, filter_dicom_pet, filter_dicom_ct, load_dicom_series_from_pydicom, save_dictionary_to_file, load_dictionary_from_file
from .image_processing import resample_image, crop_and_resize_pet
from .utils import dicom_to_numpy, find_first_nonzero_slice


class PetProcessor:
    def __init__(self,base_path,dataset_folder,target_description_pet,target_description_number_ct,target_study):
        "Initializes the PET processor with target descriptions and paths"
        self.base_path=base_path
        self.dataset_folder=dataset_folder
        self.target_description_pet=target_description_pet
        self.target_description_number_ct=target_description_number_ct
        self.target_study=target_study

    def load_images(self,directory_index=None,specific_directory=None):
        "Loads PET and CT images based on directory index or specific directory"
        
        if specific_directory:
            path_sample_patient=os.path.join(self.base_path,self.dataset_folder,specific_directory)
        else:
            all_directories=os.listdir(os.path.join(self.base_path,self.dataset_folder))
            directory=all_directories[directory_index]if directory_index is not None else all_directories[0]
            path_sample_patient=os.path.join(self.base_path,self.dataset_folder,directory)
        
        if check_target_series_in_folder(path_sample_patient,"E2T"):
            self.target_description_pet="PET AC Sag"
        
        self.pet_image_dicom=filter_dicom_pet(path_sample_patient,self.target_description_pet)
        self.ct_image_dicom=filter_dicom_ct(path_sample_patient,self.target_description_number_ct)
        self.pet_image=load_dicom_series_from_pydicom(self.pet_image_dicom)
        self.ct_image=load_dicom_series_from_pydicom(self.ct_image_dicom)

    def resample_and_process(self):
        "Resamples and processes PET and CT images"
        
        self.resampled_pet=resample_image(self.pet_image,self.ct_image)
        resampled_pet_np=sitk.GetArrayFromImage(self.resampled_pet)
        resampled_pet_np=resampled_pet_np[::-1]
        threshold=find_first_nonzero_slice(resampled_pet_np)
        self.pet_image_np_final=crop_and_resize_pet(resampled_pet_np,threshold)
        self.ct_image_np=dicom_to_numpy(self.ct_image_dicom)
        
        return self.ct_image_np,self.pet_image_np_final

    def process_all(self,directory_index=None,specific_directory=None,save_dict=False,load_dict=False,dict_file="data_dict.pkl"):
        "Processes all PET data and optionally saves or loads the result"
        
        if load_dict and os.path.exists(dict_file):
            return load_dictionary_from_file(dict_file)
        
        data_dict={}
        self.load_images(directory_index=directory_index,specific_directory=specific_directory)
        ct_np,pet_np_final=self.resample_and_process()
        patient_index=specific_directory if specific_directory else directory_index
        data_dict[patient_index]=[ct_np,pet_np_final]
        
        if save_dict:
            save_dictionary_to_file(data_dict,dict_file)
        
        return data_dict
