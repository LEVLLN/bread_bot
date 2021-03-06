import re


async def composite_mask(collection, split=True) -> str:
    mask_part = "\\b{}\\b" if split else "{}"
    return '|'.join(
        map(
            lambda x: mask_part.format(re.escape(x)),
            collection,
        )
    )
