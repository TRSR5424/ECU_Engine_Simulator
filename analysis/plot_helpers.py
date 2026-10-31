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

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="air_fuel_ratio"
    )

    fig.savefig(out_path)


def plot_afr_vs_target_afr(df: pd.DataFrame, out_path: str, label: str | None = None):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.plot(df['time'], df['air_fuel_ratio'], color='blue', label='AFR')
    ax1.set_ylabel('AFR')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2.plot(df['time'], df['target_air_fuel_ratio'],
             color='orange', label='Target AFR')
    ax2.set_ylabel('Target AFR')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_xlabel('Time')

    fig.savefig(out_path)


def plot_rpm(df: pd.DataFrame, out_path: str, label: str | None = None):
    sns.set_theme(style="darkgrid")

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="engine_speed_rpm"
    )

    fig.savefig(out_path)


def plot_throttle(df: pd.DataFrame, out_path: str, label: str | None = None):
    sns.set_theme(style="darkgrid")

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="throttle"
    )

    fig.savefig(out_path)


def plot_throttle_rpm_afr(df: pd.DataFrame, out_path: str):
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


def plot_torque_vs_rpm(df: pd.DataFrame, out_path: str):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.plot(df['time'], df['engine_speed_rpm'], color='orange', label='RPM')
    ax1.set_ylabel('RPM')
    ax1.tick_params(axis='y', labelcolor='orange')

    ax2.plot(df['time'], df['torque'], color='blue', label='Torque')
    ax2.set_ylabel('Torque')
    ax2.tick_params(axis='y', labelcolor='blue')

    ax1.set_xlabel('Time')

    fig.savefig(out_path)


def plot_fuel_injection_with_air_mass(df: pd.DataFrame, out_path: str):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.plot(df['time'], df['fuel_injection'],
             color='blue', label='Fuel Injection')
    ax1.set_ylabel('Fuel Injection')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2.plot(df['time'], df['air_mass'], color='orange', label='Air Mass')
    ax2.set_ylabel('Air Mass')
    ax2.tick_params(axis='y', labelcolor='orange')

    ax1.set_xlabel('Time')

    fig.savefig(out_path)


def _get_experiments_from_csv(file: str) -> list[str]:
    experiments = []
    with open("analysis/" + file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                experiments.append(line)
    return experiments


def _create_df_for_comparison(experiments: list[str], compared_on: str, out_path: str) -> pd.DataFrame:
    comparison_data = []
    for exp in experiments:
        loaded_data = load_data(find_csv_in_folder(exp))
        experiment_data = loaded_data.loc[:, ["time", compared_on]].copy()
        experiment_data["experiment"] = os.path.basename(os.path.normpath(exp))
        comparison_data.append(experiment_data)

    if not comparison_data:
        return pd.DataFrame(columns=["time", compared_on, "experiment"])

    return pd.concat(comparison_data, ignore_index=True)


def afr_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="air_fuel_ratio", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="air_fuel_ratio",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)


def torque_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="torque", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="torque",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)


def rpm_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="engine_speed_rpm", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="engine_speed_rpm",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)


def throttle_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="throttle", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="throttle",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)


def fuel_injection_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="fuel_injection", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="fuel_injection",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)


def air_mass_comparison_plot(file: str, out_path: str):
    sns.set_theme(style="darkgrid")

    experiments = _get_experiments_from_csv(file)

    df = _create_df_for_comparison(
        experiments, compared_on="air_mass", out_path=out_path)

    fig = sns.relplot(
        data=df,
        kind="line",
        x="time",
        y="air_mass",
        hue="experiment",
        estimator=None,
    )

    for exp in experiments:
        if not os.path.exists(exp + "/comparison"):
            os.makedirs(exp + "/comparison")
        fig.savefig(exp + "/" + out_path)
