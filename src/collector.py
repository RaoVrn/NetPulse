import pandas as pd
import glob
import os

def collect_data(data_folder="data", output_file="data/network_data_output.csv"):
    """
    Collects all CSVs from a folder, normalizes columns, fills missing data,
    and saves a combined CSV.
    """
    csv_files = glob.glob(os.path.join(data_folder, "*.csv"))
    if not csv_files:
        print(f"No CSV files found in {data_folder}/")
        return

    data_frames = []
    for file in csv_files:
        df = pd.read_csv(file)

        # Rename columns if needed
        df = df.rename(columns={
            "dBm": "Signal_dBm",
            "NetworkType": "Network_Type"
        })

        # Fill missing columns with defaults
        for col, default in {
            "Location": "Unknown",
            "Download_Mbps": 0,
            "Upload_Mbps": 0,
            "Latency_ms": 0,
            "Signal_dBm": -100,
            "Network_Type": "Unknown"
        }.items():
            if col not in df.columns:
                df[col] = default

        data_frames.append(df)

    # Combine all CSVs into one DataFrame
    combined = pd.concat(data_frames, ignore_index=True)

    # Save combined CSV
    combined.to_csv(output_file, index=False)
    print(f"Data collected and saved to {output_file}")
