import os
from typing import Tuple

import pandas as pd
import matplotlib.pyplot as plt


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


def plot_afr(df: pd.DataFrame, out_path: str, label: str = None):
    fig, ax = plt.subplots()
    ycol = 'measured_air_fuel_ratio' if 'measured_air_fuel_ratio' in df.columns else 'air_fuel_ratio'
    ax.plot(df['time'], df[ycol], label=label or ycol)
    ax.set_xlabel('time')
    ax.set_ylabel('AFR')
    ax.set_title('Air-Fuel Ratio')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_rpm(df: pd.DataFrame, out_path: str, label: str = None):
    fig, ax = plt.subplots()
    col = 'engine_speed_rpm' if 'engine_speed_rpm' in df.columns else 'rpm'
    ax.plot(df['time'], df[col], label=label or col)
    ax.set_xlabel('time')
    ax.set_ylabel('RPM')
    ax.set_title('Engine Speed (RPM)')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_throttle(df: pd.DataFrame, out_path: str, label: str = None):
    fig, ax = plt.subplots()
    col = 'throttle' if 'throttle' in df.columns else 'throttle_input'
    ax.plot(df['time'], df[col], label=label or col)
    ax.set_xlabel('time')
    ax.set_ylabel('Throttle')
    ax.set_title('Throttle')
    if label:
        ax.legend()
    _save_fig(fig, out_path)


def plot_comparison(df_a: pd.DataFrame, df_b: pd.DataFrame, column: str, out_path: str, labels: Tuple[str, str] = (None, None)):
    fig, ax = plt.subplots()
    ax.plot(df_a['time'], df_a[column], label=labels[0] or 'A')
    ax.plot(df_b['time'], df_b[column], label=labels[1] or 'B')
    ax.set_xlabel('time')
    ax.set_ylabel(column)
    ax.set_title(f'Comparison: {column}')
    ax.legend()
    _save_fig(fig, out_path)
