import math, re
import uuid
import json
from pathlib import Path
CATALOG = json.loads((Path(__file__).resolve().parent.parent / "static/studio/avatar-catalog.json").read_text())

PARTS = {"skin", "hair", "shirt", "trousers", "shoes", "eyes", "horns"}
ASSETS = {"chair-v1", "desk-v1", "pillow-v1", "clock-v1", "books-v1", "teddy-v1", "guitar-v1", "microphone-v1", "speaker-v1", "skateboard-v1", "balloon-v1", "ball-v1", "mushroom-v1", "pond-v1", "tent-v1", "bench-v1","photo-v1","sofa-v1", "bed-v1", "table-v1", "shelf-v1", "rug-v1", "lamp-v1", "window-v1", "door-v1", "house-v1", "castle-v1", "tree-v1", "flower-v1", "cloud-v1", "rock-v1", "plant-v1", "sun-v1"}
def validate_document(doc):
    if not isinstance(doc, dict) or set(doc) != {"version", "canvas", "objects"} or type(doc["version"]) is not int or doc["version"] not in (1, 2):
        raise ValueError("Unbekanntes Projektformat.")
    version = doc["version"]
    canvas = doc["canvas"]
    if not isinstance(canvas, dict) or set(canvas) != ({"width", "height", "background"} if version == 1 else {"width", "height", "background", "ground"}) or canvas["width"] != (600 if version == 1 else 900) or canvas["height"] != 650 or not color(canvas["background"]):
        raise ValueError("Ungültige Arbeitsfläche.")
    if version == 2 and not color(canvas["ground"]):
        raise ValueError("Ungültige Bodenfarbe.")
    objects = doc["objects"]
    if not isinstance(objects, list) or not (1 if version == 1 else 0) <= len(objects) <= (20 if version == 1 else 100):
        raise ValueError("Ungültige Objektanzahl (Figur: 1–20, Raum/Ort/Szene: 0–100).")
    ids = set()
    for obj in objects:
        if not isinstance(obj, dict) or set(obj) != ({"id", "asset", "x", "y", "scale", "rotation", "flipped", "colors", "variant"} | ({"photo"} if obj.get("asset") == "photo-v1" else {"appearance"} if obj.get("asset") == "avatar-v2" else set())):
            raise ValueError("Ungültiges Objekt.")
        if not isinstance(obj["id"], str) or len(obj["id"]) > 50 or obj["id"] in ids:
            raise ValueError("Ungültige Objektkennung.")
        ids.add(obj["id"])
        if not isinstance(obj["asset"], str) or obj["asset"] not in ({"sprout-v1", "avatar-v2"} if version == 1 else ASSETS | {"sprout-v1", "avatar-v2"}) or type(obj["variant"]) is not int or obj["variant"] not in [0, 1, 2] or type(obj["flipped"]) is not bool:
            raise ValueError("Unbekannte Figur.")
        if obj["asset"] == "avatar-v2":
            appearance = obj["appearance"]
            if not isinstance(appearance, dict) or set(appearance) != {"choices", "body"}:
                raise ValueError("Ungültige Figureneinstellungen.")
            for section in ("choices", "body"):
                values = appearance[section]
                if not isinstance(values, dict) or set(values) != set(CATALOG[section]):
                    raise ValueError("Unvollständige Figureneinstellungen.")
                for key, spec in CATALOG[section].items():
                    value = values[key]
                    if section == "choices":
                        if not isinstance(value, str) or value not in [option[0] for option in spec["options"]]:
                            raise ValueError("Unbekannter Figurenbaustein.")
                    elif type(value) not in (int, float) or not math.isfinite(value) or not spec["min"] <= value <= spec["max"]:
                        raise ValueError("Ungültige Körperproportionen.")
        if obj["asset"] == "photo-v1":
            photo = obj["photo"]
            if not isinstance(photo, dict) or set(photo) != {"id", "width", "height"}:
                raise ValueError("Ungültiges Foto.")
            if not isinstance(photo["id"], str) or str(uuid.UUID(photo["id"])) != photo["id"]:
                raise ValueError("Ungültige Fotokennung.")
            if any(type(photo[k]) is not int or not 1 <= photo[k] <= 1600 for k in ('width', 'height')):
                raise ValueError("Ungültige Fotogröße.")
        for key, low, high in [("x", 0, canvas["width"]), ("y", 0, 650), ("scale", .3, 1.8), ("rotation", -180, 180)]:
            value = obj[key]
            if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError("Ungültige Position oder Größe.")
        if not isinstance(obj["colors"], dict) or set(obj["colors"]) != (PARTS if obj["asset"] == "sprout-v1" else set(CATALOG["colors"]) if obj["asset"] == "avatar-v2" else {"main", "detail", "accent"}) or not all(color(c) for c in obj["colors"].values()):
            raise ValueError("Ungültige Farben.")
    return doc
def color(value):
    return isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) is not None
