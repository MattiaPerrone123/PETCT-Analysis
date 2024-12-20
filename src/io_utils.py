import os
import shutil
import pydicom
import numpy as np
import SimpleITK as sitk
import pickle
from .utils import extract_pixel_array, compute_spacing_and_origin, compute_direction

def setup_input_ts_folder(base_path='.', folder_name='input_ts'):
    """Sets up and clears the input folder for totalsegmentator"""
    input_ts_path=os.path.join(base_path,folder_name)
    if os.path.exists(input_ts_path):
        for filename in os.listdir(input_ts_path):
            file_path=os.path.join(input_ts_path,filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(input_ts_path)
    return input_ts_path

def copy_dicom_files(source_path, destination_path, study_description, series_number):
    """Copies DICOM files matching a given study and series number to the destination folder"""
    copied_count=0
    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    for curr_img in os.listdir(source_path):
        path_fin=os.path.join(source_path,curr_img)
        try:
            dicom_file=pydicom.dcmread(path_fin)
            if dicom_file.SeriesNumber==series_number and study_description in dicom_file.StudyDescription:
                shutil.copy2(path_fin,os.path.join(destination_path,curr_img))
                copied_count+=1
        except Exception as e:
            pass
    return copied_count

def check_target_series_in_folder(patient_folder_path, target_series):
    """Checks if the target series is present in the given folder"""
    for dicom_file in os.listdir(patient_folder_path):
        dicom_path=os.path.join(patient_folder_path,dicom_file)
        dicom_read=pydicom.dcmread(dicom_path)
        if target_series in dicom_read.SeriesDescription:
            return True
    return False

def load_dicom_volume(folder_path, target_study, target_number):
    """Loads DICOM volume as a SimpleITK image for the specified study and series number"""
    files=[]
    for f_name in os.listdir(folder_path):
        if f_name.endswith('.dcm'):
            dcm_file=pydicom.dcmread(os.path.join(folder_path,f_name))
            if target_study in dcm_file.StudyDescription and str(dcm_file.SeriesNumber)==str(target_number):
                files.append(dcm_file)

    if not files:
        raise FileNotFoundError("No DICOM files found for the specified study/series")

    image_array=np.stack([f.pixel_array for f in files])
    image_sitk=sitk.GetImageFromArray(image_array.astype(np.float32))
    image_sitk.SetSpacing((float(files[0].PixelSpacing[0]),float(files[0].PixelSpacing[1]),float(files[0].SliceThickness)))
    return image_sitk


def save_dictionary_to_file(dictionary, filename):
    """Saves the given dictionary to a pickle file"""
    with open(filename, 'wb') as file:
        pickle.dump(dictionary, file)

def load_dictionary_from_file(filename):
    """Loads a dictionary from a pickle file"""
    with open(filename, 'rb') as file:
        return pickle.load(file)

def filter_dicom_pet(directory,target_description):
    """Filters DICOM PET files matching the target description"""
    pet_scans=[]
    for filename in os.listdir(directory):
        if filename.lower().endswith(".dcm"): 
            filepath=os.path.join(directory,filename)
            try:
                dicom_data=pydicom.dcmread(filepath,force=True)
                if hasattr(dicom_data,'PixelData'):
                    if ('SeriesDescription' in dicom_data and 
                        target_description in dicom_data.SeriesDescription and
                        'ImagePositionPatient' in dicom_data):
                        pet_scans.append(dicom_data)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
    return pet_scans

def filter_dicom_ct(directory,target_description_number):
    """Filters DICOM CT files matching the target series number"""
    ct_scans=[]
    for filename in os.listdir(directory):
        if filename.lower().endswith(".dcm"): 
            filepath=os.path.join(directory,filename)
            try:
                dicom_data=pydicom.dcmread(filepath,force=True)
                if dicom_data.SeriesNumber==target_description_number:
                    ct_scans.append(dicom_data)
            except Exception as e:
                print(f"Failed to read {filename}: {e}")
    return ct_scans

def load_dicom_series_from_pydicom(dicom_dataset_list):
    """Loads and converts a DICOM series into a SimpleITK image"""
    dicom_dataset_list.sort(key=lambda ds: ds.ImagePositionPatient[2])
    pixel_data=extract_pixel_array(dicom_dataset_list)
    first_dataset=dicom_dataset_list[0]
    pixel_spacing,slice_thickness,origin=compute_spacing_and_origin(first_dataset)
    direction=compute_direction(first_dataset)
    image=sitk.GetImageFromArray(pixel_data)
    image.SetSpacing([pixel_spacing[0],pixel_spacing[1],slice_thickness])
    image.SetOrigin(origin)
    image.SetDirection(direction)
    return image




