"""Run analysis for one or two experiment folders.

Usage:
    python run_analysis.py /path/to/experiment [--other /path/to/other_experiment]

Saves plots into the experiment folder. If `--other` is provided, creates
`{other_name}_Comparison` inside each experiment and writes comparison plots there.
"""
import argparse
import os
import shutil

from analysis.plot_helpers import (
    find_csv_in_folder,
    load_data,
    plot_afr,
    plot_rpm,
    plot_throttle,
    plot_comparison,
    ensure_dir,
)

from analysis.plot_helpers import (
    plot_torque_vs_rpm,
    plot_torque_vs_time,
    plot_fuel_rate,
    plot_air_fuel_masses,
    plot_cumulative_fuel,
    plot_afr_hist,
    plot_afr_vs_rpm,
    plot_throttle_vs_rpm,
    plot_rolling_stats,
    plot_psd,
    plot_correlation_heatmap,
)


def save_single(exp_folder: str):
    csv = find_csv_in_folder(exp_folder)
    df = load_data(csv)
    plot_afr(df, os.path.join(exp_folder, 'afr.png'))
    plot_rpm(df, os.path.join(exp_folder, 'rpm.png'))
    plot_throttle(df, os.path.join(exp_folder, 'throttle.png'))
    # additional diagnostics
    plot_torque_vs_rpm(df, os.path.join(exp_folder, 'torque_vs_rpm.png'))
    plot_torque_vs_time(df, os.path.join(exp_folder, 'torque_vs_time.png'))
    plot_fuel_rate(df, os.path.join(exp_folder, 'fuel_rate.png'))
    plot_air_fuel_masses(df, os.path.join(exp_folder, 'air_fuel_masses.png'))
    plot_cumulative_fuel(df, os.path.join(exp_folder, 'cumulative_fuel.png'))
    plot_afr_hist(df, os.path.join(exp_folder, 'afr_hist.png'))
    plot_afr_vs_rpm(df, os.path.join(exp_folder, 'afr_vs_rpm.png'))
    plot_throttle_vs_rpm(df, os.path.join(exp_folder, 'throttle_vs_rpm.png'))
    plot_rolling_stats(df, os.path.join(exp_folder, 'afr_rolling.png'), column=None)
    plot_psd(df, os.path.join(exp_folder, 'rpm_psd.png'), column='engine_speed_rpm')
    plot_correlation_heatmap(df, os.path.join(exp_folder, 'correlation.png'))
    # write a short report
    from analysis.report_generator import generate_report

    generate_report(df, exp_folder)


def save_comparison(a_folder: str, b_folder: str):
    csv_a = find_csv_in_folder(a_folder)
    csv_b = find_csv_in_folder(b_folder)
    df_a = load_data(csv_a)
    df_b = load_data(csv_b)
    name_a = os.path.basename(os.path.normpath(a_folder))
    name_b = os.path.basename(os.path.normpath(b_folder))
    out_a = os.path.join(a_folder, f"{name_b}_Comparison")
    out_b = os.path.join(b_folder, f"{name_a}_Comparison")
    ensure_dir(out_a)
    ensure_dir(out_b)

    # comparison plots saved in out_a, then copied to out_b
    plot_comparison(df_a, df_b, 'measured_air_fuel_ratio', os.path.join(out_a, 'afr_comparison.png'), labels=(name_a, name_b))
    plot_comparison(df_a, df_b, 'engine_speed_rpm', os.path.join(out_a, 'rpm_comparison.png'), labels=(name_a, name_b))
    plot_comparison(df_a, df_b, 'throttle', os.path.join(out_a, 'throttle_comparison.png'), labels=(name_a, name_b))

    # copy to other folder so both have the results
    for fname in ('afr_comparison.png', 'rpm_comparison.png', 'throttle_comparison.png'):
        shutil.copy(os.path.join(out_a, fname), os.path.join(out_b, fname))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('experiment', help='Path to experiment folder containing CSV output')
    p.add_argument('--other', help='Optional other experiment folder to compare against')
    args = p.parse_args()

    exp = args.experiment
    other = args.other
    if other:
        save_comparison(exp, other)
    else:
        save_single(exp)


if __name__ == '__main__':
    main()
