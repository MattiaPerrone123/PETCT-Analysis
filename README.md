## Repo Structure
parlo un po del progetto

### Data
- parlo di input data


### Root Directory
- **Data/**: Placeholder for input data (not included in the repository).
- **docs/**: Documentation and resources, including:
  - `abstract.pdf`: Abstract (poster at ORS 2025).
  - `pipeline.log`: Example log file from a pipeline run
- **input_ts/**: Directory for timestamped input data.
- **main.ipynb**: Jupyter notebook demonstrating the pipeline's usage
- **requirements.txt**: Python dependencies required for the project
- **.gitignore**: Specifies files and folders to exclude from version control


The `src/` directory contains all scripts and modules for processing, analysis and utility functions:
- **CTpipeline.py**: Processes and performs segmentation of CT scans 
- **PETpipeline.py**: Processes and performs registration of PET scans to CT scans
- **SUVpipeline.py**: Computes and analyzes standardized uptake values (SUVs)
- **config.py**: Stores configuration constants and parameters
- **demographics.py**: Utilities for handling patient demographic data
- **image_processing.py**: Functions for preprocessing and manipulating medical images
- **io_utils.py**: Input/output utilities
- **logging_setup.py**: Configures logging for pipeline execution
- **orchestrator.py**: Coordinates the execution of the pipeline components
- **pet_mask_processing.py**: Functions for PET mask manipulation and analysis
- **suv_analysis.py**: Tools for analyzing SUV metrics
- **totalsegmentator_integration.py**: Integration with the TotalSegmentator tool for segmentation of CT
- **utils.py**: General-purpose helper functions
- **visualization.py**: Functions for visualizing data and results


## Key features
- **Segmentation of CT scans**:
  - Performing segmentation of vertebrae in CT scans using [TotalSegmentator](https://github.com/wasserth/TotalSegmentator)
- **Registration of PET scans to CT scans**:
  - Registering PET scans to CT scans to apply the masks generated in the previous step to PET scans
- **SUV calculation and analysis**:
  - Computing mean SUV values by vertebral levels and correlates them with spine level


