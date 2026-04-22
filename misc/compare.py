from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_compared_csvs(file_paths, offsets=None):
    """
    Plots n CSV files.
    file_paths: List of strings
    offsets: List of floats (seconds), must match length of file_paths
    """
    if offsets is None:
        offsets = [0.0] * len(file_paths)

    pressure_sensors = [('timestamp', 'value')]
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Generate a color map for n files
    color_map = plt.cm.get_cmap('viridis', len(file_paths))

    for idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        label_suffix = f"Run {idx}"
        offset_seconds = offsets[idx]

        for i, (t_col, v_col) in enumerate(pressure_sensors):
            if t_col not in df.columns:
                continue

            # Data conversion
            df[t_col] = pd.to_datetime(df[t_col], errors='coerce')
            df[v_col] = pd.to_numeric(df[v_col], errors='coerce')

            # Apply individual offset
            x_axis = df[t_col] - pd.Timedelta(seconds=offset_seconds)

            # Drop NaNs and plot
            valid_mask = df[v_col].notna() & x_axis.notna()
            ax1.plot(x_axis[valid_mask], df[v_col][valid_mask],
                     label=f"{file_path} (Offset: {offset_seconds}s)",
                     color=color_map(idx), alpha=0.7)

    ax1.set_ylabel("Pressure Value")
    ax1.set_xlabel("Time (Aligned)")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize='small')

    plt.tight_layout()
    plt.show()


# Example usage for n files:
files = [
    'export_pressure_cc0_label_0.8mm_1.csv',
    'export_pressure_cc0_label_0.8mm_0.csv',
    'export_pressure_cc0_label_0.8mm_2.csv',
    'export_pressure_cc0_label_0.8mm_3_leak.csv'
]
# Provide an offset for each file (e.g., align Run 1 by -450.1s, others 0)
offsets = [0.0, -450.1, 270.12, 566.80]

plot_compared_csvs(files, offsets)