import random
from typing import List, Any, Dict


def shuffle_part_results(ebay_parts: List[Any], aliexpress_parts: List[Any]) -> List[Any]:
    """
    Shuffle parts from eBay and AliExpress in a balanced way
    
    Args:
        ebay_parts: List of eBay parts
        aliexpress_parts: List of AliExpress parts
        
    Returns:
        List of shuffled parts
    """
    combined = []
    
    # Create iterator for each source
    ebay_iter = iter(ebay_parts)
    aliexpress_iter = iter(aliexpress_parts)
    
    # Flags to track if iterators are exhausted
    ebay_exhausted = False
    aliexpress_exhausted = False
    
    # Continue while both iterators have items
    while not (ebay_exhausted and aliexpress_exhausted):
        # Take 1-2 items from eBay
        if not ebay_exhausted:
            for _ in range(random.randint(1, 2)):
                try:
                    combined.append(next(ebay_iter))
                except StopIteration:
                    ebay_exhausted = True
                    break
        
        # Take 1-2 items from AliExpress
        if not aliexpress_exhausted:
            for _ in range(random.randint(1, 2)):
                try:
                    combined.append(next(aliexpress_iter))
                except StopIteration:
                    aliexpress_exhausted = True
                    break
            
    return combined


def shuffle_multiple_sources(parts_by_source: Dict[str, List[Any]]) -> List[Any]:
    """
    Shuffle parts from multiple sources in a balanced way
    
    Args:
        parts_by_source: Dictionary mapping source names to lists of parts
        
    Returns:
        List of shuffled parts
    """
    if not parts_by_source:
        return []
    
    # If only one source, return its parts
    if len(parts_by_source) == 1:
        return list(parts_by_source.values())[0]
    
    combined = []
    iterators = {source: iter(parts) for source, parts in parts_by_source.items()}
    exhausted = {source: False for source in parts_by_source.keys()}
    
    # Continue while any iterator has items
    while not all(exhausted.values()):
        # For each source, take 1-2 items
        for source, iterator in iterators.items():
            if exhausted[source]:  # Skip exhausted iterators
                continue
                
            for _ in range(random.randint(1, 2)):
                try:
                    combined.append(next(iterator))
                except StopIteration:
                    # Mark this iterator as exhausted
                    exhausted[source] = True
                    break
    
    return combined