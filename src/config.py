LOG_LEVEL="INFO"
LOG_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILENAME="config.log"

DATA_FOLDER="Data"

#First step - segmentation
TARGET_STUDY="PET-CT"
TARGET_NUMBER="3"
NEW_SPACING=[1,1,1]

#Second step - registration
TARGET_DESCRIPTION_PET="[WB_CTAC]"
TARGET_DESCRIPTION_NUMBER_CT="3"
TARGET_STUDY="PET"
EXCLUDE_PATIENTS_PET=[2,3]

#Third step - SUV calculation
PADDING=20
CT_MASKS_FLIPPED=False
EXCLUDE_PATIENTS_SUV=list(range(2,50))
METADATA_PATH="0179945-DegenScoliPETCT-2014-2024-v2.xlsx"
