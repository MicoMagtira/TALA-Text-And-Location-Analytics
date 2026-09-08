# Audio design

TALA treats sound as an optional browser-side enhancement. It never stores audio
bytes in Streamlit session state and never sends them through a Streamlit delta.
The browser fetches the runtime MP3 files from `/app/static/audio/` directly.

## Behaviour

- The language gate includes **Sound settings** before the trainee presses START.
- The gate attempts to begin background music as soon as it loads. If a browser
  blocks unmuted autoplay, the first gate interaction (including choosing a
  language, opening sound settings, or pressing START) begins the loop instead.
- Pressing START plays the dedicated start cue. Other interactive controls use
  the short click cue, including page-navigation links, Learn expanders, tabs,
  radio buttons, checkboxes, toggles, menu items, and ordinary buttons.
- The sidebar repeats the controls as **Music** and **SFX**, each with an on/off
  toggle and a 0–100 volume slider. Preferences are session-specific.
- Modern browser autoplay policies can reject the initial, unmuted playback
  attempt. The gate therefore retries from the visitor's first click, while a
  browser or operating-system mute setting can still suppress playback. The app
  remains fully usable in either case.

## Runtime assets

| File | Use | Source |
|---|---|---|
| `static/audio/tala-background.mp3` | looping background music | optimized from the supplied `assets/Sound Loop/bg.wav` master |
| `static/audio/tala-start.mp3` | language-gate START cue | supplied start-button effect |
| `static/audio/tala-click.mp3` | ordinary button cue | supplied click effect |

The supplied WAV master is 10:18 long and about 170 MB. It is deliberately not
committed: GitHub's normal file limit is lower, and serving it to every trainee
would be needlessly expensive. The checked-in MP3 is stereo, 44.1 kHz and 96
kb/s (about 7.1 MB). Keep source recordings, Adobe session files, wave caches,
and alternate takes in the ignored `assets/Sound Loop/` and `assets/Start Button/`
directories.

To rebuild the background asset locally after replacing the WAV master:

```powershell
ffmpeg -y -i "assets/Sound Loop/bg.wav" -codec:a libmp3lame -b:a 96k -ar 44100 `
  static/audio/tala-background.mp3
```

`enableStaticServing = true` in `.streamlit/config.toml` is required. Do not
turn it off unless the audio manager is changed to use another hosting route.

Before distributing the app, confirm that the team holds the required rights or
licenses for each supplied music and sound-effect source.
