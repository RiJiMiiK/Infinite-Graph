"""Constants used by the Qt GUI."""

GENERATION_STAGE_PROGRESS = {
    "Starting generation": 0,
    "Loading save file": 5,
    "Loading discarded combinations": 12,
    "Building graph model": 20,
    "Computing graph statistics": 35,
    "Computing missing combinations": 50,
    "Preparing graph structure": 58,
    "Checking layout cache": 59,
    "Initializing spring layout": 60,
    "Loading cached layout": 95,
    "Finalizing graph geometry": 96,
    "Preparing interface update": 100,
}
LAYOUT_PROGRESS_START = 60
LAYOUT_PROGRESS_END = 95
INTERFACE_PROGRESS = {
    "Updating graph view": 96,
    "Updating node table": 97,
    "Updating edge table": 98,
    "Updating statistics": 99,
    "Updating summary": 100,
}
LAYOUT_CACHE_VERSION = 2
