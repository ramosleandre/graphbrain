"""Foundation pack loading utilities."""

import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_foundation_pack_file(api, filepath: str, format: str = "auto") -> Dict[str, Any]:
    """
    Load a foundation pack from YAML or JSON file.

    Args:
        api: GraphbrainAPI instance
        filepath: Path to YAML or JSON file
        format: File format ("yaml", "json", or "auto" to detect)

    Returns:
        BulkResult dict with load statistics
    """
    path = Path(filepath)

    # Auto-detect format
    if format == "auto":
        format = "yaml" if path.suffix in ['.yaml', '.yml'] else "json"

    # Load file
    if format == "yaml":
        try:
            import yaml
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        except ImportError:
            raise ImportError("PyYAML required for YAML files: pip install pyyaml")
    else:
        with open(path, 'r') as f:
            data = json.load(f)

    # Extract edges
    edges = data.get('rules', data.get('edges', []))

    # Support both "facts" and structured edges
    if 'facts' in data:
        for fact in data['facts']:
            edges.append(fact)

    # Bulk add
    result = api.bulk_add(edges, upsert=True)

    logger.info(f"Loaded foundation pack from {filepath}: "
               f"{result['inserted']} inserted, {result['updated']} updated")

    return result
