#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
#![expect(rustdoc::missing_crate_level_docs)]

use eframe::egui;
use serde_json::Value;

const CONTROL_API_URL: &str = "http://127.0.0.1:8000";
const CONTROL_API_KEY: &str = "MakeThisBetter.txt";

fn request_json(method: reqwest::Method, path: &str, body: Option<Value>) -> Result<Value, String> {
    let client = reqwest::blocking::Client::new();
    let mut request = client
        .request(method, format!("{CONTROL_API_URL}{path}"))
        .header("Authorization", format!("Bearer {CONTROL_API_KEY}"))
        .header("Accept", "application/json");

    if let Some(body) = body {
        request = request.json(&body);
    }

    let response = request
        .send()
        .map_err(|err| format!("Request failed: {err}"))?;
    let status = response.status();
    if !status.is_success() {
        let error_body = response
            .text()
            .unwrap_or_else(|_| "Unable to read error body".to_owned());
        return Err(format!("Request failed with status {status}: {error_body}"));
    }

    response
        .json()
        .map_err(|err| format!("Invalid JSON response: {err}"))
}

struct MyApp {
    tab: usize,
    status_message: String,
    overview: Option<Value>,
    settings: Option<Value>,
    scripts: Option<Value>,
    results: Option<Value>,
    config_name: String,
    experiment_name: String,
    graph_type: String,
    script_name: String,
    echo_message: String,
    query_message: String,
    global_json: String,
    experiment_json: String,
    compare_enabled: bool,
}

impl Default for MyApp {
    fn default() -> Self {
        Self {
            tab: 0,
            status_message: "Ready. Start the control API, then refresh the overview.".to_owned(),
            overview: None,
            settings: None,
            scripts: None,
            results: None,
            config_name: String::new(),
            experiment_name: String::new(),
            graph_type: String::new(),
            script_name: "simulation".to_owned(),
            echo_message: "Hello from desktop".to_owned(),
            query_message: "Hello from query".to_owned(),
            global_json: "{\n  \"active_experiment\": \"default\"\n}".to_owned(),
            experiment_json: "{\n  \"scenario\": {}\n}".to_owned(),
            compare_enabled: false,
        }
    }
}

impl eframe::App for MyApp {
    fn ui(&mut self, ui: &mut egui::Ui, _frame: &mut eframe::Frame) {
        egui::Panel::top("header").show(ui, |ui| {
            ui.horizontal(|ui| {
                ui.heading("ECU Engine Simulator");
                ui.separator();
                ui.label("Control center");
            });
        });

        egui::Panel::left("navigation")
            .resizable(false)
            .show(ui, |ui| {
                ui.add_space(8.0);
                for (index, label) in ["Overview", "Settings", "Scripts", "Results", "Endpoints"]
                    .iter()
                    .enumerate()
                {
                    if ui.selectable_label(self.tab == index, *label).clicked() {
                        self.tab = index;
                    }
                }
                ui.separator();
                ui.small("API: http://127.0.0.1:8000");
                ui.small(format!("Status: {}", self.status_message));
            });

        egui::CentralPanel::default().show(ui, |ui| {
            egui::ScrollArea::vertical().show(ui, |ui| match self.tab {
                0 => self.overview_ui(ui),
                1 => self.settings_ui(ui),
                2 => self.scripts_ui(ui),
                3 => self.results_ui(ui),
                _ => self.endpoints_ui(ui),
            });
        });
    }
}

impl MyApp {
    fn call(&mut self, method: reqwest::Method, path: &str, body: Option<Value>) -> Option<Value> {
        match request_json(method, path, body) {
            Ok(value) => {
                self.status_message = "Request completed.".to_owned();
                Some(value)
            }
            Err(error) => {
                self.status_message = error;
                None
            }
        }
    }

    fn json_editor(ui: &mut egui::Ui, label: &str, value: &mut String) {
        ui.label(label);
        ui.add(
            egui::TextEdit::multiline(value)
                .desired_rows(8)
                .desired_width(f32::INFINITY),
        );
    }

    fn show_json(ui: &mut egui::Ui, label: &str, value: &Option<Value>) {
        if let Some(value) = value {
            egui::CollapsingHeader::new(label)
                .default_open(true)
                .show(ui, |ui| {
                    let mut formatted =
                        serde_json::to_string_pretty(value).unwrap_or_else(|_| value.to_string());
                    ui.add(
                        egui::TextEdit::multiline(&mut formatted)
                            .desired_rows(10)
                            .desired_width(f32::INFINITY),
                    );
                });
        } else {
            ui.label(format!("{label}: no data loaded"));
        }
    }

    fn overview_ui(&mut self, ui: &mut egui::Ui) {
        ui.heading("System overview");
        ui.label("Check connectivity and inspect the live control API state.");
        if ui.button("Refresh overview").clicked() {
            let mut overview = serde_json::Map::new();
            for (name, path) in [
                ("root", "/"),
                ("health", "/status"),
                ("version", "/version"),
            ] {
                if let Some(value) = self.call(reqwest::Method::GET, path, None) {
                    overview.insert(name.to_owned(), value);
                }
            }
            self.overview = Some(Value::Object(overview));
        }
        if let Some(overview) = &self.overview {
            if let Some(version) = overview.get("version").and_then(|v| v.get("version")) {
                ui.heading(format!("Control API {version}"));
            }
            if let Some(health) = overview.get("health").and_then(|v| v.get("status")) {
                ui.colored_label(egui::Color32::GREEN, format!("Service status: {health}"));
            }
        }
        Self::show_json(ui, "API response", &self.overview);
    }

    fn settings_ui(&mut self, ui: &mut egui::Ui) {
        ui.heading("Configuration");
        ui.horizontal(|ui| {
            ui.label("Config or experiment");
            ui.text_edit_singleline(&mut self.config_name);
            if ui.button("Load").clicked() {
                let query = if self.config_name.trim().is_empty() {
                    String::new()
                } else {
                    format!(
                        "?config_name={}",
                        urlencoding::encode(self.config_name.trim())
                    )
                };
                self.settings =
                    self.call(reqwest::Method::GET, &format!("/settings/{query}"), None);
            }
        });
        ui.separator();
        ui.collapsing("Global settings", |ui| {
            Self::json_editor(ui, "JSON mapping", &mut self.global_json);
            if ui.button("Update global settings").clicked() {
                match serde_json::from_str(&self.global_json) {
                    Ok(value) => {
                        self.settings = self.call(
                            reqwest::Method::POST,
                            "/settings/updateGlobal/",
                            Some(value),
                        )
                    }
                    Err(error) => self.status_message = format!("Invalid global JSON: {error}"),
                }
            }
        });
        ui.collapsing("Experiment operations", |ui| {
            ui.horizontal(|ui| {
                ui.label("Experiment name");
                ui.text_edit_singleline(&mut self.experiment_name);
            });
            Self::json_editor(ui, "Experiment sections", &mut self.experiment_json);
            ui.horizontal(|ui| {
                if ui.button("Create experiment").clicked() {
                    self.post_experiment("newExperiment");
                }
                if ui.button("Update experiment").clicked() {
                    self.post_experiment("update");
                }
                if ui.button("Compare settings").clicked() {
                    let path = format!(
                        "/settings/compare/?experiment_name={}",
                        urlencoding::encode(self.experiment_name.trim())
                    );
                    self.settings = self.call(reqwest::Method::GET, &path, None);
                }
            });
            ui.checkbox(&mut self.compare_enabled, "Comparison mode");
            if ui.button("Save comparison mode").clicked() {
                let path = format!("/settings/setCompare/{}", self.compare_enabled);
                self.settings = self.call(reqwest::Method::POST, &path, None);
            }
        });
        Self::show_json(ui, "Settings response", &self.settings);
    }

    fn post_experiment(&mut self, operation: &str) {
        let name = self.experiment_name.trim();
        if name.is_empty() {
            self.status_message = "Enter an experiment name first.".to_owned();
            return;
        }
        match serde_json::from_str(&self.experiment_json) {
            Ok(value) => {
                let path = format!("/settings/{operation}/{name}");
                self.settings = self.call(reqwest::Method::POST, &path, Some(value));
            }
            Err(error) => self.status_message = format!("Invalid experiment JSON: {error}"),
        }
    }

    fn scripts_ui(&mut self, ui: &mut egui::Ui) {
        ui.heading("Simulation scripts");
        ui.horizontal(|ui| {
            if ui.button("Load available scripts").clicked() {
                self.scripts = self.call(reqwest::Method::GET, "/scripts/", None);
            }
            if ui.button("Run all").clicked() {
                self.scripts = self.call(reqwest::Method::GET, "/scripts/runall/", None);
            }
        });
        ui.horizontal(|ui| {
            ui.label("Script");
            ui.text_edit_singleline(&mut self.script_name);
            if ui.button("Run selected").clicked() {
                let path = format!(
                    "/scripts/run/{}",
                    urlencoding::encode(self.script_name.trim())
                );
                self.scripts = self.call(reqwest::Method::GET, &path, None);
            }
        });
        if let Some(value) = &self.scripts {
            self.render_final_record(ui, value);
        }
        Self::show_json(ui, "Script response", &self.scripts);
    }

    fn results_ui(&mut self, ui: &mut egui::Ui) {
        ui.heading("Results and visualisation");
        ui.horizontal(|ui| {
            ui.label("Experiment");
            ui.text_edit_singleline(&mut self.experiment_name);
            ui.label("Graph filter");
            ui.text_edit_singleline(&mut self.graph_type);
        });
        ui.horizontal_wrapped(|ui| {
            if ui.button("Summary").clicked() {
                self.results = self.get_results("/results/");
            }
            if ui.button("Experiment files").clicked() {
                self.results = self.get_results("/results/experiments/");
            }
            if ui.button("CSV preview").clicked() {
                self.results = self.get_results("/results/csv/");
            }
            if ui.button("Graph files").clicked() {
                let mut path = "/results/graph/".to_owned();
                let mut separator = '?';
                if !self.experiment_name.trim().is_empty() {
                    path.push_str(&format!(
                        "{separator}experiment_name={}",
                        urlencoding::encode(self.experiment_name.trim())
                    ));
                    separator = '&';
                }
                if !self.graph_type.trim().is_empty() {
                    path.push_str(&format!(
                        "{separator}graph_type={}",
                        urlencoding::encode(self.graph_type.trim())
                    ));
                }
                self.results = self.call(reqwest::Method::GET, &path, None);
            }
        });
        if let Some(value) = &self.results {
            self.render_csv_table(ui, value);
            Self::show_json(ui, "Result metadata", &self.results);
        } else {
            ui.label(
                "Load a result view to inspect experiments, CSV rows, and generated graph paths.",
            );
        }
    }

    fn get_results(&mut self, base_path: &str) -> Option<Value> {
        let path = if self.experiment_name.trim().is_empty() {
            base_path.to_owned()
        } else {
            format!(
                "{base_path}?experiment_name={}",
                urlencoding::encode(self.experiment_name.trim())
            )
        };
        self.call(reqwest::Method::GET, &path, None)
    }

    fn endpoints_ui(&mut self, ui: &mut egui::Ui) {
        ui.heading("Control endpoints");
        ui.label("Direct access to the remaining diagnostic and secured API routes.");
        ui.horizontal(|ui| {
            ui.label("Path message");
            ui.text_edit_singleline(&mut self.echo_message);
            if ui.button("Echo path").clicked() {
                let path = format!("/echo/path/{}", urlencoding::encode(&self.echo_message));
                self.overview = self.call(reqwest::Method::GET, &path, None);
            }
        });
        ui.horizontal(|ui| {
            ui.label("Query message");
            ui.text_edit_singleline(&mut self.query_message);
            if ui.button("Echo query").clicked() {
                let path = format!(
                    "/echo/query/?message={}",
                    urlencoding::encode(&self.query_message)
                );
                self.overview = self.call(reqwest::Method::GET, &path, None);
            }
        });
        ui.horizontal(|ui| {
            if ui.button("Secure data").clicked() {
                self.overview = self.call(reqwest::Method::GET, "/secure-data/", None);
            }
            if ui.button("Secure info").clicked() {
                self.overview = self.call(reqwest::Method::GET, "/other/secure-info/", None);
            }
        });
        Self::show_json(ui, "Endpoint response", &self.overview);
    }

    fn render_final_record(&self, ui: &mut egui::Ui, value: &Value) {
        let record = value
            .get("final_record")
            .or_else(|| value.get("results").and_then(|v| v.get("final_record")));
        let Some(record) = record.and_then(Value::as_object) else {
            return;
        };
        ui.separator();
        ui.heading("Latest simulation metrics");
        ui.horizontal_wrapped(|ui| {
            for key in [
                "air_fuel_ratio",
                "measured_air_fuel_ratio",
                "engine_speed_rpm",
                "torque",
                "fuel_injection",
            ] {
                if let Some(number) = record.get(key).and_then(Value::as_f64) {
                    ui.group(|ui| {
                        ui.label(key.replace('_', " "));
                        ui.strong(format!("{number:.3}"));
                    });
                }
            }
        });
    }

    fn render_csv_table(&self, ui: &mut egui::Ui, value: &Value) {
        let files = value
            .get("csv_files")
            .or_else(|| value.get("results"))
            .and_then(Value::as_array);
        let Some(files) = files else { return };
        for file in files {
            let rows = file
                .get("rows")
                .or_else(|| file.get("csv").and_then(|v| v.get("rows")))
                .and_then(Value::as_array);
            let Some(rows) = rows else { continue };
            if rows.is_empty() {
                continue;
            }
            ui.separator();
            ui.label(
                file.get("path")
                    .and_then(Value::as_str)
                    .unwrap_or("CSV preview"),
            );
            let columns: Vec<String> = rows[0]
                .as_object()
                .map(|row| row.keys().cloned().collect())
                .unwrap_or_default();
            egui::Grid::new("csv-preview").striped(true).show(ui, |ui| {
                for column in &columns {
                    ui.strong(column);
                }
                ui.end_row();
                for row in rows.iter().take(10) {
                    for column in &columns {
                        ui.label(
                            row.get(column)
                                .map(|v| v.to_string())
                                .unwrap_or_default()
                                .trim_matches('"'),
                        );
                    }
                    ui.end_row();
                }
            });
        }
    }
}

fn main() -> eframe::Result {
    env_logger::init();
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([1100.0, 760.0]),
        ..Default::default()
    };
    eframe::run_native(
        "ECU Engine Simulator Control Center",
        options,
        Box::new(|_cc| Ok(Box::<MyApp>::default())),
    )
}
