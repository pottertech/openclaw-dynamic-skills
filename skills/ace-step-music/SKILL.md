---
name: ace-step-music
description: Generates professional music using ACE-Step foundation model including song generation, Lyric2Vocal, Text2Samples, audio repainting, and variations. Use when creating music tracks, vocal demos, instrument loops, podcast intros, or any audio production.
---

# ACE-Step Music Generation

Professional music generation using ACE-Step v1.5 foundation model.

**Location:** `~/.openclaw/workspace/ACE-Step/`  
**Performance:** Up to 4 minutes of music in 20 seconds (A100 GPU)  
**RTF:** 27.27x on A100, 34.48x on RTX 4090, 2.27x on M2 Max

## ⚠️ SECURITY WARNING

**Never hardcode API keys or credentials!**
```bash
export ACE_STEP_MODEL_PATH="${ACE_STEP_MODEL_PATH}"
```

## When to Use

- Creating original music tracks
- Generating vocal demos from lyrics
- Creating instrument loops and samples
- Podcast intro/outro music
- Social media background music
- Song demos and pre-production
- Audio editing and repainting

## Installation & Setup

**Already installed at:** `~/.openclaw/workspace/ACE-Step/`

**Launch GUI:**
```bash
cd ~/.openclaw/workspace/ACE-Step
acestep --port 7865
```

**Memory Optimized (Consumer GPUs):**
```bash
acestep --torch_compile true --cpu_offload true --overlapped_decode true
```

**Mac Users:** Use `--bf16 false`

## Workflows

### 1. Generate Song from Text

**Use Case:** Create complete song from description

**Steps:**
```bash
# Step 1: Launch ACE-Step
cd ~/.openclaw/workspace/ACE-Step
acestep --port 7865

# Step 2: Open browser to http://localhost:7865

# Step 3: Enter prompt
# "Upbeat pop song, catchy melody, female vocals, about summer love"

# Step 4: Add tags
# pop, upbeat, summer, female vocals, catchy

# Step 5: Set duration (e.g., 180 seconds)

# Step 6: Click Generate

# Step 7: Download result (WAV/MP3)
```

**CLI Version:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")
audio = model.generate(
    prompt="Upbeat pop song about summer",
    tags=["pop", "upbeat", "summer"],
    duration=180
)
audio.save("summer_song.wav")
```

---

### 2. Lyric2Vocal (Generate Vocals from Lyrics)

**Use Case:** Create vocal demo without recording

**Steps:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")
model.load_lora("Lyric2Vocal")

lyrics = """
[Verse 1]
Walking down the street tonight
City lights are shining bright

[Chorus]
This is my moment, this is my time
Nothing's gonna stop me, I'm gonna shine
"""

vocal_audio = model.generate_vocals(
    lyrics=lyrics,
    style="pop, female vocals, clear pronunciation"
)
vocal_audio.save("vocal_demo.wav")
```

**Applications:**
- ✅ Songwriting demos
- ✅ Guide tracks for producers
- ✅ Vocal arrangement testing
- ✅ Lyric pronunciation checking

---

### 3. Text2Samples (Generate Instrument Loops)

**Use Case:** Create instrument loops from text

**Steps:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")
model.load_lora("Text2Samples")

# Generate synth pad
synth_pad = model.generate(
    prompt="Warm analog synth pad, dreamy, C major",
    tags=["synth", "pad", "ambient"],
    duration=8  # 8-second loop
)
synth_pad.save("synth_pad_C.wav")

# Generate drum loop
drums = model.generate(
    prompt="Boom bap drum loop, 90 BPM, hip hop",
    tags=["drums", "hip hop", "boom bap"],
    duration=4  # 4-bar loop
)
drums.save("drum_loop_90bpm.wav")
```

**Applications:**
- ✅ Quick idea sketching
- ✅ Producer inspiration
- ✅ Sound design exploration
- ✅ Beat making starting points

---

### 4. Audio Repainting (Edit Generated Music)

**Use Case:** Modify specific sections

**Steps:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")

# Define mask (what to change)
mask = {
    "start_time": 30,  # seconds
    "end_time": 45,
    "operation": "repaint"
}

# Apply repainting
edited_audio = model.repaint(
    audio_path="generated_song.wav",
    mask=mask,
    new_prompt="Emotional chorus, powerful vocals, key change",
    blend_factor=0.7
)
edited_audio.save("edited_song.wav")
```

**Applications:**
- ✅ Fix specific sections
- ✅ Try alternative lyrics
- ✅ Change arrangement
- ✅ Create variations

---

### 5. Variations Generation

**Use Case:** Create multiple versions

**Steps:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")

# Generate base track
base_audio = model.generate(
    prompt="Acoustic folk song, male vocals, storytelling",
    tags=["folk", "acoustic", "storytelling"]
)

# Create variations
var1 = model.generate_variation(
    base_audio=base_audio,
    variation_strength=0.3,  # Subtle
    new_tags=["energetic", "faster"]
)

var2 = model.generate_variation(
    base_audio=base_audio,
    variation_strength=0.5,  # Moderate
    new_tags=["full band", "drums, bass"]
)

var3 = model.generate_variation(
    base_audio=base_audio,
    variation_strength=0.7,  # Significant
    new_tags=["rock version", "electric guitar"]
)
```

**Applications:**
- ✅ A/B testing
- ✅ Explore arrangements
- ✅ Create remixes
- ✅ Find best version

---

### 6. RapMachine (Rap Generation)

**Use Case:** Generate rap verses with flow

**Steps:**
```python
from ace_step import ACEStep

model = ACEStep.from_pretrained("ACE-Step/ACE-Step-v1-3.5B")
model.load_lora("ACE-Step/ACE-Step-v1-chinese-rap-LoRA")

rap_lyrics = """
[Verse 1]
Started from the bottom, now we here
Worked so hard, year after year
"""

rap_track = model.generate_rap(
    lyrics=rap_lyrics,
    style="old school hip hop, boom bap, 90 BPM",
    flow_pattern="classic",  # or "modern", "triplet"
    energy="high"
)
rap_track.save("rap_verse.wav")
```

**Applications:**
- ✅ Rap songwriting
- ✅ Battle rap practice
- ✅ Flow experimentation
- ✅ Hip hop production

---

## Performance Settings

### Consumer GPUs (8GB VRAM)
```bash
acestep --torch_compile true --cpu_offload true --overlapped_decode true
```

### High-End GPUs (RTX 4090)
```bash
acestep --bf16 true --device_id 0
# RTF: 34.48x (1 min audio in 1.74 seconds)
```

### Mac (M2 Max)
```bash
acestep --bf16 false --device_id cpu
# RTF: 2.27x (1 min audio in 26 seconds)
```

### Step Count Trade-offs
- **27 steps:** Fast generation, good quality (recommended)
- **60 steps:** Slower, higher quality

---

## Integration Examples

### Podcast Production
```bash
# 1. Generate intro (ACE-Step)
# Prompt: "Upbeat podcast intro, 30 seconds"

# 2. Generate episode content (Kokoro TTS)
curl -X POST http://localhost:8880/api/tts \
  -d '{"text": "Welcome...", "voice": "am_echo"}' \
  --output episode.wav

# 3. Generate outro (ACE-Step)
# Prompt: "Podcast outro, 20 seconds"

# 4. Combine (FFmpeg)
ffmpeg -y \
  -i intro.wav \
  -i episode.wav \
  -i outro.wav \
  -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1" \
  podcast_episode.mp3
```

### Music Video
```bash
# 1. Generate song (ACE-Step)
# 2. Generate visuals (ComfyUI)
# 3. Combine (FFmpeg)
ffmpeg -framerate 30 -i visuals_%04d.png \
  -i song.wav \
  -c:v libx264 -c:a aac \
  music_video.mp4
```

---

## Best Practices

1. **Use Specific Tags** - Genre, mood, instruments, tempo
2. **Start with 27 Steps** - Faster iteration, increase for final
3. **Use Lyric2Vocal for Demos** - Quick vocal testing
4. **Generate Variations** - Explore multiple versions
5. **Save Input Params** - Reproducibility

---

## Troubleshooting

**Issue:** Out of memory  
**Fix:** Use `--torch_compile true --cpu_offload true --overlapped_decode true`

**Issue:** Slow generation  
**Fix:** Reduce steps to 27, use lower quality preset

**Issue:** Poor lyric alignment  
**Fix:** Use Lyric2Vocal LoRA, break lyrics into smaller segments

**Issue:** Mac errors  
**Fix:** Use `--bf16 false`

---

## Resources

- **Local Path:** `~/.openclaw/workspace/ACE-Step/`
- **v1.5 Docs:** https://ace-step.github.io/ace-step-v1.5.github.io/
- **Technical Report:** https://arxiv.org/abs/2506.00045
- **Hugging Face:** https://huggingface.co/ACE-Step/ACE-Step-v1-3.5B
- **Discord:** https://discord.gg/PeWDxrkdj7

---

## Examples

**Input Params JSON:**
```json
{
  "prompt": "Upbeat pop song, catchy melody",
  "tags": ["pop", "upbeat", "catchy"],
  "duration": 180,
  "steps": 27,
  "cfg_scale": 7.0,
  "seed": 42
}
```

**Output:** WAV/MP3 audio file ready for use in productions
