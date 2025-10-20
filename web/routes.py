from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from loguru import logger
from typing import Any, Dict
from datetime import datetime # Moved this import to the top as suggestedlogger

def create_web_blueprint(config: Any, db_manager: Any, doc_processor: Any, plugin_manager: Any = None) -> Blueprint:
    """Create web interface blueprint with plugin support"""
    
    web = Blueprint('web', __name__)
    
    # --- Jinja2 Filters ---
    @web.app_template_filter('datetime')
    def format_datetime(value, format="%Y-%m-%d %H:%M"):
        """Formats a datetime string or object into a human-readable string."""
        if not value:
            return ""
        
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
    
    # --- Helper for generating basic plugin config form ---
    def generate_basic_config_form(plugin):
        """Generate a basic configuration form for a plugin"""
        form_html = f'<form id="pluginConfigForm">'
        
        # Add basic fields based on plugin config
        config_data = getattr(plugin, 'config', {}) # Use a different variable name to avoid conflict with 'config' parameter
        
        for key, value in config_data.items():
            if key in ['api_key', 'password', 'secret']:
                # Password field for sensitive data
                form_html += f'''
                <div class="mb-3">
                    <label for="config_{key}" class="form-label">{key.replace('_', ' ').title()}</label>
                    <input type="password" class="form-control" id="config_{key}" name="{key}" 
                            value="{'****' if value else ''}" placeholder="Enter {key.replace('_', ' ')}">
                    <small class="form-text text-muted">Leave blank to keep current value</small>
                </div>'''
            elif isinstance(value, bool):
                # Checkbox for boolean values
                checked = 'checked' if value else ''
                form_html += f'''
                <div class="mb-3 form-check">
                    <input type="checkbox" class="form-check-input" id="config_{key}" name="{key}" {checked}>
                    <label class="form-check-label" for="config_{key}">
                        {key.replace('_', ' ').title()}
                    </label>
                </div>'''
            elif isinstance(value, (int, float)):
                # Number input for numeric values
                form_html += f'''
                <div class="mb-3">
                    <label for="config_{key}" class="form-label">{key.replace('_', ' ').title()}</label>
                    <input type="number" class="form-control" id="config_{key}" name="{key}" 
                            value="{value}" step="{'0.01' if isinstance(value, float) else '1'}">
                </div>'''
            else:
                # Text input for other values
                form_html += f'''
                <div class="mb-3">
                    <label for="config_{key}" class="form-label">{key.replace('_', ' ').title()}</label>
                    <input type="text" class="form-control" id="config_{key}" name="{key}" 
                            value="{value or ''}" placeholder="Enter {key.replace('_', ' ')}">
                </div>'''
        
        form_html += '</form>'
        return form_html

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
            # Get recent documents from Paperless-NGX plugin if available
            recent_documents = []
            paperless_plugin = None
            
            if plugin_manager:
                paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
                if paperless_plugin and hasattr(paperless_plugin, 'get_recent_documents'):
                    try:
                        recent_documents = paperless_plugin.get_recent_documents(limit=50)
                        logger.info(f"Retrieved {len(recent_documents)} documents from Paperless-NGX")
                    except Exception as e:
                        logger.error(f"Failed to get documents from Paperless-NGX: {e}")
            
            # Get recent invoices from InvoicePlane plugin if available
            recent_invoices = []
            invoiceplane_plugin = None
            
            if plugin_manager:
                invoiceplane_plugin = plugin_manager.get_plugin('invoiceplane')
                if invoiceplane_plugin and hasattr(invoiceplane_plugin, 'client') and invoiceplane_plugin.client:
                    try:
                        recent_invoices = invoiceplane_plugin.client.get_recent_invoices(limit=20)
                        logger.info(f"Retrieved {len(recent_invoices)} invoices from InvoicePlane")
                    except Exception as e:
                        logger.error(f"Failed to get invoices from InvoicePlane: {e}")
            
            # Fallback: Get documents from local database
            if not recent_documents and db_manager:
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
            
            # Add Paperless-NGX stats if available
            if paperless_plugin and hasattr(paperless_plugin, 'get_stats'):
                try:
                    paperless_stats = paperless_plugin.get_stats()
                    processing_stats.update(paperless_stats)
                except Exception as e:
                    logger.error(f"Failed to get Paperless-NGX stats: {e}")
            
            return render_template('documents.html', 
                                   recent_documents=recent_documents,
                                   recent_invoices=recent_invoices,
                                   processing_stats=processing_stats,
                                   paperless_available=paperless_plugin is not None,
                                   invoiceplane_available=invoiceplane_plugin is not None)
            
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

    # InvoicePlane Routes
    @web.route('/invoiceplane/invoices')
    def invoiceplane_invoices():
        """Display InvoicePlane invoices with pagination and date filtering"""
        try:
            # Get InvoicePlane plugin
            invoiceplane_plugin = None
            if plugin_manager:
                invoiceplane_plugin = plugin_manager.get_plugin('invoiceplane')

            if not invoiceplane_plugin:
                return render_template('invoiceplane_invoices.html',
                                       invoices=[],
                                       invoiceplane_configured=False,
                                       error_message="InvoicePlane plugin not configured or unavailable")

            # Get query parameters
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 25, type=int)
            date_from = request.args.get('date_from', '').strip()
            date_to = request.args.get('date_to', '').strip()
            status_filter = request.args.get('status', '').strip()

            # Validate page size
            page_size = min(max(page_size, 1), 100)  # Between 1 and 100

            try:
                # Get invoices from InvoicePlane
                result = invoiceplane_plugin.client.get_invoices(
                    page=page,
                    per_page=page_size,
                    date_from=date_from if date_from else None,
                    date_to=date_to if date_to else None,
                    status=status_filter if status_filter else None
                )

                if result:
                    invoices = result.get('data', [])

                    # Create pagination object
                    from plugins.invoiceplane.client import InvoicePlanePagination
                    pagination = InvoicePlanePagination(result, page, page_size)

                    # Get plugin status
                    plugin_status = invoiceplane_plugin.get_status() if hasattr(invoiceplane_plugin, 'get_status') else {}

                    return render_template('invoiceplane_invoices.html',
                                           invoices=invoices,
                                           pagination=pagination,
                                           date_from=date_from,
                                           date_to=date_to,
                                           status_filter=status_filter,
                                           invoiceplane_configured=True,
                                           plugin_status=plugin_status)
                else:
                    return render_template('invoiceplane_invoices.html',
                                           invoices=[],
                                           invoiceplane_configured=True,
                                           error_message="Failed to fetch invoices from InvoicePlane")

            except Exception as e:
                logger.error(f"Failed to fetch InvoicePlane invoices: {e}")
                return render_template('invoiceplane_invoices.html',
                                       invoices=[],
                                       invoiceplane_configured=True,
                                       error_message=f"Failed to fetch invoices: {str(e)}",
                                       date_from=date_from,
                                       date_to=date_to,
                                       status_filter=status_filter)

        except Exception as e:
            logger.error(f"InvoicePlane invoices route error: {e}")
            return render_template('invoiceplane_invoices.html',
                                   invoices=[],
                                   invoiceplane_configured=False,
                                   error_message="An error occurred while loading invoices")

    # NEW: API endpoint to get plugin configuration HTML
    @web.route('/api/plugins/<plugin_name>/config', methods=['GET'])
    def get_plugin_config(plugin_name):
        """Get plugin configuration interface"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # First try to get initialized plugin
            plugin = plugin_manager.get_plugin(plugin_name)
            
            # If plugin not initialized, try to get it from plugin classes (for failed plugins)
            if not plugin and hasattr(plugin_manager, '_plugin_classes'):
                if plugin_name in plugin_manager._plugin_classes:
                    try:
                        # Create a temporary instance just for configuration
                        plugin_class = plugin_manager._plugin_classes[plugin_name]
                        plugin = plugin_class(plugin_name)
                        
                        # Set existing configuration if available
                        if config and hasattr(config, 'get_plugin_config'):
                            plugin_config = config.get_plugin_config(plugin_name)
                            if plugin_config:
                                plugin.config = plugin_config
                        
                        logger.info(f"Created temporary plugin instance for configuration: {plugin_name}")
                    except Exception as e:
                        logger.error(f"Failed to create temporary plugin instance: {e}")
                        plugin = None
            
            if not plugin:
                return jsonify({'error': f'Plugin {plugin_name} not found'}), 404
            
            # Get plugin configuration form HTML
            if hasattr(plugin, 'get_config_form'):
                config_html = plugin.get_config_form()
                return jsonify({
                    'success': True,
                    'html': config_html,
                    'plugin_name': plugin_name
                })
            else:
                # Generate a basic configuration form based on plugin config
                config_html = generate_basic_config_form(plugin)
                return jsonify({
                    'success': True,
                    'html': config_html,
                    'plugin_name': plugin_name
                })
        
        except Exception as e:
            logger.error(f"Get plugin config error: {e}")
            return jsonify({'error': str(e)}), 500

    # NEW: API endpoint to save plugin configuration
    @web.route('/api/plugins/<plugin_name>/config', methods=['POST'])
    def save_plugin_config(plugin_name):
        """Save plugin configuration"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            plugin = plugin_manager.get_plugin(plugin_name)
            
            # If plugin not initialized, try to get it from plugin classes (for failed plugins)
            if not plugin and hasattr(plugin_manager, '_plugin_classes'):
                if plugin_name in plugin_manager._plugin_classes:
                    try:
                        # Create a temporary instance just for configuration
                        plugin_class = plugin_manager._plugin_classes[plugin_name]
                        plugin = plugin_class(plugin_name)
                        
                        # Set existing configuration if available
                        if config and hasattr(config, 'get_plugin_config'):
                            plugin_config = config.get_plugin_config(plugin_name)
                            if plugin_config:
                                plugin.config = plugin_config
                        
                        logger.info(f"Created temporary plugin instance for configuration save: {plugin_name}")
                    except Exception as e:
                        logger.error(f"Failed to create temporary plugin instance for save: {e}")
                        plugin = None
            
            if not plugin:
                return jsonify({'error': f'Plugin {plugin_name} not found'}), 404
            
            # Get configuration data from request
            config_data = request.get_json()
            if not config_data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            # Update plugin configuration
            if hasattr(plugin, 'update_config'):
                success = plugin.update_config(config_data)
                if success:
                    # Save to configuration file
                    if config and hasattr(config, 'set_plugin_config'):
                        config.set_plugin_config(plugin_name, plugin.config)
                        if hasattr(config, 'save_plugin_configs'):
                            config.save_plugin_configs()
                    
                    return jsonify({
                        'success': True,
                        'message': 'Configuration saved successfully'
                    })
                else:
                    return jsonify({'error': 'Failed to update plugin configuration'}), 500
            else:
                # Basic configuration update
                for key, value in config_data.items():
                    if hasattr(plugin, key):
                        setattr(plugin, key, value)
                    plugin.config[key] = value
                
                # Save to configuration file
                if config and hasattr(config, 'set_plugin_config'):
                    config.set_plugin_config(plugin_name, plugin.config)
                    if hasattr(config, 'save_plugin_configs'):
                        config.save_plugin_configs()
                
                return jsonify({
                    'success': True,
                    'message': 'Configuration saved successfully'
                })
        
        except Exception as e:
            logger.error(f"Save plugin config error: {e}")
            return jsonify({'error': str(e)}), 500

    # NEW: API endpoint to test plugin connection
    @web.route('/api/plugins/<plugin_name>/test-connection', methods=['POST'])
    def test_plugin_connection(plugin_name):
        """Test plugin connection"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            plugin = plugin_manager.get_plugin(plugin_name)
            if not plugin:
                return jsonify({'error': f'Plugin {plugin_name} not found'}), 404
            
            # Get test configuration data
            test_config = request.get_json() if request.is_json else None
            
            # Test connection
            if hasattr(plugin, 'test_connection_with_config'):
                success = plugin.test_connection_with_config(test_config)
            elif hasattr(plugin, 'test_connection'):
                success = plugin.test_connection()
            else:
                return jsonify({'error': 'Plugin does not support connection testing'}), 400
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Connection test successful'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Connection test failed'
                })
        
        except Exception as e:
            logger.error(f"Test plugin connection error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            })

    @web.route('/system')
    def system_diagnostics():
        """System diagnostics and network information"""
        try:
            import socket
            import subprocess
            import os
            
            # Get container information
            container_info = {
                'hostname': socket.gethostname(),
                'container_ip': None,
                'network_interfaces': [],
                'dns_servers': [],
                'docker_network': None,
                'environment_vars': {}
            }
            
            # Get container IP address
            try:
                container_info['container_ip'] = socket.gethostbyname(socket.gethostname())
            except:
                container_info['container_ip'] = 'Unknown'
            
            # Get network interfaces
            try:
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True, timeout=5)
                container_info['network_interfaces'] = result.stdout.split('\n')[:20]  # Limit output
            except:
                container_info['network_interfaces'] = ['Unable to get network interfaces']
            
            # Get DNS configuration
            try:
                if os.path.exists('/etc/resolv.conf'):
                    with open('/etc/resolv.conf', 'r') as f:
                        container_info['dns_servers'] = [line.strip() for line in f.readlines()[:10]]
            except:
                container_info['dns_servers'] = ['Unable to read DNS configuration']
            
            # Get Docker network information
            try:
                result = subprocess.run(['cat', '/proc/1/cgroup'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if 'docker' in line and '/' in line:
                        container_info['docker_network'] = line.split('/')[-1][:12]  # Container ID
                        break
            except:
                container_info['docker_network'] = 'Unable to determine'
            
            # Get relevant environment variables
            env_vars_to_show = ['COMPOSE_PROJECT_NAME', 'COMPOSE_SERVICE', 'HOSTNAME', 'PATH']
            for var in env_vars_to_show:
                container_info['environment_vars'][var] = os.environ.get(var, 'Not set')
            
            # Test connectivity to common targets
            connectivity_tests = {
                'localhost': test_connection('localhost', 8000),
                'host.docker.internal': test_connection('host.docker.internal', 8000),
                'paperless-ngx': test_connection('paperless-ngx', 8000),
                'simple.local': test_connection('simple.local', 8000),
                'google_dns': test_connection('8.8.8.8', 53)
            }
            
            return render_template('system.html', 
                                 container_info=container_info,
                                 connectivity_tests=connectivity_tests)
        except Exception as e:
            logger.error(f"System diagnostics error: {e}")
            return f"Error getting system information: {str(e)}", 500
    
    def test_connection(host, port, timeout=3):
        """Test TCP connection to host:port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            return f"Error: {str(e)}"

    # Fallback routes for plugins that failed to load
    @web.route('/plugins/<plugin_name>')
    def plugin_fallback(plugin_name):
        """Fallback route for plugins that failed to register blueprints"""
        try:
            if not plugin_manager:
                return render_template('errors/plugin_error.html', 
                                     plugin_name=plugin_name.title(),
                                     error='Plugin manager not available')
            
            plugin = plugin_manager.get_plugin(plugin_name)
            if not plugin:
                return render_template('errors/plugin_error.html', 
                                     plugin_name=plugin_name.title(),
                                     error='Plugin not found or failed to load')
            
            # If plugin exists but blueprint failed to register
            return render_template('errors/plugin_error.html', 
                                 plugin_name=plugin_name.title(),
                                 error='Plugin blueprint failed to register. Check logs for details.')
                                 
        except Exception as e:
            logger.error(f"Fallback route error for plugin {plugin_name}: {e}")
            return render_template('errors/plugin_error.html', 
                                 plugin_name=plugin_name.title(),
                                 error=f'Plugin error: {str(e)}')

    return web


def create_api_blueprint(config: Any, db_manager: Any, doc_processor: Any, plugin_manager: Any = None) -> Blueprint:
    """Create API blueprint with plugin support"""
    
    api = Blueprint('api', __name__)
    @api.route('/health')
    def health():
        """API health check"""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(), # Corrected usage
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
    
    @api.route('/plugins/<plugin_name>/retry', methods=['POST'])
    def retry_failed_plugin(plugin_name):
        """Retry a specific failed plugin"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            app_context = {
                'config': config,
                'db_manager': db_manager,
                'doc_processor': doc_processor
            }
            
            success = plugin_manager.retry_failed_plugin(plugin_name, app_context)
            
            if success:
                return jsonify({'success': True, 'message': f'Plugin {plugin_name} retried successfully'})
            else:
                return jsonify({'success': False, 'error': f'Failed to retry plugin {plugin_name}'}), 500
            
        except Exception as e:
            logger.error(f"Plugin retry error: {e}")
            return jsonify({'error': str(e)}), 500
    
    @api.route('/plugins/retry-all-failed', methods=['POST'])
    def retry_all_failed_plugins():
        """Retry all failed plugins"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            app_context = {
                'config': config,
                'db_manager': db_manager,
                'doc_processor': doc_processor
            }
            
            results = plugin_manager.retry_all_failed_plugins(app_context)
            
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            return jsonify({
                'success': True,
                'message': f'Retried {success_count} out of {total_count} failed plugins',
                'results': results,
                'success_count': success_count,
                'total_count': total_count
            })
            
        except Exception as e:
            logger.error(f"Plugin retry all error: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/documents/<int:doc_id>/ocr', methods=['GET'])
    def get_document_ocr(doc_id):
        """Get OCR content for a document"""
        try:
            logger.info(f"Fetching OCR content for document ID: {doc_id}")
            
            if not plugin_manager:
                logger.error("Plugin manager not available")
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # Get Paperless-NGX plugin
            paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            if not paperless_plugin:
                logger.error("Paperless-NGX plugin not found")
                return jsonify({'error': 'Paperless-NGX plugin not available'}), 404
            
            # Check for placeholder API key
            if paperless_plugin.api_key in ['YOUR_REAL_API_TOKEN_HERE', 'PLACEHOLDER_TOKEN_REPLACE_ME', 'your_api_token_here']:
                logger.warning("Paperless-NGX plugin using placeholder API key")
                return jsonify({'error': 'Please update the Paperless-NGX API token with a real token from your Paperless-NGX instance.'}), 400
            
            # Get OCR content
            ocr_content = paperless_plugin.get_document_content(doc_id)
            
            return jsonify({
                'success': True,
                'document_id': doc_id,
                'ocr_content': ocr_content
            })
            
        except Exception as e:
            logger.error(f"Failed to get OCR content for document {doc_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/documents/<int:doc_id>/details', methods=['GET'])
    def get_document_details(doc_id):
        """Get detailed information for a document"""
        try:
            logger.info(f"Fetching document details for document ID: {doc_id}")
            
            if not plugin_manager:
                logger.error("Plugin manager not available")
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # Get Paperless-NGX plugin
            paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            if not paperless_plugin:
                logger.error("Paperless-NGX plugin not found")
                return jsonify({'error': 'Paperless-NGX plugin not available'}), 404
            
            # Check if plugin is properly configured
            if not hasattr(paperless_plugin, 'base_url') or not paperless_plugin.base_url:
                logger.error("Paperless-NGX plugin not properly configured - missing base_url")
                return jsonify({'error': 'Paperless-NGX plugin not properly configured'}), 500
                
            if not hasattr(paperless_plugin, 'api_key') or not paperless_plugin.api_key:
                logger.error("Paperless-NGX plugin not properly configured - missing API key")
                return jsonify({'error': 'Paperless-NGX plugin missing API key. Please configure in the plugins section.'}), 500
            
            # Check for placeholder API key
            if paperless_plugin.api_key in ['YOUR_REAL_API_TOKEN_HERE', 'PLACEHOLDER_TOKEN_REPLACE_ME', 'your_api_token_here']:
                logger.warning("Paperless-NGX plugin using placeholder API key")
                return jsonify({'error': 'Please update the Paperless-NGX API token with a real token from your Paperless-NGX instance.'}), 400
            
            logger.info(f"Calling paperless_plugin.get_document({doc_id})")
            
            # Get document details
            document = paperless_plugin.get_document(doc_id)
            
            logger.info(f"Successfully retrieved document details for ID: {doc_id}")
            
            return jsonify({
                'success': True,
                'document': document
            })
            
        except Exception as e:
            logger.error(f"Failed to get document details for document {doc_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/documents/<int:doc_id>/ocr/raw', methods=['GET'])
    def get_document_ocr_raw(doc_id):
        """Get raw OCR content for a document (unprocessed HTML/SVG)"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # Get Paperless-NGX plugin
            paperless_plugin = plugin_manager.get_plugin('paperless_ngx')
            if not paperless_plugin:
                return jsonify({'error': 'Paperless-NGX plugin not available'}), 404
            
            # Get raw OCR content
            raw_content = paperless_plugin.get_document_raw_content(doc_id)
            
            return jsonify({
                'success': True,
                'document_id': doc_id,
                'raw_content': raw_content
            })
            
        except Exception as e:
            logger.error(f"Failed to get raw OCR content for document {doc_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/plugins/<plugin_name>/reload-config', methods=['POST'])
    def reload_plugin_config(plugin_name):
        """Reload configuration for a specific plugin"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # Get the plugin
            plugin = plugin_manager.get_plugin(plugin_name)
            if not plugin:
                return jsonify({'error': f'Plugin {plugin_name} not found'}), 404
            
            # Reload the plugin configuration
            app_context = {
                'config': config,
                'db_manager': db_manager,
                'doc_processor': doc_processor
            }
            
            # Re-initialize the plugin to pick up new config
            success = plugin.initialize(app_context)
            
            return jsonify({
                'success': success,
                'message': f'Plugin {plugin_name} configuration reloaded',
                'plugin_status': {
                    'name': plugin.name,
                    'version': plugin.version,
                    'base_url': getattr(plugin, 'base_url', None),
                    'hostname_url': getattr(plugin, 'hostname_url', None)
                }
            })
            
        except Exception as e:
            logger.error(f"Failed to reload plugin config for {plugin_name}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/plugins/<plugin_name>/debug', methods=['GET'])
    def get_plugin_debug_info(plugin_name):
        """Get debug information for a specific plugin"""
        try:
            if not plugin_manager:
                return jsonify({'error': 'Plugin manager not available'}), 500
            
            # Get the plugin
            plugin = plugin_manager.get_plugin(plugin_name)
            if not plugin:
                return jsonify({'error': f'Plugin {plugin_name} not found'}), 404
            
            # Get debug info
            debug_info = {
                'name': plugin.name,
                'version': plugin.version,
                'config': getattr(plugin, 'config', {}),
                'base_url': getattr(plugin, 'base_url', None),
                'hostname_url': getattr(plugin, 'hostname_url', None),
                'api_key_set': bool(getattr(plugin, 'api_key', None)),
                'session_active': bool(getattr(plugin, 'session', None))
            }
            
            # Add method results if available
            if hasattr(plugin, 'get_hostname_url'):
                debug_info['hostname_url_method'] = plugin.get_hostname_url()
            if hasattr(plugin, 'get_api_url'):
                debug_info['api_url_method'] = plugin.get_api_url()
            
            return jsonify({
                'success': True,
                'plugin': plugin_name,
                'debug_info': debug_info
            })
            
        except Exception as e:
            logger.error(f"Failed to get debug info for plugin {plugin_name}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/invoiceplane/invoices/<int:invoice_id>', methods=['GET'])
    def get_invoice_details(invoice_id):
        """Get detailed information for an InvoicePlane invoice"""
        try:
            logger.info(f"Fetching invoice details for invoice ID: {invoice_id}")

            if not plugin_manager:
                logger.error("Plugin manager not available")
                return jsonify({'error': 'Plugin manager not available'}), 500

            # Get InvoicePlane plugin
            invoiceplane_plugin = plugin_manager.get_plugin('invoiceplane')
            if not invoiceplane_plugin:
                logger.error("InvoicePlane plugin not found")
                return jsonify({'error': 'InvoicePlane plugin not available'}), 404

            if not hasattr(invoiceplane_plugin, 'client') or not invoiceplane_plugin.client:
                logger.error("InvoicePlane plugin client not initialized")
                return jsonify({'error': 'InvoicePlane plugin not properly configured'}), 500

            # Get invoice details
            invoice = invoiceplane_plugin.client.get_invoice(invoice_id)

            logger.info(f"Successfully retrieved invoice details for ID: {invoice_id}")

            return jsonify({
                'success': True,
                'invoice': invoice
            })

        except Exception as e:
            logger.error(f"Failed to get invoice details for invoice {invoice_id}: {e}")
            return jsonify({'error': str(e)}), 500

    @api.route('/bigcapital/sync/invoiceplane/<int:invoice_id>', methods=['POST'])
    def sync_invoice_to_bigcapital(invoice_id):
        """Sync an InvoicePlane invoice to BigCapital"""
        try:
            logger.info(f"Syncing InvoicePlane invoice {invoice_id} to BigCapital")

            if not plugin_manager:
                logger.error("Plugin manager not available")
                return jsonify({'error': 'Plugin manager not available'}), 500

            # Get InvoicePlane plugin
            invoiceplane_plugin = plugin_manager.get_plugin('invoiceplane')
            if not invoiceplane_plugin:
                logger.error("InvoicePlane plugin not found")
                return jsonify({'error': 'InvoicePlane plugin not available'}), 404

            if not hasattr(invoiceplane_plugin, 'client') or not invoiceplane_plugin.client:
                logger.error("InvoicePlane plugin client not initialized")
                return jsonify({'error': 'InvoicePlane plugin not properly configured'}), 500

            # Get BigCapital plugin
            bigcapital_plugin = plugin_manager.get_plugin('bigcapitalpy')
            if not bigcapital_plugin:
                logger.error("BigCapital plugin not found")
                return jsonify({'error': 'BigCapital plugin not available'}), 404

            # Get invoice details from InvoicePlane
            invoice = invoiceplane_plugin.client.get_invoice(invoice_id)
            if not invoice:
                return jsonify({'error': f'Invoice {invoice_id} not found in InvoicePlane'}), 404

            # Sync invoice to BigCapital
            sync_result = bigcapital_plugin.sync_invoice_from_invoiceplane(invoice)

            logger.info(f"Successfully synced invoice {invoice_id} to BigCapital")

            return jsonify({
                'success': True,
                'message': f'Invoice {invoice_id} synced successfully to BigCapital',
                'sync_result': sync_result
            })

        except Exception as e:
            logger.error(f"Failed to sync invoice {invoice_id} to BigCapital: {e}")
            return jsonify({'error': str(e)}), 500

    return api
