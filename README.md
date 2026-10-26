# GIMP Pix2Pix Plugin

A student GIMP 3 plug-in that sends the currently selected drawable to a
separately running local Pix2Pix inference API and inserts the returned image
as a new layer. This repository contains the GIMP-side integration only. It
does **not** contain the inference server, Pix2Pix model, model weights, or a
complete end-to-end application.

## Project status

The plug-in source and request/response integration are present, but
end-to-end image generation has not been verified in this environment because
GIMP and the inference server are unavailable. Treat this as a portfolio
integration project rather than a ready-to-use distribution.

## Features implemented

- Registers a GIMP procedure named `python-fu-pix2pix-compulsory-2`.
- Adds **Pix2Pix Compulsory 2** under `Filters > Compulsory`.
- Reads the first selected drawable from the current image.
- Converts its pixels to 8-bit RGBA and Base64-encodes them.
- Sends a JSON `POST` request to a local inference endpoint.
- Validates the returned dimensions, format, and decoded pixel length.
- Inserts the response as a new RGBA layer named `Pix2Pix Output`.
- Wraps the operation in a GIMP undo group.
- Logs messages through GIMP and to a temporary log file.

## Architecture and data flow

1. GIMP loads [`-01-plug-in-pix2pix-compulsory-2.py`](
-01-plug-in-pix2pix-compulsory-2.py), which calls `Gimp.main()` and registers
   the plug-in procedure.
2. When the menu procedure runs, it calls
   [`plugin_implementation.py`](plugin_implementation.py).
3. The implementation uses [`gimp_layer.py`](gimp_layer.py) to read the first
   drawable's GEGL buffer as `RGBA u8` pixels.
4. [`api_client.py`](api_client.py) sends the encoded payload to the
   configured local API.
5. The response is decoded and validated by `gimp_layer.py`.
6. A new GIMP layer is created, populated, inserted at the top of the image,
   and displayed.

[`config.py`](config.py) contains the procedure/menu identifiers, local API
host and port, endpoint, and request timeout. [`logger.py`](logger.py)
centralizes GIMP and temporary-file logging.

## Project structure

| File | Purpose |
| --- | --- |
| `-01-plug-in-pix2pix-compulsory-2.py` | Active GIMP 3 plug-in entry point and registration |
| `plugin_implementation.py` | Undo-grouped processing workflow |
| `gimp_layer.py` | GEGL pixel extraction and output-layer insertion |
| `api_client.py` | JSON HTTP client for the local inference API |
| `config.py` | Procedure, menu, endpoint, and timeout settings |
| `logger.py` | GIMP and temporary-file logging |
| `pix2pix_test_plugin_DISABLED.py` | Disabled early HTTP/GIMP prototype |

The `pix2pix_test_plugin_DISABLED.py` file is retained as historical
experimental code. It creates a test layer and sends `{"test": "hello"}`; it
does not implement the active pixel-processing workflow and should not be
installed alongside the active plug-in.

## Compatibility

The active plug-in explicitly requests:

```python
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
```

It uses the GIMP 3 Python GObject introspection API, including
`Gimp.PlugIn`, `Gimp.ImageProcedure`, `Gimp.Layer.new`, GEGL buffers, and
`Gimp.main`. It therefore targets **GIMP 3.x**, not the older GIMP 2.x
Python-Fu API. The source uses Python 3 syntax and standard-library modules;
the exact Python runtime is the one bundled or configured by the GIMP 3
installation. The plug-in has not been migrated or tested against GIMP 2.x.

## Installation and plug-in setup

1. Install GIMP 3.x with its Python/GObject introspection support.
2. Keep the files in this repository together; the active entry point imports
   the neighboring modules by name.
3. Install or copy the plug-in according to the GIMP 3 plug-in installation
   instructions for your operating system.
4. Ensure the active entry-point file is executable where the platform
   requires executable plug-ins.
5. Start GIMP and confirm that **Pix2Pix Compulsory 2** appears under
   `Filters > Compulsory`.

The repository does not include a `requirements.txt` because the active
plug-in uses Python standard-library modules (`json`, `urllib`, `base64`,
`tempfile`, and related modules) plus `gi.repository`, which must be supplied
by GIMP. Installing packages into ordinary system Python does not necessarily
make them available inside GIMP's Python environment.

## Inference server requirements

The plug-in alone cannot generate an image. A separately running local
inference server must implement the API contract below and provide the
Pix2Pix model and weights.

By default, the plug-in sends requests to:

```text
POST http://127.0.0.1:5000/infer
```

The request body is JSON:

```json
{
  "width": 256,
  "height": 256,
  "format": "RGBA",
  "pixels_b64": "<base64-encoded RGBA u8 pixel bytes>"
}
```

The actual width and height are taken from the selected drawable. The Base64
value decodes to exactly `width * height * 4` bytes.

The response must be JSON with the same fields:

```json
{
  "width": 256,
  "height": 256,
  "format": "RGBA",
  "pixels_b64": "<base64-encoded RGBA u8 output bytes>"
}
```

The plug-in accepts only `format: "RGBA"` and rejects responses whose decoded
pixel length does not equal `width * height * 4`. The request timeout is
configured as `API_TIMEOUT_SECONDS = 120` in [`config.py`](config.py).
HTTP errors, invalid JSON, connection failures, and validation failures are
logged and propagated to the GIMP procedure as an execution error.

No inference server implementation, model, weights, server URL beyond the
local default, or server-specific preprocessing is included in this project.

## Configuration

Edit [`config.py`](config.py) to change:

- `API_HOST`
- `API_PORT`
- `API_TIMEOUT_SECONDS`
- GIMP procedure and menu identifiers

The current configuration has no credentials or API keys. The endpoint is
hardcoded to the local address `127.0.0.1:5000/infer`; changing it requires
editing `config.py`. Do not place credentials in source files or commit local
configuration containing secrets.

## Usage

1. Start the compatible local inference API.
2. Start GIMP 3.x with the plug-in installed.
3. Open an image.
4. Select the drawable to process.
5. Choose **Filters > Compulsory > Pix2Pix Compulsory 2**.
6. If the API returns a valid RGBA image, the plug-in inserts it as
   `Pix2Pix Output`.

Only the first drawable in the procedure's `drawables` collection is used.
The plug-in does not expose a dialog for model parameters, preprocessing,
output naming, or server selection.

## Testing and validation

There are no automated tests or mock inference server in this repository.
Without GIMP and a compatible inference server, only static validation can be
performed. The Python files can be syntax-checked with:

```text
python -m py_compile *.py
```

This checks parsing only; it does not verify GIMP registration, GEGL buffer
access, network communication, response decoding, or layer insertion.
End-to-end testing requires GIMP 3.x, the plug-in installed in GIMP, an open
image with a selected drawable, and a compatible local `/infer` server.

## Known limitations

- The inference server and trained Pix2Pix model are not included.
- The default endpoint is local and HTTP-only; there is no authentication or
  TLS configuration.
- The plug-in sends the complete selected drawable as raw Base64 RGBA data,
  which can be large for high-resolution images.
- The server is responsible for any model-specific resizing, normalization,
  and output generation.
- Only RGBA 8-bit buffers and RGBA responses are supported.
- Only the first selected drawable is processed.
- The active source uses broad exception handling at the GIMP boundary so
  failures are reported as procedure errors; detailed diagnostics are
  written to the temporary log.
- The disabled prototype remains in the repository for historical context and
  is not part of the active workflow.
