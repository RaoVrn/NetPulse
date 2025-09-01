import pandas as pd
import matplotlib.pyplot as plt

def visualize_data(input_file, save_figures=False):
    df = pd.read_csv(input_file)

    # ---- 1. Aggregate signal by Network Type ----
    if "Network_Type" in df.columns:
        network_avg_signal = df.groupby("Network_Type")["Signal_dBm"].mean()
        plt.figure(figsize=(8, 4))
        network_avg_signal.plot(kind="bar", color="skyblue")
        plt.xlabel("Network Type")
        plt.ylabel("Average Signal (dBm)")
        plt.title("Average Signal by Network Type")
        plt.grid(True)
        if save_figures:
            plt.savefig("graphs/signal_by_network_type.png")
        plt.show()

    # ---- 2. Signal distribution histogram ----
    plt.figure(figsize=(8, 4))
    plt.hist(df["Signal_dBm"], bins=20, color="salmon", edgecolor="black")
    plt.xlabel("Signal Strength (dBm)")
    plt.ylabel("Frequency")
    plt.title("Signal Strength Distribution")
    plt.grid(axis="y")
    if save_figures:
        plt.savefig("graphs/signal_distribution.png")
    plt.show()

    # ---- 3. Time series of signal over time ----
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        plt.figure(figsize=(10, 4))
        plt.plot(df["Timestamp"], df["Signal_dBm"], marker='o', linestyle='-', color='green')
        plt.xlabel("Time")
        plt.ylabel("Signal (dBm)")
        plt.title("Signal Variation Over Time")
        plt.grid(True)
        if save_figures:
            plt.savefig("graphs/signal_over_time.png")
        plt.show()
