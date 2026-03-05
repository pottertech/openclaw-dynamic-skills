---
name: video-production
description: Professional video editing and production using FFmpeg. Use when editing videos, adding audio tracks, creating reels/shorts, format conversion, compression, or any video production workflow.
---

# Video Production - FFmpeg Workflows

Professional video editing, processing, and production using FFmpeg and related tools.

## When to Use

- Editing video clips (trim, merge, cut)
- Adding audio tracks or voiceovers
- Creating reels/shorts from long-form content
- Format conversion (MP4, MOV, WebM, etc.)
- Video compression/optimization
- Thumbnail extraction
- Subtitle/caption embedding
- Creating slideshows from images
- Screen recording processing

## Basic Operations

### Trim Video

```bash
# Trim from 00:01:30 to 00:02:30 (1 minute)
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:02:30 -c copy output.mp4

# Trim with re-encoding (more precise)
ffmpeg -i input.mp4 -ss 00:01:30 -t 60 -c:v libx264 -c:a aac output.mp4
```

### Merge Videos

```bash
# Create file list
echo "file 'video1.mp4'" > files.txt
echo "file 'video2.mp4'" >> files.txt
echo "file 'video3.mp4'" >> files.txt

# Merge
ffmpeg -f concat -safe 0 -i files.txt -c copy merged.mp4
```

### Extract Audio

```bash
# Extract audio from video
ffmpeg -i video.mp4 -vn -acodec copy audio.m4a

# Extract as MP3
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

### Add Audio to Video

```bash
# Add audio track (replace existing)
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4

# Mix audio with existing (background music)
ffmpeg -i video.mp4 -i music.mp3 \
  -filter_complex "[1:a]volume=0.3[bg];[0:a][bg]amix=inputs=2:duration=first" \
  -c:v copy output.mp4
```

## Production Workflows

### 1. Create Social Media Reel

```bash
# Convert landscape to vertical (9:16)
ffmpeg -i landscape.mp4 \
  -vf "crop=ih*(9/16):ih,scale=1080:1920" \
  -c:v libx264 -c:a aac \
  reel_vertical.mp4

# Add text overlay
ffmpeg -i input.mp4 \
  -vf "drawtext=text='Amazing Content!':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=50" \
  output.mp4
```

### 2. Add Voiceover to Video

```bash
# 1. Generate voiceover (Kokoro TTS)
curl -X POST http://localhost:8880/api/tts \
  -d '{"text": "Welcome to this tutorial...", "voice": "af_heart"}' \
  --output voiceover.wav

# 2. Mix with original audio
ffmpeg -i video.mp4 -i voiceover.wav \
  -filter_complex "[0:a]volume=0.3[orig];[1:a]volume=1.0[voice];[orig][voice]amix" \
  -c:v copy video_with_voiceover.mp4
```

### 3. Create Video from Images

```bash
# Slideshow from images (3 seconds each)
ffmpeg -framerate 1/3 -i image_%03d.jpg \
  -c:v libx264 -pix_fmt yuv420p \
  slideshow.mp4

# With background music
ffmpeg -framerate 1/3 -i image_%03d.jpg -i music.mp3 \
  -c:v libx264 -c:a aac \
  -shortest \
  slideshow_with_music.mp4
```

### 4. Extract Frames for ComfyUI

```bash
# Extract all frames
ffmpeg -i video.mp4 frames/frame_%04d.png

# Extract 1 frame per second
ffmpeg -i video.mp4 -vf "fps=1" frames/frame_%04d.png

# Extract specific frame (at 00:01:30)
ffmpeg -ss 00:01:30 -i video.mp4 -vframes 1 thumbnail.png
```

### 5. Compress Video

```bash
# H.264 compression (good quality/size)
ffmpeg -i input.mp4 \
  -c:v libx264 -crf 23 \
  -c:a aac -b:a 128k \
  compressed.mp4

# H.265 compression (better quality/size)
ffmpeg -i input.mp4 \
  -c:v libx265 -crf 28 \
  -c:a aac -b:a 128k \
  compressed_h265.mp4

# For web (smaller)
ffmpeg -i input.mp4 \
  -c:v libx264 -crf 28 -preset slow \
  -c:a aac -b:a 96k \
  -vf "scale=1280:720" \
  web_optimized.mp4
```

### 6. Add Subtitles

```bash
# Burn subtitles into video
ffmpeg -i video.mp4 -i subtitles.srt \
  -c:v libx264 -c:a aac \
  -vf "subtitles=subtitles.srt" \
  video_with_subs.mp4

# Soft subtitles (can be toggled)
ffmpeg -i video.mp4 -i subtitles.srt \
  -c:v copy -c:a copy -c:s mov_text \
  video_soft_subs.mp4
```

### 7. Create Thumbnail

```bash
# Extract frame at specific time
ffmpeg -ss 00:00:05 -i video.mp4 -vframes 1 thumbnail.jpg

# Generate collage (4 frames)
ffmpeg -i video.mp4 \
  -vf "fps=1,select=not(mod(n\,10)),scale=320:180,tile=2x2" \
  -vframes 1 collage.jpg
```

### 8. Screen Recording Processing

```bash
# Crop and scale screen recording
ffmpeg -i screen_recording.mp4 \
  -vf "crop=1920:1080:0:0,scale=1280:720" \
  processed.mp4

# Add webcam overlay (picture-in-picture)
ffmpeg -i screen.mp4 -i webcam.mp4 \
  -filter_complex "[1:v]scale=320:240[webcam];[0:v][webcam]overlay=W-w-10:H-h-10" \
  output.mp4
```

## Integration Examples

### With ACE-Step (Music Video)

```bash
# 1. Generate music (ACE-Step)
# Use ace-step-music skill

# 2. Generate images (ComfyUI)
# Use comfyui-image-gen skill

# 3. Create video from images
ffmpeg -framerate 1/2 -i image_%04d.png -i music.wav \
  -c:v libx264 -c:a aac \
  -shortest \
  music_video.mp4
```

### With Kokoro TTS (Tutorial Video)

```bash
# 1. Generate voiceover (Kokoro)
curl -X POST http://localhost:8880/api/tts \
  -d '{"text": "In this tutorial...", "voice": "am_echo"}' \
  --output narration.wav

# 2. Combine with screen recording
ffmpeg -i screen_recording.mp4 -i narration.wav \
  -filter_complex "[0:a]volume=0.2[screen];[1:a]volume=1.0[narration];[screen][narration]amix" \
  tutorial.mp4
```

## Performance Tips

### Hardware Acceleration

```bash
# NVIDIA GPU (NVENC)
ffmpeg -i input.mp4 -c:v h264_nvenc -crf 23 output.mp4

# Intel QuickSync
ffmpeg -i input.mp4 -c:v h264_qsv -crf 23 output.mp4

# Apple VideoToolbox
ffmpeg -i input.mp4 -c:v h264_videotoolbox output.mp4
```

### Batch Processing

```bash
#!/bin/bash
# Compress all videos in folder
for video in *.mp4; do
  ffmpeg -i "$video" \
    -c:v libx264 -crf 23 \
    -c:a aac \
    "compressed_${video}"
done
```

## Best Practices

1. **Use -c copy** when possible (no re-encoding)
2. **CRF 18-23** for good quality (lower = better)
3. **AAC audio** at 128-192 kbps
4. **H.264** for compatibility, **H.265** for efficiency
5. **Always test** with short clip first
6. **Keep originals** before processing
7. **Use hardware acceleration** when available

## Resources

- **FFmpeg Docs:** https://ffmpeg.org/documentation.html
- **FFmpeg Examples:** https://trac.ffmpeg.org/wiki/
- **CRF Guide:** https://trac.ffmpeg.org/wiki/Encode/H.264

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Status: Production Ready*
