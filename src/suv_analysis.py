import numpy as np


def compute_mean_suv_for_patient(suv_volume,masked_image):
    "Compute mean SUV for each vertebra in a single patient"
    mean_suv_by_vertebra={}
    unique_labels=np.unique(masked_image)
    
    for label in unique_labels:
        if label==0:
            continue
        vertebra_mask=(masked_image==label)
        vertebra_suv_values=suv_volume[vertebra_mask]
        
        if vertebra_suv_values.size>0:
            mean_suv_by_vertebra[label]=np.mean(vertebra_suv_values)
        else:
            mean_suv_by_vertebra[label]=None
    return mean_suv_by_vertebra

def compute_mean_suv_across_patients(suv_volume_dict,masked_images_dict):
    "Compute mean SUV for each vertebra across all patients"
    mean_suv_by_vertebra_by_patient={}
    mean_suv_by_vertebral_level_across_patients={}
    
    for patient_id,suv_volume in suv_volume_dict.items():
        masked_image=masked_images_dict[patient_id]
        mean_suv_by_vertebra=compute_mean_suv_for_patient(suv_volume,masked_image)
        mean_suv_by_vertebra_by_patient[patient_id]=mean_suv_by_vertebra
        
        for label,mean_suv in mean_suv_by_vertebra.items():
            if mean_suv is not None:
                mean_suv_by_vertebral_level_across_patients.setdefault(label,[]).append(mean_suv)
    return mean_suv_by_vertebra_by_patient,mean_suv_by_vertebral_level_across_patients

