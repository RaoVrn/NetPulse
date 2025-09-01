import glob
import os
from src.collector import collect_data
from src.analyzer import analyze_data
from src.visualizer import visualize_data

def main():
    print("=== NetPulse: QoS Analysis ===")

    # Automatically pick the latest CSV from data folder
    csv_files = glob.glob("data/*.csv")
    if not csv_files:
        print("No CSV files found in 'data/' folder.")
        return

    # Pick the newest file based on modified time
    latest_csv = max(csv_files, key=os.path.getmtime)
    print(f"Using latest CSV: {latest_csv}")

    output_file = "data/network_data_output.csv"

    # Step 1: Collect data
    collect_data(latest_csv, output_file)

    # Step 2: Analyze data
    analysis_results = analyze_data(output_file)
    print("\nAnalysis Summary:")
    for key, value in analysis_results.items():
        print(f"{key}: {value}")

    # Step 3: Visualize data
    visualize_data(output_file)

if __name__ == "__main__":
    main()
