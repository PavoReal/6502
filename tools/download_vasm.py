import os
import sys
import urllib.request
import zipfile

if __name__ == '__main__':
    # Get the path to the directory containing this script.
    script_dir = os.path.dirname(os.path.realpath(__file__));
    
    # Get the path to the directory containing the vasm executable.
    vasm_dir = os.path.join(script_dir, 'vasm6502/vasm6502_oldstyle');

    os_specific_dir = 'linux';

    if sys.platform == 'win32':
        os_specific_dir = 'win';
    elif sys.platform == 'darwin':
        os_specific_dir = 'mac';

    vasm_dir = os.path.join(vasm_dir, os_specific_dir);

    vasm_exe = os.path.join(vasm_dir, 'vasm6502_oldstyle');
    
    # If the vasm executable doesn't exist, download it.
    if not os.path.isfile(vasm_exe):
        # Get the path to the zip file.
        zip_path = os.path.join(script_dir, 'vasm6502.zip')
        
        # If the zip file doesn't exist, download it.
        if not os.path.isfile(zip_path):
            
            # Get the URL of the zip file.
            url = 'http://www.ibaug.de/vasm/vasm6502.zip'
            
            # Download the zip file.
            print('Downloading vasm6502.zip...')
            urllib.request.urlretrieve(url, zip_path)
        
        # Extract the zip file.
        print('Extracting vasm6502.zip...')
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(script_dir)