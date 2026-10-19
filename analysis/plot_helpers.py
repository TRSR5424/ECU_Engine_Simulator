import os

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def find_csv_in_folder(folder: str) -> str:
    for fname in os.listdir(folder):
        if fname.lower().endswith('.csv'):
            return os.path.join(folder, fname)
    raise FileNotFoundError(f"No CSV file found in {folder}")


def load_data(csv_path: str) -> pd.DataFrame:
    return pd.read_csv(csv_path)



def plot_afr(df: pd.DataFrame, out_path: str, label: str | None = None):
    sns.set_theme(style="darkgrid")
    
    graph = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="air_fuel_ratio"
    )
    
    graph.savefig(out_path)


def plot_rpm(df: pd.DataFrame, out_path: str, label: str | None = None):
    sns.set_theme(style="darkgrid")
    
    graph = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="engine_speed_rpm"
    )
    
    graph.savefig(out_path)
    

def plot_throttle(df: pd.DataFrame, out_path: str, label: str | None = None):
    sns.set_theme(style="darkgrid")
    
    graph = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="throttle"
    )
    
    graph.savefig(out_path)
    
def plot_throttle_rpm_afr(df: pd.DataFrame, out_path: str):
    print("IDK")

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()
        
    ax1.plot(df['time'], df['engine_speed_rpm'], color='orange', label='RPM')
    ax1.set_ylabel('RPM')
    ax1.tick_params(axis='y', labelcolor='orange')
    
    ax2.plot(df['time'], df['air_fuel_ratio'], color='blue', label='AFR')
    ax2.set_ylabel('AFR')
    ax2.tick_params(axis='y', labelcolor='blue')
    
    ax3.plot(df['time'], df['throttle'], color='green')
    ax3.set_axis_off()
    
    ax1.set_xlabel('Time')
    
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax3.legend(loc='lower right')
    
    fig.savefig(out_path)
    

# def plot_comparison(
#     df_a: pd.DataFrame,
#     df_b: pd.DataFrame,
#     column: str,
#     out_path: str,
#     labels: Tuple[str | None, str | None] = (None, None),
#  ):


# def plot_torque_vs_rpm(df: pd.DataFrame, out_path: str):

# def plot_torque_vs_time(df: pd.DataFrame, out_path: str):


# def plot_fuel_rate(df: pd.DataFrame, out_path: str):


# def plot_air_fuel_masses(df: pd.DataFrame, out_path: str):


# def plot_cumulative_fuel(df: pd.DataFrame, out_path: str):


# def plot_afr_hist(df: pd.DataFrame, out_path: str):

# def plot_afr_vs_rpm(df: pd.DataFrame, out_path: str):


# def plot_throttle_vs_rpm(df: pd.DataFrame, out_path: str):


# def plot_rolling_stats(df: pd.DataFrame, out_path: str, column: str | None = None, window: int = 50):


# def plot_psd(df: pd.DataFrame, out_path: str, column: str = 'engine_speed_rpm'):


# def plot_correlation_heatmap(df: pd.DataFrame, out_path: str, columns: list[str] | None = None):
