#!/usr/bin/env python3
"""
Test script to generate a sample image with various characters and symbols
for testing compression artifacts.

This script creates a lossless PNG with:
- ASCII/Unicode text symbols
- Mathematical symbols
- Emojis and special characters
- Geometric shapes (circles, squares, lines)
- Varying line thicknesses

Usage:
    python tests/test_compression_artifacts.py
    
Output:
    symbol_sample.png - Lossless baseline image for compression testing

Testing Steps:
1. Run this script to generate symbol_sample.png
2. Compress using ImageMagick: convert symbol_sample.png -quality 50 compressed.jpg
3. Compare original vs compressed for artifacts:
   - Ringing (oscillations around edges)
   - Blocking (grid patterns)
   - Loss of detail on thin lines
   - Distortion of curves
4. Test at various quality levels (10-30% for extreme artifacts)
"""

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def generate_symbol_sample(output_path='symbol_sample.png'):
    """
    Generate a test image with various symbols for compression artifact testing.
    
    Args:
        output_path: Path where the PNG will be saved
    """
    # Create a blank white canvas
    fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
    ax.set_xlim(0, 512)
    ax.set_ylim(0, 512)
    ax.axis('off')
    ax.set_facecolor('white')

    # Add various symbols with high-contrast black color
    # Text symbols (ASCII/Unicode)
    ax.text(50, 450, 'ABC123!@#', fontsize=40, color='black', fontweight='bold')
    ax.text(50, 350, 'π ∑ ∫ √ ∞', fontsize=40, color='black')  # Math symbols
    ax.text(50, 250, '❤️ ★ ☯︎ ♻︎', fontsize=40, color='black')  # Emojis/shapes

    # Geometric shapes for edge testing
    # Circle
    circle = plt.Circle((150, 150), 50, color='black', fill=False, linewidth=5)
    ax.add_patch(circle)

    # Square
    square = plt.Rectangle((300, 100), 100, 100, color='black', fill=False, linewidth=5)
    ax.add_patch(square)

    # Line with varying thickness
    ax.plot([50, 450], [50, 50], color='black', linewidth=3)
    ax.plot([50, 450], [100, 100], color='black', linewidth=10, linestyle='--')

    # Save as lossless PNG
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close()
    
    print(f"✓ Generated test image: {output_path}")
    print(f"  File size: {Path(output_path).stat().st_size:,} bytes")
    return output_path


if __name__ == '__main__':
    output_file = generate_symbol_sample()
    print(f"\nNext steps:")
    print(f"1. Compress the image: convert {output_file} -quality 50 compressed.jpg")
    print(f"2. Compare original vs compressed for artifacts")
    print(f"3. Test at various quality levels (10-30% for extreme artifacts)")

