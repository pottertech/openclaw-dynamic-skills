---
name: creative-workflows
description: Manages creative production workflows using local tools including ComfyUI for image generation, FFmpeg for video editing, and Kokoro for audio/TTS. Use when creating multimedia content, marketing materials, social media graphics, or video productions.
---

# Creative Workflows - Local Production

Complete guide to creative production using 100% local tools (no cloud subscriptions).

## ⚠️ SECURITY WARNING

**Keep API keys secure:**
```bash
export COMFYUI_API_KEY="${COMFYUI_API_KEY}"
export KOKORO_ENDPOINT="http://localhost:8880"
```

## When to Use

- Creating social media graphics
- Producing marketing videos
- Generating product images
- Creating audio voiceovers
- Designing brand materials

## Tools Available

| Tool | Purpose | Location |
|------|---------|----------|
| **ComfyUI** | Image generation | `/Volumes/ComfyUI-and-Data/comfyui` |
| **FFmpeg** | Video editing | System (brew install ffmpeg) |
| **Kokoro TTS** | Audio generation | `http://localhost:8880` |
| **Chatterbox** | Voice cloning | Local (when configured) |

## Workflows

### Social Media Graphics

**Instagram Post:**
```bash
# Step 1: Generate Base Image (ComfyUI)
cd /Volumes/ComfyUI-and-Data/comfyui
source venv/bin/activate
python main.py --workflow instagram_post.json \
  --prompt "Professional product photo, studio lighting" \
  --output /Volumes/SharedData/instagram_post.png

# Step 2: Apply Brand Guidelines
# Use creating-brand-guidelines skill
# - Apply brand colors
# - Use brand fonts
# - Follow brand voice

# Step 3: Add Text Overlay
# Use designing-canvases skill
# - Set up artboard (1080x1080 for Instagram)
# - Add text with brand fonts
# - Export as WebP

# Step 4: Export & Post
# ComfyUI → WebP format
# using-telegram-bot → Schedule post
```

**LinkedIn Banner:**
```bash
# ComfyUI workflow
python main.py --workflow linkedin_banner.json \
  --prompt "Professional business background, corporate style" \
  --dimensions 1584x396 \
  --output banner.png
```

### Marketing Videos

**Product Demo Video:**
```bash
# Step 1: Generate Scene Images (ComfyUI)
python main.py --workflow product_scenes.json \
  --prompt "Product showcase, professional lighting" \
  --batch-size 5 \
  --output-dir /tmp/scenes/

# Step 2: Create Voiceover (Kokoro TTS)
curl -X POST http://localhost:8880/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Introducing our amazing product...",
    "voice": "af_heart",
    "speed": 1.0
  }' \
  --output /tmp/voiceover.wav

# Step 3: Edit Together (FFmpeg)
ffmpeg -y \
  -framerate 1/3 \
  -i /tmp/scenes/image_%01d.png \
  -i /tmp/voiceover.wav \
  -c:v libx264 \
  -c:a aac \
  -shortest \
  -pix_fmt yuv420p \
  output.mp4

# Step 4: Add Transitions (FFmpeg)
ffmpeg -i output.mp4 \
  -vf "fade=in:0:30,fade=out:120:30" \
  -c:a copy \
  final.mp4

# Step 5: Export for Social Media
# Instagram: 1080x1080, <60s
# YouTube: 1920x1080, any length
# LinkedIn: 1920x1080, <10min
```

**Testimonial Video:**
```bash
# Combine customer photo + text + voiceover
ffmpeg -y \
  -loop 1 -i customer_photo.jpg \
  -i testimonial_audio.wav \
  -vf "drawtext=text='Great product!':fontsize=24:fontcolor=white:x=50:y=50" \
  -t 15 \
  testimonial.mp4
```

### Brand Guidelines

**Brand Identity Package:**
```bash
# Step 1: Define Brand Elements
# Use creating-brand-guidelines skill
# - Primary colors (HEX/RGB)
# - Typography (fonts, sizes)
# - Voice & tone
# - Logo usage

# Step 2: Create Templates
# Use designing-canvases skill
# - Social media templates
# - Email templates
# - Presentation templates

# Step 3: Generate Examples
# Use ComfyUI with brand colors
python main.py --workflow brand_examples.json \
  --prompt "Brand showcase, consistent style" \
  --controlnet-colors "#0066CC,#FF6600" \
  --output brand_examples.png

# Step 4: Interactive Brand Guide
# Use building-web-artifacts skill
# - Create React component
# - Show color palette
# - Typography scale
# - Usage examples
```

### Audio Production

**Podcast Intro:**
```bash
# Step 1: Generate Voiceover (Kokoro)
curl -X POST http://localhost:8880/api/tts \
  -d '{
    "text": "Welcome to the podcast!",
    "voice": "am_echo",
    "speed": 1.0
  }' \
  --output intro.wav

# Step 2: Add Background Music
ffmpeg -y \
  -i intro.wav \
  -i background_music.mp3 \
  -filter_complex "[1]volume=0.3[bg];[0][bg]amix" \
  intro_with_music.wav

# Step 3: Normalize Audio
ffmpeg -i intro_with_music.wav \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
  intro_final.wav
```

**Audiobook Narration:**
```bash
# Batch generate chapters
for chapter in chapters/*.txt; do
  curl -X POST http://localhost:8880/api/tts \
    -d "{
      \"text\": \"$(cat $chapter)\",
      \"voice\": \"af_heart\",
      \"speed\": 0.9
    }" \
    --output "audio/$(basename $chapter .txt).wav"
done

# Combine chapters
ffmpeg -f concat -i filelist.txt -c copy audiobook.mp3
```

### Data Visualization

**Marketing Dashboard:**
```bash
# Step 1: Pull Data
# Use database-query-and-export skill
psql -d marketing -c "
  SELECT date, impressions, clicks, conversions
  FROM campaigns
  WHERE date > NOW() - INTERVAL '30 days'
" --csv > campaign_data.csv

# Step 2: Analyze
# Use csv-data-summarizer skill

# Step 3: Visualize
# Use d3js-data-visualization skill
# - Line chart for trends
# - Bar chart for comparisons
# - Pie chart for distribution

# Step 4: Export
# Use building-web-artifacts skill
# - Interactive React dashboard
# - Export as PNG/PDF
```

## Best Practices

### Image Generation (ComfyUI)
- Use Flux models for photorealistic results
- Set appropriate resolution (1024x1024 for social)
- Use controlnets for consistency
- Batch generate for variations

### Video Editing (FFmpeg)
- Always use `-y` to overwrite
- Set appropriate codecs (libx264 for video, aac for audio)
- Use `-pix_fmt yuv420p` for compatibility
- Normalize audio levels

### Audio (Kokoro)
- Choose appropriate voice (af_heart for warm, am_echo for authoritative)
- Adjust speed (0.9-1.1 for natural feel)
- Add background music at -20dB
- Normalize to -16 LUFS

### Workflow Efficiency
- Create template workflows (JSON files)
- Batch process when possible
- Use consistent naming conventions
- Document successful prompts

## Troubleshooting

**Issue:** ComfyUI out of memory
**Fix:** Reduce batch size, use --lowvram flag

**Issue:** FFmpeg encoding slow
**Fix:** Use hardware acceleration (-c:v h264_videotoolbox on Mac)

**Issue:** TTS sounds robotic
**Fix:** Adjust speed (0.9-1.0), add pauses in text

**Issue:** Inconsistent brand colors
**Fix:** Use controlnet-colors in ComfyUI, create color palette reference

## Example Prompts

**Product Photography:**
```
Professional product photo, studio lighting, white background, 
high detail, commercial photography, 50mm lens
```

**Social Media Graphic:**
```
Instagram post design, modern minimalist, brand colors, 
clean typography, engaging visual, marketing material
```

**Video Thumbnail:**
```
YouTube thumbnail, eye-catching, bold text, vibrant colors, 
professional quality, high contrast, click-worthy
```

