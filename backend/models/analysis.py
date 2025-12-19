from pymongo import MongoClient, DESCENDING
from datetime import datetime
from bson import ObjectId
from config import Config
import logging

logger = logging.getLogger(__name__)


class AnalysisModel:
    """MongoDB model for analysis operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            # MongoDB Atlas connection string handling
            mongo_uri = Config.MONGO_URI
            # Ensure connection string ends properly
            if not mongo_uri.endswith('/'):
                mongo_uri += '/'
            # Add database name and connection options for Atlas
            if 'mongodb+srv://' in mongo_uri or 'mongodb://' in mongo_uri:
                # For Atlas, add retryWrites and other options
                if '?' not in mongo_uri:
                    mongo_uri = mongo_uri.rstrip('/') + '/?retryWrites=true&w=majority'
            
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[Config.DB_NAME]
            self.collection = self.db['analyses']
            
            # Create indexes for better performance (with error handling)
            try:
                self.collection.create_index([("created_at", DESCENDING)])
                self.collection.create_index("score")
            except Exception as idx_error:
                logger.warning(f"Index creation warning: {str(idx_error)}")
            
            # Test connection (non-blocking)
            try:
                self.client.server_info()
                logger.info("MongoDB connection established successfully")
            except Exception as conn_error:
                logger.warning(f"MongoDB connection test failed: {str(conn_error)}")
                logger.warning("App will continue but database operations may fail")
            
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            logger.warning("App will continue but database operations will fail")
            # Don't raise - allow app to start without MongoDB
            self.client = None
            self.db = None
            self.collection = None
    
    def create_analysis(self, data: dict) -> str:
        """
        Save analysis result to MongoDB
        
        Args:
            data (dict): Analysis data to save
            
        Returns:
            str: Inserted document ID
        """
        if not self.collection:
            raise Exception("MongoDB connection not available")
        try:
            document = {
                "resume_text": data.get("resume_text", ""),
                "resume_skills": data.get("resume_skills", []),
                "job_description": data.get("job_description", ""),
                "jd_skills": data.get("jd_skills", []),
                "matched_skills": data.get("matched_skills", []),
                "missing_skills": data.get("missing_skills", []),
                "score": data.get("score", 0),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(document)
            logger.info(f"Analysis created with ID: {result.inserted_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating analysis: {str(e)}")
            raise
    
    def get_analysis(self, analysis_id: str) -> dict:
        """
        Retrieve analysis by ID
        
        Args:
            analysis_id (str): Analysis document ID
            
        Returns:
            dict: Analysis document or None
        """
        if not self.collection:
            return None
        try:
            result = self.collection.find_one({"_id": ObjectId(analysis_id)})
            
            if result:
                result["_id"] = str(result["_id"])
                result["created_at"] = result["created_at"].isoformat()
                result["updated_at"] = result["updated_at"].isoformat()
                logger.info(f"Analysis retrieved: {analysis_id}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving analysis {analysis_id}: {str(e)}")
            return None
    
    def get_all_analyses(self, limit: int = 10, skip: int = 0) -> list:
        """
        Get recent analyses with pagination
        
        Args:
            limit (int): Number of documents to return
            skip (int): Number of documents to skip
            
        Returns:
            list: List of analysis documents
        """
        if not self.collection:
            return []
        try:
            cursor = self.collection.find().sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            analyses = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                doc["updated_at"] = doc["updated_at"].isoformat()
                analyses.append(doc)
            
            logger.info(f"Retrieved {len(analyses)} analyses")
            return analyses
            
        except Exception as e:
            logger.error(f"Error retrieving analyses: {str(e)}")
            return []
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete analysis by ID
        
        Args:
            analysis_id (str): Analysis document ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        if not self.collection:
            return False
        try:
            result = self.collection.delete_one({"_id": ObjectId(analysis_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Analysis deleted: {analysis_id}")
                return True
            else:
                logger.warning(f"Analysis not found: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting analysis {analysis_id}: {str(e)}")
            return False
    
    def get_statistics(self) -> dict:
        """
        Get overall statistics
        
        Returns:
            dict: Statistics data
        """
        if not self.collection:
            return {
                "total_analyses": 0,
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0
            }
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_analyses": {"$sum": 1},
                        "avg_score": {"$avg": "$score"},
                        "max_score": {"$max": "$score"},
                        "min_score": {"$min": "$score"}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                stats = result[0]
                stats.pop("_id")
                stats["avg_score"] = round(stats["avg_score"], 2)
                return stats
            else:
                return {
                    "total_analyses": 0,
                    "avg_score": 0,
                    "max_score": 0,
                    "min_score": 0
                }
                
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

