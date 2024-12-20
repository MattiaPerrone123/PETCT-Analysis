## Repository Structure

### Root Directory
- **Data/**: Placeholder for input and output data (not included in the repository).
- **docs/**: Documentation and resources, including:
  - `abstract.md`: Study abstract.
  - `sample_pipeline.log`: Example log file from a pipeline run.
- **input_ts/**: Directory for timestamped input data.
- **main.ipynb**: Jupyter notebook demonstrating the pipeline's usage.
- **requirements.txt**: Python dependencies.
- **.gitignore**: Specifies files and folders to exclude from version control.
- **README.md**: Project documentation (this file).

### Source Code (`src/`)
The `src/` directory contains all scripts and modules for processing, analysis, and utility functions:
- **CTpipeline.py**: Processes CT images and prepares data for analysis.
- **PETpipeline.py**: Handles PET image processing tasks.
- **SUVpipeline.py**: Computes and analyzes standardized uptake values (SUVs).
- **config.py**: Stores configuration constants and parameters.
- **demographics.py**: Utilities for handling patient demographic data.
- **image_processing.py**: Functions for preprocessing and manipulating medical images.
- **io_utils.py**: Input/output utilities, including file loading and saving.
- **logging_setup.py**: Configures logging for pipeline execution.
- **orchestrator.py**: Coordinates the execution of the pipeline components.
- **pet_mask_processing.py**: Functions for PET mask manipulation and analysis.
- **suv_analysis.py**: Tools for analyzing SUV metrics.
- **totalsegmentator_integration.py**: Integration with the TotalSegmentator tool for advanced segmentation.
- **utils.py**: General-purpose helper functions.
- **visualization.py**: Functions for visualizing data and results.

---

## Key Features
- **Comprehensive Processing Pipelines**:
  - Modular pipelines for CT, PET, and SUV data processing.
  - Integration with TotalSegmentator for segmentation tasks.
- **SUV Analysis**:
  - Computes mean SUV values by vertebral levels and correlates them with spine morphology.
- **Visualization Tools**:
  - Interactive slice visualization for manual review.
  - Automated generation of SUV boxplots for spinal levels.
- **Extensible Framework**:
  - Modular design allows for easy integration of new features and tools.

## Getting Started

### Prerequisites
- Python 3.8+
- Recommended: Use a virtual environment for dependency management.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PETCT-Analysis.git
   cd PETCT-Analysis-main
