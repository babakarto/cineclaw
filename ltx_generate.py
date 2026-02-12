#!/usr/bin/env python3
"""
ltx_generate.py — LTX-2 video generation for CineClaw skill

Cross-platform (Linux/Mac/Windows). No external dependencies (stdlib only).

Usage:
    python3 ltx_generate.py t2v "prompt"                                    # Text-to-video (fast, 1080p, 6s)
    python3 ltx_generate.py t2v "prompt" --model ltx-2-pro --duration 10    # Pro quality
    python3 ltx_generate.py t2v "prompt" --resolution 4k --fps 50          # 4K 50fps
    python3 ltx_generate.py t2v "prompt" --camera dolly_in                  # With camera motion
    python3 ltx_generate.py t2v "prompt" --no-audio                         # Silent video
    python3 ltx_generate.py i2v "motion prompt" --image photo.jpg           # Image-to-video
    python3 ltx_generate.py a2v "scene prompt" --audio track.mp3            # Audio-to-video
    python3 ltx_generate.py --test                                          # Test API connection
    python3 ltx_generate.py --estimate t2v --model ltx-2-pro --duration 10 --resolution 4k
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

BASE_URL = "https://api.ltx.video/v1"

# Resolution mappings
RESOLUTIONS = {
    "1080p": "1920x1080",
    "1080": "1920x1080",
    "1920x1080": "1920x1080",
    "1440p": "2560x1440",
    "1440": "2560x1440",
    "2560x1440": "2560x1440",
    "2k": "2560x1440",
    "4k": "3840x2160",
    "2160p": "3840x2160",
    "3840x2160": "3840x2160",
    "uhd": "3840x2160",
}

# Cost per second estimates (USD)
COST_PER_SEC = {
    "ltx-2-fast": {"1920x1080": 0.02, "2560x1440": 0.04, "3840x2160": 0.08},
    "ltx-2-pro":  {"1920x1080": 0.05, "2560x1440": 0.10, "3840x2160": 0.20},
}

CAMERA_MOTIONS = [
    "dolly_in", "dolly_out", "pan_left", "pan_right",
    "crane_up", "crane_down", "static", "handheld"
]


def get_token():
    token = os.environ.get("LTX_API_KEY", "")
    if not token:
        print("ERROR: LTX_API_KEY is not set.", file=sys.stderr)
        print("Set it with: export LTX_API_KEY=your_key_here", file=sys.stderr)
        print("Get your key at: https://console.ltx.video", file=sys.stderr)
        sys.exit(1)
    return token


def resolve_resolution(res_input):
    key = res_input.lower().strip()
    if key in RESOLUTIONS:
        return RESOLUTIONS[key]
    print(f"ERROR: Unknown resolution '{res_input}'.", file=sys.stderr)
    print(f"Valid options: 1080p, 1440p, 4k (or full format like 1920x1080)", file=sys.stderr)
    sys.exit(1)


def estimate_cost(model, resolution, duration):
    res = resolve_resolution(resolution)
    cost_sec = COST_PER_SEC.get(model, {}).get(res, 0.05)
    total = cost_sec * duration
    print(f"=== COST ESTIMATE ===")
    print(f"Model: {model}")
    print(f"Resolution: {res}")
    print(f"Duration: {duration} sec")
    print(f"Cost/sec: ~${cost_sec:.3f}")
    print(f"Est. TOTAL: ~${total:.2f}")
    print(f"=====================")


def ensure_output_dir():
    out_dir = Path.home() / "Desktop" / "cineclaw"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def test_connection(token):
    """Test API connectivity with a minimal request check."""
    url = f"{BASE_URL}/text-to-video"
    payload = json.dumps({
        "prompt": "test",
        "model": "ltx-2-fast",
        "duration": 6,
        "resolution": "1920x1080",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "CineClaw/1.0",
    })

    try:
        # We expect either success or a known error — either proves connectivity
        with urllib.request.urlopen(req) as resp:
            print(f"OK - LTX-2 API working (HTTP {resp.status})")
            # Discard the test video data
            resp.read()
            return True
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"ERROR: HTTP 401 — API key invalid or expired.", file=sys.stderr)
            print("Get a new key at: https://console.ltx.video", file=sys.stderr)
            return False
        elif e.code == 403:
            print(f"ERROR: HTTP 403 — No credits remaining.", file=sys.stderr)
            print("Add funds at: https://console.ltx.video", file=sys.stderr)
            return False
        elif e.code == 422:
            # 422 means API is reachable but rejected our test params — still OK
            print(f"OK - LTX-2 API reachable (got 422 for test payload, expected)")
            return True
        elif e.code == 429:
            print(f"OK - LTX-2 API reachable but rate limited. Wait and retry.")
            return True
        else:
            body = e.read().decode("utf-8", errors="replace")
            print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
            return False
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed: {e.reason}", file=sys.stderr)
        return False


def generate_video(mode, prompt, token, model="ltx-2-fast", duration=6,
                   resolution="1920x1080", fps=25, camera_motion=None,
                   generate_audio=True, image_path=None, audio_path=None,
                   output_path=None):
    """Generate a video via the LTX-2 API."""

    # Determine endpoint
    if mode == "t2v":
        endpoint = f"{BASE_URL}/text-to-video"
    elif mode == "i2v":
        endpoint = f"{BASE_URL}/image-to-video"
    elif mode == "a2v":
        endpoint = f"{BASE_URL}/audio-to-video"
    else:
        print(f"ERROR: Unknown mode '{mode}'. Use t2v, i2v, or a2v.", file=sys.stderr)
        sys.exit(1)

    # Build payload
    payload = {
        "prompt": prompt,
        "model": model,
        "duration": duration,
        "resolution": resolution,
        "fps": fps,
        "generate_audio": generate_audio,
    }

    if camera_motion:
        payload["camera_motion"] = camera_motion

    # Audio-to-video constraints
    if mode == "a2v":
        payload["model"] = "ltx-2-pro"
        payload["resolution"] = "1920x1080"
        # Remove duration — driven by audio length
        payload.pop("duration", None)
        payload.pop("fps", None)
        payload.pop("generate_audio", None)
        if audio_path:
            if audio_path.startswith("http"):
                payload["audio_url"] = audio_path
            else:
                print("ERROR: Audio must be a public HTTPS URL for the API.", file=sys.stderr)
                print("Upload your audio file first and provide the URL.", file=sys.stderr)
                sys.exit(1)

    # Image-to-video: add image URL
    if mode == "i2v":
        if image_path:
            if image_path.startswith("http"):
                payload["image_url"] = image_path
            else:
                print("ERROR: Image must be a public HTTPS URL for the API.", file=sys.stderr)
                print("Upload your image first and provide the URL.", file=sys.stderr)
                sys.exit(1)
        else:
            print("ERROR: Image-to-video requires --image URL.", file=sys.stderr)
            sys.exit(1)

    # Print generation info
    res_label = resolution
    cost_sec = COST_PER_SEC.get(model, {}).get(resolution, 0.05)
    est_cost = cost_sec * duration if mode != "a2v" else cost_sec * 10  # estimate

    print(f"[CineClaw] Generating {mode.upper()} video...")
    print(f"  Model: {model}")
    print(f"  Resolution: {resolution}")
    if mode != "a2v":
        print(f"  Duration: {duration}s @ {fps}fps")
    print(f"  Audio: {'yes' if generate_audio else 'no'}")
    if camera_motion:
        print(f"  Camera: {camera_motion}")
    print(f"  Est. cost: ~${est_cost:.2f}")
    print()
    print(f"  Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
    print()
    print("  Generating... (this may take 10-90 seconds)")
    print()

    # Make request
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "CineClaw/1.0",
    })

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            content_type = resp.headers.get("Content-Type", "")
            request_id = resp.headers.get("x-request-id", "unknown")

            if "video/mp4" not in content_type and "application/octet-stream" not in content_type:
                # Might be JSON error
                body = resp.read().decode("utf-8", errors="replace")
                print(f"WARNING: Unexpected content type: {content_type}", file=sys.stderr)
                print(f"Response: {body[:500]}", file=sys.stderr)
                return None

            # Save video
            if output_path:
                out_file = Path(output_path)
            else:
                out_dir = ensure_output_dir()
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                out_file = out_dir / f"cineclaw-{mode}-{timestamp}.mp4"

            video_data = resp.read()
            out_file.write_bytes(video_data)

            size_mb = len(video_data) / (1024 * 1024)
            print(f"  ✓ Video saved: {out_file}")
            print(f"  ✓ Size: {size_mb:.1f} MB")
            print(f"  ✓ Request ID: {request_id}")
            print(f"  ✓ Est. cost: ~${est_cost:.2f}")
            return str(out_file)

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {e.code}", file=sys.stderr)
        try:
            err = json.loads(body)
            msg = err.get("error", {}).get("message", body)
            print(f"  {msg}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"  {body[:500]}", file=sys.stderr)

        if e.code == 401:
            print("  → API key invalid. Get a new one at console.ltx.video", file=sys.stderr)
        elif e.code == 403:
            print("  → No credits. Add funds at console.ltx.video", file=sys.stderr)
        elif e.code == 429:
            print("  → Rate limited. Wait 30 seconds and retry.", file=sys.stderr)
        elif e.code == 422:
            print("  → Invalid parameter combination. Check model/resolution/duration.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    args = sys.argv[1:]

    if not args:
        print("CineClaw — LTX-2 Video Generation")
        print()
        print("Usage:")
        print("  python3 ltx_generate.py t2v \"prompt\"           Text-to-video")
        print("  python3 ltx_generate.py i2v \"prompt\" --image URL  Image-to-video")
        print("  python3 ltx_generate.py a2v \"prompt\" --audio URL  Audio-to-video")
        print("  python3 ltx_generate.py --test                    Test connection")
        print("  python3 ltx_generate.py --estimate t2v [options]  Cost estimate")
        print()
        print("Options:")
        print("  --model ltx-2-fast|ltx-2-pro   Model (default: ltx-2-fast)")
        print("  --duration N                    Seconds (default: 6)")
        print("  --resolution 1080p|1440p|4k     Resolution (default: 1080p)")
        print("  --fps 25|50                     Frame rate (default: 25)")
        print("  --camera MOTION                 Camera motion preset")
        print("  --no-audio                      Disable audio generation")
        print("  --image URL                     Image URL for i2v")
        print("  --audio URL                     Audio URL for a2v")
        print("  --output PATH                   Custom output path")
        sys.exit(0)

    token = get_token()

    # Test mode
    if args[0] == "--test":
        test_connection(token)
        return

    # Parse arguments
    estimate_mode = False
    mode = None
    prompt = None
    model = "ltx-2-fast"
    duration = 6
    resolution = "1920x1080"
    fps = 25
    camera_motion = None
    generate_audio = True
    image_path = None
    audio_path = None
    output_path = None

    i = 0
    while i < len(args):
        if args[i] == "--estimate":
            estimate_mode = True
            i += 1
        elif args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 2
        elif args[i] == "--duration" and i + 1 < len(args):
            duration = int(args[i + 1])
            i += 2
        elif args[i] == "--resolution" and i + 1 < len(args):
            resolution = resolve_resolution(args[i + 1])
            i += 2
        elif args[i] == "--fps" and i + 1 < len(args):
            fps = int(args[i + 1])
            i += 2
        elif args[i] == "--camera" and i + 1 < len(args):
            cam = args[i + 1]
            if cam not in CAMERA_MOTIONS:
                print(f"WARNING: Unknown camera motion '{cam}'.", file=sys.stderr)
                print(f"Available: {', '.join(CAMERA_MOTIONS)}", file=sys.stderr)
            camera_motion = cam
            i += 2
        elif args[i] == "--no-audio":
            generate_audio = False
            i += 1
        elif args[i] == "--image" and i + 1 < len(args):
            image_path = args[i + 1]
            i += 2
        elif args[i] == "--audio" and i + 1 < len(args):
            audio_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] in ("t2v", "i2v", "a2v"):
            mode = args[i]
            i += 1
        elif not args[i].startswith("--") and prompt is None:
            prompt = args[i]
            i += 1
        else:
            i += 1

    if estimate_mode:
        estimate_cost(model, resolution, duration)
        return

    if not mode:
        print("ERROR: Specify mode: t2v, i2v, or a2v", file=sys.stderr)
        sys.exit(1)

    if not prompt:
        print("ERROR: No prompt provided.", file=sys.stderr)
        sys.exit(1)

    generate_video(
        mode=mode,
        prompt=prompt,
        token=token,
        model=model,
        duration=duration,
        resolution=resolution,
        fps=fps,
        camera_motion=camera_motion,
        generate_audio=generate_audio,
        image_path=image_path,
        audio_path=audio_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
