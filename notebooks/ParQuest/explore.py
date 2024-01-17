# Ensure you have pandas and pyarrow installed:
# pip install pandas pyarrow
import os
import pandas as pd

def read_parquet_file(file_path):
    
    try:
        # Reading the parquet file
        df = pd.read_parquet(file_path)

        # Displaying the DataFrame
        print(df)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Error file: {file_path}")

def main():
    
    current_path = os.getcwd()
    print("Current Working Directory:", current_path)
    
    
    file_path = "../../output/test/QCD_HT1000to1500_jet1msd_0.parquet"
    read_parquet_file(file_path)
    
    
    return

if __name__ == '__main__':
    main()

