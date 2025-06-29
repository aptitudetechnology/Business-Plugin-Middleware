"""
Modular Routes with Plugin Support
"""
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
import logging
from typing import Any, Dict


def create_web_blueprint(config: Any, db_manager: Any, doc_processor: Any, plugin_manager: Any = None) -> Blueprint:
    """Create web interface blueprint with plugin support"""
    
    web = Blueprint('web', __name__)
    logger = logging.getLogger(__name__)
    
    @web.route('/')
    def dashboard():
        """Main dashboard with plugin information"""
        try:
            # Get plugin status
            plugin_status = {}
            menu_items = []
            
            if plugin_manager:
                plugin_status = plugin_manager.get_plugin_status()
                
                # Get menu items from web plugins
                for plugin in plugin_manager.get_web_plugins():
                    try:
                        plugin_menu_items = plugin.get_menu_items()
                        for item in plugin_menu_items:
                            item['plugin'] = plugin.name
                            menu_items.append(item)
                    except Exception as e:
                        logger.warning(f"Failed to get menu items from {plugin.name}: {e}")
            
            # Get processing stats
            processing_stats = {}
            if doc_processor:
                try:
                    processing_stats = doc_processor.get_processing_stats()
                except Exception as e:
                    logger.error(f"Failed to get processing stats: {e}")
            
            return render_template('dashboard.html', 
                                 plugin_status=plugin_status,
                                 menu_items=menu_items,
                                 processing_stats=processing_stats)
        
        except Exception as e:
            logger.error(f"Dashboard error: {e}")
            return render_template('errors/500.html'), 500
    
    @web.route('/plugins')
    def plugins():
        """Plugin management page"""
        try:
            plugin_info = {}
            
            if plugin_manager:
                plugin_info = plugin_manager.get_plugin_status()
                
                # Add detailed plugin information
                for plugin_name, plugin in plugin_manager._plugins.items():
                    plugin_info['plugins'][plugin_name].update({
                        'type': plugin.__class__.__name__,
                        'dependencies': plugin.dependencies,
                        'config': plugin.config
                    })
            
            return render_template('plugins.html', plugin_info=plugin_info)
        
        except Exception as e:
            logger.error(f"Plugins page error: {e}")
            return render_template('errors/500.html'), 500
    
    @web.route('/documents')
    def documents():
        """Document management page"""
        try:
            # Get recent documents from database
            recent_documents = []
            if db_manager:
                try:
                    # This would depend on your database schema
                    # For now, just return empty list
                    pass
                except Exception as e:
                    logger.error(f"Failed to get recent documents: {e}")
            
            # Get processing stats
            processing_stats = {}
            if doc_processor:
                try:
                    processing_stats = doc_processor.get_processing_stats()
                except Exception as e:
                    logger.error(f"Failed to get processing stats: {e}")
            
            return render_template('documents.html', 
                                 recent_documents=recent_documents,
                                 processing_stats=processing_stats)
        
        except Exception as e:
            logger.error(f"Documents page error: {e}")
            return render_template('errors/500.html'), 500
    
    @web.route('/upload', methods=['GET', 'POST'])
    def upload_document():
        """Document upload page and handler"""
        if request.method == 'GET':
            processing_stats = {}
            if doc_processor:
                try:
                    processing_stats = doc_processor.get_processing_stats()
                except Exception as e:
                    logger.error(f"Failed to get processing stats: {e}")
            
            return render_template('upload.html', processing_stats=processing_stats)
        
        try:
            # Handle file upload
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not doc_processor:
                return jsonify({'error': 'Document processor not available'}), 500
            
            if not doc_processor.is_allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Save uploaded file
            import os
            import uuid
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(doc_processor.upload_folder, filename)
            file.save(file_path)
            
            # Process the document
            metadata = {
                'uploaded_by': request.form.get('uploaded_by', 'anonymous'),
                'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
                'notes': request.form.get('notes', '')
            }
            
            result = doc_processor.process_document(file_path, metadata)
            
            if result['success']:
                return jsonify({
                    'success': True,
                    'message': 'Document processed successfully',
                    'result': result
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Processing failed')
                }), 500
        
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @web.route('/config')
    def configuration():
        """Configuration page"""
        try:
            # Get current configuration (sanitized)
            config_data = {}
            if config:
                # Only show non-sensitive configuration
                config_data = {
                    'web_interface': {
                        'host': config.get('web_interface', 'host', '0.0.0.0'),
                        'port': config.get('web_interface', 'port', '5000'),
                        'debug': config.getboolean('web_interface', 'debug', False)
                    },
                    'processing': {
                        'upload_folder': config.get('processing', 'upload_folder', 'uploads'),
                        'max_file_size': config.get('processing', 'max_file_size', '10485760'),
                        'allowed_extensions': config.get('processing', 'allowed_extensions', 'pdf,png,jpg,jpeg,tiff,txt')
                    }
                }
            
            return render_template('config.html', config_data=config_data)
        
        except Exception as e:
            logger.error(f"Configuration page error: {e}")
            return render_template('errors/500.html'), 500
    
    return web


def create_api_blueprint(config: Any, db_manager: Any, doc_processor: Any, plugin_manager: Any = None) -> Blueprint:
    """Create API blueprint with plugin support"""
    
    api = Blueprint('api', __name__)
    logger = logging.getLogger(__name__)
    
    @api.route('/health')
    def health():
        """API health check"""
        health_data = {
            'status': 'healthy',
            'timestamp': import_datetime().utcnow().isoformat(),
            'components': {}
        }
        
        # Check database
        if db_manager:
            try:
                # This would depend on your database implementation
                health_data['components']['database'] = 'healthy'
            except Exception as e:
                health_data['components']['database'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
        
        # Check plugins
        if plugin_manager:
            try:
                plugin_status = plugin_manager.get_plugin_status()
                health_data['components']['plugins'] = {
                    'total': plugin_status['total_discovered'],
                    'initialized': plugin_status['initialized'],
                    'failed': plugin_status['failed']
                }
                
                if plugin_status['failed'] > 0:
                    health_data['status'] = 'degraded'
            except Exception as e:
                health_data['components']['plugins'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
        
        return jsonify(health_data)
    
    @api.route('/plugins')
    def api_plugins():
        """Get plugin information via API"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            plugin_status = plugin_manager.get_plugin_status()
            return jsonify(plugin_status)
        
        except Exception as e:
            logger.error(f"API plugins error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/plugins/<plugin_name>/reload', methods=['POST'])
    def reload_plugin(plugin_name):
        """Reload a specific plugin"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            app_context = {
                'config': config,
                'db_manager': db_manager,
                'doc_processor': doc_processor
            }
            
            success = plugin_manager.reload_plugin(plugin_name, app_context)
            
            if success:
                return jsonify({'success': True, 'message': f'Plugin {plugin_name} reloaded successfully'})
            else:
                return jsonify({'success': False, 'error': f'Failed to reload plugin {plugin_name}'}), 500
        
        except Exception as e:
            logger.error(f"Plugin reload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/documents/upload', methods=['POST'])
    def api_upload():
        """API endpoint for document upload"""
        try:
            if not doc_processor:
                return jsonify({'error': 'Document processor not available'}), 500
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not doc_processor.is_allowed_file(file.filename):
                return jsonify({'error': 'File type not allowed'}), 400
            
            # Save uploaded file
            import os
            import uuid
            filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(doc_processor.upload_folder, filename)
            file.save(file_path)
            
            # Get metadata from request
            metadata = {}
            if request.is_json:
                metadata = request.get_json() or {}
            else:
                # Extract metadata from form data
                metadata = {
                    'uploaded_by': request.form.get('uploaded_by', 'api'),
                    'tags': request.form.get('tags', '').split(',') if request.form.get('tags') else [],
                    'notes': request.form.get('notes', '')
                }
            
            # Process the document
            result = doc_processor.process_document(file_path, metadata)
            
            return jsonify(result)
        
        except Exception as e:
            logger.error(f"API upload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/documents/batch', methods=['POST'])
    def api_batch_upload():
        """API endpoint for batch document upload"""
        try:
            if not doc_processor:
                return jsonify({'error': 'Document processor not available'}), 500
            
            files = request.files.getlist('files')
            if not files:
                return jsonify({'error': 'No files provided'}), 400
            
            # Save all files and collect paths
            import os
            import uuid
            file_paths = []
            
            for file in files:
                if file.filename and doc_processor.is_allowed_file(file.filename):
                    filename = f"{uuid.uuid4()}_{file.filename}"
                    file_path = os.path.join(doc_processor.upload_folder, filename)
                    file.save(file_path)
                    file_paths.append(file_path)
            
            if not file_paths:
                return jsonify({'error': 'No valid files to process'}), 400
            
            # Get metadata from request
            metadata = {}
            if request.is_json:
                metadata = request.get_json() or {}
            
            # Process batch
            results = doc_processor.process_batch(file_paths, metadata)
            
            return jsonify({
                'success': True,
                'total_files': len(file_paths),
                'results': results
            })
        
        except Exception as e:
            logger.error(f"API batch upload error: {e}")
            return jsonify({'error': str(e)}), 500
    
    return api


def import_datetime():
    """Helper to import datetime module"""
    from datetime import datetime
    return datetime
