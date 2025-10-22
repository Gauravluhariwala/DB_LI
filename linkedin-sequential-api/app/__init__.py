# LinkedIn Sequential Search API

# CRITICAL: Override sqlite3 with pysqlite3 for AWS Lambda compatibility
# Lambda has SQLite 3.7.17, but ChromaDB requires >= 3.35.0
# Even CloudClient (HTTP-only) triggers this check on import
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    # pysqlite3 not available (local dev), use system sqlite3
    pass

# CRITICAL: Set cache directories to /tmp for Lambda (read-only filesystem)
import os
os.environ['HF_HOME'] = '/tmp/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'
os.environ['XDG_CACHE_HOME'] = '/tmp/cache'
