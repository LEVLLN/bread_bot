import re


def composite_mask(collection, split=True) -> str:
    mask_part = "\\b{}\\b" if split else "{}"
    return "|".join(
        mask_part.format(re.escape(x)) for x in sorted(collection, key=len, reverse=True)
    )
