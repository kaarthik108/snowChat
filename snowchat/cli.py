import subprocess
import os

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the Streamlit script
    streamlit_script_path = os.path.join(script_dir, 'main.py')

    # Run the Streamlit script using subprocess
    subprocess.run(["streamlit", "run", streamlit_script_path])

if __name__ == "__main__":
    main()
