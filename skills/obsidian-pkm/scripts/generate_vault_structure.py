#!/usr/bin/env python3
"""
Generate Obsidian vault folder structures for PKM workflows.

Usage:
    python3 generate_vault_structure.py --type para --path ~/Vault
    python3 generate_vault_structure.py --type zettelkasten --path ~/Vault
    python3 generate_vault_structure.py --type hybrid --path ~/Vault
"""

import argparse
import os
from pathlib import Path

def create_folder(path: Path, name: str) -> None:
    """Create a folder if it doesn't exist."""
    folder = path / name
    folder.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {folder}")

def create_para_structure(base_path: Path) -> None:
    """Create PARA folder structure."""
    print(f"\n📁 Creating PARA structure at {base_path}")
    
    # Main folders
    create_folder(base_path, "1. Projects")
    create_folder(base_path, "2. Areas")
    create_folder(base_path, "3. Resources")
    create_folder(base_path, "4. Archives")
    
    # Project subfolders
    create_folder(base_path, "1. Projects/Active")
    create_folder(base_path, "1. Projects/Upcoming")
    
    # Area examples
    create_folder(base_path, "2. Areas/Health")
    create_folder(base_path, "2. Areas/Career")
    create_folder(base_path, "2. Areas/Finances")
    create_folder(base_path, "2. Areas/Learning")
    
    # Resource examples
    create_folder(base_path, "3. Resources/Articles")
    create_folder(base_path, "3. Resources/Books")
    create_folder(base_path, "3. Resources/Research")
    create_folder(base_path, "3. Resources/Notes")
    
    # Utility folders
    create_folder(base_path, "Attachments")
    create_folder(base_path, "Templates")
    
    print("\n✅ PARA structure created!")
    print("\nNext steps:")
    print("1. Copy templates from assets/templates/ to Templates/")
    print("2. Configure Obsidian to use Templates folder")
    print("3. Start capturing in Projects/Active")

def create_zettelkasten_structure(base_path: Path) -> None:
    """Create Zettelkasten folder structure."""
    print(f"\n📁 Creating Zettelkasten structure at {base_path}")
    
    # Main folders (flat structure)
    create_folder(base_path, "01 Fleeting")
    create_folder(base_path, "02 Literature")
    create_folder(base_path, "03 Permanent")
    create_folder(base_path, "04 Indexes")
    create_folder(base_path, "05 Projects")
    
    # Utility folders
    create_folder(base_path, "Attachments")
    create_folder(base_path, "Templates")
    
    print("\n✅ Zettelkasten structure created!")
    print("\nNext steps:")
    print("1. Copy templates from assets/templates/ to Templates/")
    print("2. Set up Templater plugin for ID generation")
    print("3. Start capturing in 01 Fleeting")

def create_hybrid_structure(base_path: Path) -> None:
    """Create hybrid PARA + Zettelkasten structure."""
    print(f"\n📁 Creating Hybrid structure at {base_path}")
    
    # PARA backbone
    create_folder(base_path, "1. Projects")
    create_folder(base_path, "2. Areas")
    create_folder(base_path, "3. Resources")
    create_folder(base_path, "4. Archives")
    
    # Knowledge folders (Zettelkasten-style)
    create_folder(base_path, "3. Resources/00 Inbox")
    create_folder(base_path, "3. Resources/01 Fleeting")
    create_folder(base_path, "3. Resources/02 Literature")
    create_folder(base_path, "3. Resources/03 Permanent")
    create_folder(base_path, "3. Resources/04 Maps of Content")
    
    # Utility folders
    create_folder(base_path, "Attachments")
    create_folder(base_path, "Templates")
    
    print("\n✅ Hybrid structure created!")
    print("\nNext steps:")
    print("1. Copy templates from assets/templates/ to Templates/")
    print("2. Use PARA for actionable items")
    print("3. Use Zettelkasten for knowledge building")

def main():
    parser = argparse.ArgumentParser(
        description="Generate Obsidian vault folder structures"
    )
    parser.add_argument(
        "--type",
        choices=["para", "zettelkasten", "hybrid"],
        required=True,
        help="Type of structure to create"
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Base path for the vault"
    )
    
    args = parser.parse_args()
    
    # Create base path
    args.path.mkdir(parents=True, exist_ok=True)
    
    # Generate structure
    if args.type == "para":
        create_para_structure(args.path)
    elif args.type == "zettelkasten":
        create_zettelkasten_structure(args.path)
    elif args.type == "hybrid":
        create_hybrid_structure(args.path)
    
    print(f"\n📂 Vault ready at: {args.path.absolute()}")

if __name__ == "__main__":
    main()
