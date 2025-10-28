from typing import List, Tuple, Any, Dict


def parse_non_empty_args(args: List[Tuple[str, Any]]) -> Dict[str, Any]:
    # Slightly faster than comprehension in small cases, and avoids need for intermediate structures
    result: Dict[str, Any] = {}
    for arg_name, val in args:
        if val is not None:
            result[arg_name] = val
    return result
