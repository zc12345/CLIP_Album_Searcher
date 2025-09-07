import open_clip
from cn_clip import clip
from loguru import logger
import functools

@functools.lru_cache(maxsize=4)
def get_model(device="cpu", lang="en"):
    if lang == "zh-cn":
        model, preprocess = clip.load_from_name("ViT-B-16", device=device)
    else:
        model, _, preprocess = open_clip.create_model_and_transforms(
            'ViT-B-16', pretrained='laion2b_s34b_b88k'
        )
    model = model.to(device)
    model.eval()
    logger.debug(f"Initialized model")
    return model, preprocess


@functools.lru_cache(maxsize=4)
def get_tokenizer(lang="en"):
    if lang == "zh-cn":
        tokenizer = clip.tokenize
    else:
        tokenizer = open_clip.get_tokenizer('ViT-B-16')
    return tokenizer
