from datetime import datetime
import numpy as np

class SUVProcessor:
    def __init__(self,path_patient,exclude_indices,masked_pet_images_dict):
        "Initialize SUVProcessor with paths and data dictionaries"
        
        self.path_patient=path_patient
        self.exclude_indices=exclude_indices
        self.masked_pet_images_dict=masked_pet_images_dict
        self.suv_metadata_dict={}
        self.patients_processed_list=[]
        self.suv_volume_dict={}

    @staticmethod
    def parse_time(time_str):
        "Parses DICOM time strings into datetime objects"
        
        time_format="%H%M%S.%f" if '.' in time_str else "%H%M%S"
        if len(time_str.split('.')[0])<6:
            time_str=time_str.zfill(6+(len(time_str)-len(time_str.split('.')[0])))
        return datetime.strptime(time_str,time_format)

    @staticmethod
    def calculate_decay_constant(half_life_seconds):
        "Calculates the decay constant for a given half-life"
        return np.log(2)/half_life_seconds

    @staticmethod
    def calculate_decayed_dose(injected_dose_bq,decay_constant,time_diff_seconds):
        "Calculates the decayed dose using exponential decay"
        return injected_dose_bq*np.exp(-decay_constant*time_diff_seconds)

    @staticmethod
    def calculate_time_difference(injection_time,acquisition_time):
        "Calculates the time difference in seconds, accounting for day rollover"
        time_diff_seconds=(acquisition_time-injection_time).total_seconds()
        if time_diff_seconds<0:
            time_diff_seconds+=24*3600
        return time_diff_seconds

    @staticmethod
    def sort_dicom_slices(dicom_datasets):
        "Sorts DICOM slices by InstanceNumber"
        return sorted(
            [ds for ds in dicom_datasets if hasattr(ds,'InstanceNumber')],
            key=lambda ds:int(ds.InstanceNumber)
        )

    @staticmethod
    def extract_metadata(dicom_dataset):
        "Extracts metadata required for SUV calculation from a DICOM dataset"
        radiopharm_info=dicom_dataset.RadiopharmaceuticalInformationSequence[0]
        
        return {
            'patient_weight_g':float(dicom_dataset.PatientWeight)*1000,
            'injected_dose_bq':float(radiopharm_info.RadionuclideTotalDose),
            'half_life_seconds':float(radiopharm_info.RadionuclideHalfLife),
            'injection_time':SUVProcessor.parse_time(radiopharm_info.RadiopharmaceuticalStartTime),
            'acquisition_time':SUVProcessor.parse_time(dicom_dataset.AcquisitionTime),
            'rescale_slope':float(dicom_dataset.get('RescaleSlope',1)),
            'rescale_intercept':float(dicom_dataset.get('RescaleIntercept',0)),
            'units':dicom_dataset.Units
        }
