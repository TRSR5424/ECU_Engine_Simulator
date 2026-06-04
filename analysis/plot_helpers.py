import os
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def find_csv_in_folder(folder: str) -> str:
    for fname in os.listdir(folder):
        if fname.lower().endswith('.csv'):
            return os.path.join(folder, fname)
    raise FileNotFoundError(f"No CSV file found in {folder}")


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def _save_fig(fig, out_path: str):
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def _first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def plot_afr(df: pd.DataFrame, out_path: str, label: str | None = None):
    fig, ax = plt.subplots()
    ycol = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio'
    ax.plot(df['time'], df[ycol], label=label or ycol)
    ax.set_xlabel('time')
    ax.set_ylabel('AFR')
    ax.set_title('Air-Fuel Ratio')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_rpm(df: pd.DataFrame, out_path: str, label: str | None = None):
    fig, ax = plt.subplots()
    col = 'engine_speed_rpm' if 'engine_speed_rpm' in df.columns else 'rpm'
    ax.plot(df['time'], df[col], label=label or col)
    ax.set_xlabel('time')
    ax.set_ylabel('RPM')
    ax.set_title('Engine Speed (RPM)')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_throttle(df: pd.DataFrame, out_path: str, label: str | None = None):
    fig, ax = plt.subplots()
    col = 'throttle' if 'throttle' in df.columns else 'throttle_input'
    ax.plot(df['time'], df[col], label=label or col)
    ax.set_xlabel('time')
    ax.set_ylabel('Throttle')
    ax.set_title('Throttle')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_comparison(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    column: str,
    out_path: str,
    labels: Tuple[str | None, str | None] = (None, None),
):
    fig, ax = plt.subplots()
    ax.plot(df_a['time'], df_a[column], label=labels[0] or 'A')
    ax.plot(df_b['time'], df_b[column], label=labels[1] or 'B')
    ax.set_xlabel('time')
    ax.set_ylabel(column)
    ax.set_title(f'Comparison: {column}')
    ax.legend()
    _save_fig(fig, out_path)


def plot_torque_vs_rpm(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots()
    ax.scatter(df['engine_speed_rpm'], df['torque'], s=4)
    ax.set_xlabel('RPM')
    ax.set_ylabel('Torque')
    ax.set_title('Torque vs RPM')
    _save_fig(fig, out_path)


def plot_torque_vs_time(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots()
    ax.plot(df['time'], df['torque'])
    ax.set_xlabel('time')
    ax.set_ylabel('torque')
    ax.set_title('Torque vs Time')
    _save_fig(fig, out_path)


def plot_fuel_rate(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots()
    if 'fuel_injection' in df.columns:
        ax.plot(df['time'], df['fuel_injection'])
        ax.set_ylabel('fuel_injection')
    else:
        ax.plot(df['time'], df.get('fuel_mass', pd.Series([0]*len(df))))
        ax.set_ylabel('fuel_mass')
    ax.set_xlabel('time')
    ax.set_title('Fuel Injection / Fuel Rate')
    _save_fig(fig, out_path)


def plot_air_fuel_masses(df: pd.DataFrame, out_path: str):
    fig, ax1 = plt.subplots()
    ax1.plot(df['time'], df.get('air_mass', pd.Series([0]*len(df))), color='tab:blue', label='air_mass')
    ax1.set_xlabel('time')
    ax1.set_ylabel('air_mass', color='tab:blue')
    ax2 = ax1.twinx()
    ax2.plot(df['time'], df.get('fuel_mass', pd.Series([0]*len(df))), color='tab:red', label='fuel_mass')
    ax2.set_ylabel('fuel_mass', color='tab:red')
    fig.suptitle('Air mass and Fuel mass')
    _save_fig(fig, out_path)


def plot_cumulative_fuel(df: pd.DataFrame, out_path: str):
    if 'fuel_mass' in df.columns:
        fuel = df['fuel_mass']
    elif 'fuel_injection' in df.columns:
        fuel = df['fuel_injection']
    else:
        fuel = pd.Series([0] * len(df), index=df.index)
    cum = fuel.cumsum()
    fig, ax = plt.subplots()
    ax.plot(df['time'], cum)
    ax.set_xlabel('time')
    ax.set_ylabel('cumulative_fuel')
    ax.set_title('Cumulative Fuel Consumed')
    _save_fig(fig, out_path)


def plot_afr_hist(df: pd.DataFrame, out_path: str):
    ycol = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio'
    fig, ax = plt.subplots()
    ax.hist(df[ycol].dropna(), bins=50)
    ax.set_xlabel('AFR')
    ax.set_title('AFR Distribution')
    _save_fig(fig, out_path)


def plot_afr_vs_rpm(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots()
    throttle_col = _first_existing_column(df, ['throttle', 'throttle_input'])
    c = df[throttle_col] if throttle_col is not None else None
    sc = ax.scatter(df['engine_speed_rpm'], df.get('measured_air_fuel_ratio', df.get('air_fuel_ratio', np.nan)), c=c, s=6, cmap='viridis')
    ax.set_xlabel('RPM')
    ax.set_ylabel('AFR')
    ax.set_title('AFR vs RPM (color=throttle)')
    if c is not None:
        fig.colorbar(sc, ax=ax, label='throttle')
    _save_fig(fig, out_path)


def plot_throttle_vs_rpm(df: pd.DataFrame, out_path: str):
    fig, ax = plt.subplots()
    throttle_col = _first_existing_column(df, ['throttle', 'throttle_input'])
    ax.scatter(df['engine_speed_rpm'], df[throttle_col] if throttle_col is not None else np.nan, s=6)
    ax.set_xlabel('RPM')
    ax.set_ylabel('throttle')
    ax.set_title('Throttle vs RPM')
    _save_fig(fig, out_path)


def plot_rolling_stats(df: pd.DataFrame, out_path: str, column: str | None = None, window: int = 50):
    if column is None:
        column = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio'
    ser = df[column].rolling(window=window)
    mean = ser.mean()
    std = ser.std()
    fig, ax = plt.subplots()
    ax.plot(df['time'], mean, label='rolling_mean')
    ax.plot(df['time'], std, label='rolling_std')
    ax.set_xlabel('time')
    ax.set_ylabel(column)
    ax.set_title(f'Rolling mean/std ({column})')
    ax.legend()
    _save_fig(fig, out_path)


def plot_psd(df: pd.DataFrame, out_path: str, column: str = 'engine_speed_rpm'):
    x = df[column].dropna().to_numpy(dtype=float)
    if len(x) < 2:
        return
    n = len(x)
    # compute time spacing from positive unique deltas so duplicate timestamps do not zero it out
    time_values = df['time'].dropna().to_numpy(dtype=float)
    deltas = np.diff(time_values)
    positive_deltas = deltas[deltas > 0]
    if positive_deltas.size == 0:
        return
    d = float(np.median(positive_deltas))
    if d <= 0:
        return
    xf = np.fft.rfftfreq(n, d=d)
    yf = np.abs(np.fft.rfft(x - x.mean()))
    fig, ax = plt.subplots()
    ax.plot(xf, yf)
    ax.set_xlabel('frequency')
    ax.set_ylabel('magnitude')
    ax.set_title(f'PSD of {column}')
    _save_fig(fig, out_path)


def plot_correlation_heatmap(df: pd.DataFrame, out_path: str, columns: list[str] | None = None):
    if columns is None:
        throttle_col = _first_existing_column(df, ['throttle', 'throttle_input'])
        columns = [
            'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio',
            'engine_speed_rpm',
        ]
        if throttle_col is not None:
            columns.append(throttle_col)
    cols = [c for c in columns if c in df.columns]
    if len(cols) < 2:
        return
    corr = df[cols].corr().fillna(0)
    constant_cols = [c for c in cols if df[c].nunique(dropna=True) <= 1]
    fig, ax = plt.subplots()
    im = ax.imshow(corr, vmin=-1, vmax=1, cmap='RdBu')
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha='right')
    ax.set_yticklabels(cols)
    for row_index in range(len(cols)):
        for col_index in range(len(cols)):
            value = corr.iloc[row_index, col_index]
            ax.text(col_index, row_index, f'{value:.2f}', ha='center', va='center', color='black', fontsize=8)
    fig.colorbar(im, ax=ax)
    if constant_cols:
        ax.set_title(f"Correlation heatmap (constant: {', '.join(constant_cols)})")
    else:
        ax.set_title('Correlation heatmap')
    _save_fig(fig, out_path)
