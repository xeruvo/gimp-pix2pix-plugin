import base64

from gi.repository import Gimp, Gegl

from logger import log


def get_drawable_as_client_json(drawable) -> dict:
    log("Drawable reading started")

    try:
        width = drawable.get_width()
        height = drawable.get_height()
        buffer = drawable.get_buffer()
        rect = Gegl.Rectangle.new(0, 0, width, height)

        raw_bytes = bytes(buffer.get(rect, 1.0, "R'G'B'A u8", Gegl.AbyssPolicy.NONE))
        expected_size = width * height * 4
        if len(raw_bytes) != expected_size:
            raise ValueError(
                f"Drawable byte size mismatch: expected {expected_size}, got {len(raw_bytes)}"
            )

        result = {
            "width": width,
            "height": height,
            "format": "RGBA",
            "pixels_b64": base64.b64encode(raw_bytes).decode("utf-8"),
        }
        log("Drawable reading succeeded")
        return result
    except Exception as error:
        log(f"Drawable reading failed: {error}")
        raise


def insert_response_as_layer(image, response_json, layer_name="Pix2Pix Output"):
    try:
        width = int(response_json["width"])
        height = int(response_json["height"])
        pixel_format = response_json["format"]
        pixels_b64 = response_json["pixels_b64"]

        if pixel_format != "RGBA":
            raise ValueError(f"Unsupported format: {pixel_format}")

        raw_bytes = base64.b64decode(pixels_b64)
        expected_size = width * height * 4
        if len(raw_bytes) != expected_size:
            raise ValueError(
                f"Decoded byte size mismatch: expected {expected_size}, got {len(raw_bytes)}"
            )

        layer = Gimp.Layer.new(
            image,
            layer_name,
            width,
            height,
            Gimp.ImageType.RGBA_IMAGE,
            50,
            Gimp.LayerMode.NORMAL,
        )
        image.insert_layer(layer, None, 0)

        buffer = layer.get_buffer()
        rect = Gegl.Rectangle.new(0, 0, width, height)
        buffer.set(rect, "RGBA u8", raw_bytes)
        buffer.flush()
        layer.update(0, 0, width, height)

        log("Response layer inserted successfully")
        return layer
    except Exception as error:
        log(f"Response layer insertion failed: {error}")
        raise
