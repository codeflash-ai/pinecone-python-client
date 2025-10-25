from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SearchQueryVector:
    """
    SearchQueryVector represents the vector values used to query.
    """

    values: Optional[List[float]] = None
    """
    The vector data included in the search request.
    Optional.
    """

    sparse_values: Optional[List[float]] = None
    """
    The sparse embedding values to search with.
    Optional.
    """

    sparse_indices: Optional[List[int]] = None
    """
    The sparse embedding indices to search with.
    Optional.
    """

    def as_dict(self) -> dict:
        """
        Returns the SearchQueryVector as a dictionary.
        """
        # Directly construct the dictionary only with non-None attributes
        result = {}
        values = self.values
        if values is not None:
            result["values"] = values
        sparse_values = self.sparse_values
        if sparse_values is not None:
            result["sparse_values"] = sparse_values
        sparse_indices = self.sparse_indices
        if sparse_indices is not None:
            result["sparse_indices"] = sparse_indices
        return result
