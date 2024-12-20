import pandas as pd

def parse_height(height_str):
    """Parses a height string into total inches"""
    if not isinstance(height_str,str):return None
    height_str=height_str.replace('"','').replace("''",'').strip()
    if "'" in height_str:
        feet_part,inches_part=height_str.split("'")
        feet_part=feet_part.strip()
        inches_part=inches_part.strip()
        feet=int(feet_part) if feet_part.isdigit() else 0
        inches=float(inches_part) if inches_part.replace('.','',1).isdigit() else 0.0
    else:
        feet=0
        inches=float(height_str) if height_str.replace('.','',1).isdigit() else 0.0
    total_inches=feet*12+inches
    return total_inches*0.0254

def calculate_bmi(weight_g,height_m):
    """Calculates BMI given weight in grams and height in meters"""
    if height_m==0:return None
    weight_kg=weight_g/1000
    return weight_kg/(height_m**2)

def height_weight_to_bmi(height_str,weight_g):
    """Main function to calculate BMI from height string and weight in grams"""
    height_m=parse_height(height_str)
    if height_m is None:return None
    return calculate_bmi(weight_g,height_m)

def pad_numbers_to_max_length(numbers):
    """Pads a list of numbers with leading zeros to match the length of the largest number"""
    max_length=len(str(max(numbers)))
    padded_numbers=[str(number).zfill(max_length) for number in numbers]
    return padded_numbers

def create_patient_info_dataframe(metadata_path):
    """Creates a patient info dataframe from an Excel metadata file"""
    metadata=pd.read_excel(metadata_path)
    patients_ids=pad_numbers_to_max_length(metadata["PrimaryMRN"])
    heights=metadata["Height"]
    weights=metadata["WeightInGrams"]
    bmi_values=[height_weight_to_bmi(h,w) for h,w in zip(heights,weights)]
    patient_info_dataframe=pd.DataFrame({
        'patients_ids':patients_ids,
        'Age':metadata["AgeAtEncounter"],
        'Sex':metadata["Sex"],
        'Bmi':bmi_values
    })
    return patient_info_dataframe
