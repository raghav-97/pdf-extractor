import pdfplumber
import json
import sys
import re
import traceback
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime

@dataclass
class ExtractedField:
    value: str
    confidence: float
    method: str
    raw_matches: List[str] = None

class EnhancedPDFParser:
    def __init__(self, debug_mode: bool = False):
        self._setup_logging(debug_mode)
        self._initialize_patterns()
        
    def _setup_logging(self, debug_mode: bool):
        """Configure logging with timestamp and appropriate level"""
        level = logging.DEBUG if debug_mode else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stderr)]
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_patterns(self):
        """Initialize regex patterns for different fields"""
        self.patterns = {
            'name': {
                'labeled': [
                    (r'Name\s*:\s*([^\n]+)', 0.9),
                    (r'Full Name\s*:\s*([^\n]+)', 0.9),
                    (r'Customer Name\s*:\s*([^\n]+)', 0.8),
                    (r'Client Name\s*:\s*([^\n]+)', 0.8),
                    (r'First Name\s*:\s*([^\n]+)(?:\s+Last Name\s*:\s*([^\n]+))?', 0.7)
                ],
                'unlabeled': [
                    (r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b', 0.4)  # Basic name pattern
                ]
            },
            'phone': {
                'labeled': [
                    (r'Phone\s*:\s*([\+\d\s\(\)-]+)', 0.9),
                    (r'Contact\s*:\s*([\+\d\s\(\)-]+)', 0.8),
                    (r'Tel(?:ephone)?\s*:\s*([\+\d\s\(\)-]+)', 0.8),
                    (r'Mobile\s*:\s*([\+\d\s\(\)-]+)', 0.8),
                    (r'Phone Number\s*:\s*([\+\d\s\(\)-]+)', 0.9)
                ],
                'unlabeled': [
                    (r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', 0.6),
                    (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 0.5)
                ]
            },
            'address': {
                'labeled': [
                    (r'Address\s*:\s*([^\n]+?)(?=\s*Role\s*:|$|\n)', 0.9),
                    (r'Location\s*:\s*([^\n]+?)(?=\s*Role\s*:|$|\n)', 0.8),
                    (r'Residence\s*:\s*([^\n]+?)(?=\s*Role\s*:|$|\n)', 0.8),
                    (r'Mailing Address\s*:\s*([^\n]+?)(?=\s*Role\s*:|$|\n)', 0.9)
                ],
                'unlabeled': [
                    (r'\b\d+\s+[A-Za-z0-9\s,.-]+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Ln|Rd|Blvd|Dr|St)\.?\s*,\s*[A-Za-z\s]+,\s*[A-Z]{2}\s+\d{5}\b', 0.7),
                    (r'\b\d+\s+[A-Za-z0-9\s,.-]+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Ln|Rd|Blvd|Dr|St)\.?', 0.5)
                ]
            }
        }

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF with enhanced error handling"""
        try:
            self.logger.info(f"Processing PDF: {pdf_path}")
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")

            with pdfplumber.open(pdf_path) as pdf:
                text = []
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                            self.logger.debug(f"Extracted text from page {page_num}")
                    except Exception as e:
                        self.logger.error(f"Error extracting text from page {page_num}: {str(e)}")
                
                full_text = '\n'.join(text)
                if not full_text.strip():
                    self.logger.warning("No text could be extracted from the PDF")
                    return None
                return full_text

        except Exception as e:
            self.logger.error(f"Error in text extraction: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return None

    def _validate_name(self, name: str) -> float:
        """Validate name and return confidence score"""
        if not name:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Check for reasonable length
        if 2 <= len(name.split()) <= 4:
            confidence += 0.2
        
        # Check for proper capitalization
        if all(word[0].isupper() for word in name.split() if word):
            confidence += 0.2
        
        # Check for unusual characters
        if not re.search(r'[^A-Za-z\s\'-]', name):
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _validate_phone(self, phone: str) -> float:
        """Validate phone number and return confidence score"""
        if not phone:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Remove all non-numeric characters
        numbers_only = re.sub(r'\D', '', phone)
        
        # Check length
        if len(numbers_only) == 10:
            confidence += 0.3
        elif len(numbers_only) == 11 and numbers_only.startswith('1'):
            confidence += 0.2
            
        # Check format
        if re.match(r'^\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$', phone):
            confidence += 0.2
            
        return min(confidence, 1.0)

    def _validate_address(self, address: str) -> float:
        """Validate address and return confidence score"""
        if not address:
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Check for street number
        if re.search(r'\d+', address):
            confidence += 0.1
            
        # Check for street type
        if re.search(r'(Street|Road|Avenue|Lane|Drive|Boulevard|St|Rd|Ave|Ln|Dr|Blvd)\b', address, re.I):
            confidence += 0.1
            
        # Check for state and ZIP code
        if re.search(r'\b[A-Z]{2}\s+\d{5}\b', address):
            confidence += 0.2
            
        # Check for city
        if re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b', address):
            confidence += 0.1
            
        # Check for reasonable length
        if 10 <= len(address) <= 200:
            confidence += 0.1
            
        return min(confidence, 1.0)

    def _find_best_match(self, text: str, field_type: str) -> ExtractedField:
        """Find the best match for a given field type with confidence scoring"""
        best_match = ExtractedField(value='', confidence=0.0, method='none', raw_matches=[])
        patterns = self.patterns[field_type]

        # Try labeled patterns first
        for pattern, base_confidence in patterns['labeled']:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                value = match.group(1).strip()
                if not value:
                    continue
                
                # Get validation confidence based on field type
                validation_confidence = {
                    'name': self._validate_name,
                    'phone': self._validate_phone,
                    'address': self._validate_address
                }[field_type](value)
                
                # Combined confidence score
                confidence = (base_confidence + validation_confidence) / 2
                
                if confidence > best_match.confidence:
                    best_match = ExtractedField(
                        value=value,
                        confidence=confidence,
                        method='labeled',
                        raw_matches=[value]
                    )

        # If no good labeled match, try unlabeled patterns
        if best_match.confidence < 0.6:
            for pattern, base_confidence in patterns['unlabeled']:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    value = match.group(0).strip()
                    if not value:
                        continue
                    
                    validation_confidence = {
                        'name': self._validate_name,
                        'phone': self._validate_phone,
                        'address': self._validate_address
                    }[field_type](value)
                    
                    confidence = (base_confidence + validation_confidence) / 2
                    
                    if confidence > best_match.confidence:
                        best_match = ExtractedField(
                            value=value,
                            confidence=confidence,
                            method='unlabeled',
                            raw_matches=[value]
                        )

        return best_match

    def process_pdf(self, pdf_path: str, min_confidence: float = 0.5) -> Dict:
        """Process PDF and return structured data with confidence scores"""
        try:
            text = self.extract_text(pdf_path)
            if text is None:
                return {'error': 'Could not extract text from PDF'}

            # Extract data for each field
            results = {}
            for field in ['name', 'phone', 'address']:
                match = self._find_best_match(text, field)
                results[field] = {
                    'value': match.value,
                    'confidence': round(match.confidence, 2),
                    'method': match.method
                }

            # Add metadata
            results['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'file_name': os.path.basename(pdf_path),
                'file_size': os.path.getsize(pdf_path),
                'extraction_successful': any(
                    result['confidence'] >= min_confidence 
                    for result in results.values() 
                    if isinstance(result, dict) and 'confidence' in result
                )
            }

            # Log extraction results
            self.logger.info("Extraction completed with results:")
            for field, data in results.items():
                if isinstance(data, dict) and 'value' in data:
                    self.logger.info(f"{field}: {data['value']} (confidence: {data['confidence']})")

            return results

        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return {'error': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No PDF path provided'}))
        sys.exit(1)

    pdf_path = sys.argv[1]
    parser = EnhancedPDFParser(debug_mode=True)
    result = parser.process_pdf(pdf_path)
    print(json.dumps(result, indent=2))