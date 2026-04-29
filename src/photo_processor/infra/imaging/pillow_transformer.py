from __future__ import annotations

from photo_processor.core.resize_rules import ResizePlan
from photo_processor.infra.imaging.pillow_runtime import require_pillow


DEFAULT_BACKGROUND = (255, 255, 255)


def render_to_frame(image, target_width: int, target_height: int, plan: ResizePlan):
    image_module, _ = require_pillow()
    resampling = getattr(image_module, "Resampling", image_module)

    transformed = image.resize(
        (plan.resized_width, plan.resized_height),
        resample=resampling.LANCZOS,
    )

    if plan.crop_box is not None:
        transformed = transformed.crop(plan.crop_box)

    if plan.padding is None:
        return transformed

    canvas_mode = "RGBA" if "A" in transformed.getbands() else "RGB"
    background = DEFAULT_BACKGROUND + (0,) if canvas_mode == "RGBA" else DEFAULT_BACKGROUND
    canvas = image_module.new(canvas_mode, (target_width, target_height), background)
    left, top, _, _ = plan.padding
    canvas.paste(transformed, (left, top))
    return canvas

