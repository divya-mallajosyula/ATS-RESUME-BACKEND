from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.pdf_parser import extract_text_from_pdf, validate_pdf
from utils.skill_matcher import extract_skills
import logging
import base64
import io

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    """
    Upload PDF resume and extract text + skills
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: file (PDF) - can be sent as 'file', 'resume', or 'pdf'
    
    Response:
        {
            "success": bool,
            "text": str,
            "skills": list,
            "message": str
        }
    """
    try:
        # Log request details for debugging
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Request files keys: {list(request.files.keys())}")
        logger.info(f"Request form keys: {list(request.form.keys())}")
        
        # Try to find the file with multiple possible field names
        file = None
        file_field_name = None
        
        # Common field names for file uploads
        possible_field_names = ['file', 'resume', 'pdf', 'document', 'upload']
        
        for field_name in possible_field_names:
            if field_name in request.files:
                file = request.files[field_name]
                file_field_name = field_name
                logger.info(f"Found file in field: {field_name}")
                break
        
        # If no file found in multipart/form-data, try JSON with base64
        if not file:
            # Check if files dict exists but is empty
            if request.files:
                logger.warning(f"Request has files dict but no file found. Keys: {list(request.files.keys())}")
            else:
                logger.warning("No files in request.files, trying JSON format")
            
            # Try to get file from JSON (base64 encoded)
            if request.is_json:
                try:
                    data = request.get_json()
                    logger.info("Request is JSON, checking for base64 file")
                    
                    # Check for base64 file in various possible keys
                    base64_file = None
                    for key in ['file', 'resume', 'pdf', 'data', 'content']:
                        if key in data:
                            base64_file = data[key]
                            logger.info(f"Found base64 file in key: {key}")
                            break
                    
                    if base64_file:
                        # Decode base64
                        try:
                            # Remove data URL prefix if present
                            if ',' in base64_file:
                                base64_file = base64_file.split(',')[1]
                            
                            pdf_bytes = base64.b64decode(base64_file)
                            # Create a file-like object from bytes
                            file = io.BytesIO(pdf_bytes)
                            file.filename = data.get('filename', 'resume.pdf')
                            logger.info(f"Successfully decoded base64 file: {file.filename}")
                        except Exception as decode_error:
                            logger.error(f"Failed to decode base64: {str(decode_error)}")
                            return jsonify({
                                "success": False,
                                "message": f"Invalid base64 file data: {str(decode_error)}"
                            }), 400
                except Exception as json_error:
                    logger.error(f"Error parsing JSON: {str(json_error)}")
            
            # If still no file, return error
            if not file:
                return jsonify({
                    "success": False,
                    "message": "No file uploaded. Please send file as multipart/form-data with field name 'file', 'resume', or 'pdf'.",
                    "debug_info": {
                        "content_type": request.content_type,
                        "is_json": request.is_json,
                        "files_keys": list(request.files.keys()) if request.files else [],
                        "form_keys": list(request.form.keys()) if request.form else []
                    }
                }), 400
        
        # Check if file is actually provided (not empty)
        if file.filename == '':
            logger.warning("File field exists but filename is empty")
            return jsonify({
                "success": False,
                "message": "No file selected. Please choose a PDF file to upload."
            }), 400
        
        # Validate file
        is_valid, error_message = validate_pdf(file)
        if not is_valid:
            logger.warning(f"File validation failed: {error_message}")
            return jsonify({
                "success": False,
                "message": error_message
            }), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        logger.info(f"Processing file: {filename} (from field: {file_field_name}, size: {len(file.read())} bytes)")
        file.seek(0)  # Reset file pointer after reading size
        
        # Extract text from PDF
        try:
            text = extract_text_from_pdf(file)
            logger.info(f"Extracted {len(text)} characters from PDF")
            
            # Log a preview of extracted text for debugging
            preview = text[:200] + "..." if len(text) > 200 else text
            logger.debug(f"Text preview: {preview}")
            
        except ValueError as ve:
            logger.error(f"Text extraction failed: {str(ve)}")
            return jsonify({
                "success": False,
                "message": str(ve),
                "error_type": "extraction_error"
            }), 400
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "message": f"Failed to parse PDF: {str(e)}",
                "error_type": "parsing_error"
            }), 500
        
        # Extract skills
        skills = extract_skills(text)
        logger.info(f"Extracted {len(skills)} skills")
        
        # Success response
        return jsonify({
            "success": True,
            "text": text,
            "extractedText": text,  # Frontend compatibility
            "skills": skills,
            "message": f"Resume processed successfully. Found {len(skills)} skills.",
            "stats": {
                "character_count": len(text),
                "word_count": len(text.split()),
                "skill_count": len(skills)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error in upload_resume: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while processing your resume"
        }), 500


@upload_bp.route('/validate-pdf', methods=['POST'])
def validate_pdf_endpoint():
    """
    Validate PDF file without processing
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: file (PDF)
    
    Response:
        {
            "success": bool,
            "valid": bool,
            "message": str
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "success": False,
                "valid": False,
                "message": "No file uploaded"
            }), 400
        
        file = request.files['file']
        is_valid, error_message = validate_pdf(file)
        
        if is_valid:
            return jsonify({
                "success": True,
                "valid": True,
                "message": "File is valid"
            }), 200
        else:
            return jsonify({
                "success": False,
                "valid": False,
                "message": error_message
            }), 400
            
    except Exception as e:
        logger.error(f"Error in validate_pdf_endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "valid": False,
            "message": "Validation failed"
        }), 500

