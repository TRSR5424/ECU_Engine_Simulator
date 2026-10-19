"""Run analysis for one or two experiment folders.

Usage:
    python run_analysis.py /path/to/experiment [--other /path/to/other_experiment]

Saves plots into the experiment folder. If `--other` is provided, creates
`{other_name}_Comparison` inside each experiment and writes comparison plots there.
"""
import argparse
import os
import shutil
import sys
from pathlib import Path

# Always ensure project root is on sys.path so `from analysis import ...` works
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from analysis.plot_helpers import (
    find_csv_in_folder,
    load_data,
    plot_afr,
    plot_rpm,
    plot_throttle,
    plot_throttle_rpm_afr,
    plot_torque_vs_rpm
)

def run_single(exp_folder: str):
    data = load_data(find_csv_in_folder(exp_folder))
    plot_afr(data, os.path.join(exp_folder, 'afr_plot.png'), label='AFR')
    plot_rpm(data, os.path.join(exp_folder, 'rpm_plot.png'), label='RPM')
    plot_throttle(data, os.path.join(exp_folder, 'throttle_plot.png'), label='Throttle')
    plot_throttle_rpm_afr(data, os.path.join(exp_folder, 'throttle_rpm_afr_plot.png'))
    plot_torque_vs_rpm(data, os.path.join(exp_folder, 'torque_vs_rpm_plot.png'))


def run_comparison(a_folder: str, b_folder: str):
    print("Refactoring")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-experiment', help='Path to experiment folder containing CSV output')
    p.add_argument('--other', help='Optional other experiment folder to compare against')
    args = p.parse_args()

    exp = args.experiment
    
    if exp == None:
        exp = input("Please input experiment: ")
        
    other = args.other
    if other == None:
        other = input("Please input experiment (click 'enter' to skip) to compare: ")
        
    if other != "":
        run_comparison(exp, other)
    else:
        run_single(exp)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
