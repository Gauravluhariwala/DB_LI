"""
Chroma Vector Search Service
Semantic search for company specialties using Chroma Cloud
"""

import chromadb
from typing import List, Dict, Any

# Chroma Cloud credentials
CHROMA_API_KEY = "ck-FKdQTjDBNkXeXVuBSdqPTBJyPXmYawWSSNvubUvnCGUx"
CHROMA_TENANT = "599241ad-5097-4286-be4c-b7b36baaef1a"
CHROMA_DATABASE = "Tags"

class ChromaService:
    """
    Semantic search service for company specialties
    Uses Chroma Cloud vector database with 44,899 specialties
    """
    _instance = None
    _client = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize Chroma Cloud connection (singleton)"""
        if self._client is not None:
            return

        # Connect to Chroma Cloud (official CloudClient method)
        self._client = chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE
        )

        # Get collection
        self._collection = self._client.get_collection("company_specialties")

    @property
    def collection(self):
        """Get collection instance"""
        if self._collection is None:
            self._initialize()
        return self._collection

    def search_similar_specialties(
        self,
        query: str,
        n_results: int = 3,
        min_count: int = None,
        where: Dict[str, Any] = None,
        sort_by_count: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find specialties semantically similar to query

        Args:
            query: Search query (e.g., "artificial intelligence", "web dev")
            n_results: Number of results to return
            min_count: Optional minimum company count filter (e.g., only specialties with 10+ companies)
            where: Optional metadata filter dict (e.g., {"count": {"$gte": 10}})

        Returns:
            List of similar specialties with metadata and similarity scores

        Example:
            search_similar_specialties("AI", n_results=5, min_count=10)
            Returns: [
                {"specialty": "AI", "count": 79, "rank": 23, "similarity_score": 0.95},
                {"specialty": "Artificial Intelligence", "count": 57, "rank": 47, "similarity_score": 0.87},
                ...
            ]
        """
        try:
            # Build where clause for filtering
            where_clause = where or {}
            if min_count is not None:
                where_clause["count"] = {"$gte": min_count}

            # Query with explicit include parameter for documents, metadatas, and distances
            query_params = {
                "query_texts": [query],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]  # Specify what to return
            }

            # Add where clause if filters exist
            if where_clause:
                query_params["where"] = where_clause

            results = self.collection.query(**query_params)

            # Format results with actual similarity scores
            similar_specialties = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                similar_specialties.append({
                    'specialty': doc,
                    'count': metadata.get('count', 0),
                    'rank': metadata.get('rank', i + 1),
                    'similarity_score': round(1.0 - distance, 4)  # Convert distance to similarity (0-1)
                })

            # Sort by count AND similarity (both descending) if requested
            if sort_by_count:
                similar_specialties.sort(key=lambda x: (x['count'], x['similarity_score']), reverse=True)

            return similar_specialties

        except Exception as e:
            print(f"Error searching specialties: {e}")
            return []

    def expand_specialty_query(
        self,
        user_query: str,
        expansion_count: int = 5
    ) -> List[str]:
        """
        Expand user query to include similar specialties

        Args:
            user_query: User's search term (e.g., "AI")
            expansion_count: How many similar terms to include

        Returns:
            List of specialty names including original + similar

        Example:
            expand_specialty_query("AI", 5)
            Returns: ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "Data Science"]

        Use case:
            User searches for "AI companies"
            Expand to companies with ANY of: AI, Artificial Intelligence, Machine Learning, etc.
        """
        similar = self.search_similar_specialties(user_query, expansion_count)

        # Extract just the specialty names
        expanded_terms = [s['specialty'] for s in similar]

        return expanded_terms

    def get_specialty_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the specialty database

        Returns:
            Dictionary with collection stats
        """
        try:
            count = self.collection.count()

            return {
                'total_specialties': count,
                'database': CHROMA_DATABASE,
                'collection': self.collection.name,
                'status': 'active'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Global instance
chroma_service = ChromaService()
