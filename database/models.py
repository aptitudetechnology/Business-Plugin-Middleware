"""
Database Models for Plugin Architecture
"""
from datetime import datetime
from typing import Dict, Any, Optional
import json


class Document:
    """Document model"""
    
    def __init__(self, file_path: str, filename: str, file_size: int, 
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = None  # Will be set by database
        self.file_path = file_path
        self.filename = filename
        self.file_size = file_size
        self.metadata = metadata or {}
        self.upload_date = datetime.utcnow()
        self.processed_date = None
        self.processing_status = 'pending'  # pending, processing, completed, failed
        self.processing_results = {}
        self.extracted_text = None
        self.document_type = None  # invoice, expense, receipt, etc.
        self.extracted_info = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'file_path': self.file_path,
            'filename': self.filename,
            'file_size': self.file_size,
            'metadata': self.metadata,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
            'processed_date': self.processed_date.isoformat() if self.processed_date else None,
            'processing_status': self.processing_status,
            'processing_results': self.processing_results,
            'extracted_text': self.extracted_text,
            'document_type': self.document_type,
            'extracted_info': self.extracted_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        doc = cls(
            file_path=data['file_path'],
            filename=data['filename'],
            file_size=data['file_size'],
            metadata=data.get('metadata', {})
        )
        doc.id = data.get('id')
        doc.upload_date = datetime.fromisoformat(data['upload_date']) if data.get('upload_date') else None
        doc.processed_date = datetime.fromisoformat(data['processed_date']) if data.get('processed_date') else None
        doc.processing_status = data.get('processing_status', 'pending')
        doc.processing_results = data.get('processing_results', {})
        doc.extracted_text = data.get('extracted_text')
        doc.document_type = data.get('document_type')
        doc.extracted_info = data.get('extracted_info', {})
        return doc


class PluginStatus:
    """Plugin status tracking model"""
    
    def __init__(self, plugin_name: str, version: str, status: str = 'inactive'):
        self.plugin_name = plugin_name
        self.version = version
        self.status = status  # active, inactive, failed, disabled
        self.last_updated = datetime.utcnow()
        self.error_message = None
        self.configuration = {}
        self.statistics = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'plugin_name': self.plugin_name,
            'version': self.version,
            'status': self.status,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'error_message': self.error_message,
            'configuration': self.configuration,
            'statistics': self.statistics
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginStatus':
        plugin_status = cls(
            plugin_name=data['plugin_name'],
            version=data['version'],
            status=data.get('status', 'inactive')
        )
        plugin_status.last_updated = datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
        plugin_status.error_message = data.get('error_message')
        plugin_status.configuration = data.get('configuration', {})
        plugin_status.statistics = data.get('statistics', {})
        return plugin_status


class ProcessingJob:
    """Processing job tracking model"""
    
    def __init__(self, document_id: int, plugin_name: str):
        self.id = None  # Will be set by database
        self.document_id = document_id
        self.plugin_name = plugin_name
        self.status = 'queued'  # queued, running, completed, failed
        self.created_date = datetime.utcnow()
        self.started_date = None
        self.completed_date = None
        self.result = {}
        self.error_message = None
        self.retry_count = 0
        self.max_retries = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'document_id': self.document_id,
            'plugin_name': self.plugin_name,
            'status': self.status,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'started_date': self.started_date.isoformat() if self.started_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'result': self.result,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingJob':
        job = cls(
            document_id=data['document_id'],
            plugin_name=data['plugin_name']
        )
        job.id = data.get('id')
        job.status = data.get('status', 'queued')
        job.created_date = datetime.fromisoformat(data['created_date']) if data.get('created_date') else None
        job.started_date = datetime.fromisoformat(data['started_date']) if data.get('started_date') else None
        job.completed_date = datetime.fromisoformat(data['completed_date']) if data.get('completed_date') else None
        job.result = data.get('result', {})
        job.error_message = data.get('error_message')
        job.retry_count = data.get('retry_count', 0)
        job.max_retries = data.get('max_retries', 3)
        return job


class SyncRecord:
    """Data synchronization tracking model"""
    
    def __init__(self, document_id: int, plugin_name: str, external_id: str = None):
        self.id = None  # Will be set by database
        self.document_id = document_id
        self.plugin_name = plugin_name
        self.external_id = external_id
        self.sync_status = 'pending'  # pending, synced, failed
        self.sync_date = None
        self.last_sync_attempt = datetime.utcnow()
        self.sync_data = {}
        self.error_message = None
        self.retry_count = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'document_id': self.document_id,
            'plugin_name': self.plugin_name,
            'external_id': self.external_id,
            'sync_status': self.sync_status,
            'sync_date': self.sync_date.isoformat() if self.sync_date else None,
            'last_sync_attempt': self.last_sync_attempt.isoformat() if self.last_sync_attempt else None,
            'sync_data': self.sync_data,
            'error_message': self.error_message,
            'retry_count': self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncRecord':
        sync_record = cls(
            document_id=data['document_id'],
            plugin_name=data['plugin_name'],
            external_id=data.get('external_id')
        )
        sync_record.id = data.get('id')
        sync_record.sync_status = data.get('sync_status', 'pending')
        sync_record.sync_date = datetime.fromisoformat(data['sync_date']) if data.get('sync_date') else None
        sync_record.last_sync_attempt = datetime.fromisoformat(data['last_sync_attempt']) if data.get('last_sync_attempt') else None
        sync_record.sync_data = data.get('sync_data', {})
        sync_record.error_message = data.get('error_message')
        sync_record.retry_count = data.get('retry_count', 0)
        return sync_record


class AuditLog:
    """Audit log model for tracking system activities"""
    
    def __init__(self, action: str, entity_type: str, entity_id: str, 
                 user: str = 'system', details: Optional[Dict[str, Any]] = None):
        self.id = None  # Will be set by database
        self.timestamp = datetime.utcnow()
        self.action = action  # create, update, delete, sync, process, etc.
        self.entity_type = entity_type  # document, plugin, configuration, etc.
        self.entity_id = entity_id
        self.user = user
        self.details = details or {}
        self.ip_address = None
        self.user_agent = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'user': self.user,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        audit_log = cls(
            action=data['action'],
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            user=data.get('user', 'system'),
            details=data.get('details', {})
        )
        audit_log.id = data.get('id')
        audit_log.timestamp = datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None
        audit_log.ip_address = data.get('ip_address')
        audit_log.user_agent = data.get('user_agent')
        return audit_log
