import os
import numpy as np
from . import config
from .io_utils import save_dictionary_to_file, load_dictionary_from_file, filter_dicom_pet
from .pet_mask_processing import transform_data_dict, get_masks_and_pet_dict, crop_all_images_and_masks, multiply_pet_data_and_masks
from .CTpipeline import CTProcessingPipeline
from .PETpipeline import PetProcessor
from .SUVpipeline import SUVProcessor

def process_patients_segmentation(data_folder, logger,limit=None, save_temp=False, load_temp=False, temp_file="temp_dict.pkl"):
    """Runs the CT processing pipeline for the specified number of patients"""
    patient_ids=os.listdir(data_folder)
    
    if limit is None:
        limit=len(patient_ids)
    
    if load_temp and os.path.exists(temp_file):
        logger.info(f"Loading existing dictionary from {temp_file}")
        result_dict=load_dictionary_from_file(temp_file)
    else:
        result_dict={}
    
    for i,patient_id in enumerate(patient_ids[:limit]):
        if patient_id in result_dict:
            logger.info(f"Skipping already processed patient ID: {patient_id}")
            continue
        logger.info(f"Processing patient ID: {patient_id}")
        source_path=os.path.join(data_folder,patient_id)
        processor=CTProcessingPipeline(
            source_path=source_path,
            target_study=config.TARGET_STUDY,
            target_number=config.TARGET_NUMBER,
            temp_file=temp_file
        )
        try:
            result=processor.process(save_temp=False,load_temp=False)
            result_dict[patient_id]=result
            logger.info(f"Processing complete for patient ID: {patient_id}")
        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {e}")
            continue
        
        if save_temp:
            save_dictionary_to_file(result_dict,temp_file)
            logger.info(f"Saved intermediate results to {temp_file}")
    
    return result_dict

def process_patients_registration(
    data_folder, logger,target_description_pet, target_description_number_ct, target_study,
    limit=None, save_dict=False, load_dict=False ,dict_file="registration_data.pkl"
):
    """Orchestrates the second step of the pipeline by looping over patients"""
    
    if load_dict and os.path.exists(dict_file):
        logger.info(f"Loading data from {dict_file}")
        return load_dictionary_from_file(dict_file)
    
    patient_ids=os.listdir(data_folder)
    
    if limit is None:
        limit=len(patient_ids)
    
    result_dict={}
    
    for i,patient_id in enumerate(patient_ids[:limit]):
        logger.info(f"Processing patient ID: {patient_id}")
        
        if i in config.EXCLUDE_PATIENTS_PET:
            logger.info(f"Skipping patient ID: {patient_id}")
            continue
        processor=PetProcessor(
            base_path=data_folder,
            dataset_folder="",
            target_description_pet=target_description_pet,
            target_description_number_ct=target_description_number_ct,
            target_study=target_study
        )
        try:
            processor.load_images(specific_directory=patient_id)
            ct_np,pet_np_final=processor.resample_and_process()
            result_dict[patient_id]=[ct_np,pet_np_final]
            logger.info(f"Processing complete for patient: {patient_id}")
        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {e}")
    
    if save_dict:
        save_dictionary_to_file(result_dict,dict_file)
        logger.info(f"Saved data to {dict_file}")
    return result_dict

def orchestrate_pet_processing(ct_dict, pet_dict,padding=20, ct_masks_flipped=False):
    """Orchestrates PET data processing, including transformation, cropping, and mask application"""
    
    transformed_data=transform_data_dict(ct_dict,ct_masks_flipped=ct_masks_flipped)
    masks_and_pet_dict=get_masks_and_pet_dict(transformed_data,pet_dict)
    cropped_data=crop_all_images_and_masks(masks_and_pet_dict,padding=padding)
    masked_pet_images,masked_images=multiply_pet_data_and_masks(cropped_data)
    return masked_pet_images,masked_images

def process_metadata(path_patient, exclude_indices, masked_pet_images_dict, logger,temp_file="metadata_dict.pkl", load_temp=False):
    """Processes metadata for all patients with an option to save/load intermediate results"""
    
    if load_temp and os.path.exists(temp_file):
        logger.info(f"Loading existing metadata dictionary from {temp_file}")
        return load_dictionary_from_file(temp_file)
    
    pipeline=SUVProcessor(
        path_patient=path_patient,
        exclude_indices=exclude_indices,
        masked_pet_images_dict=masked_pet_images_dict
    )
    patient_ids=os.listdir(pipeline.path_patient)
    
    for i,curr_pat in enumerate(patient_ids):
        
        if i in pipeline.exclude_indices:
            continue
        path_curr_pat=os.path.join(pipeline.path_patient,curr_pat)
        dicom_files=filter_dicom_pet(path_curr_pat,"[WB_CTAC]")
        
        if not dicom_files:
            logger.info(f"No PET DICOM files found for patient {curr_pat}")
            continue
        sorted_dicom=pipeline.sort_dicom_slices(dicom_files)
        first_ds=sorted_dicom[0]
        
        try:
            metadata=pipeline.extract_metadata(first_ds)
            time_diff_seconds=pipeline.calculate_time_difference(
                metadata['injection_time'],metadata['acquisition_time']
            )
            decay_constant=pipeline.calculate_decay_constant(metadata['half_life_seconds'])
            metadata['decayed_dose_bq']=pipeline.calculate_decayed_dose(
                metadata['injected_dose_bq'],decay_constant,time_diff_seconds
            )
            
            if metadata['units']!="BQML":
                raise ValueError(f"Units are {metadata['units']}, but 'BQML' is required for SUV calculation")
            pipeline.suv_metadata_dict[curr_pat]=metadata
            pipeline.patients_processed_list.append(curr_pat)
            logger.info(f"Processed patient {curr_pat}")
        except Exception as e:
            logger.error(f"Error processing patient {curr_pat}: {e}")
            continue
    
    save_dictionary_to_file(pipeline.suv_metadata_dict,temp_file)
    logger.info(f"Saved metadata dictionary to {temp_file}")
    return pipeline

def calculate_suv(path_patient, masked_pet_images_dict=None, logger=None, temp_file="suv_dict.pkl", load_temp=False):
    """Calculates SUV volumes for patients using metadata and pixel data, with save/load options"""
    
    if load_temp and os.path.exists(temp_file):
        if logger:
            logger.info(f"Loading existing SUV volumes dictionary from {temp_file}")
        return load_dictionary_from_file(temp_file)
    
    if masked_pet_images_dict is None:
        raise ValueError("masked_pet_images_dict is required when load_temp=False")
    pipeline=process_metadata(
        path_patient=path_patient,
        exclude_indices=config.EXCLUDE_PATIENTS_SUV,
        masked_pet_images_dict=masked_pet_images_dict,
        logger=logger,
        temp_file="metadata_dict.pkl",
        load_temp=load_temp
    )
    
    for curr_pat,metadata in pipeline.suv_metadata_dict.items():
        pixel_data_volume=pipeline.masked_pet_images_dict.get(curr_pat)
        if pixel_data_volume is None:
            if logger:
                logger.info(f"No pixel data found for patient {curr_pat}")
            continue
        try:
            suv_volume=(
                (pixel_data_volume.astype(np.float64)*metadata['patient_weight_g'])/
                metadata['decayed_dose_bq']
            )
            pipeline.suv_volume_dict[curr_pat]=suv_volume
            if logger:
                logger.info(f"Computed SUV for patient {curr_pat}")
        except Exception as e:
            if logger:
                logger.error(f"Error computing SUV for patient {curr_pat}: {e}")
            continue
    save_dictionary_to_file(pipeline.suv_volume_dict,temp_file)
    
    if logger:
        logger.info(f"Saved SUV volumes dictionary to {temp_file}")
    
    return pipeline.suv_volume_dict







