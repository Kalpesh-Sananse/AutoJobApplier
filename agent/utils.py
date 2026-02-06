
import logging
import yaml
import os

def setup_logger(log_level="INFO"):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agent.log')
        ]
    )
    return logging.getLogger("AutoJobApplier")


def get_project_root():
    # Assumes utils.py is in agent/ folder
    return os.path.dirname(os.path.abspath(__file__))

def load_config(config_path="config.yaml"):
    # Try current dir first
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Try relative to this file
    abs_path = os.path.join(get_project_root(), config_path)
    if os.path.exists(abs_path):
        with open(abs_path, 'r') as f:
            return yaml.safe_load(f)
            
    raise FileNotFoundError(f"Config file not found at {config_path} or {abs_path}")

def load_secrets(secrets_path="secrets.yaml"):
    # Try current dir first
    if os.path.exists(secrets_path):
        with open(secrets_path, 'r') as f:
            return yaml.safe_load(f)

    # Try relative to this file
    abs_path = os.path.join(get_project_root(), secrets_path)
    if os.path.exists(abs_path):
        with open(abs_path, 'r') as f:
            return yaml.safe_load(f)

    raise FileNotFoundError(f"Secrets file not found at {secrets_path}. Please create one based on the template.")
