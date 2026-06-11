# Stockfish Engine Setup

This directory is where Stockfish engine binary should be placed.

## Windows

1. Download the latest Stockfish for Windows from: https://stockfishchess.org/download/
2. Extract the zip file
3. Copy the `.exe` file to this directory and rename it to `stockfish.exe`

The final path should be: `backend/engines/stockfish.exe`

## Linux / macOS

On Linux/macOS, you can either:

**Option A:** Place the binary here as `stockfish` (no extension)

**Option B:** Install via package manager:
```bash
# Ubuntu/Debian
sudo apt install stockfish

# macOS (Homebrew)
brew install stockfish
```

If Stockfish is on your `PATH`, the app will find it automatically.

## Verification

To verify Stockfish is working:
```bash
./stockfish.exe
# Should open an interactive UCI prompt — type "quit" to exit
```

## Performance Note

Analysis depth is set to 20 in `config.py`. Deeper analysis = more accurate but slower.
For faster analysis, lower the depth by editing `ANALYSIS_DEPTH` in `backend/app/config.py`.
