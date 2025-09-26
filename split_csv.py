import pandas as pd
import os

def split_csv(input_file="output2.csv", output_dir="output_chunks", chunk_size=3000):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    total_rows = len(df)
    num_files = (total_rows // chunk_size) + (1 if total_rows % chunk_size != 0 else 0)
    
    print(f"Total records: {total_rows}")
    print(f"Splitting into {num_files} files...")

    for i in range(num_files):
        start_row = i * chunk_size
        end_row = start_row + chunk_size
        chunk = df.iloc[start_row:end_row]
        
        output_file = os.path.join(output_dir, f"test_part_{i+1}.csv")
        chunk.to_csv(output_file, index=False)
        
        print(f"[OK] Created: {output_file} with {len(chunk)} records")
    
    print("[DONE] All files created successfully.")

# Run the function
split_csv()
