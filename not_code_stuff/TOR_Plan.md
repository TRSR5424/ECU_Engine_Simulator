TOR Paragraph Suggestions
=========================

Project: ECU Engine Simulator

Project Title
-------------

Development and Evaluation of a Configurable ECU Engine-Control Simulator

Alternative:
A Timestep-Based Simulator for Testing Engine Controllers and Sensor Behaviour

1. Background to Project (maximum 300 words)
---------------------------------------------

Points to include:

- Introduce the project as a software simulator for electronic engine control
  units.
- Explain that testing real engine-control systems can be expensive, unsafe and
  difficult to reproduce.
- Explain that the simulator provides engine dynamics, configurable throttle,
  load and target air-fuel ratio, multiple controllers, different sensor
  behaviours, CSV logging and analysis tools.
- Describe the computing aspects: Python simulation architecture, C++
  controller implementation, Python-to-C++ integration using ctypes,
  configuration-driven experiments, automated testing and data analysis.
- Explain that the project enables repeatable controller experiments and helps
  investigate how sensor imperfections affect control performance.
- Explain the technical challenge of combining physics modelling, software
  architecture, control logic, native-code integration and experimental
  evaluation.
- Support claims about control systems, ECU simulation and feedback control
  with academic references.

**Paragraph layout:**
Start with the limitations of testing engine-control algorithms on physical
hardware. Introduce the simulator as a safer and more repeatable alternative.
Finish by explaining the technical challenge and intended benefits to students,
researchers or developers working with engine-control systems.

2. Aim of Project (maximum 100 words)
--------------------------------------

Use one clear sentence beginning with **"To"**:

To develop and evaluate a configurable timestep-based ECU engine simulator that
enables repeatable investigation of engine controllers and sensor behaviours.

**Alternative:**

To develop and evaluate a configurable software simulator for comparing
engine-control strategies under different engine loads, target air-fuel ratios
and sensor conditions.

Keep controller development, sensor modelling and evaluation as objectives
supporting this single aim rather than creating several separate aims.

3. Objectives (maximum 150 words and maximum 10 objectives)
------------------------------------------------------------

1. Review literature on ECU control, feedback control, engine modelling and
   sensor imperfections.
2. Specify the functional and non-functional requirements for the simulator.
3. Design the architecture for the engine, sensor, controller, simulation and
   analysis components.
4. Implement a configurable timestep-based engine simulation environment.
5. Implement and integrate multiple controller strategies, including fixed-
   output and PID-based control.
6. Implement configurable ideal, noisy and delayed sensor behaviours.
7. Develop experiment configuration, logging and visualisation features for
   repeatable simulations.
8. Test the simulator using automated tests and validation checks for
   controller and engine behaviour.
9. Compare controller performance under different loads, targets and sensor
   conditions using measurable metrics.
10. Evaluate the simulator against reference datasets or expected behaviours
    and identify its limitations.

4. Proposed Methodology / Work (maximum 300 words)
---------------------------------------------------

**Include:**

- A literature review covering ECU systems, air-fuel-ratio control, PID
  control, engine simulation and software testing.
- Requirements defining supported engine variables, controller inputs, sensor
  types, configuration options and experiment outputs.
- A system design separating the engine model, sensor layer, controller layer,
  simulation loop, logger and analysis tools.
- Python for simulation orchestration, configuration and analysis.
- C++ for native controller implementations where appropriate.
- ctypes for communication between Python and C++.
- YAML for experiment configuration.
- Controlled experiments using different controllers, throttle schedules,
  engine loads, target AFR values, noise levels and sensor delays.
- Evaluation based on tracking error, settling behaviour, overshoot, stability,
  robustness and execution reliability.
- Unit tests, integration tests and invariant checks.
- Repeated identical configurations to test reproducibility.
- A limitation stating that the simulator is not a replacement for a complete
  physical engine model or real-vehicle validation.

**Paragraph layout:**
Describe the project as an iterative software-engineering and experimental
process. Explain what will be investigated, how the system will be built, how
experiments will be controlled and how results will be evaluated. Explain why
each technology is appropriate rather than simply listing technologies.

5. Sources of Information / Bibliography (maximum 10 references)
----------------------------------------------------------------

Consider sources from these categories:

- ECU and engine-control systems.
- PID and feedback-control theory.
- Engine or air-fuel-ratio modelling.
- Sensor noise and measurement delay.
- Software testing and validation.
- Experimental design and performance evaluation.
- VED dataset documentation, if used.
- EngineFaultDB documentation, if used.
- Python ctypes documentation.
- CMake documentation.

Åström and Hägglund on PID controllers, a recognised automotive engine-control
textbook, a source on internal-combustion engine modelling, a control-system
simulation source, and a software-engineering testing textbook. Verify exact
publication details.

### Confirmed Sources

- [Åström and Hägglund, Advanced PID Control](https://www.isa.org/getmedia/fb0e41bc-e4f3-422a-9f67-b9bd31340e16/Advanced-PID-Control_AstromHagglund_Chapter1-Introduction.pdf)

### Sources currently being considered

- [Model-Based Control of Diesel Engines for Fuel Efficiency Optimization](https://www.researchgate.net/publication/300910047_Model-Based_Control_of_Diesel_Engines_for_Fuel_Efficiency_Optimization)
  — Find a better link.
- [Model-Based Control of Torque and Nitrogen Oxide Emissions](https://www.mdpi.com/1996-1073/14/4/1107)
  — Too specific.
- [ScienceDirect article](https://www.sciencedirect.com/science/article/abs/pii/S0967066122000223)
  — To Confirm and Find better link
- [Lambda and carbon-dioxide relationship figure](https://www.researchgate.net/figure/The-relation-between-air-fuel-equivalence-ratio-or-lambda-l-values-and-carbon-dioxide_fig7_336680338)
  — Find and cite the original source rather than the figure-hosting page.
- [Impact of Aggressive and Moderate Driving Intensity on Vehicle Air-Fuel Ratio Stability](https://www.researchgate.net/publication/404705501_Impact_of_Aggressive_and_Moderate_Driving_Intensity_on_Vehicle_Air-Fuel_Ratio_Stability)
  — Find the journal link.
- [Automotive Control Systems: For Engine, Driveline, and Vehicle](https://ftp.idu.ac.id/wp-content/uploads/ebook/tdg/ADVANCED%20ENGINE%20TECHNOLOGY%20AND%20PERFORMANCE/epdf.pub_automotive-control-systems-for-engine-driveline-an.pdf)
  — Find and use the official publisher link.

### Look further into

- [John B. Heywood, Internal Combustion Engine Fundamentals, 2nd edition](https://www.mheducation.com/highered/mhp/product/internal-combustion-engine-fundamentals-2e.html)
- [Katsuhiko Ogata, Modern Control Engineering, 5th edition](https://www.pearson.com/en-us/subject-catalog/p/modern-control-engineering/P200000003521/9780133002256)
- [Robert G. Sargent, Verification and Validation of Simulation Models](https://link.springer.com/article/10.1057/jos.2012.20)
- [Glenford J. Myers, Corey Sandler and Tom Badgett, The Art of Software Testing, 3rd edition](https://www.wiley.com/en-us/The+Art+of+Software+Testing%2C+3rd+Edition-p-x000565567)
- [Vehicle Energy Dataset (VED) research paper](https://arxiv.org/abs/1905.02081)
- [EngineFaultDB publication](https://doi.org/10.1109/ACCESS.2023.3331316)


6. Resources Required (maximum 100 words)
------------------------------------------

- Windows computer: development, simulation execution and data analysis.
- Python 3.11 or later: simulation, configuration and analysis.
- C++17 compiler and CMake: building native controller components.
- Visual Studio Code: source-code development and debugging.
- Python packages listed in requirements.txt: testing, numerical processing and
  plotting.
- Git repository: version control and experiment tracking.
- University computer: backup development environment and
  demonstration.
- Reference datasets: comparison and evaluation where appropriate.
- PDF/Word software: preparation of the TOR and final report.

**Note:** Mention that all software will be appropriately licensed and that the simulator
can be demonstrated using a university computer if the personal machine is
unavailable.

7. Deliverables (maximum 50 words)
-----------------------------------

- Configurable ECU engine simulator.
- Engine, controller and sensor source code.
- Python/C++ integration layer.
- Requirements and architecture documentation.
- Experiment configurations and generated datasets.
- Automated test suite and test results.
- Performance graphs and evaluation results.
- Final project report and user/developer documentation.

8. Assessment Criteria for Practical Computing Work (maximum 200 words)
------------------------------------------------------------------------

### Category 1: Fitness for purpose

- The simulator correctly executes the intended timestep data flow.
- Users can configure engine, controller, sensor and experiment parameters
  without changing source code.
- Controllers respond appropriately to changes in target AFR, throttle and
  load.
- The system records sufficient output data for later analysis.
- The simulator produces repeatable results for identical configurations.
- Sensor noise and delay produce measurable and expected changes in controller
  behaviour.

### Category 2: Build quality

- The architecture clearly separates engine, sensor, controller, simulation
  and analysis responsibilities.
- Python/C++ integration is reliable and handles errors appropriately.
- The implementation follows consistent naming, structure and documentation
  practices.
- Automated tests cover key components and integration paths.
- Results are supported by graphs, numerical metrics and documented
  experimental settings.
- The project demonstrates appropriate use of version control and reproducible
  configuration.

Evidence can include test results, requirements traceability, demonstration
scenarios, CSV output, performance metrics, graphs, code documentation and
comparison with reference or expected results. Each criterion should be
measurable. For example, state that a new experiment can be configured through
YAML and executed without source-code changes.

9. Project Plan
---------------

|Week|Objective|Dependencies|Expected Outcome|
|----|---------|------------|----------------|
|Week 1|xyz|xyz|xyz|


Dependencies:

- Requirements must be defined before finalising the architecture.
- The engine and simulation loop must exist before controller experiments can
  run.
- Controllers and sensors must be integrated before comparative testing.
- Testing should occur throughout development, not only at the end.
- Evaluation depends on stable experiments and recorded output data.
