import numpy as np
import SimpleITK as sitk
import cv2

def reorient_and_rotate_images(resampled_array,resampled_mask):
    """Reorients and rotates the given CT volume and its corresponding mask"""
    reoriented_array=np.transpose(resampled_array,(2,1,0))
    processed_array=np.rot90(np.flipud(reoriented_array),k=1,axes=(1,2))
    processed_mask=np.rot90(np.fliplr(resampled_mask),k=1,axes=(1,2))
    flipped_second_dim=np.flipud(processed_mask.swapaxes(0,1)).swapaxes(0,1)
    rotated_array=np.array([np.rot90(slice,2) for slice in processed_array])
    mirrored_array=np.flip(np.flip(rotated_array,axis=2),axis=1)
    rotated_mask=np.array([np.rot90(slice,2) for slice in flipped_second_dim[::-1]])
    mirrored_mask=np.round(np.flip(np.flip(rotated_mask,axis=2),axis=1))
    return mirrored_array,mirrored_mask

def custom_transform(volume):
    """Applies a custom transformation to the given volume"""
    transformed_volume=np.flip(np.transpose(volume,(1,2,0)),axis=2)[::-1]
    return transformed_volume

def resample_image(image,reference_image):
    """Resamples an image to match a reference image"""
    resampler=sitk.ResampleImageFilter()
    resampler.SetReferenceImage(reference_image)
    resampler.SetInterpolator(sitk.sitkLinear) 
    resampler.SetTransform(sitk.Transform())
    resampler.SetDefaultPixelValue(0)  
    return resampler.Execute(image)

def crop_and_resize_pet(image,threshold):
    """Crops a PET image above a threshold and resizes it to its original dimensions"""
    if threshold>=image.shape[0]:
        raise ValueError("Threshold must be less than the height of the image.")
    cropped_image=image[threshold:,:,:] 
    resized_image=np.zeros_like(image)
    for i in range(image.shape[2]):
        resized_image[:,:,i]=cv2.resize(cropped_image[:,:,i],(image.shape[1],image.shape[0]),interpolation=cv2.INTER_LINEAR)
    return resized_image
