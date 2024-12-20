import subprocess

def run_totalsegmentator(input_path, output_prefix):
    """Runs the totalsegmentator command to segment the given input volume"""
    command=["TotalSegmentator","-i",input_path,"-o",output_prefix]
    subprocess.run(command,check=True)



