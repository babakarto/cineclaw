---
name: cineclaw
description: >
  AI video generation skill for OpenClaw using the LTX-2 API. Generates cinematic
  videos from text prompts or static images. Supports text-to-video, image-to-video,
  and audio-to-video with LTX-2 Fast (speed) and LTX-2 Pro (quality) models.
  Use when: (1) user says "generate a video", "create a video", "make a video",
  "cineclaw", "text to video", "image to video", "animate this image",
  "video from audio", "/cineclaw", (2) user describes a scene they want to see as
  video, (3) user shares an image and wants it animated, (4) user shares audio
  and wants a matching video.
  NOT for: video editing, trimming, merging, or post-production. NOT for streaming
  or real-time video. NOT for downloading videos from the internet.
  Requires: LTX_API_KEY environment variable set with a valid API key from
  console.ltx.video.
---

# CineClaw — AI Video Generation for OpenClaw

Generate cinematic AI videos from text, images, or audio using the LTX-2 API.
One script handles everything. Cross-platform (Linux/Mac/Windows).

For API details and prompting tips: read `references/ltx-api.md` and `references/prompting-guide.md`.

## Important: Cost Awareness

LTX-2 API bills per second of generated video. Costs vary by model and resolution.

**Before generating, always tell the user the estimated cost:**

| Model | 1080p | 1440p | 4K |
|-------|-------|-------|-----|
| ltx-2-fast | ~$0.02/sec | ~$0.04/sec | ~$0.08/sec |
| ltx-2-pro | ~$0.05/sec | ~$0.10/sec | ~$0.20/sec |

Quick estimates:
- **Fast preview** (fast, 1080p, 6 sec) ≈ $0.12
- **Standard clip** (pro, 1080p, 8 sec) ≈ $0.40
- **Cinematic shot** (pro, 4K, 10 sec) ≈ $2.00

Always start with the cheapest option (fast, 1080p, 6 sec) unless the user
explicitly asks for higher quality. Iterate on the prompt first, then scale up.

## Setup: Create the Generation Script

Before generating any video, ensure `ltx_generate.py` exists in the working directory.
If it doesn't exist, create it with the content from `scripts/ltx_generate.py`.

This script handles all API calls, file saving, and error handling.
It must be created ONCE and then reused for all generations.

## Choosing the Right Model

| | ltx-2-fast | ltx-2-pro |
|---|---|---|
| Speed | ~5-15 seconds | ~30-90 seconds |
| Quality | Good, slight artifacts | Cinematic, sharp details |
| Max duration | 20 sec (1080p/25fps) | 10 sec |
| Max resolution | 4K (3840x2160) | 4K (3840x2160) |
| Audio sync | Yes | Yes |
| Best for | Previews, iteration, drafts | Final output, client work |

**Decision rules:**
- User wants quick preview or is iterating → **ltx-2-fast**
- User wants final quality, cinematic look → **ltx-2-pro**
- User says "quick", "fast", "draft" → **ltx-2-fast**
- User says "best quality", "cinematic", "pro", "final" → **ltx-2-pro**
- When in doubt → start with **ltx-2-fast**, offer to upgrade

## Generation Workflow

### 1. Preflight Check

Verify API key and connectivity:

```
python3 ltx_generate.py --test
```

- `OK` → proceed
- `ERROR: LTX_API_KEY is not set` → tell user to set it: `export LTX_API_KEY=your_key`
- `ERROR: 401` → key invalid, get a new one at console.ltx.video
- `ERROR: 403` → no credits, add funds at console.ltx.video

### 2. Build the Prompt

**This is the most important step.** A great prompt = a great video. A lazy prompt = garbage.

Read `references/prompting-guide.md` for the full guide. Quick rules:

1. **One flowing paragraph** — no bullet points, no line breaks
2. **Present tense** — "A woman walks" not "A woman walked"
3. **Chronological order** — describe what happens first, then next
4. **Be specific** — "A 30-year-old woman in a red coat" not "a person"
5. **Include camera** — "The camera slowly dollies forward"
6. **Include atmosphere** — lighting, weather, mood, colors
7. **Include audio cues** — dialog in quotes, sound effects described
8. **4-8 sentences** — not too short, not too long

**Always enhance the user's prompt** before sending to the API. If the user says
"make a video of a cat on a beach", expand it into a proper cinematic prompt.

### 3. Generate

#### Text-to-Video (most common)

```bash
python3 ltx_generate.py t2v "Your detailed prompt here" --model ltx-2-fast --duration 6 --resolution 1080p
```

#### Image-to-Video

```bash
python3 ltx_generate.py i2v "Description of desired motion" --image /path/to/image.jpg --model ltx-2-pro --duration 8
```

#### Audio-to-Video (Pro only, 1080p only)

```bash
python3 ltx_generate.py a2v "Visual scene description" --audio /path/to/audio.mp3 --model ltx-2-pro
```

### 4. Camera Motion (optional)

Add `--camera` flag for preset camera movements:

```bash
python3 ltx_generate.py t2v "prompt" --camera dolly_in
```

Available motions: `dolly_in`, `dolly_out`, `pan_left`, `pan_right`, `crane_up`, `crane_down`, `static`, `handheld`

### 5. Audio Generation

By default, videos include AI-generated audio. To disable:

```bash
python3 ltx_generate.py t2v "prompt" --no-audio
```

### 6. Output

Videos are saved as MP4 to:
```
~/Desktop/cineclaw/cineclaw-{timestamp}.mp4
```

After generation, always:
1. Tell the user the file location
2. Report the actual cost/credits consumed
3. Ask if they want to iterate (refine prompt) or scale up (higher quality)

## Prompt Enhancement

When the user gives a vague prompt, ALWAYS enhance it before generating.

**User says:** "a dog running"
**You send to API:** "A medium wide shot of a golden retriever sprinting joyfully across a sunlit meadow at golden hour. The dog's ears flap in the wind as its paws kick up small clouds of grass and dirt. The camera tracks alongside the dog at ground level, slightly bouncing with the motion. Warm amber light filters through scattered wildflowers in the background. The sound of panting, rustling grass, and distant birdsong fills the air."

**User says:** "futuristic city"
**You send to API:** "A sweeping aerial establishing shot of a neon-drenched megacity at night. Towering holographic billboards pulse between chrome skyscrapers as flying vehicles weave through illuminated traffic corridors. The camera slowly cranes down from above, revealing rain-slicked streets reflecting a kaleidoscope of blue and magenta light. Steam rises from grated vents on the ground. A low electronic hum underlays the ambient noise of distant engines and muffled city chatter."

Always show the enhanced prompt to the user before generating so they can approve or adjust.

## Iterative Workflow (Recommended)

Best results come from iteration:

1. **Draft** → fast model, 1080p, 6 sec, basic prompt
2. **Refine** → adjust prompt based on what you see, keep fast model
3. **Polish** → switch to pro model, bump resolution/duration
4. **Final** → pro model, desired resolution, with audio

This saves money and gets better results than one expensive shot.

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| `401 Unauthorized` | API key invalid | User needs new key from console.ltx.video |
| `403 Forbidden` | No credits remaining | User needs to add funds |
| `422 Unprocessable` | Invalid params (bad resolution, duration combo) | Check supported models table in references/ltx-api.md |
| `429 Too Many Requests` | Rate limited | Wait 30 seconds and retry |
| `503 Service Unavailable` | API down | Wait 5 min, retry once |
| `504 Gateway Timeout` | Generation took too long | Try shorter duration or lower resolution |
| Empty/corrupt file | Generation failed silently | Retry with simpler prompt |

## Example Prompts by Category

### Cinematic / Film
- "Generate a cinematic shot of a lone figure walking through fog in an abandoned warehouse"
- "Create a dramatic slow-motion close-up of rain hitting a window at night"

### Product / Commercial
- "Animate this product photo with a slow 360 rotation and soft studio lighting"
- "Make a sleek product reveal video for this sneaker image"

### Nature / Landscape
- "Generate a timelapse of clouds rolling over a mountain range at sunset"
- "Create an underwater shot of coral reef with fish swimming through"

### Creative / Abstract
- "Make an abstract video of liquid gold flowing through geometric shapes"
- "Generate a dreamlike sequence of floating islands in a purple sky"

### Social Media / Short-form
- "Quick 6-second loop of coffee being poured in slow motion"
- "Animated background for a podcast clip — neon waves on dark background"
