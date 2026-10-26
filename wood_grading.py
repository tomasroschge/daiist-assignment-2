"""
The business rule for grading boards, shared by train.py and app.py so that the
training evaluation and the dashboard always apply exactly the same logic.

See REPORT.md, "Business problem" and "Dataset".
"""

from PIL import Image

# Defects that disqualify a board from the premium grade (the positive class).
POSITIVE_CLASSES = {
    "0 Blue_Stain",
    "1 Crack",
    "2 Dead_Knot",
    "3 Knot_missing",
    "5 Marrow",
    "7 knot_with_crack",
    "9 resin",
}
# Defects that are acceptable in the premium grade.
ACCEPTABLE_CLASSES = {"4 Live_Knot", "6 Quartzity"}
# Too rare to learn or evaluate (2 examples in train, none in test).
EXCLUDED_CLASSES = {"8 overgrown"}


def to_landscape(image: Image.Image) -> Image.Image:
    """Turn a portrait image 90° counter-clockwise so the board lies horizontally,
    the orientation the model was trained on. Landscape images are returned unchanged."""
    if image.height > image.width:
        return image.transpose(Image.Transpose.ROTATE_90)
    return image


def board_score(result, positive_ids: set[int] | None) -> float:
    """
    The board's score: the highest confidence among detections of disqualifying
    defects, or 0 if there are none. `result` is one Ultralytics prediction.
    With positive_ids=None every detection counts (used for the COCO baseline,
    whose classes have nothing to do with wood).
    """
    best = 0.0
    for cls, conf in zip(result.boxes.cls.tolist(), result.boxes.conf.tolist()):
        if positive_ids is None or int(cls) in positive_ids:
            best = max(best, conf)
    return best


def positive_ids(names: dict[int, str]) -> set[int]:
    """Class ids of the disqualifying defects, given a model's or dataset's id -> name map."""
    return {i for i, n in names.items() if n in POSITIVE_CLASSES}
