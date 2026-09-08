#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")] // hide console window on Windows in release
#![expect(rustdoc::missing_crate_level_docs)] // it's an example

use eframe::egui;

const CONTROL_API_URL: &str = "http://127.0.0.1:8000/settings/";
const CONTROL_API_KEY: &str = "MakeThisBetter.txt";

fn get_settings() -> Result<String, String> {
    let response = reqwest::blocking::Client::new()
        .get(CONTROL_API_URL)
        .header("Authorization", format!("Bearer {}", CONTROL_API_KEY))
        .send()
        .map_err(|err| format!("Request failed: {err}"))?;

    let status = response.status();
    if !status.is_success() {
        let error_body = response
            .text()
            .unwrap_or_else(|_| "Unable to read error body".to_string());
        return Err(format!(
            "Settings request failed with status {}: {}",
            status,
            error_body
        ));
    }

    response
        .text()
        .map_err(|err| format!("Failed to read response: {err}"))
}

struct MyApp {
    name: String,
    age: u32,
    settings: String,
}

impl Default for MyApp {
    fn default() -> Self {
        Self {
            name: "Arthur".to_owned(),
            age: 42,
            settings: "No settings loaded yet.".to_owned(),
        }
    }
}

impl eframe::App for MyApp {
    fn ui(&mut self, ui: &mut egui::Ui, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ui, |ui| {
            ui.heading("My egui Application");
            ui.horizontal(|ui| {
                let name_label = ui.label("Your name: ");
                ui.text_edit_singleline(&mut self.name)
                    .labelled_by(name_label.id);
            });
            ui.add(egui::Slider::new(&mut self.age, 0..=120).text("age"));
            if ui.button("Increment").clicked() {
                self.age += 1;
            }
            if ui.button("Load settings").clicked() {
                match get_settings() {
                    Ok(settings) => {
                        self.settings = settings;
                    }
                    Err(error) => {
                        self.settings = format!("Error: {error}");
                    }
                }
            }
            ui.label(format!("Hello '{}', age {}", self.name, self.age));
            ui.separator();
            ui.heading("Settings");
            ui.add(egui::TextEdit::multiline(&mut self.settings).desired_rows(12));
        });
    }
}

fn main() -> eframe::Result {
    env_logger::init(); // Log to stderr (if you run with `RUST_LOG=debug`).
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([320.0, 240.0]),
        ..Default::default()
    };
    eframe::run_native(
        "My egui App",
        options,
        Box::new(|_cc| Ok(Box::<MyApp>::default())),
    )
}