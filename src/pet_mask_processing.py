import numpy as np

def custom_transform(volume):
    "Applies a custom transformation to the given volume"
    transformed_volume=np.flip(np.transpose(volume,(1,2,0)),axis=2)[::-1]
    return transformed_volume

def transform_data_dict(data_dict,ct_masks_flipped=None):
    "Transforms a data dictionary with an optional mask flip"
    
    transformed_dict={}
    for key,value in data_dict.items():
        transformed_first=custom_transform(value[0])
        transformed_second=custom_transform(value[1])
        if ct_masks_flipped:
            transformed_first=transformed_first[::-1]
        transformed_dict[key]=[transformed_first,transformed_second]
    return transformed_dict

def get_masks_and_pet_dict(dict1,dict2):
    "Generates a dictionary mapping common keys to masks and PET data"
    
    common_keys=set(dict1.keys())&set(dict2.keys())
    result_dict={}
    for key in common_keys:
        second_element_dict1=dict1[key][1]
        second_element_dict2=dict2[key][1]
        result_dict[key]=[second_element_dict1,second_element_dict2]
    return result_dict

def crop_single_image_and_mask(mask,image,padding=20):
    "Crops a single image and mask based on non-zero mask regions with padding"
    
    indices=np.argwhere(mask>1)
    if indices.size==0:
        return image,mask
    min_indices=indices.min(axis=0)
    max_indices=indices.max(axis=0)+1
    min_indices=np.maximum(min_indices-padding,0)
    max_indices=np.minimum(max_indices+padding,mask.shape)
    slices=tuple(slice(start,end)for start,end in zip(min_indices,max_indices))
    cropped_image=image[slices]
    cropped_mask=mask[slices]
    return cropped_mask,cropped_image

def normalize_mask(mask,normalize_multilabels=False):
    "Converts multi-label masks to binary masks if normalize_multilabels=True"
    if normalize_multilabels:
        mask=np.where(mask>1,1,mask)
    return mask

def crop_all_images_and_masks(masks_and_pet_dict,padding=20):
    "Crops all images and masks in the dictionary with padding"
    cropped_dict={}
    
    for key,(mask,image)in masks_and_pet_dict.items():
        cropped_image,cropped_mask=crop_single_image_and_mask(mask,image,padding=padding)
        cropped_dict[key]=(cropped_mask,cropped_image)
    return cropped_dict

def multiply_pet_data_and_masks(cropped_dict):
    "Multiplies PET images with their corresponding normalized masks"
    
    masked_pet_images_dict={}
    masked_images_dict={}
    
    for key,(cropped_image,cropped_mask)in cropped_dict.items():
        normalized_mask_0_1=normalize_mask(cropped_mask,normalize_multilabels=True)
        normalized_mask_multi=normalize_mask(cropped_mask,normalize_multilabels=False)
        multiplied_image=cropped_image*normalized_mask_0_1
        masked_pet_images_dict[key]=multiplied_image
        masked_images_dict[key]=normalized_mask_multi
    
    return masked_pet_images_dict,masked_images_dict
