# Math and Algorithms

## Unit conversion

When frame units are centimeters, pixel size is derived from DPI:

```text
pixels = centimeters / 2.54 * dpi
```

Example:

```text
15 cm at 300 DPI = 15 / 2.54 * 300 = 1771.65 -> 1772 px
10 cm at 300 DPI = 10 / 2.54 * 300 = 1181.10 -> 1181 px
```

This behavior is implemented in `core/settings.py` and `core/units.py`.

## Resize modes

The core rule is a scale factor applied to the source image:

- `contain`: `min(frame_width / source_width, frame_height / source_height)`
- `fit_width`: `frame_width / source_width`
- `fit_height`: `frame_height / source_height`

The resulting dimensions are rounded and clamped to at least `1` pixel.

## Padding

When the resized image is smaller than the target frame, padding is split symmetrically:

```text
horizontal = frame_width - resized_width
vertical = frame_height - resized_height
left = horizontal // 2
right = horizontal - left
top = vertical // 2
bottom = vertical - top
```

This is used by `contain` and may also apply to `fit_height`.

## Crop box

When the resized image is larger than the target frame, crop is centered:

```text
left = (resized_width - frame_width) // 2
top = (resized_height - frame_height) // 2
right = left + frame_width
bottom = top + frame_height
```

This is used by `fit_width`, and optionally by `fit_height` when width overflows.

## Orientation choice

The current orientation heuristic compares aspect-ratio distance:

```text
score = abs((image_width / image_height) - (frame_width / frame_height))
```

If the rotated image has a lower score than the original orientation, the target frame is swapped. This is implemented in `core/orientation.py`.

## Runtime pipeline

The current one-image pipeline runs these stages:

1. read source image
2. apply EXIF orientation
3. choose target frame orientation
4. calculate resize plan
5. resize image
6. crop or pad
7. save JPEG to memory
8. reduce quality or dimensions until the file-size limit is satisfied
9. write the final output file
