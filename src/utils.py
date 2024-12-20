import numpy as np
import SimpleITK as sitk
from .image_processing import custom_transform

def transform_data_dict(data_dict,ct_masks_flipped):
    "Applies transformations to the data dictionary, flipping certain entries if specified"
    transformed_dict={}
    
    for key,value in data_dict.items():
        transformed_first=custom_transform(value[0])
        transformed_second=custom_transform(value[1])
        
        if key in ct_masks_flipped:
            transformed_first=transformed_first[::-1]
        transformed_dict[key]=[transformed_first,transformed_second]
    return transformed_dict

def collect_arrays_from_dict(transformed_data_dict):
    "Collects CT arrays and segmentation masks into separate lists from a transformed dictionary"
    list_one=[]
    list_two=[]
    
    for value in transformed_data_dict.values():
        list_one.append(value[0])
        list_two.append(value[1])
    
    return list_one,list_two

def create_dictionary(patients_processed_list,ct_array_list,segmentation_mask_list):
    "Creates a dictionary mapping patient IDs to CT arrays and segmentation masks"
    ct_masks_dictionary={
        patient:[ct_array,segmentation_mask]
        for patient,ct_array,segmentation_mask in zip(
            patients_processed_list,ct_array_list,segmentation_mask_list
        )
    }
    
    return ct_masks_dictionary

def transform_and_extract_arrays(ct_masks_dictionary,ct_masks_flipped):
    "Transforms the dictionary and extracts the arrays for CT images and their masks"
    ct_masks_dictionary_oriented=transform_data_dict(ct_masks_dictionary,ct_masks_flipped)
    ct_list_new,masks_multilabel_list=collect_arrays_from_dict(ct_masks_dictionary_oriented)
    
    return ct_list_new,masks_multilabel_list

def extract_pixel_array(dicom_dataset_list):
    "Extracts and applies rescale slope and intercept to pixel arrays"
    pixel_data_list=[]
    
    for ds in dicom_dataset_list:
        pixel_array=ds.pixel_array.astype(np.float32)
        if hasattr(ds,'RescaleSlope') and hasattr(ds,'RescaleIntercept'):
            pixel_array=pixel_array*ds.RescaleSlope+ds.RescaleIntercept
        pixel_data_list.append(pixel_array)
    
    return np.stack(pixel_data_list,axis=0)

def compute_spacing_and_origin(first_dataset):
    "Extracts spacing and origin from the first dataset"
    pixel_spacing=[float(sp) for sp in first_dataset.PixelSpacing]
    slice_thickness=float(first_dataset.SliceThickness)
    origin=[float(coord) for coord in first_dataset.ImagePositionPatient]
    
    return pixel_spacing,slice_thickness,origin

def compute_direction(first_dataset):
    "Calculates the direction matrix from ImageOrientationPatient"
    direction=[float(dir_cos) for dir_cos in first_dataset.ImageOrientationPatient]
    direction_matrix=np.array(direction).reshape(2,3)
    normal=np.cross(direction_matrix[0],direction_matrix[1])  
    full_direction=np.vstack([direction_matrix,normal]).flatten()
    
    return full_direction.tolist()

def dicom_to_numpy(dicom_datasets):
    "Converts DICOM datasets into a NumPy array"
    
    if hasattr(dicom_datasets[0],'InstanceNumber'):
        dicom_datasets.sort(key=lambda x:x.InstanceNumber)
    elif hasattr(dicom_datasets[0],'SliceLocation'):
        dicom_datasets.sort(key=lambda x:x.SliceLocation)
    images=[]
    
    for ds in dicom_datasets:
        img=ds.pixel_array.astype(np.float32)
        images.append(img)
    return np.stack(images)

def find_first_nonzero_slice(volume):
    "Finds the first slice in the volume containing non-zero values"
    mid_z=volume.shape[2]//2
    for x in range(volume.shape[0]):
        if np.any(volume[x,:,mid_z]!=0):
            return x
    return None
