import pdfplumber
import io
import re
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF file using pdfplumber with improved extraction methods
    
    Args:
        pdf_file: FileStorage object from Flask request or file-like object
        
    Returns:
        str: Extracted text from all pages
        
    Raises:
        ValueError: If no text could be extracted
        Exception: If PDF parsing fails
    """
    try:
        text_content = ""
        
        # Handle both FileStorage and file-like objects
        if hasattr(pdf_file, 'read'):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
            pdf_stream = io.BytesIO(pdf_bytes)
        else:
            pdf_stream = pdf_file
        
        # Extract text from each page with multiple strategies
        with pdfplumber.open(pdf_stream) as pdf:
            total_pages = len(pdf.pages)
            logger.info(f"Processing PDF with {total_pages} page(s)")
            
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = None
                
                # Strategy 1: Standard text extraction
                try:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 10:  # Ensure meaningful content
                        logger.debug(f"Page {page_num}: Extracted {len(page_text)} characters using standard method")
                except Exception as e:
                    logger.warning(f"Page {page_num}: Standard extraction failed: {str(e)}")
                
                # Strategy 2: Extract with layout preservation if standard fails
                if not page_text or len(page_text.strip()) < 10:
                    try:
                        # Try extracting with layout preservation
                        page_text = page.extract_text(layout=True)
                        if page_text and len(page_text.strip()) > 10:
                            logger.debug(f"Page {page_num}: Extracted using layout method")
                    except Exception as e:
                        logger.warning(f"Page {page_num}: Layout extraction failed: {str(e)}")
                
                # Strategy 3: Extract from tables if available
                if not page_text or len(page_text.strip()) < 10:
                    try:
                        tables = page.extract_tables()
                        if tables:
                            table_text = ""
                            for table in tables:
                                for row in table:
                                    if row:
                                        table_text += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
                            if table_text.strip():
                                page_text = table_text
                                logger.debug(f"Page {page_num}: Extracted from tables")
                    except Exception as e:
                        logger.warning(f"Page {page_num}: Table extraction failed: {str(e)}")
                
                # Strategy 4: Extract words and reconstruct
                if not page_text or len(page_text.strip()) < 10:
                    try:
                        words = page.extract_words()
                        if words:
                            # Sort words by position (top to bottom, left to right)
                            words_sorted = sorted(words, key=lambda w: (w.get('top', 0), w.get('x0', 0)))
                            page_text = " ".join([w.get('text', '') for w in words_sorted if w.get('text')])
                            if page_text.strip():
                                logger.debug(f"Page {page_num}: Extracted from word positions")
                    except Exception as e:
                        logger.warning(f"Page {page_num}: Word extraction failed: {str(e)}")
                
                if page_text and page_text.strip():
                    # Add page separator
                    text_content += page_text.strip() + "\n\n"
                    logger.info(f"Page {page_num}: Successfully extracted {len(page_text)} characters")
                else:
                    logger.warning(f"Page {page_num}: No text could be extracted")
        
        # Validate extraction
        if not text_content.strip():
            raise ValueError(
                "No text could be extracted from PDF. "
                "The file might be an image-based PDF (scanned document) or corrupted. "
                "Please ensure the PDF contains selectable text."
            )
        
        # Clean up text while preserving structure
        text_content = clean_extracted_text(text_content)
        
        logger.info(f"Total extracted text: {len(text_content)} characters")
        return text_content
        
    except ValueError as ve:
        raise ve
    except Exception as e:
        logger.error(f"PDF parsing error: {str(e)}")
        raise Exception(f"PDF parsing error: {str(e)}")


def clean_extracted_text(text):
    """
    Clean extracted text while preserving important structure
    
    Args:
        text: Raw extracted text
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace but preserve line breaks
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines (3+) with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove empty lines at start and end
    text = text.strip()
    
    # Fix common PDF extraction issues
    # Fix broken words (hyphenated words split across lines)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    text = re.sub(r'([.,;:!?])\s*([A-Z])', r'\1 \2', text)
    
    return text


def validate_pdf(file):
    """
    Validate PDF file
    
    Args:
        file: FileStorage object or BytesIO object
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Handle BytesIO objects (from base64) vs FileStorage objects
    is_bytesio = hasattr(file, 'getvalue') and not hasattr(file, 'filename')
    
    if not is_bytesio:
        # FileStorage object - check filename
        if not hasattr(file, 'filename') or file.filename == '':
            return False, "No file selected"
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return False, "Only PDF files are allowed"
    
    # Check file size (works for both FileStorage and BytesIO)
    try:
        current_pos = file.tell()
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(current_pos)  # Reset to original position
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return False, "File size exceeds 5MB limit"
        
        if file_size == 0:
            return False, "File is empty"
        
        # Verify it's actually a PDF by checking magic bytes
        file.seek(0)
        magic_bytes = file.read(4)
        file.seek(0)  # Reset to start
        
        if magic_bytes != b'%PDF':
            return False, "File does not appear to be a valid PDF file"
        
    except Exception as e:
        logger.error(f"Error validating file: {str(e)}")
        return False, f"Error reading file: {str(e)}"
    
    return True, None

