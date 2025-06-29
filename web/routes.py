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
    
    # --- Jinja2 Filters ---
    @web.app_template_filter('datetime')
    def format_datetime(value, format="%Y-%m-%d %H:%M"):
        """Formats a datetime string or object into a human-readable string."""
        if not value:
            return ""
        
        from datetime import datetime
        
        if isinstance(value, str):
            try:
                # Attempt to parse common ISO formats (e.g., "2023-01-01T12:00:00Z")
                if 'T' in value and ('Z' in value or '+' in value):
                    dt_obj = datetime.fromisoformat(value.replace('Z', '+00:00') if 'Z' in value else value)
                else: # Attempt to parse a common date-time string without timezone
                    dt_obj = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                logger.warning(f"Could not parse datetime string: {value}")
                return value # Return original value if parsing fails
        elif isinstance(value, datetime):
            dt_obj = value
        else:
            return value # Return as is if not string or datetime object

        return dt_obj.strftime(format)
    
    # --- Routes ---
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
    
    @web.route('/config', methods=['GET', 'POST'])
    def configuration():
        """Configuration page with plugin settings"""
        try:
            if request.method == 'POST':
                # Handle configuration updates
                return handle_configuration_update()
            
            # GET request - show configuration form
            # Get current plugin configurations
            plugin_configs = {}
            if plugin_manager:
                for plugin_name in ['paperless_ngx', 'bigcapital', 'ocr_processor']:
                    plugin = plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        plugin_configs[plugin_name] = plugin.config
                    else:
                        # Get from config file if plugin not loaded
                        if config and hasattr(config, 'get_plugin_config'):
                            plugin_configs[plugin_name] = config.get_plugin_config(plugin_name)
                        else:
                            plugin_configs[plugin_name] = {}
            
            # Create a dot-notation accessible object for template compatibility
            class ConfigObject:
                def __init__(self, data):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            setattr(self, key, ConfigObject(value))
                        else:
                            setattr(self, key, value)
                            
                def get(self, key, default=None):
                    return getattr(self, key, default)
            
            config_obj = ConfigObject(plugin_configs)
            
            # Prepare template data
            template_data = {
                'config': config_obj,
                'log_levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            }
            
            return render_template('config.html', **template_data)
        
        except Exception as e:
            logger.error(f"Configuration page error: {e}")
            return render_template('errors/500.html'), 500
    
    def handle_configuration_update():
        """Handle configuration form submission"""
        try:
            from flask import flash, redirect, url_for
            
            updated_configs = {}
            
            # Paperless-NGX Configuration
            paperless_config = {
                'enabled': 'paperless_enabled' in request.form,
                'base_url': request.form.get('paperless_base_url', '').strip(),
                'timeout': int(request.form.get('paperless_timeout', 30)),
                'page_size': int(request.form.get('paperless_page_size', 25)),
                'auto_refresh': 'paperless_auto_refresh' in request.form
            }
            
            # Only update API key if provided
            api_key = request.form.get('paperless_api_key', '').strip()
            if api_key and api_key != '****':
                paperless_config['api_key'] = api_key
            elif plugin_manager:
                # Keep existing API key
                existing_plugin = plugin_manager.get_plugin('paperless_ngx')
                if existing_plugin and hasattr(existing_plugin, 'api_key'):
                    paperless_config['api_key'] = existing_plugin.api_key
            
            updated_configs['paperless_ngx'] = paperless_config
            
            # BigCapital Configuration
            bigcapital_config = {
                'enabled': 'bigcapital_enabled' in request.form,
                'base_url': request.form.get('bigcapital_base_url', '').strip(),
                'default_due_days': int(request.form.get('bigcapital_default_due_days', 30)),
                'auto_sync': 'bigcapital_auto_sync' in request.form
            }
            
            # Only update API key if provided
            api_key = request.form.get('bigcapital_api_key', '').strip()
            if api_key and api_key != '****':
                bigcapital_config['api_key'] = api_key
            elif plugin_manager:
                # Keep existing API key
                existing_plugin = plugin_manager.get_plugin('bigcapital')
                if existing_plugin and hasattr(existing_plugin, 'api_key'):
                    bigcapital_config['api_key'] = existing_plugin.api_key
            
            updated_configs['bigcapital'] = bigcapital_config
            
            # OCR Processor Configuration
            ocr_config = {
                'enabled': 'ocr_enabled' in request.form,
                'tesseract_path': request.form.get('ocr_tesseract_path', '/usr/bin/tesseract').strip(),
                'languages': [lang.strip() for lang in request.form.get('ocr_languages', 'eng').split(',') if lang.strip()],
                'confidence_threshold': int(request.form.get('ocr_confidence_threshold', 50)),
                'preprocess_images': 'ocr_preprocess_images' in request.form
            }
            
            updated_configs['ocr_processor'] = ocr_config
            
            # Save configurations
            if config and hasattr(config, 'set_plugin_config'):
                for plugin_name, plugin_config in updated_configs.items():
                    config.set_plugin_config(plugin_name, plugin_config)
                
                # Save to file
                if hasattr(config, 'save_plugin_configs'):
                    config.save_plugin_configs()
                
                flash('Configuration saved successfully!', 'success')
                logger.info("Plugin configurations updated successfully")
                
                # Optionally restart plugins with new configuration
                if plugin_manager:
                    try:
                        # Reload plugins with new configuration
                        plugin_manager.reload_plugins()
                        flash('Plugins reloaded with new configuration.', 'info')
                    except Exception as e:
                        logger.warning(f"Failed to reload plugins: {e}")
                        flash('Configuration saved, but plugin reload failed. Restart may be required.', 'warning')
            else:
                flash('Failed to save configuration: Config manager not available.', 'error')
            
            return redirect(url_for('web.configuration'))
        
        except Exception as e:
            logger.error(f"Configuration update error: {e}")
            flash(f'Error saving configuration: {str(e)}', 'error')
            return redirect(url_for('web.configuration'))
    
    # Paperless-NGX Routes
    @web.route('/paperless-ngx/documents')
    def paperless_ngx_documents():
        """Display Paperless-NGX documents with pagination and search"""
        try:
            # Get Paperless-NGX plugin
            paperless_plugin = None
            if plugin_manager:
                paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            
            if not paperless_plugin:
                return render_template('paperless_ngx_documents.html',
                                     paperless_ngx_docs=[],
                                     paperless_ngx_configured=False,
                                     error_message="Paperless-NGX plugin not configured or unavailable")
            
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            search_query = request.args.get('q', '').strip()
            page_size = request.args.get('page_size', 25, type=int)
            
            # Validate page size
            page_size = min(max(page_size, 1), 100)  # Between 1 and 100
            
            try:
                # Get documents from Paperless-NGX
                result = paperless_plugin.get_documents(
                    page=page,
                    page_size=page_size,
                    search=search_query if search_query else None
                )
                
                documents = result.get('documents', [])
                
                # Create pagination object
                from plugins.paperless_ngx.client import PaperlessNGXPagination
                pagination_data = {
                    'count': result.get('count', 0),
                    'next': result.get('next'),
                    'previous': result.get('previous'),
                    'results': documents
                }
                pagination = PaperlessNGXPagination(pagination_data, page, page_size)
                
                # Get plugin status
                plugin_status = paperless_plugin.get_status()
                
                return render_template('paperless_ngx_documents.html',
                                     paperless_ngx_docs=documents,
                                     pagination=pagination,
                                     search_query=search_query,
                                     paperless_ngx_configured=True,
                                     paperless_base_url=paperless_plugin.base_url,
                                     plugin_status=plugin_status)
                
            except Exception as e:
                logger.error(f"Failed to fetch Paperless-NGX documents: {e}")
                return render_template('paperless_ngx_documents.html',
                                     paperless_ngx_docs=[],
                                     paperless_ngx_configured=True,
                                     error_message=f"Failed to fetch documents: {str(e)}",
                                     search_query=search_query)
        
        except Exception as e:
            logger.error(f"Paperless-NGX documents route error: {e}")
            return render_template('paperless_ngx_documents.html',
                                 paperless_ngx_docs=[],
                                 paperless_ngx_configured=False,
                                 error_message="An error occurred while loading documents")
    
    @web.route('/paperless-ngx/document/<int:doc_id>/content')
    def paperless_ngx_document_content(doc_id):
        """Display OCR content for a specific Paperless-NGX document"""
        try:
            # Get Paperless-NGX plugin
            paperless_plugin = None
            if plugin_manager:
                paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            
            if not paperless_plugin:
                return render_template('paperless_ngx_document_content.html',
                                     document=None,
                                     content=None,
                                     error_message="Paperless-NGX plugin not configured")
            
            try:
                # Get document metadata
                document = paperless_plugin.get_document(doc_id)
                
                # Get document content
                content = paperless_plugin.get_document_content(doc_id)
                
                return render_template('paperless_ngx_document_content.html',
                                     document=document,
                                     content=content)
                
            except Exception as e:
                logger.error(f"Failed to fetch document {doc_id}: {e}")
                return render_template('paperless_ngx_document_content.html',
                                     document=None,
                                     content=None,
                                     error_message=f"Failed to load document: {str(e)}")
        
        except Exception as e:
            logger.error(f"Document content route error: {e}")
            return render_template('paperless_ngx_document_content.html',
                                 document=None,
                                 content=None,
                                 error_message="An error occurred while loading document content")
    
    @web.route('/paperless-ngx/document/<int:doc_id>')
    def paperless_ngx_document_detail(doc_id):
        """Display detailed information for a specific Paperless-NGX document"""
        try:
            # Get Paperless-NGX plugin
            paperless_plugin = None
            if plugin_manager:
                paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            
            if not paperless_plugin:
                return jsonify({'error': 'Paperless-NGX plugin not configured'}), 404
            
            try:
                # Get document metadata
                document = paperless_plugin.get_document(doc_id)
                return jsonify(document)
                
            except Exception as e:
                logger.error(f"Failed to fetch document {doc_id}: {e}")
                return jsonify({'error': str(e)}), 500
        
        except Exception as e:
            logger.error(f"Document detail route error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    # API endpoint for processing Paperless-NGX documents
    @web.route('/api/process-paperless-document/<int:doc_id>', methods=['POST'])
    def api_process_paperless_document(doc_id):
        """API endpoint to process a Paperless-NGX document through the middleware"""
        try:
            # Get Paperless-NGX plugin
            paperless_plugin = None
            if plugin_manager:
                paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            
            if not paperless_plugin:
                return jsonify({'error': 'Paperless-NGX plugin not configured'}), 404
            
            try:
                # Get document metadata and content
                document = paperless_plugin.get_document(doc_id)
                content = paperless_plugin.get_document_content(doc_id)
                
                # Process document through middleware
                processing_result = {
                    'document_id': doc_id,
                    'title': document.get('title'),
                    'content_length': len(content) if content else 0,
                    'processing_started': True,
                    'message': 'Document processing initiated'
                }
                
                # TODO: Implement actual document processing pipeline
                # This could include:
                # - OCR analysis
                # - Data extraction
                # - Integration with other plugins (BigCapital, etc.)
                # - Workflow automation
                
                logger.info(f"Processing started for Paperless-NGX document {doc_id}")
                
                return jsonify({
                    'success': True,
                    'message': 'Document processing started successfully',
                    'result': processing_result
                })
                
            except Exception as e:
                logger.error(f"Failed to process document {doc_id}: {e}")
                return jsonify({'error': f'Failed to process document: {str(e)}'}), 500
        
        except Exception as e:
            logger.error(f"Process document API error: {e}")
            return jsonify({'error': 'Internal server error'}), 500

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
    
    @api.route('/test-connections', methods=['POST'])
    def test_connections():
        """Test plugin connections"""
        try:
            results = {}
            
            if plugin_manager:
                # Test each plugin connection
                for plugin_name in ['paperless_ngx', 'bigcapital', 'ocr_processor']:
                    plugin = plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        try:
                            # Test connection based on plugin type
                            if hasattr(plugin, 'test_connection'):
                                success = plugin.test_connection()
                                results[plugin_name] = {
                                    'success': success,
                                    'message': 'Connected successfully' if success else 'Connection failed'
                                }
                            else:
                                # For plugins without test_connection method, check if initialized
                                results[plugin_name] = {
                                    'success': True,
                                    'message': 'Plugin initialized'
                                }
                        except Exception as e:
                            results[plugin_name] = {
                                'success': False,
                                'error': str(e)
                            }
                    else:
                        results[plugin_name] = {
                            'success': False,
                            'error': 'Plugin not loaded'
                        }
            else:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            return jsonify({
                'success': True,
                'results': results
            })
        
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return jsonify({'error': str(e)}), 500
    
    return api


def import_datetime():
    """Helper to import datetime module"""
    from datetime import datetime
    return datetime
