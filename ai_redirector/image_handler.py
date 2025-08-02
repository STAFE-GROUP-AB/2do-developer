#!/usr/bin/env python3
"""
Image Handler - Manages clipboard image operations and preview functionality
"""

import io
import os
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageOps
import pyperclip

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ImageHandler:
    """Handles clipboard image operations and preview functionality"""
    
    def __init__(self):
        self.console = Console()
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_redirector_images"
        self.temp_dir.mkdir(exist_ok=True)
    
    def check_clipboard_for_image(self) -> Optional[Image.Image]:
        """Check if clipboard contains an image and return it"""
        try:
            # Try to get image from clipboard
            # Note: This approach works mainly on Windows/Mac with proper clipboard support
            # For cross-platform support, we might need platform-specific implementations
            
            # First try to get clipboard content as text (might be base64 or file path)
            try:
                clipboard_content = pyperclip.paste()
                
                # Check if it's a base64 encoded image
                if self._is_base64_image(clipboard_content):
                    return self._decode_base64_image(clipboard_content)
                
                # Check if it's a file path to an image
                if self._is_image_file_path(clipboard_content):
                    return Image.open(clipboard_content)
                    
            except Exception:
                pass
            
            # Try PIL clipboard methods (platform specific)
            try:
                from PIL import ImageGrab
                image = ImageGrab.grabclipboard()
                if image is not None:
                    return image
            except Exception:
                pass
                
        except Exception as e:
            # Silently fail - no image in clipboard
            pass
        
        return None
    
    def _is_base64_image(self, content: str) -> bool:
        """Check if content is a base64 encoded image"""
        try:
            if not content or len(content) < 100:
                return False
            
            # Check for data URL format
            if content.startswith('data:image/'):
                return True
            
            # Try to decode as base64
            import base64
            if content.startswith('/9j/') or content.startswith('iVBOR'):  # JPEG or PNG headers
                base64.b64decode(content)
                return True
                
        except Exception:
            pass
        return False
    
    def _decode_base64_image(self, content: str) -> Optional[Image.Image]:
        """Decode base64 image content"""
        try:
            import base64
            
            # Handle data URL format
            if content.startswith('data:image/'):
                header, data = content.split(',', 1)
                content = data
            
            # Decode base64
            image_data = base64.b64decode(content)
            image = Image.open(io.BytesIO(image_data))
            return image
            
        except Exception:
            return None
    
    def _is_image_file_path(self, content: str) -> bool:
        """Check if content is a path to an image file"""
        try:
            if not content or '\n' in content or len(content) > 500:
                return False
            
            path = Path(content.strip())
            if path.exists() and path.is_file():
                # Check for image extensions
                image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
                return path.suffix.lower() in image_extensions
                
        except Exception:
            pass
        return False
    
    def save_image_temporarily(self, image: Image.Image, prefix: str = "pasted_image") -> str:
        """Save image to temporary file and return path"""
        # Generate unique filename
        import uuid
        filename = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
        file_path = self.temp_dir / filename
        
        # Convert to RGB if necessary (for PNG saving)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Keep transparency for PNG
            image.save(file_path, 'PNG')
        else:
            # Convert to RGB for other formats
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(file_path, 'PNG')
        
        return str(file_path)
    
    def create_ascii_preview(self, image: Image.Image, max_width: int = 60, max_height: int = 20) -> str:
        """Create ASCII art preview of image"""
        try:
            # Resize image to fit in terminal
            image = image.copy()
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Convert to grayscale
            image = image.convert('L')
            
            # ASCII characters from darkest to lightest
            ascii_chars = '@%#*+=-:. '
            
            ascii_lines = []
            width, height = image.size
            
            for y in range(height):
                line = ''
                for x in range(width):
                    pixel = image.getpixel((x, y))
                    # Map pixel value (0-255) to ASCII character
                    char_index = min(len(ascii_chars) - 1, pixel * len(ascii_chars) // 256)
                    line += ascii_chars[char_index]
                ascii_lines.append(line)
            
            return '\n'.join(ascii_lines)
            
        except Exception as e:
            return f"[Error creating preview: {e}]"
    
    def display_image_info(self, image: Image.Image, file_path: str = None):
        """Display image information in a nice panel"""
        try:
            width, height = image.size
            mode = image.mode
            file_size = ""
            
            if file_path and os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                if size_bytes < 1024:
                    file_size = f"{size_bytes} bytes"
                elif size_bytes < 1024 * 1024:
                    file_size = f"{size_bytes / 1024:.1f} KB"
                else:
                    file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Create info text
            info_lines = [
                f"📐 Dimensions: {width} x {height} pixels",
                f"🎨 Mode: {mode}",
            ]
            
            if file_size:
                info_lines.append(f"💾 Size: {file_size}")
            
            if file_path:
                info_lines.append(f"📁 Path: {file_path}")
            
            info_text = "\n".join(info_lines)
            
            # Create ASCII preview
            preview = self.create_ascii_preview(image)
            
            # Display in panels
            self.console.print("\n")
            self.console.print(Panel(info_text, title="🖼️  Image Information", style="blue"))
            self.console.print(Panel(preview, title="👀 Preview", style="green"))
            
        except Exception as e:
            self.console.print(f"❌ Error displaying image info: {e}")
    
    def prompt_for_clipboard_image(self) -> Optional[str]:
        """Check for clipboard image and handle it if found"""
        image = self.check_clipboard_for_image()
        
        if image is not None:
            self.console.print("🖼️  Image detected in clipboard!")
            
            # Display preview
            self.display_image_info(image)
            
            # Ask user if they want to use it
            from rich.prompt import Confirm
            if Confirm.ask("Would you like to use this image?"):
                # Save to temporary file
                file_path = self.save_image_temporarily(image)
                self.console.print(f"✅ Image saved temporarily to: {file_path}")
                return file_path
        else:
            # No image in clipboard, but let's offer alternative
            from rich.prompt import Confirm
            if Confirm.ask("No image detected in clipboard. Would you like to load an image file instead?"):
                from rich.prompt import Prompt
                file_path = Prompt.ask("Enter path to image file")
                if file_path and os.path.exists(file_path) and self._is_image_file_path(file_path):
                    try:
                        # Load and display the image
                        image = Image.open(file_path)
                        self.display_image_info(image, file_path)
                        return file_path
                    except Exception as e:
                        self.console.print(f"❌ Error loading image: {e}")
                else:
                    self.console.print("❌ Invalid image file path")
        
        return None
    
    def cleanup_old_temp_files(self, max_age_hours: int = 24):
        """Clean up old temporary image files"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for file_path in self.temp_dir.glob("pasted_image_*.png"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        
        except Exception:
            pass  # Silently ignore cleanup errors