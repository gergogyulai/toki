#!/usr/bin/env python3
"""
Photo Library Manager CLI
"""

import os
import shutil
import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import click
from tqdm import tqdm

from .utils import (
    SUPPORTED_EXTENSIONS,
    compute_file_hash,
    get_file_datetime,
)


def collect_files(base_dir: Path) -> list[Path]:
    """Collect all supported files."""
    files = []
    for root, _, filenames in os.walk(base_dir):
        for f in filenames:
            if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(Path(root) / f)
    return files


def rename_file_worker(args: tuple[Path, bool]) -> Optional[str]:
    """Rename a single file following the rule with hash."""
    path, dry_run = args
    ext = path.suffix.lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        return None

    file_hash = compute_file_hash(path)
    dt, camera_model = get_file_datetime(path)

    if dt:
        confidence = "A"
        date_str = dt.strftime("%Y%m%d_%H%M%S")
    else:
        confidence = "C"
        date_str = "UnknownDate"

    # Format: YYYYMMDD_HHMMSS_Confidence_Camera_Hash.ext
    new_name = f"{date_str}_{confidence}_{camera_model}_{file_hash}{ext}"
    new_path = path.with_name(new_name)

    # Handle duplicates
    if new_path.exists():
        base = new_path.stem
        i = 1
        while new_path.exists():
            new_path = path.with_name(f"{base}_dup{i}{ext}")
            i += 1

    if dry_run:
        return f"Would rename: {path.name} → {new_path.name}"
    else:
        try:
            shutil.move(str(path), str(new_path))
            return f"Renamed: {path.name} → {new_path.name}"
        except Exception as e:
            return f"Error renaming {path}: {e}"


def organize_file_worker(args: tuple[Path, Path, bool, bool]) -> Optional[str]:
    """Organize a single file into YYYY/MM/DD structure."""
    path, output_dir, dry_run, copy_mode = args
    ext = path.suffix.lower()
    
    if ext not in SUPPORTED_EXTENSIONS:
        return None

    dt, _ = get_file_datetime(path)
    
    # Use file modification time as fallback
    if not dt:
        timestamp = path.stat().st_mtime
        dt = datetime.datetime.fromtimestamp(timestamp)
    
    # Create directory structure: YYYY/MM/DD/
    year = dt.strftime("%Y")
    month = dt.strftime("%m")
    day = dt.strftime("%d")
    
    target_dir = output_dir / year / month / day
    target_path = target_dir / path.name
    
    # Handle duplicates
    if target_path.exists():
        base = target_path.stem
        i = 1
        while target_path.exists():
            target_path = target_dir / f"{base}_dup{i}{ext}"
            i += 1
    
    action = "copy" if copy_mode else "move"
    
    if dry_run:
        return f"Would {action}: {path} → {target_path.relative_to(output_dir)}"
    else:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            if copy_mode:
                shutil.copy2(str(path), str(target_path))
            else:
                shutil.move(str(path), str(target_path))
            return f"{action.capitalize()}d: {path.name} → {target_path.relative_to(output_dir)}"
        except Exception as e:
            return f"Error {action}ing {path}: {e}"


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Photo Library Manager - Organize and manage your photo collections."""
    pass


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--workers", type=int, default=None, help="Number of worker processes (default: CPU count - 1)")
def rename(directory: Path, dry_run: bool, workers: Optional[int]):
    """Rename media files to YYYYMMDD_HHMMSS_Confidence_Camera_Hash.ext format.
    
    Confidence levels:
    - A: Date extracted from EXIF/metadata
    - C: Unknown date (fallback)
    """
    files = collect_files(directory)
    total = len(files)
    
    if total == 0:
        click.echo("No supported files found.")
        return
    
    click.echo(f"Found {total} files to process...")
    
    if dry_run:
        click.echo(click.style("DRY RUN MODE - No changes will be made", fg="yellow", bold=True))
    
    if workers is None:
        workers = max(1, os.cpu_count() - 1)
    
    args = [(f, dry_run) for f in files]
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(rename_file_worker, arg): arg for arg in args}
        
        with tqdm(total=total, desc="Processing files", unit="file") as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    tqdm.write(result)
                pbar.update(1)
    
    click.echo(f"\n✓ Completed: {total}/{total} files processed")


@cli.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("destination", type=click.Path(file_okay=False, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--copy", is_flag=True, help="Copy files instead of moving them")
@click.option("--workers", type=int, default=None, help="Number of worker processes (default: CPU count - 1)")
def organize(source: Path, destination: Path, dry_run: bool, copy: bool, workers: Optional[int]):
    """Organize media files into YYYY/MM/DD directory structure.
    
    Restructures a photo library into a date-based hierarchy:
    
    \b
    Organized/
    ├── 2024/
    │   ├── 01/
    │   │   └── 23/
    │   │       └── photo1.jpg
    └── 2025/
        ├── 02/
        │   └── 12/
        │       └── photo2.jpg
    
    Dates are extracted from EXIF/metadata, with file modification time as fallback.
    """
    files = collect_files(source)
    total = len(files)
    
    if total == 0:
        click.echo("No supported files found.")
        return
    
    click.echo(f"Found {total} files to organize...")
    click.echo(f"Source: {source}")
    click.echo(f"Destination: {destination}")
    
    if dry_run:
        click.echo(click.style("DRY RUN MODE - No changes will be made", fg="yellow", bold=True))
    
    action = "Copying" if copy else "Moving"
    click.echo(f"Action: {action} files\n")
    
    if workers is None:
        workers = max(1, os.cpu_count() - 1)
    
    args = [(f, destination, dry_run, copy) for f in files]
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(organize_file_worker, arg): arg for arg in args}
        
        with tqdm(total=total, desc=f"{action} files", unit="file") as pbar:
            for future in as_completed(futures):
                result = future.result()
                if result:
                    tqdm.write(result)
                pbar.update(1)
    
    click.echo(f"\n✓ Completed: {total}/{total} files processed")


if __name__ == "__main__":
    cli()
