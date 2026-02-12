# LTX-2 Prompting Guide

## Golden Rule

Write prompts like a cinematographer describing a single shot. One flowing paragraph,
present tense, chronological order, 4-8 sentences. No bullet points, no lists.

## Prompt Structure (in order)

1. **Shot type** — Close-up, medium, wide, aerial, POV
2. **Scene/environment** — Location, lighting, weather, time of day, atmosphere
3. **Subject + action** — Who/what, physical appearance, what they're doing
4. **Camera movement** — Dolly, pan, crane, track, static, handheld
5. **Visual style** — Color grade, film stock look, lens choice
6. **Audio cues** — Dialog in "quotes", ambient sounds, music mood

## Examples by Quality Level

### Bad prompt (vague, no structure)
> a cat on a beach

### Okay prompt (some detail)
> A cat sitting on a sandy beach at sunset with waves in the background

### Great prompt (cinematic, detailed)
> A medium close-up of an orange tabby cat sitting regally on warm golden sand at
> sunset. Gentle waves lap at the shore behind it as the sky burns with deep amber
> and rose hues. The cat turns its head slowly toward camera, whiskers catching the
> last light. The camera holds steady at the cat's eye level, with a shallow depth
> of field blurring the ocean into soft bokeh. The sound of rolling waves and a
> distant seagull fill the air.

## Camera Language

Use these terms for precise camera control:

| Term | Effect |
|------|--------|
| dolly in/out | Camera moves toward/away from subject |
| pan left/right | Camera rotates horizontally |
| tilt up/down | Camera rotates vertically |
| crane up/down | Camera physically moves up/down |
| track left/right | Camera moves sideways alongside subject |
| orbit | Camera circles around subject |
| handheld | Natural slight shake for documentary feel |
| steadicam | Smooth floating follow shot |
| static | Camera doesn't move |
| rack focus | Focus shifts from foreground to background |

**Rule: One camera movement per shot.** Don't stack "dolly in while panning left 
and craning up". Pick one.

## Lens Language (optional, adds realism)

- `35mm` — Natural perspective, good for medium shots
- `50mm` — Portrait-like, slight compression
- `85mm` — Strong background blur, close-ups
- `24mm` — Wide angle, environments, establishing shots
- `macro` — Extreme close-up on small details
- `anamorphic` — Cinematic wide format with lens flares

## Lighting Keywords

- `golden hour` — Warm, directional, magic hour
- `overcast` — Soft, even, diffused
- `neon-lit` — Saturated artificial colors
- `dramatic side lighting` — Strong contrast, moody
- `backlit` — Subject silhouetted against bright background
- `practical lighting` — Light from sources in the scene (lamps, screens)
- `chiaroscuro` — High contrast dark/light, Rembrandt-style

## Audio Description

LTX-2 generates synchronized audio. Include audio cues in your prompt:

- **Dialog**: Put in quotes — `The man says "I've been waiting for this"`
- **Ambient sounds**: "The hum of fluorescent lights and distant traffic"
- **Music mood**: "A melancholic piano melody plays softly"
- **Sound effects**: "Footsteps echo on wet concrete"
- **Silence**: "The room is eerily silent except for a ticking clock"

## What to AVOID

- **Internal emotions**: Don't say "she feels sad" — show it: "her shoulders slump, she stares at the floor"
- **Text/logos on screen**: The model struggles with readable text
- **Complex physics**: Avoid fluid simulations, fire propagation, breaking glass
- **Multiple subjects with separate actions**: Keep it to 1-2 subjects max
- **Overloaded prompts**: More than 8-10 sentences degrades quality
- **Past tense**: Always present tense ("walks" not "walked")
- **Abstract concepts**: Be literal and visual, not metaphorical

## Duration Tips

| Duration | Best for |
|----------|----------|
| 6 sec | Single action, loop-friendly, social media |
| 8 sec | Complete mini-scene with beginning and end |
| 10 sec | Full narrative moment with setup and payoff |
| 15-20 sec | Extended scene (fast model only at 1080p/25fps) |

For longer shots, structure the prompt as a mini-narrative:
"[Opening setup]. [Action unfolds]. [Resolution or transition]."

## Style Modifiers (append to any prompt)

- `film grain, 35mm film stock` — Analog cinema look
- `raw footage, handheld, documentary style` — Gritty realism
- `smooth, polished, commercial grade` — Clean advertising look
- `dreamy, soft focus, ethereal` — Surreal/artistic
- `high contrast, desaturated, noir` — Dark moody thriller
- `vibrant, saturated, pop colors` — Energetic social media
- `stop-motion, tactile, handcrafted` — Animation style
- `anime style, cel-shaded` — Animated look

## Prompt Templates

### Product Shot
"A [shot type] of [product] on [surface] in [environment]. [Lighting description].
The camera [movement] revealing [detail]. [Surface reflections/textures]. [Ambient sound]."

### Portrait / Character
"A [shot type] of [person description: age, appearance, clothing] in [location].
[What they're doing]. [Facial expression/body language]. The camera [movement].
[Lighting]. [Audio: dialog or ambient]."

### Landscape / Environment
"A [shot type] of [location] at [time of day]. [Weather/atmosphere]. [Key visual
elements in foreground and background]. The camera [movement] across the scene.
[Colors and light quality]. [Natural sounds]."

### Action / Motion
"A [shot type] tracking [subject] as [they/it] [action verb] through [environment].
[Speed and energy description]. The camera [movement] keeping pace. [Motion blur,
particles, or environmental reactions]. [Impact sounds or music]."
