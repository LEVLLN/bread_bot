import re


def composite_mask(collection, split=True) -> str:
    mask_part = "\\b{}\\b" if split else "{}"
    return "|".join(
        map(
            lambda x: mask_part.format(re.escape(x)),
            collection,
        )
    )


async def async_composite_mask(collection, split=True) -> str:
    return composite_mask(collection, split)
