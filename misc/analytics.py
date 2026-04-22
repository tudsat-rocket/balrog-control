import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import MultiCursor

def plot_combined_rocket_data(df):
    start_time = pd.Timestamp("2024-03-22 13:10:00")
    end_time = pd.Timestamp("2027-03-22 16:00:00")

    pressure_sensors = [
        #('Time pressure 0', 'Pressure 0'), #tank
        #('Time pressure 1', 'Pressure 1'), #bottle
        #('Time pressure 2', 'Pressure 2'), #pre
        #('Time temperature Nitrous', 'Temperature Nitrous'),
        #('Time Engine', 'Temperature Engine'),
        #('Time load cell', 'Thrust load cell'),
        #('Time Nitrous load cell', 'Nitrous load cell'),
        #('Time CC0', 'CC0 pressure'),
        #('Time CC1', 'CC1 pressure')
        ('Time pressure 2', 'pressure_2'), #pre
    ]
    valves = [
        #('Time N2OMainValve', 'N2OValveState'),
        #('Time N2PurgeValve', 'N2PurgeValveState'),
        #('TIme N2PressureValve', 'N2PressureValveState'),
        #('Time N2OFillValve', 'N2OFillValveState'),
        #('Time N2OVentValve', 'N2OVentValveState'),
    ]

    # Use subplots with shared X-axis and custom height ratios
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]})

    # Define color palettes for distinct visual separation
    p_colors = plt.cm.viridis(np.linspace(0, 0.9, len(pressure_sensors)))
    v_colors = plt.cm.Set1(np.linspace(0, 1, len(valves)))


    # --- AXIS 1: Pressure ---
    for i, (t_col, v_col) in enumerate(pressure_sensors):
        if t_col not in df.columns: continue
        df[t_col] = pd.to_datetime(df[t_col], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
        df[v_col] = pd.to_numeric(df[v_col], errors='coerce')

        mask = (df[t_col] >= start_time) & (df[t_col] <= end_time)
        data = df.loc[mask, [t_col, v_col]].dropna().sort_values(t_col)
        ax1.plot(data[t_col], data[v_col], "x",label=v_col, color=p_colors[i], alpha=0.8)

    ax1.set_ylabel("Sensor value")
    ax1.grid(True, alpha=0.3)
    #ax1.set_ylim(2.6, None)  # Keep pressure above 0

    # --- AXIS 2: Servos (Stacked in separate plot) ---
    stack_step = 1.5

    for i, (t_col, v_col) in enumerate(valves):
        if t_col not in df.columns: continue

        df[t_col] = pd.to_datetime(df[t_col], format='%Y-%m-%d %H:%M:%S.%f', errors='coerce')
        df[v_col] = pd.to_numeric(df[v_col], errors='coerce')

        past_data = df[df[t_col] < start_time].sort_values(t_col)
        init_val = 1 if (not past_data.empty and past_data[v_col].iloc[-1] != 0) else 0

        mask = (df[t_col] >= start_time) & (df[t_col] <= end_time)
        win_data = df.loc[mask, [t_col, v_col]].dropna().sort_values(t_col)

        plot_df = pd.concat([
            pd.DataFrame({t_col: [start_time], v_col: [init_val]}),
            win_data,
            pd.DataFrame({t_col: [end_time], v_col: [0]})
        ]).sort_values(t_col)

        time_axis = plot_df[t_col]

        # Base level is now positive since it's in its own dedicated subplot
        base_level = i * stack_step
        binary_state = (plot_df[v_col] != 0).astype(int) + base_level

        # Plot the step line using high-contrast valve colors
        color = v_colors[i]
        ax2.step(time_axis, binary_state, where='post', color=color, linewidth=2)

        # Shade the area between the base_level and the active state
        ax2.fill_between(
            time_axis,
            base_level,
            binary_state,
            step="post",
            color=color,
            alpha=0.2
        )

        # Use yaxis_transform so label stays on the left edge regardless of X-zoom
        ax2.text(0.01, base_level + 0.1, f"{v_col}", transform=ax2.get_yaxis_transform(),
                 va='bottom', ha='left', color=color, fontweight='bold', fontsize=9)

    ax2.set_ylabel("Valve States")
    ax2.set_xlabel("Time")
    ax2.set_yticks([])
    ax2.set_ylim(-0.5, len(valves) * stack_step)
    ax2.grid(True, axis='x', alpha=0.3)

    # Combined or separate legends
    ax1.legend(loc='upper left')

    #global multi
    #multi = MultiCursor(fig.canvas, (ax1, ), color='gray', lw=1, ls='--', alpha=0.6, horizOn=True, vertOn=True, useblit=True)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0)
    plt.show()

plot_combined_rocket_data(pd.read_csv('/home/lukas/PycharmProjects/balrog-control/logs/dump_2026-04-01_15-27-09.csv', low_memory=False))
#plot_combined_rocket_data(pd.read_csv('dump_2026-03-22_15-22-18.csv', low_memory=False))