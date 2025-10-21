"""
OpenSearch Client Service
Singleton pattern with connection pooling for Lambda efficiency
"""

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from app.config import settings

class OpenSearchClient:
    """
    Singleton OpenSearch client with connection pooling
    Reuses connection across Lambda invocations for better performance
    """
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_client()
        return cls._instance

    def _initialize_client(self):
        """Initialize OpenSearch client once"""
        if self._client is not None:
            return

        # Get AWS credentials
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            settings.aws_region,
            'aoss',  # Service name for OpenSearch Serverless
            session_token=credentials.token
        )

        # Create client with connection pooling
        self._client = OpenSearch(
            hosts=[{
                'host': settings.opensearch_endpoint,
                'port': 443
            }],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30,
            max_retries=2,
            retry_on_timeout=True,
            pool_maxsize=10  # Connection pooling for Lambda
        )

    @property
    def client(self):
        """Get OpenSearch client instance"""
        if self._client is None:
            self._initialize_client()
        return self._client

# Global instance
opensearch_client = OpenSearchClient()
