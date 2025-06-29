"""
Document Processor with Plugin Support
"""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from core.base_plugin import ProcessingPlugin
from core.exceptions import DocumentProcessingError, ProcessingError


class DocumentProcessor:
    """Main document processor that coordinates with processing plugins"""
    
    def __init__(self, config: Any, db_manager: Any, plugin_manager: Any = None):
        self.config = config
        self.db_manager = db_manager
        self.plugin_manager = plugin_manager
        self.logger = logging.getLogger(__name__)
        
        # Processing configuration
        self.upload_folder = config.get('processing', 'upload_folder', 'uploads')
        self.max_file_size = int(config.get('processing', 'max_file_size', '10485760'))  # 10MB
        self.allowed_extensions = set(config.get('processing', 'allowed_extensions', 
                                                'pdf,png,jpg,jpeg,tiff,txt').split(','))
        
        # Ensure upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def get_processing_plugins(self) -> List[ProcessingPlugin]:
        """Get all available processing plugins"""
        if self.plugin_manager:
            return self.plugin_manager.get_processing_plugins()
        return []
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return ('.' in filename and 
                filename.rsplit('.', 1)[1].lower() in self.allowed_extensions)
    
    def process_document(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a document using available processing plugins
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata about the document
            
        Returns:
            Dictionary with processing results
        """
        if metadata is None:
            metadata = {}
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise DocumentProcessingError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            if file_size > self.max_file_size:
                raise DocumentProcessingError(f"File too large: {file_size} bytes")
            
            filename = os.path.basename(file_path)
            if not self.is_allowed_file(filename):
                raise DocumentProcessingError(f"File type not allowed: {filename}")
            
            # Prepare processing context
            processing_context = {
                'file_path': file_path,
                'filename': filename,
                'file_size': file_size,
                'metadata': metadata,
                'config': self.config,
                'db_manager': self.db_manager
            }
            
            # Get processing plugins
            processing_plugins = self.get_processing_plugins()
            
            if not processing_plugins:
                self.logger.warning("No processing plugins available")
                return {
                    'success': False,
                    'error': 'No processing plugins available',
                    'file_path': file_path,
                    'metadata': metadata
                }
            
            # Process document with each plugin
            results = {
                'success': True,
                'file_path': file_path,
                'filename': filename,
                'file_size': file_size,
                'metadata': metadata,
                'processing_results': {}
            }
            
            for plugin in processing_plugins:
                try:
                    if self._plugin_supports_format(plugin, filename):
                        self.logger.info(f"Processing with plugin: {plugin.name}")
                        plugin_result = plugin.process_document(file_path, processing_context)
                        results['processing_results'][plugin.name] = plugin_result
                        
                        # Merge any additional metadata
                        if 'metadata' in plugin_result:
                            results['metadata'].update(plugin_result['metadata'])
                    
                except Exception as e:
                    self.logger.error(f"Plugin {plugin.name} failed to process document: {e}")
                    results['processing_results'][plugin.name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Save to database if configured
            if self.db_manager:
                try:
                    self._save_processing_results(results)
                except Exception as e:
                    self.logger.error(f"Failed to save processing results: {e}")
                    results['database_error'] = str(e)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
                'metadata': metadata
            }
    
    def _plugin_supports_format(self, plugin: ProcessingPlugin, filename: str) -> bool:
        """Check if plugin supports the file format"""
        try:
            supported_formats = plugin.supported_formats()
            if not supported_formats:
                return True  # Plugin supports all formats
            
            file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            return file_ext in supported_formats
        except Exception:
            return True  # Default to True if plugin doesn't implement this method
    
    def _save_processing_results(self, results: Dict[str, Any]):
        """Save processing results to database"""
        # This would depend on your database schema
        # For now, just log the action
        self.logger.info(f"Saving processing results for: {results['filename']}")
        # TODO: Implement actual database saving logic
    
    def get_supported_formats(self) -> List[str]:
        """Get all supported file formats from all plugins"""
        formats = set(self.allowed_extensions)
        
        for plugin in self.get_processing_plugins():
            try:
                plugin_formats = plugin.supported_formats()
                formats.update(plugin_formats)
            except Exception as e:
                self.logger.warning(f"Failed to get supported formats from {plugin.name}: {e}")
        
        return list(formats)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        plugins = self.get_processing_plugins()
        
        return {
            'total_plugins': len(plugins),
            'active_plugins': [p.name for p in plugins if p.enabled],
            'supported_formats': self.get_supported_formats(),
            'max_file_size': self.max_file_size,
            'upload_folder': self.upload_folder
        }
    
    def process_batch(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Process multiple documents
        
        Args:
            file_paths: List of file paths to process
            metadata: Optional metadata to apply to all documents
            
        Returns:
            List of processing results
        """
        results = []
        
        for file_path in file_paths:
            try:
                result = self.process_document(file_path, metadata)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'file_path': file_path
                })
        
        return results
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            temp_dir = Path(self.upload_folder) / 'temp'
            if temp_dir.exists():
                import time
                current_time = time.time()
                max_age_seconds = max_age_hours * 3600
                
                for file_path in temp_dir.iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_path.unlink()
                            self.logger.info(f"Cleaned up temporary file: {file_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup temporary files: {e}")
