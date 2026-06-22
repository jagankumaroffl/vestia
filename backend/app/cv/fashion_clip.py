"""
FashionCLIP inference module.

Model : patrickjohncyh/fashion-clip
       CLIP architecture fine-tuned on ~700k fashion product images.

Used for:
  - Zero-shot category / subcategory / style / pattern / season / gender classification
  - 512-dim L2-normalised embedding extraction for FAISS indexing
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Dict, List, Tuple

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger(__name__)

MODEL_NAME = "patrickjohncyh/fashion-clip"

# ── Classification label sets ─────────────────────────────────────────────────
# Each set maps to one predicted attribute.
# Keys in *_KEYS lists must align positionally with *_LABELS prompts.

CATEGORY_PROMPTS: List[str] = [
    "a photo of a shirt or top worn on the upper body",
    "a photo of trousers or bottoms worn on the lower body",
    "a photo of shoes or footwear",
    "a photo of an outerwear jacket or coat",
    "a photo of a fashion accessory such as a watch, belt, or bag",
]
CATEGORY_KEYS = ["topwear", "bottomwear", "footwear", "outerwear", "accessory"]

SUBCATEGORY_PROMPTS: Dict[str, List[str]] = {
    "topwear": [
        "a photo of a plain t-shirt",
        "a photo of a polo shirt with collar",
        "a photo of an oxford or dress shirt with buttons",
        "a photo of a casual open-collar shirt",
        "a photo of a formal shirt",
        "a photo of a hoodie with hood",
        "a photo of a sweatshirt without hood",
        "a photo of a knit sweater",
        "a photo of a sleeveless tank top",
        "a photo of a blouse",
    ],
    "bottomwear": [
        "a photo of denim jeans",
        "a photo of chino trousers",
        "a photo of formal dress trousers",
        "a photo of shorts",
        "a photo of jogger pants",
        "a photo of cargo pants",
        "a photo of linen trousers",
        "a photo of slim-fit trousers",
    ],
    "footwear": [
        "a photo of sneakers or athletic shoes",
        "a photo of formal leather shoes",
        "a photo of loafers",
        "a photo of boots",
        "a photo of sandals",
        "a photo of oxford shoes",
        "a photo of derby shoes",
        "a photo of slip-on shoes",
    ],
    "outerwear": [
        "a photo of a blazer",
        "a photo of a leather jacket",
        "a photo of a denim jacket",
        "a photo of a bomber jacket",
        "a photo of a long overcoat",
        "a photo of a trench coat",
        "a photo of a windbreaker",
    ],
    "accessory": [
        "a photo of a wristwatch",
        "a photo of a leather belt",
        "a photo of sunglasses",
        "a photo of a cap or hat",
        "a photo of a handbag",
        "a photo of a scarf",
        "a photo of a bracelet",
    ],
}
SUBCATEGORY_KEYS: Dict[str, List[str]] = {
    "topwear":   ["t-shirt","polo","oxford shirt","casual shirt","formal shirt","hoodie","sweatshirt","sweater","tank top","blouse"],
    "bottomwear":["jeans","chinos","formal trousers","shorts","joggers","cargo pants","linen trousers","slim fit trousers"],
    "footwear":  ["sneakers","formal shoes","loafers","boots","sandals","oxfords","derby shoes","slip-ons"],
    "outerwear": ["blazer","leather jacket","denim jacket","bomber jacket","overcoat","trench coat","windbreaker"],
    "accessory": ["watch","belt","sunglasses","cap","bag","scarf","bracelet"],
}

STYLE_PROMPTS = [
    "casual everyday clothing",
    "formal business clothing",
    "business casual smart clothing",
    "smart casual stylish clothing",
    "party or nightout clothing",
    "sportswear athletic clothing",
    "traditional ethnic clothing",
]
STYLE_KEYS = ["casual","formal","business_casual","smart_casual","party","sports","ethnic"]

PATTERN_PROMPTS = [
    "solid single-color clothing with no pattern",
    "striped clothing with parallel lines",
    "checked or plaid pattern clothing",
    "printed clothing with abstract or logo print",
    "floral pattern clothing with flower motifs",
    "graphic tee clothing with graphic design",
    "textured fabric clothing with visible texture",
]
PATTERN_KEYS = ["solid","striped","checked","printed","floral","graphic","textured"]

SEASON_PROMPTS = [
    "lightweight breathable summer clothing for hot weather",
    "thick warm winter clothing for cold weather",
    "waterproof rainy season clothing",
    "all-season versatile clothing suitable any weather",
]
SEASON_KEYS = ["summer","winter","rainy","all_season"]

GENDER_PROMPTS = [
    "men's clothing designed for men",
    "women's clothing designed for women",
    "unisex clothing suitable for everyone",
]
GENDER_KEYS = ["male","female","unisex"]


# ── Model loading ──────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _load_model() -> Tuple[CLIPModel, CLIPProcessor, torch.device]:
    logger.info("Loading FashionCLIP: %s", MODEL_NAME)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    logger.info("FashionCLIP ready on %s", device)
    return model, processor, device


# ── Core inference helpers ────────────────────────────────────────────────────

def _classify(
    image: Image.Image,
    prompts: List[str],
    model: CLIPModel,
    processor: CLIPProcessor,
    device: torch.device,
) -> Tuple[int, float]:
    """
    Zero-shot CLIP classification.
    Returns (best_index, softmax_confidence).
    """
    inputs = processor(
        text=prompts,
        images=image,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=77,
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        logits = model(**inputs).logits_per_image[0]
        probs = logits.softmax(dim=0)
    best = int(probs.argmax().item())
    return best, float(probs[best].item())


def _extract_embedding(
    image: Image.Image,
    model: CLIPModel,
    processor: CLIPProcessor,
    device: torch.device,
) -> List[float]:
    """L2-normalised 512-dim visual embedding for FAISS."""
    inputs = processor(images=image, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        features = model.get_image_features(**inputs)
        features = features / features.norm(dim=-1, keepdim=True)
    return features[0].cpu().tolist()


# ── Public analyser ───────────────────────────────────────────────────────────

class FashionCLIPAnalyzer:
    """
    Lazy-loading wrapper for all FashionCLIP inference.
    Model is loaded once on first call and cached.
    """

    def __init__(self) -> None:
        self._ready = False

    def _load(self) -> Tuple[CLIPModel, CLIPProcessor, torch.device]:
        return _load_model()

    def analyze(self, image: Image.Image) -> dict:
        """
        Run full zero-shot analysis on a preprocessed PIL Image.
        Returns metadata dict compatible with pipeline.py contract.
        """
        model, processor, device = self._load()

        # ── Category ─────────────────────────────────────────────────────────
        cat_idx, cat_conf = _classify(image, CATEGORY_PROMPTS, model, processor, device)
        category = CATEGORY_KEYS[cat_idx]

        # ── Subcategory (scoped to detected category) ─────────────────────────
        sub_prompts = SUBCATEGORY_PROMPTS[category]
        sub_keys    = SUBCATEGORY_KEYS[category]
        sub_idx, sub_conf = _classify(image, sub_prompts, model, processor, device)
        subcategory = sub_keys[sub_idx]

        # ── Style ─────────────────────────────────────────────────────────────
        sty_idx, sty_conf = _classify(image, STYLE_PROMPTS, model, processor, device)
        style = STYLE_KEYS[sty_idx]

        # ── Pattern ───────────────────────────────────────────────────────────
        pat_idx, pat_conf = _classify(image, PATTERN_PROMPTS, model, processor, device)
        pattern = PATTERN_KEYS[pat_idx]

        # ── Season ────────────────────────────────────────────────────────────
        sea_idx, sea_conf = _classify(image, SEASON_PROMPTS, model, processor, device)
        season = SEASON_KEYS[sea_idx]

        # ── Gender ────────────────────────────────────────────────────────────
        gen_idx, gen_conf = _classify(image, GENDER_PROMPTS, model, processor, device)
        gender = GENDER_KEYS[gen_idx]

        # ── Embedding ─────────────────────────────────────────────────────────
        embedding = _extract_embedding(image, model, processor, device)

        # Aggregate confidence: weighted by attribute importance
        confidence = (
            cat_conf  * 0.40 +
            sub_conf  * 0.25 +
            sty_conf  * 0.20 +
            pat_conf  * 0.10 +
            sea_conf  * 0.05
        )

        return {
            "category":    category,
            "subcategory": subcategory,
            "style":       style,
            "pattern":     pattern,
            "season":      season,
            "gender":      gender,
            "embedding":   embedding,
            "confidence":  round(confidence, 4),
        }
