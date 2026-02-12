# LTX-2 API Reference

## Authentication

Bearer token from env var `LTX_API_KEY`.
Get your key at: https://console.ltx.video

## Base URL

```
https://api.ltx.video/v1
```

## Endpoints

### Text-to-Video

```
POST /v1/text-to-video
```

Returns: MP4 file directly (Content-Type: video/mp4)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | Yes | Scene description, max 5000 chars |
| model | enum | Yes | `ltx-2-fast` or `ltx-2-pro` |
| duration | integer | Yes | Seconds of video |
| resolution | string | Yes | `1920x1080`, `2560x1440`, or `3840x2160` |
| fps | integer | No | `25` (default) or `50` |
| camera_motion | enum | No | See camera motions table below |
| generate_audio | boolean | No | `true` (default) or `false` |

### Image-to-Video

```
POST /v1/image-to-video
```

Returns: MP4 file directly

Same params as text-to-video, plus:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| image_url | string | Yes | URL of the source image (HTTPS) |

The image anchors composition and identity. The prompt describes motion and camera.

### Audio-to-Video

```
POST /v1/audio-to-video
```

Returns: MP4 file directly

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | Yes | Visual scene description |
| audio_url | string | Yes | URL of audio file (HTTPS) |
| model | string | Yes | Only `ltx-2-pro` supported |
| resolution | string | Yes | Only `1920x1080` supported |

Audio defines structure, pacing, and motion. Video syncs to the audio.

## Camera Motion Values

| Value | Effect |
|-------|--------|
| `dolly_in` | Camera moves forward toward subject |
| `dolly_out` | Camera moves backward away from subject |
| `pan_left` | Camera pans horizontally left |
| `pan_right` | Camera pans horizontally right |
| `crane_up` | Camera moves upward |
| `crane_down` | Camera moves downward |
| `static` | Camera stays still |
| `handheld` | Slight natural shake |

## Supported Configurations

### ltx-2-fast

| Resolution | FPS | Duration |
|-----------|-----|----------|
| 1920x1080 | 25 | 6-20 sec |
| 1920x1080 | 50 | 6-10 sec |
| 2560x1440 | 25 | 6-10 sec |
| 3840x2160 | 25 | 6-10 sec |

### ltx-2-pro

| Resolution | FPS | Duration |
|-----------|-----|----------|
| 1920x1080 | 25 | 6-10 sec |
| 1920x1080 | 50 | 6-10 sec |
| 2560x1440 | 25 | 6-10 sec |
| 2560x1440 | 50 | 6-10 sec |
| 3840x2160 | 25 | 6-10 sec |
| 3840x2160 | 50 | 6-10 sec |

## Pricing (per second of output video)

| Model | 1080p | 1440p | 4K |
|-------|-------|-------|-----|
| ltx-2-fast | ~$0.02 | ~$0.04 | ~$0.08 |
| ltx-2-pro | ~$0.05 | ~$0.10 | ~$0.20 |

Audio generation is included at no extra cost when `generate_audio=true`.

## Response Headers

Successful responses include:
- `Content-Type: video/mp4`
- `x-request-id`: Unique ID for tracking/debugging

## Error Responses

Errors return JSON:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Duration must be between 6 and 20 seconds for ltx-2-fast at 1080p/25fps"
  }
}
```

| HTTP Code | Meaning |
|-----------|---------|
| 400 | Bad request — invalid params |
| 401 | Unauthorized — bad or missing API key |
| 422 | Unprocessable — valid JSON but impossible combination |
| 429 | Rate limited — slow down |
| 500 | Server error — retry |
| 503 | Service unavailable — API down |
| 504 | Timeout — generation too slow, try simpler params |

## Rate Limits

Controlled by your account tier. If you hit 429, wait 30 seconds and retry.
For sustained high volume, contact sales at ltx.studio.
