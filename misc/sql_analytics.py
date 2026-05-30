import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3


def plot_rocket_log(db_path, start_str, end_str):
    # Zeitfenster für den Plot
    start_time = pd.to_datetime(start_str)
    end_time = pd.to_datetime(end_str)

    # Konfiguration (Sensorname in DB, Label im Plot)
    pressure_sensors = [
        #('pressure_tank', 'Tank Pressure', 1),
        #('pressure_ox_bottle', 'Ox Bottle Pressure', 1),
        #('pressure_n2_bottle', 'N2 Bottle Pressure', 1),
        #('pressure_cc_pre', 'CC Pre Pressure', 1),
        #('pressure_cc0', 'CC Pressure 0', 15),
        ('cc0_CAN', 'CC Pressure 0 CAN', 0.2),
        #('pressure_cc1', 'CC Pressure 1'),
        #('pressure_cc1_can', 'CC Pressure 1 CAN'),
        ('temp_ox', 'Ox Temperature', 1),
        ('temp_engine', 'Engine Temperature', 1),
        ('temp_1', 'Temperature 1', 1),
        ('temp_2', 'Temperature 2', 1),
        ('load_cell_thrust', 'Thrust Force', 1),
        #('load_cell_ox', 'N2O Tank Weight', 1)
    ]
    valves = [
        ('main_valve', 'Main Valve'),
        #('vent_valve', 'Vent Valve'),
        #('pressurization_valve', 'Pressurization Valve'),
        #('fill_valve', 'Fill Valve'),
        #('purge_valve', 'Purge Valve'),
        #('vent_solenoid', 'Vent Solenoid'),
        #('fill_solenoid', 'Fill Solenoid'),
        #('qd_solenoid', 'QD Solenoid'),
        #('qd_servo', 'QD Servo')
    ]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True,
                                   gridspec_kw={'height_ratios': [3, 1]})

    p_colors = plt.cm.viridis(np.linspace(0, 0.9, len(pressure_sensors) or 1))
    v_colors = plt.cm.Set1(np.linspace(0, 1, len(valves) or 1))

    conn = sqlite3.connect(db_path)

    # --- AXIS 1: Sensoren ---
    for i, (db_name, label, factor) in enumerate(pressure_sensors):
        # Nutzt den Index idx_ts für schnelles Laden
        query = """
                SELECT timestamp, value \
                FROM sensor_data
                WHERE sensor_name = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC \
                """
        df = pd.read_sql_query(query, conn, params=(db_name, start_time.timestamp(), end_time.timestamp()))

        if df.empty: continue

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        ax1.plot(df['timestamp'], df['value'] * factor, label=label, color=p_colors[i], alpha=0.8)

        df_to_export = df[['timestamp', 'value']].copy()
        df_to_export.to_csv(f"export_{db_name}_label.csv", index=False)

    ax1.set_ylabel("Sensor Value")
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    # --- AXIS 2: Ventile (Stacked) ---
    stack_step = 1.5
    for i, (db_name, label) in enumerate(valves):
        # Hier auch das Fenster nutzen
        query = "SELECT timestamp, value FROM sensor_data WHERE sensor_name = ? ORDER BY timestamp ASC"
        df_v = pd.read_sql_query(query, conn, params=(db_name,))
        if df_v.empty: continue

        df_v['timestamp'] = pd.to_datetime(df_v['timestamp'], unit='s')

        # Initialwert vor dem Startfenster finden
        past_data = df_v[df_v['timestamp'] < start_time]
        init_val = 1 if (not past_data.empty and past_data['value'].iloc[-1] != 0) else 0

        mask = (df_v['timestamp'] >= start_time) & (df_v['timestamp'] <= end_time)
        win_data = df_v.loc[mask]

        plot_df = pd.concat([
            pd.DataFrame({'timestamp': [start_time], 'value': [init_val]}),
            win_data,
            pd.DataFrame({'timestamp': [end_time], 'value': [0]})  # Dummy Ende
        ]).sort_values('timestamp')

        base_level = i * stack_step
        binary_state = (plot_df['value'] != 0).astype(int) + base_level

        ax2.step(plot_df['timestamp'], binary_state, where='post', color=v_colors[i], linewidth=2)
        ax2.fill_between(plot_df['timestamp'], base_level, binary_state, step="post", color=v_colors[i], alpha=0.2)
        ax2.text(0.01, base_level + 0.1, f"{label}", transform=ax2.get_yaxis_transform(),
                 va='bottom', ha='left', color=v_colors[i], fontweight='bold', fontsize=9)


    conn.close()
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


# Beispielaufruf
plot_rocket_log('/home/lukas/PycharmProjects/balrog-control/telemetry_2026-05-30_14-36-39', "2026-05-30 12:00:00", "2026-05-30 14:10:00")