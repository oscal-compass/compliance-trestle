from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, BaseSettings, Field


class Settings(BaseSettings):
    tmp_dir: str = './tmp'
    GITHUB_TOKENS: Optional[Dict[str, str]] = {}
    # [catalog]
    # decomposition_rules: List[str] = ['catalog.groups.*.controls.*']
    # create_number_of_groups: int = 2
    # create_number_of_controls: int = 2
    # [profile]
    # decomposition_rules: List[str] = []
    # [target-definition]
    # decomposition_rules: List[str] = ['target-definition.targets.*.target-control-implementations.*']
    # create_number_of_targets: int = 2
    # create_number_of_target_control_implementations: int = 2
    # [component-definition]
    # decomposition_rules: List[str] = []
    # [system-security-plan]
    # decomposition_rules: List[str] = []
    # [assessment-plan]
    # decomposition_rules: List[str] = []
    # [assessment-result]
    # decomposition_rules: List[str] = []
    # [plan-of-action-and-milestone]
    # decomposition_rules: List[str] = []

    class Config:
        """Loads the dotenv file."""
        env_file: str = ".env"
        env_file_encoding: str = 'utf-8'
        env_prefix: str = "TRESTLE_"