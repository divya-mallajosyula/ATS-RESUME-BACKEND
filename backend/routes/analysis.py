from flask import Blueprint, request, jsonify
from utils.skill_matcher import extract_skills, calculate_match, get_skill_suggestions
from models.analysis import AnalysisModel
import logging

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Lazy initialization - only connect when needed
_analysis_model = None

def get_analysis_model():
    """Get or create AnalysisModel instance (lazy initialization)"""
    global _analysis_model
    if _analysis_model is None:
        _analysis_model = AnalysisModel()
    return _analysis_model


@analysis_bp.route('/analyze-match', methods=['POST'])
def analyze_match():
    """
    Analyze match between resume and job description
    
    Request:
        {
            "resume_skills": list,
            "job_description": str,
            "resume_text": str (optional)
        }
    
    Response:
        {
            "success": bool,
            "analysis_id": str,
            "score": float,
            "matched_skills": list,
            "missing_skills": list,
            "jd_skills": list,
            "suggestions": list (optional)
        }
    """
    try:
        # Log request details for debugging
        logger.info(f"Analysis request - Content-Type: {request.content_type}")
        logger.info(f"Analysis request - Method: {request.method}")
        
        data = request.get_json()
        
        # Log what we received
        if data:
            logger.info(f"Received data keys: {list(data.keys())}")
        else:
            logger.warning("No JSON data in request")
        
        # Validate input
        if not data:
            return jsonify({
                "success": False,
                "message": "No data provided. Please send JSON with 'resume_skills' and 'job_description' fields.",
                "debug_info": {
                    "content_type": request.content_type,
                    "has_data": False
                }
            }), 400
        
        # Try to get resume_skills with multiple possible field names
        resume_skills = None
        if 'resume_skills' in data:
            resume_skills = data['resume_skills']
        elif 'skills' in data:
            resume_skills = data['skills']
            logger.info("Using 'skills' field instead of 'resume_skills'")
        elif 'resumeSkills' in data:
            resume_skills = data['resumeSkills']
            logger.info("Using 'resumeSkills' field instead of 'resume_skills'")
        
        # Try to get job_description with multiple possible field names
        job_description = None
        if 'job_description' in data:
            job_description = data['job_description']
        elif 'jobDescription' in data:
            job_description = data['jobDescription']
            logger.info("Using 'jobDescription' field instead of 'job_description'")
        elif 'jobDescription' in data:
            job_description = data['jobDescription']
        elif 'description' in data:
            job_description = data['description']
            logger.info("Using 'description' field instead of 'job_description'")
        
        # Get resume_text (optional)
        resume_text = data.get('resume_text', '') or data.get('resumeText', '') or data.get('text', '') or data.get('extractedText', '')
        
        # If resume_skills is not provided but resume_text is, extract skills from text
        if not resume_skills and resume_text:
            logger.info("resume_skills not provided, extracting from resume_text")
            resume_skills = extract_skills(resume_text)
            logger.info(f"Extracted {len(resume_skills)} skills from resume text")
        
        # Validate required fields
        missing_fields = []
        if not resume_skills:
            missing_fields.append("resume_skills (or skills)")
        if not job_description:
            missing_fields.append("job_description (or jobDescription)")
        
        if missing_fields:
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "debug_info": {
                    "received_keys": list(data.keys()) if data else [],
                    "content_type": request.content_type
                }
            }), 400
        
        # Validate resume_skills is a list
        if not isinstance(resume_skills, list):
            # Try to convert if it's a string (comma-separated)
            if isinstance(resume_skills, str):
                resume_skills = [s.strip() for s in resume_skills.split(',') if s.strip()]
                logger.info(f"Converted string to list: {len(resume_skills)} skills")
            else:
                return jsonify({
                    "success": False,
                    "message": "resume_skills must be a list or comma-separated string"
                }), 400
        
        # Extract skills from job description
        jd_skills = extract_skills(job_description)
        logger.info(f"Extracted {len(jd_skills)} skills from job description")
        
        # Calculate match
        match_result = calculate_match(resume_skills, jd_skills)
        
        # Get suggestions if requested
        suggestions = []
        if data.get('include_suggestions', False):
            suggestions = get_skill_suggestions(match_result['missing_skills'])
        
        # Prepare data for database
        analysis_data = {
            "resume_text": resume_text,
            "resume_skills": resume_skills,
            "job_description": job_description,
            "jd_skills": jd_skills,
            "matched_skills": match_result['matched_skills'],
            "missing_skills": match_result['missing_skills'],
            "score": match_result['score']
        }
        
        # Save to database
        analysis_id = None
        try:
            analysis_model = get_analysis_model()
            analysis_id = analysis_model.create_analysis(analysis_data)
            logger.info(f"Analysis saved with ID: {analysis_id}")
        except Exception as db_error:
            logger.error(f"Failed to save analysis to database: {str(db_error)}")
            # Continue without saving - don't fail the request
        
        # Prepare response
        response = {
            "success": True,
            "score": match_result['score'],
            "matched_skills": match_result['matched_skills'],
            "missing_skills": match_result['missing_skills'],
            "jd_skills": jd_skills,
            "total_jd_skills": match_result['total_jd_skills'],
            "total_matched": match_result['total_matched'],
            "message": f"Match score: {match_result['score']}%"
        }
        
        # Add analysis_id if saved successfully
        if 'analysis_id' in locals():
            response["analysis_id"] = analysis_id
        
        # Add suggestions if requested
        if suggestions:
            response["suggestions"] = suggestions
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in analyze_match: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Analysis failed: {str(e)}"
        }), 500


@analysis_bp.route('/analysis-history', methods=['GET'])
def get_analysis_history():
    """
    Get analysis history with pagination
    
    Query Parameters:
        - limit (int): Number of results (default: 10)
        - skip (int): Number of results to skip (default: 0)
    
    Response:
        {
            "success": bool,
            "analyses": list,
            "total": int,
            "limit": int,
            "skip": int
        }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        skip = request.args.get('skip', 0, type=int)
        
        # Validate parameters
        if limit < 1 or limit > 100:
            limit = 10
        if skip < 0:
            skip = 0
        
        # Get analyses from database
        try:
            analysis_model = get_analysis_model()
            analyses = analysis_model.get_all_analyses(limit=limit, skip=skip)
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                "success": False,
                "message": "Database connection failed. Please ensure MongoDB is running."
            }), 503
        
        return jsonify({
            "success": True,
            "analyses": analyses,
            "limit": limit,
            "skip": skip,
            "count": len(analyses)
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_analysis_history: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve analysis history: {str(e)}"
        }), 500


@analysis_bp.route('/analysis/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """
    Get specific analysis by ID
    
    Response:
        {
            "success": bool,
            "analysis": dict or None
        }
    """
    try:
        analysis_model = get_analysis_model()
        analysis = analysis_model.get_analysis(analysis_id)
        
        if analysis:
            return jsonify({
                "success": True,
                "analysis": analysis
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Analysis not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in get_analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve analysis: {str(e)}"
        }), 500


@analysis_bp.route('/analysis/<analysis_id>', methods=['DELETE'])
def delete_analysis(analysis_id):
    """
    Delete analysis by ID
    
    Response:
        {
            "success": bool,
            "message": str
        }
    """
    try:
        analysis_model = get_analysis_model()
        deleted = analysis_model.delete_analysis(analysis_id)
        
        if deleted:
            return jsonify({
                "success": True,
                "message": "Analysis deleted successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Analysis not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error in delete_analysis: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to delete analysis: {str(e)}"
        }), 500


@analysis_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get overall statistics
    
    Response:
        {
            "success": bool,
            "statistics": dict
        }
    """
    try:
        analysis_model = get_analysis_model()
        stats = analysis_model.get_statistics()
        
        return jsonify({
            "success": True,
            "statistics": stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_statistics: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to retrieve statistics: {str(e)}"
        }), 500

