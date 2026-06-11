def get_settings(config_name: str | None = None):
    if config_name is None:
        return {"settings": "Here are all the current settings!"}
    return {"settings": f"Here are the current {config_name} settings!"}

def create_new_experiment(experiment_name: str, experiment_settings: dict[str, dict]):
    return {"experiment": experiment_name, "settings": experiment_settings, "message": "Experiment created successfully!"}

def update_settings(experiment_name: str, new_settings: dict[str, dict]):
    return {"experiment": experiment_name, "new_settings": new_settings, "message": "Settings updated successfully!"}

def update_global_settings(new_settings: dict[str, str]):
    return {"new_settings": new_settings, "message": "Global settings updated successfully!"}

def compare_settings(experiment_name: str):
    return {"compare": True}

def set_compare(value: bool):
    return {"compare": value}