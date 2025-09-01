import pandas as pd

def analyze_data(input_file):
    df = pd.read_csv(input_file)

    # Basic metrics
    avg_signal = round(df["Signal_dBm"].mean(), 2)
    avg_download = round(df["Download_Mbps"].mean(), 2)
    avg_upload = round(df["Upload_Mbps"].mean(), 2)
    avg_latency = round(df["Latency_ms"].mean(), 2)

    # Classify signal quality
    df["Signal_Quality"] = df["Signal_dBm"].apply(
        lambda x: "Excellent" if x > -85 else ("Good" if x > -95 else "Poor")
    )

    signal_quality_counts = df["Signal_Quality"].value_counts().to_dict()
    best_location = df.loc[df["Signal_dBm"].idxmax(), "Location"]
    worst_location = df.loc[df["Signal_dBm"].idxmin(), "Location"]

    summary = {
        "Average Signal (dBm)": avg_signal,
        "Average Download Speed (Mbps)": avg_download,
        "Average Upload Speed (Mbps)": avg_upload,
        "Average Latency (ms)": avg_latency,
        "Signal Quality Distribution": signal_quality_counts,
        "Best Location": best_location,
        "Worst Location": worst_location
    }
    return summary
