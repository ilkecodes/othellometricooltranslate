from typing import List, Any, Dict


def paginate(items: List[Any], page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    page = max(page, 1)
    start = (page - 1) * page_size
    end = start + page_size
    total = len(items)
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    }
