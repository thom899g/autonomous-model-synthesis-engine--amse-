"""
AMSE Configuration Management
Handles environment variables, Firebase configuration, and runtime settings.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration dataclass"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    client_x509_cert_url: str = "https://www.googleapis.com/robot/v1/metadata/x509/..."

@dataclass
class DataConfig:
    """Data source configuration"""
    ccxt_exchanges: list = None
    data_freshness_minutes: int = 5
    historical_days: int = 365
    max_symbols_per_exchange: int = 50

@dataclass
class ModelConfig:
    """Model synthesis configuration"""
    max_model_complexity: int = 10
    min_backtest_period_days: int = 30
    required_sharpe_ratio: float = 1.0
    max_drawdown_percent: float = 20.0
    genetic_population_size: int = 50

class Config:
    """Main configuration manager"""
    
    def __init__(self):
        self.firebase: Optional[FirebaseConfig] = None
        self.data: DataConfig = DataConfig()
        self.model: ModelConfig = ModelConfig()
        self._load_firebase_config()
        
    def _load_firebase_config(self) -> None:
        """Load Firebase configuration from environment"""
        try:
            firebase_json = os.getenv('FIREBASE_SERVICE_ACCOUNT_JSON')
            if firebase_json:
                config_dict = json.loads(firebase_json)
                self.firebase = FirebaseConfig(**config_dict)
            else:
                logging.warning("FIREBASE_SERVICE_ACCOUNT_JSON not found in environment")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Firebase config: {e}")
        except Exception as e:
            logging.error(f"Failed to load Firebase config: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'firebase': asdict(self.firebase) if self.firebase else None,
            'data': asdict(self.data),
            'model': asdict(self.model)
        }

# Global config instance
config = Config()