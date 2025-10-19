"""
Example OCR Processing Plugin
"""
import os
from loguru import logger
from typing import Dict, Any, List
from pathlib import Path

from core.base_plugin import ProcessingPlugin
from core.exceptions import ProcessingError


class OCRProcessorPlugin(ProcessingPlugin):
    """OCR document processing plugin"""
    
    def __init__(self, name: str = "ocr_processor", version: str = "1.0.0"):
        super().__init__(name, version)
        self.ocr_engine = None
        self._supported_formats = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']
    
    def initialize(self, app_context: Dict[str, Any]) -> bool:
        """Initialize OCR processor"""
        try:
            # Try to import OCR libraries
            try:
                import pytesseract
                from PIL import Image
                import fitz  # PyMuPDF for PDFs
                
                self.pytesseract = pytesseract
                self.Image = Image
                self.fitz = fitz
                
                # Configure tesseract path if specified in config
                tesseract_path = self.config.get('tesseract_path')
                if tesseract_path:
                    pytesseract.pytesseract.tesseract_cmd = tesseract_path
                
                logger.info("OCR processor initialized successfully")
                return True
                
            except ImportError as e:
                logger.error(f"OCR libraries not available: {e}")
                logger.info("Install required packages: pip install pytesseract pillow pymupdf")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize OCR processor: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Cleanup OCR processor resources"""
        try:
            # No specific cleanup needed for OCR libraries
            logger.info("OCR processor cleaned up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup OCR processor: {e}")
            return False
    
    def process_document(self, document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process document with OCR"""
        try:
            if not os.path.exists(document_path):
                raise ProcessingError(f"Document not found: {document_path}")
            
            file_ext = Path(document_path).suffix.lower().lstrip('.')
            
            if file_ext == 'pdf':
                return self._process_pdf(document_path, metadata)
            elif file_ext in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']:
                return self._process_image(document_path, metadata)
            else:
                raise ProcessingError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'plugin': self.name
            }
    
    def _process_pdf(self, pdf_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process PDF document"""
        try:
            extracted_text = ""
            page_count = 0
            
            # Open PDF document
            doc = self.fitz.open(pdf_path)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_count += 1
                
                # Try to extract text directly first
                text = page.get_text()
                if text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} ---\n{text}"
                else:
                    # If no text, perform OCR on page image
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image for OCR
                    from io import BytesIO
                    img = self.Image.open(BytesIO(img_data))
                    ocr_text = self.pytesseract.image_to_string(img)
                    
                    if ocr_text.strip():
                        extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n{ocr_text}"
            
            doc.close()
            
            # Extract potential invoice/expense information
            extracted_info = self._extract_document_info(extracted_text)
            
            return {
                'success': True,
                'plugin': self.name,
                'text': extracted_text,
                'page_count': page_count,
                'extracted_info': extracted_info,
                'metadata': {
                    'processing_method': 'pdf_text_and_ocr',
                    'text_length': len(extracted_text)
                }
            }
            
        except Exception as e:
            raise ProcessingError(f"PDF processing failed: {e}")
    
    def _process_image(self, image_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process image document"""
        try:
            # Open image
            img = self.Image.open(image_path)
            
            # Perform OCR
            ocr_text = self.pytesseract.image_to_string(img)
            
            # Extract potential invoice/expense information
            extracted_info = self._extract_document_info(ocr_text)
            
            return {
                'success': True,
                'plugin': self.name,
                'text': ocr_text,
                'extracted_info': extracted_info,
                'metadata': {
                    'processing_method': 'image_ocr',
                    'image_size': img.size,
                    'image_mode': img.mode,
                    'text_length': len(ocr_text)
                }
            }
            
        except Exception as e:
            raise ProcessingError(f"Image processing failed: {e}")
    
    def _extract_document_info(self, text: str) -> Dict[str, Any]:
        """Extract structured information from text"""
        import re
        
        info = {
            'type': 'unknown',
            'amounts': [],
            'dates': [],
            'emails': [],
            'phone_numbers': [],
            'companies': []
        }
        
        # Extract amounts (basic pattern)
        amount_patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*USD',
            r'Total[:\s]*[\$]?[\d,]+\.?\d*',
            r'Amount[:\s]*[\$]?[\d,]+\.?\d*'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            info['amounts'].extend(matches)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{2,4}'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            info['dates'].extend(matches)
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        info['emails'] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'[\+]?[\d\s\-\(\)]{10,}'
        potential_phones = re.findall(phone_pattern, text)
        info['phone_numbers'] = [p for p in potential_phones if len(re.sub(r'[^\d]', '', p)) >= 10]
        
        # Determine document type based on keywords
        invoice_keywords = ['invoice', 'bill', 'receipt', 'payment due', 'total amount']
        expense_keywords = ['expense', 'reimbursement', 'receipt', 'purchase']
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in invoice_keywords):
            info['type'] = 'invoice'
        elif any(keyword in text_lower for keyword in expense_keywords):
            info['type'] = 'expense'
        
        return info
    
    def supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return self._supported_formats
    
    def get_menu_items(self) -> List[Dict[str, str]]:
        """
        Get menu items for the web interface
        
        Returns:
            List of menu item dictionaries
        """
        return []
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate OCR processor configuration"""
        # OCR processor doesn't require specific configuration
        return True
