from typing import Dict, List, Optional, Tuple

BOUNDARY_CM = 1.5

# Men's Tops chest ranges in cm: (min inclusive, max exclusive), smallest to largest.
# H&M: official chart. Zara: sizecharter.com (inches, converted; XS extrapolated).
# Uniqlo: sizecharter.com (inches, converted; XS extrapolated). Verify against brand pages.
BRAND_SIZE_CHARTS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "H&M": {
        "XS": (78, 86), "S": (86, 94), "M": (94, 102), "L": (102, 110),
        "XL": (110, 118), "XXL": (118, 126), "3XL": (126, 134),
    },
    "Zara": {
        "XS": (83.8, 88.9), "S": (88.9, 94.0), "M": (94.0, 99.1),
        "L": (99.1, 104.1), "XL": (104.1, 109.2), "XXL": (109.2, 114.3),
    },
    "Uniqlo": {
        "XS": (81.3, 88.9), "S": (88.9, 96.5), "M": (96.5, 104.1),
        "L": (104.1, 111.8), "XL": (111.8, 119.4), "XXL": (119.4, 127.0),
    },
}


def list_brands() -> List[str]:
    """Returns the brands that have a sizing chart."""
    return list(BRAND_SIZE_CHARTS)


def _boundary_warning(labels: List[str], idx: int, chest_cm: float, low: float, high: float) -> Optional[str]:
    """Warns when the chest is within BOUNDARY_CM of a neighbouring size."""
    if high - chest_cm <= BOUNDARY_CM and idx < len(labels) - 1:
        return (f"You are very close to a {labels[idx + 1]}. "
                f"For a looser fit, size up.")
    if chest_cm - low <= BOUNDARY_CM and idx > 0:
        return (f"You are very close to a {labels[idx - 1]}. "
                f"For a closer fit, size down.")
    return None


def recommend_size(chest_cm: float, brand: str = "H&M") -> Dict[str, object]:
    """Returns {"size", "range", "boundary_warning"}; size is None when out of range."""
    chart = BRAND_SIZE_CHARTS[brand]
    labels = list(chart)
    smallest_min, largest_max = chart[labels[0]][0], chart[labels[-1]][1]

    if chest_cm < smallest_min or chest_cm > largest_max:
        side = "below" if chest_cm < smallest_min else "above"
        return {"size": None, "range": None, "boundary_warning": None,
                "message": f"{chest_cm} cm is {side} {brand}'s standard range "
                           f"({smallest_min}-{largest_max} cm)."}

    for idx, label in enumerate(labels):
        low, high = chart[label]
        # Shared edges go to the larger size; the very top of the largest size is included
        if low <= chest_cm < high or (idx == len(labels) - 1 and chest_cm == high):
            return {"size": label, "range": (low, high), "message": None,
                    "boundary_warning": _boundary_warning(labels, idx, chest_cm, low, high)}
    return {"size": None, "range": None, "boundary_warning": None, "message": "Out of standard range."}


if __name__ == "__main__":
    for brand in list_brands():
        print(brand, recommend_size(106.1, brand))
