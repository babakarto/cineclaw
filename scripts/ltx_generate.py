#!/usr/bin/env python3
"""
ltx_generate.py — LTX-2 video generation for CineClaw OpenClaw skill

Cross-platform (Windows/Mac/Linux). No curl, no bash escaping issues.

Usage:
    python3 ltx_generate.py --mode t2v --prompt "scene description"
    python3 ltx_generate.py --mode t2v --prompt "scene" --model ltx-2-pro --duration 10
    python3 ltx_generate.py --mode i2v --image photo.jpg --prompt "motion description"
    python3 ltx_generate.py --mode a2v --audio voice.mp3 --prompt "visual description"
    python3 ltx_generate.py --mode t2v --prompt "scene" --resolution 3840x2160
    python3 ltx_generate.py --estimate --mode t2v --duration 10 --model ltx-2-pro
    python3 ltx_generate.py --test
"""

import sys
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import time
from datetime import datetime
from pathlib import Path

BASE_URL = "https://api.ltx.video/v1"

# Cost per second of video (approximate)
COST_TABLE = {
    "ltx-2-fast": {"1920x1080": 0.02, "2560x1440": 0.04, "3840x2160": 0.08},
    "ltx-2-pro": {"1920x1080": 0.05, "2560x1440": 0.10, "3840x2160": 0.20},
}


def get_api_key():
    key = os.environ.get("LTX_API_KEY", "")
    if not key:
        print("ERROR: LTX_API_KEY is not set.", file=sys.stderr)
        print("Get your key at https://console.ltx.video", file=sys.stderr)
        print("Set it: export LTX_API_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(endpoint, api_key, method="GET", data=None, files=None):
    url = f"{BASE_URL}{endpoint}"

    if files:
        # Multipart upload for image/audio files
        boundary = "----CineClawBoundary"
        body_parts = []

        for key, value in (data or {}).items():
            body_parts.append(f"--{boundary}\r\n".encode())
            body_parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body_parts.append(f"{value}\r\n".encode())

        for key, filepath in files.items():
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as f:
                file_data = f.read()
            body_parts.append(f"--{boundary}\r\n".encode())
            body_parts.append(
                f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode()
            )
            body_parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
            body_parts.append(file_data)
            body_parts.append(b"\r\n")

        body_parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(body_parts)

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    elif data and method == "POST":
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
    else:
        req = urllib.request.Request(url, method=method)

    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("User-Agent", "CineClaw/1.0")

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {e.code}: {body}", file=sys.stderr)
        if e.code == 401:
            print("API key invalid. Check at console.ltx.video", file=sys.stderr)
        elif e.code == 402:
            print("Insufficient credits. Add credits at console.ltx.video", file=sys.stderr)
        elif e.code == 429:
            print("Rate limited. Wait a minute and retry.", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def test_connection(api_key):
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/health",
            headers={"Authorization": f"Bearer {api_key}", "User-Agent": "CineClaw/1.0"},
        )
        with urllib.request.urlopen(req) as resp:
            print(f"OK - LTX API reachable (HTTP {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code}", file=sys.stderr)
        if e.code == 401:
            print("API key invalid. Regenerate at console.ltx.video", file=sys.stderr)
        return False
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed: {e.reason}", file=sys.stderr)
        return False


def estimate_cost(model, resolution, duration):
    cost_per_sec = COST_TABLE.get(model, {}).get(resolution, 0.02)
    total = cost_per_sec * duration
    print(f"=== COST ESTIMATE ===")
    print(f"Model: {model}")
    print(f"Resolution: {resolution}")
    print(f"Duration: {duration}s")
    print(f"Cost/second: ${cost_per_sec:.2f}")
    print(f"Estimated TOTAL: ${total:.2f}")
    print(f"=====================")
    return total


def poll_generation(gen_id, api_key, timeout=300):
    """Poll for generation completion."""
    start = time.time()
    while time.time() - start < timeout:
        result = api_request(f"/generations/{gen_id}", api_key)
        status = result.get("status", "unknown")

        if status == "completed":
            return result
        elif status in ("failed", "error"):
            print(f"ERROR: Generation failed: {result.get('error', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)

        elapsed = int(time.time() - start)
        print(f"  Status: {status} ({elapsed}s elapsed)...", end="\r")
        time.sleep(3)

    print(f"\nERROR: Generation timed out after {timeout}s", file=sys.stderr)
    sys.exit(1)


def download_video(video_url, output_path):
    """Download the generated video."""
    req = urllib.request.Request(video_url, headers={"User-Agent": "CineClaw/1.0"})
    with urllib.request.urlopen(req) as resp:
        with open(output_path, "wb") as f:
            f.write(resp.read())
    return output_path


def generate(mode, prompt, api_key, model="ltx-2-fast", resolution="1920x1080",
             duration=6, fps=25, seed=None, image_path=None, audio_path=None,
             output_dir=None):
    """Main generation function."""

    # Validate A2V model
    if mode == "a2v" and model != "ltx-2-pro":
        print("NOTE: Audio-to-video requires ltx-2-pro. Switching automatically.")
        model = "ltx-2-pro"

    # Estimate cost
    est = estimate_cost(model, resolution, duration)
    print()

    # Build request
    if mode == "t2v":
        endpoint = "/generations/text-to-video"
        data = {
            "prompt": prompt,
            "model": model,
            "resolution": resolution,
            "duration": duration,
            "fps": fps,
        }
        if seed is not None:
            data["seed"] = seed
        files = None

    elif mode == "i2v":
        if not image_path:
            print("ERROR: --image required for image-to-video mode", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(image_path):
            print(f"ERROR: Image file not found: {image_path}", file=sys.stderr)
            sys.exit(1)
        endpoint = "/generations/image-to-video"
        data = {
            "prompt": prompt,
            "model": model,
            "resolution": resolution,
            "duration": duration,
            "fps": fps,
        }
        if seed is not None:
            data["seed"] = seed
        files = {"image": image_path}

    elif mode == "a2v":
        if not audio_path:
            print("ERROR: --audio required for audio-to-video mode", file=sys.stderr)
            sys.exit(1)
        if not os.path.exists(audio_path):
            print(f"ERROR: Audio file not found: {audio_path}", file=sys.stderr)
            sys.exit(1)
        endpoint = "/generations/audio-to-video"
        data = {
            "prompt": prompt,
            "model": "ltx-2-pro",
            "resolution": "1920x1080",
        }
        files = {"audio": audio_path}
    else:
        print(f"ERROR: Unknown mode '{mode}'. Use t2v, i2v, or a2v.", file=sys.stderr)
        sys.exit(1)

    # Send request
    print(f"[{mode.upper()}] Generating: {prompt[:80]}...")
    print(f"  Model: {model} | Resolution: {resolution} | Duration: {duration}s | FPS: {fps}")
    print()

    result = api_request(endpoint, api_key, method="POST", data=data, files=files)

    gen_id = result.get("id")
    status = result.get("status", "processing")

    if status == "completed":
        video_url = result.get("video_url")
    elif gen_id:
        print(f"Generation started (ID: {gen_id}). Polling for completion...")
        result = poll_generation(gen_id, api_key)
        video_url = result.get("video_url")
    else:
        print(f"ERROR: Unexpected response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    if not video_url:
        print("ERROR: No video URL in response", file=sys.stderr)
        sys.exit(1)

    # Download video
    if not output_dir:
        output_dir = os.path.expanduser("~/Desktop/cineclaw")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"output-{mode}-{model}-{timestamp}.mp4"
    output_path = os.path.join(output_dir, filename)

    print(f"Downloading video...")
    download_video(video_url, output_path)

    actual_cost = result.get("cost", est)
    print()
    print(f"=== DONE ===")
    print(f"Video saved: {output_path}")
    print(f"Cost: ~${actual_cost:.2f}")
    print(f"Duration: {duration}s | Model: {model} | Resolution: {resolution}")
    print(f"=============")

    return output_path


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: python3 ltx_generate.py --mode t2v --prompt \"your prompt\"")
        print()
        print("Modes:")
        print("  t2v    Text-to-Video")
        print("  i2v    Image-to-Video (requires --image)")
        print("  a2v    Audio-to-Video (requires --audio, forces ltx-2-pro)")
        print()
        print("Options:")
        print("  --prompt TEXT        Video/scene description")
        print("  --model MODEL        ltx-2-fast (default) or ltx-2-pro")
        print("  --resolution RES     1920x1080 (default), 2560x1440, 3840x2160")
        print("  --duration N         Seconds (default: 6)")
        print("  --fps N              25 (default) or 50")
        print("  --seed N             Seed for reproducibility")
        print("  --image PATH         Image file for i2v mode")
        print("  --audio PATH         Audio file for a2v mode")
        print("  --output DIR         Output directory (default: ~/Desktop/cineclaw)")
        print("  --estimate           Estimate cost only, don't generate")
        print("  --test               Test API connection")
        sys.exit(0)

    api_key = get_api_key()

    # Test mode
    if args[0] == "--test":
        test_connection(api_key)
        return

    # Parse arguments
    mode = None
    prompt = None
    model = "ltx-2-fast"
    resolution = "1920x1080"
    duration = 6
    fps = 25
    seed = None
    image_path = None
    audio_path = None
    output_dir = None
    estimate_only = False

    i = 0
    while i < len(args):
        if args[i] == "--mode" and i + 1 < len(args):
            mode = args[i + 1]
            i += 2
        elif args[i] == "--prompt" and i + 1 < len(args):
            prompt = args[i + 1]
            i += 2
        elif args[i] == "--model" and i + 1 < len(args):
            model = args[i + 1]
            i += 2
        elif args[i] == "--resolution" and i + 1 < len(args):
            resolution = args[i + 1]
            i += 2
        elif args[i] == "--duration" and i + 1 < len(args):
            duration = int(args[i + 1])
            i += 2
        elif args[i] == "--fps" and i + 1 < len(args):
            fps = int(args[i + 1])
            i += 2
        elif args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif args[i] == "--image" and i + 1 < len(args):
            image_path = args[i + 1]
            i += 2
        elif args[i] == "--audio" and i + 1 < len(args):
            audio_path = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_dir = args[i + 1]
            i += 2
        elif args[i] == "--estimate":
            estimate_only = True
            i += 1
        else:
            i += 1

    if estimate_only:
        if not mode:
            mode = "t2v"
        estimate_cost(model, resolution, duration)
        return

    if not mode:
        print("ERROR: --mode required (t2v, i2v, or a2v)", file=sys.stderr)
        sys.exit(1)

    if not prompt:
        print("ERROR: --prompt required", file=sys.stderr)
        sys.exit(1)

    generate(mode, prompt, api_key, model, resolution, duration, fps, seed,
             image_path, audio_path, output_dir)


if __name__ == "__main__":
    main()
