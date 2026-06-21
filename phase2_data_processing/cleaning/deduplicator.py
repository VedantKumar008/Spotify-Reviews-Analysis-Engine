"""
Deduplication Module
Detects and removes duplicate and near-duplicate content using MinHash and LSH
"""

from typing import Dict, Any, List, Set, Tuple
import logging
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from datasketch import MinHash, MinHashLSH
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class DeduplicationResult:
    """Result of deduplication"""
    original_count: int
    duplicate_count: int
    unique_count: int
    duplicate_pairs: List[Tuple[str, str]]
    near_duplicate_pairs: List[Tuple[str, str, float]]


class Deduplicator:
    """
    Deduplicates reviews using exact and near-duplicate detection
    Uses MinHash and LSH for efficient near-duplicate detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize deduplicator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.exact_duplicates: Set[str] = set()
        self.near_duplicate_threshold = config.get('near_duplicate_threshold', 0.8)
        self.num_permutations = config.get('num_permutations', 128)
        self.lsh_threshold = config.get('lsh_threshold', 0.7)
    
    def deduplicate(
        self,
        reviews: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], DeduplicationResult]:
        """
        Deduplicate reviews
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            Tuple of (deduplicated reviews, deduplication result)
        """
        logger.info(f"Starting deduplication for {len(reviews)} reviews")
        
        # Step 1: Exact duplicate detection
        exact_duplicates = self._find_exact_duplicates(reviews)
        logger.info(f"Found {len(exact_duplicates)} exact duplicate groups")
        
        # Step 2: Near-duplicate detection
        near_duplicates = self._find_near_duplicates(reviews)
        logger.info(f"Found {len(near_duplicates)} near-duplicate pairs")
        
        # Step 3: Build deduplicated list
        deduplicated = self._build_deduplicated_list(
            reviews,
            exact_duplicates,
            near_duplicates
        )
        
        # Build result
        duplicate_pairs = []
        for group in exact_duplicates:
            for i in range(1, len(group)):
                duplicate_pairs.append((group[0], group[i]))
        
        result = DeduplicationResult(
            original_count=len(reviews),
            duplicate_count=len(duplicate_pairs) + len(near_duplicates),
            unique_count=len(deduplicated),
            duplicate_pairs=duplicate_pairs,
            near_duplicate_pairs=near_duplicates
        )
        
        logger.info(f"Deduplication complete: {result.unique_count} unique reviews")
        
        return deduplicated, result
    
    def _find_exact_duplicates(
        self,
        reviews: List[Dict[str, Any]]
    ) -> List[List[str]]:
        """
        Find exact duplicates using content hashing
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            List of duplicate groups (each group is a list of review IDs)
        """
        content_hashes: Dict[str, List[str]] = {}
        
        for review in reviews:
            review_id = review.get('review_id')
            content = review.get('content', '')
            
            # Create hash of content
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            if content_hash not in content_hashes:
                content_hashes[content_hash] = []
            
            content_hashes[content_hash].append(review_id)
        
        # Filter to only groups with duplicates
        duplicate_groups = [
            group for group in content_hashes.values()
            if len(group) > 1
        ]
        
        return duplicate_groups
    
    def _find_near_duplicates(
        self,
        reviews: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, float]]:
        """
        Find near-duplicates using MinHash and LSH
        
        Args:
            reviews: List of review dictionaries
            
        Returns:
            List of (review_id_1, review_id_2, similarity) tuples
        """
        if len(reviews) < 2:
            return []
        
        # Create MinHash for each review
        minhashes: Dict[str, MinHash] = {}
        review_ids = []
        
        for review in reviews:
            review_id = review.get('review_id')
            content = review.get('content', '')
            
            # Tokenize content
            tokens = self._tokenize(content)
            
            # Create MinHash
            minhash = MinHash(num_perm=self.num_permutations)
            for token in tokens:
                minhash.update(token.encode('utf-8'))
            
            minhashes[review_id] = minhash
            review_ids.append(review_id)
        
        # Create LSH index
        lsh = MinHashLSH(
            threshold=self.lsh_threshold,
            num_perm=self.num_permutations
        )
        
        for review_id in review_ids:
            lsh.insert(review_id, minhashes[review_id])
        
        # Find near-duplicates
        near_duplicates = []
        checked_pairs: Set[Tuple[str, str]] = set()
        
        for review_id in review_ids:
            # Query LSH for similar items
            similar = lsh.query(minhashes[review_id])
            
            for similar_id in similar:
                if similar_id == review_id:
                    continue
                
                # Avoid checking same pair twice
                pair = tuple(sorted((review_id, similar_id)))
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                
                # Calculate actual Jaccard similarity
                similarity = minhashes[review_id].jaccard(minhashes[similar_id])
                
                if similarity >= self.near_duplicate_threshold:
                    near_duplicates.append((review_id, similar_id, similarity))
        
        return near_duplicates
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for MinHash
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Simple tokenization - split into words and n-grams
        words = text.lower().split()
        
        # Add 3-grams
        tokens = words.copy()
        for i in range(len(words) - 2):
            trigram = ' '.join(words[i:i+3])
            tokens.append(trigram)
        
        return tokens
    
    def _build_deduplicated_list(
        self,
        reviews: List[Dict[str, Any]],
        exact_duplicates: List[List[str]],
        near_duplicates: List[Tuple[str, str, float]]
    ) -> List[Dict[str, Any]]:
        """
        Build deduplicated list keeping only unique reviews
        
        Args:
            reviews: Original reviews
            exact_duplicates: Exact duplicate groups
            near_duplicates: Near-duplicate pairs
            
        Returns:
            Deduplicated list of reviews
        """
        # Create set of review IDs to remove
        to_remove: Set[str] = set()
        
        # Add exact duplicates (keep first, remove rest)
        for group in exact_duplicates:
            for review_id in group[1:]:
                to_remove.add(review_id)
        
        # Add near-duplicates (keep one based on criteria)
        for id1, id2, similarity in near_duplicates:
            # Keep the one with more metadata or earlier timestamp
            review1 = next((r for r in reviews if r.get('review_id') == id1), None)
            review2 = next((r for r in reviews if r.get('review_id') == id2), None)
            
            if not review1 or not review2:
                continue
            
            # If one is already marked for removal, skip
            if id1 in to_remove or id2 in to_remove:
                continue
            
            # Decide which to keep
            to_remove_id = self._choose_to_remove(review1, review2)
            to_remove.add(to_remove_id)
        
        # Build deduplicated list
        deduplicated = [
            review for review in reviews
            if review.get('review_id') not in to_remove
        ]
        
        return deduplicated
    
    def _choose_to_remove(
        self,
        review1: Dict[str, Any],
        review2: Dict[str, Any]
    ) -> str:
        """
        Choose which review to remove based on quality criteria
        
        Args:
            review1: First review
            review2: Second review
            
        Returns:
            Review ID to remove
        """
        # Prefer reviews with more metadata
        metadata1 = review1.get('metadata', {})
        metadata2 = review2.get('metadata', {})
        
        if len(metadata1) > len(metadata2):
            return review2.get('review_id')
        elif len(metadata2) > len(metadata1):
            return review1.get('review_id')
        
        # Prefer reviews with timestamps
        timestamp1 = review1.get('timestamp')
        timestamp2 = review2.get('timestamp')
        
        if timestamp1 and not timestamp2:
            return review2.get('review_id')
        elif timestamp2 and not timestamp1:
            return review1.get('review_id')
        
        # Prefer earlier review
        if timestamp1 and timestamp2:
            if timestamp1 < timestamp2:
                return review2.get('review_id')
            else:
                return review1.get('review_id')
        
        # Default: keep the first one
        return review2.get('review_id')
    
    def cross_source_deduplication(
        self,
        reviews_by_source: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Deduplicate reviews across different sources
        
        Args:
            reviews_by_source: Dictionary mapping source to list of reviews
            
        Returns:
            Dictionary with deduplicated reviews per source
        """
        logger.info("Starting cross-source deduplication")
        
        # Combine all reviews
        all_reviews = []
        for source, reviews in reviews_by_source.items():
            for review in reviews:
                review['source'] = source
                all_reviews.append(review)
        
        # Deduplicate
        deduplicated, result = self.deduplicate(all_reviews)
        
        # Split back by source
        deduplicated_by_source: Dict[str, List[Dict[str, Any]]] = {}
        for review in deduplicated:
            source = review.get('source')
            if source not in deduplicated_by_source:
                deduplicated_by_source[source] = []
            deduplicated_by_source[source].append(review)
        
        logger.info(f"Cross-source deduplication complete")
        
        return deduplicated_by_source
