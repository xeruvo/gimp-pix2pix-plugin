from gi.repository import Gimp

from logger import log
from gimp_layer import get_drawable_as_client_json, insert_response_as_layer
from api_client import send_infer_request


def run_pix2pix(image, drawables):
    log("Pix2Pix execution started")

    if image is None:
        raise ValueError("image cannot be None")

    if not drawables:
        raise ValueError("drawables cannot be empty")

    undo_started = False

    try:
        input_drawable = drawables[0]

        image.undo_group_start()
        undo_started = True

        payload = get_drawable_as_client_json(input_drawable)
        response_json = send_infer_request(payload)
        layer = insert_response_as_layer(image, response_json)

        image.undo_group_end()
        undo_started = False

        Gimp.displays_flush()
        log("Pix2Pix execution succeeded")
        return layer
    except Exception as error:
        log(f"Pix2Pix execution failed: {error}")
        if undo_started:
            try:
                image.undo_group_end()
            except Exception:
                pass
        raise
