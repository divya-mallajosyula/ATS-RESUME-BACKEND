# ATS Resume Analyzer API Documentation

**Base URL:** `http://localhost:5000`  
**API Prefix:** `/api`

---

## 📋 Table of Contents

1. [General Information](#general-information)
2. [Upload Endpoints](#upload-endpoints)
3. [Analysis Endpoints](#analysis-endpoints)
4. [Utility Endpoints](#utility-endpoints)
5. [Error Handling](#error-handling)

---

## General Information

### Base Endpoints

#### `GET /`
Get API information

**Response:**
```json
{
  "message": "ATS Resume Analyzer API",
  "version": "1.0.0",
  "endpoints": {
    "upload": "/api/upload-resume",
    "analyze": "/api/analyze-match",
    "history": "/api/analysis-history"
  }
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy"
}
```

**Status Code:** `200`

---

## Upload Endpoints

### 1. Upload Resume

**Endpoint:** `POST /api/upload-resume`

**Description:** Upload a PDF resume and extract text + skills

**Content-Type:** `multipart/form-data` or `application/json`

**Request Body (multipart/form-data):**
- Field name can be: `file`, `resume`, `pdf`, `document`, or `upload`
- File must be a PDF (max 5MB)

**Request Body (JSON with base64):**
```json
{
  "file": "base64_encoded_pdf_string",
  "filename": "resume.pdf"  // optional
}
```

**Success Response (200):**
```json
{
  "success": true,
  "text": "Extracted text from PDF...",
  "extractedText": "Extracted text from PDF...",
  "skills": ["Python", "JavaScript", "React", "Node.js"],
  "message": "Resume processed successfully. Found 4 skills.",
  "stats": {
    "character_count": 2500,
    "word_count": 450,
    "skill_count": 4
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "No file uploaded. Please send file as multipart/form-data...",
  "debug_info": {
    "content_type": "application/json",
    "files_keys": [],
    "form_keys": []
  }
}
```

**Error Response (400) - Invalid PDF:**
```json
{
  "success": false,
  "message": "Only PDF files are allowed",
  "error_type": "extraction_error"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload-resume \
  -F "file=@resume.pdf"
```

**JavaScript Example:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:5000/api/upload-resume', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.skills); // Array of extracted skills
```

---

### 2. Validate PDF

**Endpoint:** `POST /api/validate-pdf`

**Description:** Validate PDF file without processing

**Content-Type:** `multipart/form-data`

**Request Body:**
- Field name: `file`
- File must be a PDF

**Success Response (200):**
```json
{
  "success": true,
  "valid": true,
  "message": "File is valid"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "valid": false,
  "message": "Only PDF files are allowed"
}
```

---

## Analysis Endpoints

### 1. Analyze Match

**Endpoint:** `POST /api/analyze-match`

**Description:** Analyze match between resume and job description

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "resume_skills": ["Python", "JavaScript", "React"],
  "job_description": "We are looking for a Python developer with React experience...",
  "resume_text": "Optional: Full resume text...",
  "include_suggestions": false  // optional
}
```

**Alternative Field Names Supported:**
- `resume_skills` → `skills` or `resumeSkills`
- `job_description` → `jobDescription` or `description`
- `resume_text` → `resumeText` or `text` or `extractedText`

**Note:** If `resume_skills` is not provided but `resume_text` is, skills will be automatically extracted.

**Success Response (200):**
```json
{
  "success": true,
  "analysis_id": "507f1f77bcf86cd799439011",
  "score": 75.5,
  "matched_skills": ["Python", "React"],
  "missing_skills": ["Docker", "AWS"],
  "jd_skills": ["Python", "React", "Docker", "AWS"],
  "total_jd_skills": 4,
  "total_matched": 2,
  "message": "Match score: 75.5%",
  "suggestions": [
    "Learn Docker through online courses or projects",
    "Consider gaining experience with AWS"
  ]
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Missing required fields: resume_skills (or skills), job_description (or jobDescription)",
  "debug_info": {
    "received_keys": ["resume_text"],
    "content_type": "application/json"
  }
}
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:5000/api/analyze-match', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    resume_skills: ['Python', 'JavaScript', 'React'],
    job_description: 'Looking for a full-stack developer...',
    include_suggestions: true
  })
});

const data = await response.json();
console.log(`Match Score: ${data.score}%`);
console.log(`Matched: ${data.matched_skills}`);
console.log(`Missing: ${data.missing_skills}`);
```

---

### 2. Get Analysis History

**Endpoint:** `GET /api/analysis-history`

**Description:** Get analysis history with pagination

**Query Parameters:**
- `limit` (int, optional): Number of results (default: 10, max: 100)
- `skip` (int, optional): Number of results to skip (default: 0)

**Success Response (200):**
```json
{
  "success": true,
  "analyses": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "resume_text": "...",
      "resume_skills": ["Python", "JavaScript"],
      "job_description": "...",
      "jd_skills": ["Python", "React"],
      "matched_skills": ["Python"],
      "missing_skills": ["React"],
      "score": 50.0,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "limit": 10,
  "skip": 0,
  "count": 1
}
```

**Error Response (503):**
```json
{
  "success": false,
  "message": "Database connection failed. Please ensure MongoDB is running."
}
```

**Example:**
```bash
curl "http://localhost:5000/api/analysis-history?limit=20&skip=0"
```

---

### 3. Get Specific Analysis

**Endpoint:** `GET /api/analysis/<analysis_id>`

**Description:** Get specific analysis by ID

**URL Parameters:**
- `analysis_id` (string): MongoDB ObjectId of the analysis

**Success Response (200):**
```json
{
  "success": true,
  "analysis": {
    "_id": "507f1f77bcf86cd799439011",
    "resume_text": "...",
    "resume_skills": ["Python", "JavaScript"],
    "job_description": "...",
    "jd_skills": ["Python", "React"],
    "matched_skills": ["Python"],
    "missing_skills": ["React"],
    "score": 50.0,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Analysis not found"
}
```

**Example:**
```bash
curl http://localhost:5000/api/analysis/507f1f77bcf86cd799439011
```

---

### 4. Delete Analysis

**Endpoint:** `DELETE /api/analysis/<analysis_id>`

**Description:** Delete analysis by ID

**URL Parameters:**
- `analysis_id` (string): MongoDB ObjectId of the analysis

**Success Response (200):**
```json
{
  "success": true,
  "message": "Analysis deleted successfully"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Analysis not found"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/analysis/507f1f77bcf86cd799439011
```

---

### 5. Get Statistics

**Endpoint:** `GET /api/statistics`

**Description:** Get overall statistics about analyses

**Success Response (200):**
```json
{
  "success": true,
  "statistics": {
    "total_analyses": 150,
    "avg_score": 65.5,
    "max_score": 95.0,
    "min_score": 20.0
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/statistics
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "error_type": "error_category",  // optional
  "debug_info": {                  // optional
    "content_type": "...",
    "files_keys": []
  }
}
```

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (validation errors, missing fields)
- `404` - Not Found (resource doesn't exist)
- `413` - Payload Too Large (file exceeds 5MB)
- `500` - Internal Server Error
- `503` - Service Unavailable (database connection issues)

### Common Error Messages

1. **No file uploaded:**
   ```json
   {
     "success": false,
     "message": "No file uploaded. Please send file as multipart/form-data..."
   }
   ```

2. **Invalid file type:**
   ```json
   {
     "success": false,
     "message": "Only PDF files are allowed"
   }
   ```

3. **File too large:**
   ```json
   {
     "success": false,
     "message": "File size exceeds 5MB limit"
   }
   ```

4. **Missing required fields:**
   ```json
   {
     "success": false,
     "message": "Missing required fields: resume_skills and job_description"
   }
   ```

5. **PDF extraction failed:**
   ```json
   {
     "success": false,
     "message": "No text could be extracted from PDF...",
     "error_type": "extraction_error"
   }
   ```

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8081`
- Custom frontend URL (configured in `.env`)

**Allowed Methods:** `GET`, `POST`, `DELETE`, `OPTIONS`

**Allowed Headers:** `Content-Type`, `Authorization`

---

## Rate Limits

Currently, there are no rate limits implemented. Consider implementing rate limiting for production use.

---

## File Size Limits

- Maximum file size: **5MB**
- Supported file type: **PDF only**

---

## Database

- **Database:** MongoDB Atlas
- **Collection:** `analyses`
- **Indexes:** 
  - `created_at` (descending)
  - `score`

---

## Example Workflow

### Complete Analysis Workflow

1. **Upload Resume:**
   ```javascript
   const uploadResponse = await fetch('http://localhost:5000/api/upload-resume', {
     method: 'POST',
     body: formData
   });
   const uploadData = await uploadResponse.json();
   // uploadData.skills contains extracted skills
   // uploadData.extractedText contains resume text
   ```

2. **Analyze Match:**
   ```javascript
   const analyzeResponse = await fetch('http://localhost:5000/api/analyze-match', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       resume_skills: uploadData.skills,
       job_description: jobDescriptionText,
       resume_text: uploadData.extractedText,
       include_suggestions: true
     })
   });
   const analysisData = await analyzeResponse.json();
   // analysisData.score contains match percentage
   // analysisData.matched_skills contains matched skills
   // analysisData.missing_skills contains missing skills
   ```

3. **View History:**
   ```javascript
   const historyResponse = await fetch('http://localhost:5000/api/analysis-history?limit=10');
   const historyData = await historyResponse.json();
   // historyData.analyses contains list of past analyses
   ```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Analysis IDs are MongoDB ObjectIds (24 character hex strings)
- Skills are case-insensitive but returned with original casing from database
- The API automatically extracts skills from job descriptions
- If `resume_skills` is not provided, the API will extract them from `resume_text` if available

