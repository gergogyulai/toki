<div align="center">
  <p>
    organize and rename your photo library the right way  
    <br/>
    <a href="https://github.com/gergogyulai/toki">github.com/gergogyulai/toki</a>
  </p>
  <br/>
</div>

toki is a fast, metadata-aware CLI tool for renaming and organizing photo and video collections.

---

### features

- Metadata-based filename standardization  
- Automatic date-based folder organization  
- Parallel processing for speed  
- Dry-run mode for safe previews  
- Supports JPG, PNG, HEIC, MP4, MOV, AVI  

---

### installation

#### quick setup (recommended)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/gergogyulai/toki/main/setup.sh)
```

If you see a PATH warning:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Check installation:

```bash
toki --help
```

#### manual setup

```bash
git clone https://github.com/gergogyulai/toki.git
cd toki
uv sync
uv pip install -e .
```

---

### usage

#### rename

Rename media files using metadata.  
Format: `YYYYMMDD_HHMMSS_Confidence_Camera_Hash.ext`

```bash
# preview only
toki rename /path/to/photos --dry-run

# rename files
toki rename /path/to/photos

# set number of workers
toki rename /path/to/photos --workers 4
```

Example:  
`20241130_143022_A_iPhone_15_Pro_a3f2d1e8.jpg`

| Field | Description |
|--------|-------------|
| YYYYMMDD_HHMMSS | Date and time from metadata |
| Confidence | A = accurate, C = unknown |
| Camera | Camera model or "Unknown" |
| Hash | 8-character MD5 hash |

---

#### organize

Restructure photos into a date-based folder hierarchy.

```bash
# preview only
toki organize /path/to/source /path/to/dest --dry-run

# move files
toki organize /path/to/source /path/to/dest

# copy instead of move
toki organize /path/to/source /path/to/dest --copy
```

Example output:

```
Organized/
├── 2024/
│   ├── 01/23/
│   │   ├── photo1.jpg
│   │   └── video1.mp4
│   └── 12/31/photo2.jpg
└── 2025/
    └── 02/12/photo3.jpg
```

---

### options

| Option | Description |
|--------|--------------|
| `--dry-run` | Preview actions without modifying files |
| `--workers N` | Number of parallel workers (default: CPU count - 1) |
| `--copy` | Copy files instead of moving (organize only) |
| `--version` | Show version information |
| `--help` | Display help message |

---

### example workflow

```bash
# organize into date-based folders
toki organize ~/messy-photos ~/organized-photos --dry-run
toki organize ~/messy-photos ~/organized-photos

# standardize filenames
toki rename ~/organized-photos --dry-run
toki rename ~/organized-photos
```

Always start with `--dry-run` to review changes before applying them.

---

### development

toki is built with [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/gergogyulai/toki.git
cd toki
uv sync
uv pip install -e .
```

Run from source:

```bash
python -m photolibnamer.main --help
```

---

### license

toki is open source, released under the [MIT License](LICENSE).