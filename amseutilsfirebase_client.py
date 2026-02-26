"""
Firebase Client for AMSE state management
Provides Firestore database and real-time capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1.base_query import FieldFilter

from amse.config import config

class FirebaseClient:
    """Firebase client singleton for state management"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True
    
    def _initialize(self) -> None:
        """Initialize Firebase connection"""
        try:
            if not config.firebase:
                raise ValueError("Firebase configuration not loaded")
            
            # Create credentials from config
            cred_dict = {
                "type": "service_account",
                "project_id": config.firebase.project_id,
                "private_key_id": config.firebase.private_key_id,
                "private_key": config.firebase.private_key.replace('\\n', '\n'),
                "client_email": config.firebase.client_email,
                "client_id": config.firebase.client_id,
                "auth_uri": config.firebase.auth_uri,
                "token_uri": config.firebase.token_uri,
                "auth_provider_x509_cert_url": config.firebase.auth_provider_x509_cert_url,
                "client_x509_cert_url": config.firebase.client_x509_cert_url
            }
            
            cred = credentials.Certificate(cred_dict)
            
            # Initialize app if not already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'projectId': config.firebase.project_id,
                    'databaseURL': f'https://{config.firebase.project_id}.firebaseio.com'
                })
            
            self.firestore = firestore.client()
            self.realtime_db = db.reference()
            logging.info("Firebase client initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize Firebase client: {e}")
            raise
    
    # --- Firestore Operations ---
    
    def save_model(self, model_data: Dict[str, Any]) -> str:
        """Save a trading model to Firestore"""
        try:
            model_ref = self.firestore.collection('models').document()
            model_data['created_at'] = datetime.utcnow()
            model_data['updated_at'] = datetime.utcnow()
            model_ref.set(model_data)
            model_id = model_ref.id
            logging.info(f"Model saved with ID: {model_id}")
            return model_id
        except Exception as e:
            logging.error(f"Failed to save model: {e}")
            raise
    
    def update_model_performance(self, model_id: str, performance: Dict[str, Any]) -> None:
        """Update model performance metrics"""
        try:
            model_ref = self.firestore.collection('models').document(model_id)
            update_data = {
                'performance': performance,
                'updated_at': datetime.utcnow(),
                'last_evaluated': datetime.utcnow()
            }
            model_ref.update(update_data