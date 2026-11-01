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
    plot_torque_vs_rpm,
    plot_afr_vs_target_afr,
    plot_torque_vs_rpm,
    plot_fuel_injection_with_air_mass,
    afr_comparison_plot,
    torque_comparison_plot,
    rpm_comparison_plot,
    throttle_comparison_plot,
    fuel_injection_comparison_plot,
    air_mass_comparison_plot,
)

def run_single(exp_folder: str):
    """Run the run single operation."""
    data = load_data(find_csv_in_folder(exp_folder))
    plot_afr(data, os.path.join(exp_folder, 'afr_plot.png'), label='AFR')
    plot_rpm(data, os.path.join(exp_folder, 'rpm_plot.png'), label='RPM')
    plot_throttle(data, os.path.join(exp_folder, 'throttle_plot.png'), label='Throttle')
    plot_throttle_rpm_afr(data, os.path.join(exp_folder, 'throttle_rpm_afr_plot.png'))
    plot_torque_vs_rpm(data, os.path.join(exp_folder, 'torque_vs_rpm_plot.png'))
    plot_afr_vs_target_afr(data, os.path.join(exp_folder, 'afr_vs_target_afr_plot.png'))
    plot_torque_vs_rpm(data, os.path.join(exp_folder, 'torque_vs_rpm_afr_plot.png'))
    plot_fuel_injection_with_air_mass(data, os.path.join(exp_folder, 'throttle_vs_rpm_afr_plot.png'))


def run_comparison(file: str):
    """Run the run comparison operation."""
    afr_comparison_plot(file, 'comparison/afr_comparison_plot.png')
    rpm_comparison_plot(file, 'comparison/rpm_comparison_plot.png')
    torque_comparison_plot(file, 'comparison/torque_comparison_plot.png')
    throttle_comparison_plot(file, 'comparison/throttle_comparison_plot.png')
    air_mass_comparison_plot(file, 'comparison/air_mass_comparison_plot.png')
    fuel_injection_comparison_plot(file, 'comparison/fuel_injection_comparison_plot.png')


def main():
    """Parse inputs and run the command-line entry point."""
    p = argparse.ArgumentParser()
    p.add_argument('-experiment', help='Path to experiment folder containing CSV output or CSV with paths to multiple experiment folders')
    args = p.parse_args()

    exp = args.experiment
    
    if exp == None:
        exp = input("Please input experiment (or comparison file): ")
        
    
    if exp.endswith('.txt'):
        # Comparison mode
        run_comparison(exp)   
    else:
        # Single experiment mode
        run_single(exp)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
