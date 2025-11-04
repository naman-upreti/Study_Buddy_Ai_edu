"""Document Retriever Module

Implements semantic search and retrieval for RAG systems using embeddings.
"""

from typing import List, Tuple
import numpy as np

from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class DocumentRetriever:
    """Retrieves relevant document chunks using semantic similarity."""
    
    def __init__(self, embedding_model=None):
        """Initialize the retriever.
        
        Args:
            embedding_model: Custom embedding model (optional)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.documents: List[str] = []
        self.embeddings: List[List[float]] = []
        self.embedding_model = embedding_model
        self.logger.info("DocumentRetriever initialized")
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts using a simple approach.
        
        For production, use proper embedding models like OpenAI, HuggingFace, etc.
        
        Args:
            texts: List of text chunks
            
        Returns:
            List of embedding vectors
        """
        try:
            if self.embedding_model:
                return self.embedding_model.embed_documents(texts)
            
            # Fallback: Simple TF-IDF style embeddings for demo
            embeddings = []
            for text in texts:
                # Create simple vector from word frequencies
                words = text.lower().split()
                # This is a simplified approach - in production use proper embeddings
                vector = np.zeros(300)  # 300-dimensional vector
                for word in words:
                    vector[hash(word) % 300] += 1.0
                embeddings.append(vector.tolist())
            
            return embeddings
        
        except Exception as e:
            error_msg = f"Failed to generate embeddings: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            float: Similarity score (0-1)
        """
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def add_documents(self, documents: List[str]) -> None:
        """Add documents to the retriever.
        
        Args:
            documents: List of document chunks
            
        Raises:
            CustomException: If adding documents fails
        """
        try:
            if not documents:
                raise CustomException("No documents provided")
            
            self.documents = documents
            self.embeddings = self._get_embeddings(documents)
            
            self.logger.info(f"Added {len(documents)} documents to retriever")
        
        except CustomException:
            raise
        except Exception as e:
            error_msg = f"Failed to add documents: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Retrieve top-k relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of tuples (document_chunk, relevance_score)
            
        Raises:
            CustomException: If retrieval fails
        """
        try:
            if not self.documents:
                raise CustomException("No documents in retriever. Add documents first.")
            
            # Generate embedding for query
            query_embedding = self._get_embeddings([query])[0]
            
            # Calculate similarity scores
            similarities = []
            for i, doc_embedding in enumerate(self.embeddings):
                score = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((i, score))
            
            # Sort by similarity and get top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_k_indices = similarities[:top_k]
            
            # Return documents with scores
            results = [
                (self.documents[idx], score)
                for idx, score in top_k_indices
                if score > 0
            ]
            
            self.logger.info(f"Retrieved {len(results)} documents for query")
            return results
        
        except CustomException:
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve documents: {str(e)}"
            self.logger.error(error_msg)
            raise CustomException(error_msg, e)
    
    def clear(self) -> None:
        """Clear all documents from the retriever."""
        self.documents = []
        self.embeddings = []
        self.logger.info("Retriever cleared")
