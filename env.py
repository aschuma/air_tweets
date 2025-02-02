#!/usr/bin/env python3
import os
import configparser
from typing import Optional, Dict, Any, Union
from pathlib import Path

def mask_sensitive_value(value: str, show_chars: int = 3) -> str:
    """
    Mask sensitive information showing only the first few characters.
    Returns "..." if the value is empty or None.
    """
    if not value:
        return "..."
    return f"{value[:show_chars]}..." if len(value) > show_chars else value

def read_template_file(template_path: str) -> str:
    """
    Read a template file and return its contents with preserved newlines
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Template file not found: {template_path}")
        return ""

def get_config_value(env_key: str, config: configparser.ConfigParser, 
                    section: str, key: str, default: Any = None, 
                    value_type: Union[type, None] = str) -> Any:
    """
    Helper function to get configuration value from environment or config file
    with type conversion
    """
    # Get value from environment or config file with fallback
    value = os.getenv(env_key, config.get(section, key, fallback=str(default)))
    
    # Handle empty string for optional values
    if value == '' and default is None:
        return None
    
    # Convert value to specified type
    if value_type is bool:
        return str(value).lower() in ('true', '1', 'yes', 'on')
    elif value_type is int:
        return int(value)
    return value

def load_configuration(config_path: str = 'config/config.ini') -> Dict[str, Any]:
    """
    Load configuration from INI file with environment variable overrides
    """
    # Read configuration from file
    config = configparser.ConfigParser(interpolation=None)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config.read(config_path)
    print(f"Configuration loaded from {config_path} and env variables")

    # Get the base directory for template files
    config_dir = Path(config_path).parent

    # Build configuration dictionary using helper function
    conf = {
        # Storage configuration
        'conf_storage': get_config_value(
            'CONF_STORAGE', config, 'storage', 'storage_path', 
            default="/tmp/.air_tweet"),

        # Sensor configuration
        'conf_particle_sensor_id': get_config_value(
            'CONF_PARTICLE_SENSOR_ID', config, 'sensors', 'particle_sensor_id',
            default=90887, value_type=int),
        'conf_temperature_sensor_id': get_config_value(
            'CONF_TEMPERATURE_SENSOR_ID', config, 'sensors', 'temperature_sensor_id',
            default=None),

        # URL configuration
        'conf_url_pm_sensor': get_config_value(
            'CONF_URL_PM_SENSOR', config, 'urls', 'pm_sensor_url'),
        'conf_url_th_sensor': get_config_value(
            'CONF_URL_TH_SENSOR', config, 'urls', 'th_sensor_url'),

        # Template parameter configuration
        'conf_luftdaten_graph_url': get_config_value(
            'CONF_LUFTDATEN_GRAPH_URL', config, 'template_parameter', 'luftdaten_graph_url'),
        'conf_luftdaten_graph_mime_type': get_config_value(
            'CONF_LUFTDATEN_GRAPH_MIME_TYPE', config, 'template_parameter', 'luftdaten_graph_mime_type'),
        'conf_luftdaten_map_url': get_config_value(
            'CONF_LUFTDATEN_MAP_URL', config, 'template_parameter', 'luftdaten_map_url'),

        # Limits configuration
        'conf_limit_pm_10_0': get_config_value(
            'CONF_LIMIT_PM_10_0', config, 'limits', 'limit_pm_10_0',
            default=50, value_type=int),
        'conf_quiet_period_in_hours': get_config_value(
            'CONF_QUIET_PERIOD_IN_HOURS', config, 'limits', 'quiet_period_in_hours',
            default=6, value_type=int),

        # Mastodon configuration
        'mastodon_enabled': get_config_value(
            'MASTODON_ENABLED', config, 'mastodon', 'enabled',
            default=True, value_type=bool),
        'mastodon_api_base_url': get_config_value(
            'MASTODON_API_BASE_URL', config, 'mastodon', 'api_base_url'),
        'mastodon_access_token': get_config_value(
            'MASTODON_ACCESS_TOKEN', config, 'mastodon', 'access_token'),
        'mastodon_template_file': config.get('mastodon', 'template_file'),

        # Bluesky configuration
        'bluesky_enabled': get_config_value(
            'BLUESKY_ENABLED', config, 'bluesky', 'enabled',
            default=False, value_type=bool),
        'bluesky_handle': get_config_value(
            'BLUESKY_HANDLE', config, 'bluesky', 'handle'),
        'bluesky_password': get_config_value(
            'BLUESKY_PASSWORD', config, 'bluesky', 'password'),
        'bluesky_template_file': config.get('bluesky', 'template_file'),
    }

    # Add template contents after getting template file names
    mastodon_template_path = config_dir.parent / conf['mastodon_template_file']
    bluesky_template_path = config_dir.parent / conf['bluesky_template_file']
    
    conf['MASTODON_TEMPLATE_CONTENT'] = read_template_file(str(mastodon_template_path))
    conf['BLUESKY_TEMPLATE_CONTENT'] = read_template_file(str(bluesky_template_path))

    # Log configuration
    def log_configuration():
        print("""
    # Storage Configuration
    CONF_STORAGE="{}"

    # Sensor Configuration
    CONF_PARTICLE_SENSOR_ID={}
    CONF_TEMPERATURE_SENSOR_ID="{}"

    # URL Configuration
    CONF_URL_PM_SENSOR="{}"
    CONF_URL_TH_SENSOR="{}"

    # Template Parameter Configuration
    CONF_LUFTDATEN_GRAPH_URL="{}"
    CONF_LUFTDATEN_GRAPH_MIME_TYPE="{}"
    CONF_LUFTDATEN_MAP_URL="{}"

    # Limits Configuration
    CONF_LIMIT_PM_10_0={}
    CONF_QUIET_PERIOD_IN_HOURS={}

    # Mastodon Configuration
    MASTODON_ENABLED={}
    MASTODON_API_BASE_URL="{}"
    MASTODON_ACCESS_TOKEN="{}"
    MASTODON_TEMPLATE_FILE="{}"
    CALCULATED MASTODON_TEMPLATE_CONTENT='''{}'''

    # Bluesky Configuration
    BLUESKY_ENABLED={}
    BLUESKY_HANDLE="{}"
    BLUESKY_PASSWORD="{}"
    BLUESKY_TEMPLATE_FILE="{}"
    CALCULATED BLUESKY_TEMPLATE_CONTENT='''{}'''
    """.format(
            conf['conf_storage'],
            conf['conf_particle_sensor_id'],
            conf['conf_temperature_sensor_id'] if conf['conf_temperature_sensor_id'] else '',
            conf['conf_url_pm_sensor'],
            conf['conf_url_th_sensor'],
            conf['conf_luftdaten_graph_url'],
            conf['conf_luftdaten_graph_mime_type'],
            conf['conf_luftdaten_map_url'],
            conf['conf_limit_pm_10_0'],
            conf['conf_quiet_period_in_hours'],
            str(conf['mastodon_enabled']).lower(),
            conf['mastodon_api_base_url'],
            mask_sensitive_value(conf['mastodon_access_token']),
            conf['mastodon_template_file'],
            conf['MASTODON_TEMPLATE_CONTENT'],
            str(conf['bluesky_enabled']).lower(),
            conf['bluesky_handle'],
            mask_sensitive_value(conf['bluesky_password']),
            conf['bluesky_template_file'],
            conf['BLUESKY_TEMPLATE_CONTENT']
        ))

    log_configuration()
    return conf

if __name__ == '__main__':
    config = load_configuration()