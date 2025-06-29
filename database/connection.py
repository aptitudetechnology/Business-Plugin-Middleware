"""
Database Connection and Management
"""
import sqlite3
import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from .models import Document, PluginStatus, ProcessingJob, SyncRecord, AuditLog


class DatabaseManager:
    """Database manager with plugin support"""
    
    def __init__(self, config: Any):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.connection = None
        self.db_type = config.get('database', 'type', 'sqlite')
        self.db_path = config.get('database', 'path', 'data/middleware.db')
        
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection and tables"""
        try:
            if self.db_type == 'sqlite':
                self._init_sqlite()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        # Create directory if it doesn't exist (unless using :memory:)
        if self.db_path != ':memory:':
            os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        
        # Create tables
        self._create_tables()
        
        self.logger.info(f"SQLite database initialized: {self.db_path}")
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                metadata TEXT,
                upload_date TEXT NOT NULL,
                processed_date TEXT,
                processing_status TEXT DEFAULT 'pending',
                processing_results TEXT,
                extracted_text TEXT,
                document_type TEXT,
                extracted_info TEXT
            )
        ''')
        
        # Plugin status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plugin_status (
                plugin_name TEXT PRIMARY KEY,
                version TEXT NOT NULL,
                status TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                error_message TEXT,
                configuration TEXT,
                statistics TEXT
            )
        ''')
        
        # Processing jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                plugin_name TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                created_date TEXT NOT NULL,
                started_date TEXT,
                completed_date TEXT,
                result TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Sync records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                plugin_name TEXT NOT NULL,
                external_id TEXT,
                sync_status TEXT DEFAULT 'pending',
                sync_date TEXT,
                last_sync_attempt TEXT NOT NULL,
                sync_data TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                user TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_processing_jobs_status ON processing_jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_records_status ON sync_records(sync_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)')
        
        self.connection.commit()
        self.logger.info("Database tables created successfully")
    
    def get_connection(self):
        """Get database connection"""
        return self.connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute a SELECT query and return results"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.rowcount
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last row ID"""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.lastrowid
    
    # Document operations
    def save_document(self, document: Document) -> int:
        """Save a document to the database"""
        import json
        
        query = '''
            INSERT INTO documents (
                file_path, filename, file_size, metadata, upload_date,
                processed_date, processing_status, processing_results,
                extracted_text, document_type, extracted_info
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            document.file_path,
            document.filename,
            document.file_size,
            json.dumps(document.metadata),
            document.upload_date.isoformat() if document.upload_date else None,
            document.processed_date.isoformat() if document.processed_date else None,
            document.processing_status,
            json.dumps(document.processing_results),
            document.extracted_text,
            document.document_type,
            json.dumps(document.extracted_info)
        )
        
        document_id = self.execute_insert(query, params)
        document.id = document_id
        return document_id
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID"""
        query = 'SELECT * FROM documents WHERE id = ?'
        rows = self.execute_query(query, (document_id,))
        
        if rows:
            return self._row_to_document(rows[0])
        return None
    
    def get_documents(self, limit: int = 100, offset: int = 0) -> List[Document]:
        """Get documents with pagination"""
        query = '''
            SELECT * FROM documents 
            ORDER BY upload_date DESC 
            LIMIT ? OFFSET ?
        '''
        rows = self.execute_query(query, (limit, offset))
        return [self._row_to_document(row) for row in rows]
    
    def _row_to_document(self, row: sqlite3.Row) -> Document:
        """Convert database row to Document object"""
        import json
        from datetime import datetime
        
        doc = Document(
            file_path=row['file_path'],
            filename=row['filename'],
            file_size=row['file_size'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
        
        doc.id = row['id']
        doc.upload_date = datetime.fromisoformat(row['upload_date']) if row['upload_date'] else None
        doc.processed_date = datetime.fromisoformat(row['processed_date']) if row['processed_date'] else None
        doc.processing_status = row['processing_status']
        doc.processing_results = json.loads(row['processing_results']) if row['processing_results'] else {}
        doc.extracted_text = row['extracted_text']
        doc.document_type = row['document_type']
        doc.extracted_info = json.loads(row['extracted_info']) if row['extracted_info'] else {}
        
        return doc
    
    # Plugin status operations
    def save_plugin_status(self, plugin_status: PluginStatus):
        """Save plugin status to database"""
        import json
        
        query = '''
            INSERT OR REPLACE INTO plugin_status (
                plugin_name, version, status, last_updated,
                error_message, configuration, statistics
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            plugin_status.plugin_name,
            plugin_status.version,
            plugin_status.status,
            plugin_status.last_updated.isoformat() if plugin_status.last_updated else None,
            plugin_status.error_message,
            json.dumps(plugin_status.configuration),
            json.dumps(plugin_status.statistics)
        )
        
        self.execute_update(query, params)
    
    def get_plugin_status(self, plugin_name: str) -> Optional[PluginStatus]:
        """Get plugin status by name"""
        query = 'SELECT * FROM plugin_status WHERE plugin_name = ?'
        rows = self.execute_query(query, (plugin_name,))
        
        if rows:
            return self._row_to_plugin_status(rows[0])
        return None
    
    def get_all_plugin_status(self) -> List[PluginStatus]:
        """Get all plugin statuses"""
        query = 'SELECT * FROM plugin_status ORDER BY plugin_name'
        rows = self.execute_query(query)
        return [self._row_to_plugin_status(row) for row in rows]
    
    def _row_to_plugin_status(self, row: sqlite3.Row) -> PluginStatus:
        """Convert database row to PluginStatus object"""
        import json
        from datetime import datetime
        
        plugin_status = PluginStatus(
            plugin_name=row['plugin_name'],
            version=row['version'],
            status=row['status']
        )
        
        plugin_status.last_updated = datetime.fromisoformat(row['last_updated']) if row['last_updated'] else None
        plugin_status.error_message = row['error_message']
        plugin_status.configuration = json.loads(row['configuration']) if row['configuration'] else {}
        plugin_status.statistics = json.loads(row['statistics']) if row['statistics'] else {}
        
        return plugin_status
    
    # Audit log operations
    def log_activity(self, action: str, entity_type: str, entity_id: str, 
                    user: str = 'system', details: Dict[str, Any] = None):
        """Log system activity"""
        audit_log = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user=user,
            details=details
        )
        
        self.save_audit_log(audit_log)
    
    def save_audit_log(self, audit_log: AuditLog):
        """Save audit log entry"""
        import json
        
        query = '''
            INSERT INTO audit_log (
                timestamp, action, entity_type, entity_id, user,
                details, ip_address, user_agent
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            audit_log.timestamp.isoformat() if audit_log.timestamp else None,
            audit_log.action,
            audit_log.entity_type,
            audit_log.entity_id,
            audit_log.user,
            json.dumps(audit_log.details),
            audit_log.ip_address,
            audit_log.user_agent
        )
        
        self.execute_insert(query, params)
    
    def get_audit_logs(self, limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Get audit logs with pagination"""
        query = '''
            SELECT * FROM audit_log 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        '''
        rows = self.execute_query(query, (limit, offset))
        return [self._row_to_audit_log(row) for row in rows]
    
    def _row_to_audit_log(self, row: sqlite3.Row) -> AuditLog:
        """Convert database row to AuditLog object"""
        import json
        from datetime import datetime
        
        audit_log = AuditLog(
            action=row['action'],
            entity_type=row['entity_type'],
            entity_id=row['entity_id'],
            user=row['user'],
            details=json.loads(row['details']) if row['details'] else {}
        )
        
        audit_log.id = row['id']
        audit_log.timestamp = datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
        audit_log.ip_address = row['ip_address']
        audit_log.user_agent = row['user_agent']
        
        return audit_log
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.close()
