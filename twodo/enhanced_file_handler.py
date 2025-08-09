"""
Enhanced File Handler - Faster file operations with better user experience
"""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Callable
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
import concurrent.futures
import hashlib
import json

from .permission_manager import SessionPermissionManager

console = Console()

class FileOperationCache:
    """Cache for file operations to improve performance"""
    
    def __init__(self, cache_size: int = 1000):
        self.cache_size = cache_size
        self.read_cache: Dict[str, Dict] = {}
        self.metadata_cache: Dict[str, Dict] = {}
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Get quick hash of file for cache key"""
        try:
            stat = file_path.stat()
            return hashlib.md5(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()
        except:
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def get_cached_content(self, file_path: Path) -> Optional[str]:
        """Get cached file content if still valid"""
        try:
            file_hash = self._get_file_hash(file_path)
            cache_entry = self.read_cache.get(str(file_path))
            
            if cache_entry and cache_entry['hash'] == file_hash:
                return cache_entry['content']
        except:
            pass
        return None
    
    def cache_content(self, file_path: Path, content: str):
        """Cache file content"""
        try:
            if len(self.read_cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = min(self.read_cache.keys(), 
                               key=lambda k: self.read_cache[k]['timestamp'])
                del self.read_cache[oldest_key]
            
            file_hash = self._get_file_hash(file_path)
            self.read_cache[str(file_path)] = {
                'content': content,
                'hash': file_hash,
                'timestamp': time.time()
            }
        except Exception as e:
            console.print(f"⚠️ Cache error: {e}")
    
    def invalidate(self, file_path: Path):
        """Invalidate cache for a file"""
        self.read_cache.pop(str(file_path), None)
        self.metadata_cache.pop(str(file_path), None)


class EnhancedFileHandler:
    """Enhanced file handler with performance optimizations and better UX"""
    
    def __init__(self, permission_manager: SessionPermissionManager):
        self.permission_manager = permission_manager
        self.cache = FileOperationCache()
        self.operation_history: List[Dict] = []
        
    async def read_file_fast(self, file_path: Union[str, Path], 
                           show_progress: bool = True) -> str:
        """Fast file reading with caching and progress indication"""
        file_path = Path(file_path).resolve()
        
        # Check permissions first
        if not self.permission_manager.current_session:
            self.permission_manager.create_session()
        
        if not self.permission_manager.current_session.has_permission(str(file_path), 'read'):
            granted = self.permission_manager.request_permission(
                str(file_path), 'read', 
                reason="Fast file reading operation"
            )
            if not granted:
                raise PermissionError(f"Read permission denied for {file_path}")
        
        # Check cache first
        cached_content = self.cache.get_cached_content(file_path)
        if cached_content is not None:
            console.print(f"⚡ Cache hit: {file_path.name}")
            return cached_content
        
        # Read file with progress indication
        if show_progress and file_path.stat().st_size > 1024 * 100:  # Show progress for files > 100KB
            return await self._read_file_with_progress(file_path)
        else:
            return await self._read_file_simple(file_path)
    
    async def _read_file_simple(self, file_path: Path) -> str:
        """Simple file reading for small files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Cache the content
            self.cache.cache_content(file_path, content)
            
            # Record operation
            self._record_operation('read', file_path, len(content))
            
            return content
            
        except Exception as e:
            console.print(f"❌ Error reading {file_path}: {e}")
            raise
    
    async def _read_file_with_progress(self, file_path: Path) -> str:
        """Read large files with progress indication"""
        file_size = file_path.stat().st_size
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(f"Reading {file_path.name}", total=file_size)
            
            content_chunks = []
            bytes_read = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                while True:
                    chunk = f.read(8192)  # Read in 8KB chunks
                    if not chunk:
                        break
                    
                    content_chunks.append(chunk)
                    bytes_read += len(chunk.encode('utf-8'))
                    progress.update(task, completed=min(bytes_read, file_size))
            
            content = ''.join(content_chunks)
            
            # Cache the content
            self.cache.cache_content(file_path, content)
            
            # Record operation
            self._record_operation('read', file_path, len(content))
            
            progress.update(task, completed=file_size)
            console.print(f"✅ Read {file_path.name} ({self._format_size(file_size)})")
            
            return content
    
    async def write_file_fast(self, file_path: Union[str, Path], content: str,
                            show_progress: bool = True, create_backup: bool = True) -> bool:
        """Fast file writing with progress and backup options"""
        file_path = Path(file_path).resolve()
        
        # Check permissions
        if not self.permission_manager.current_session:
            self.permission_manager.create_session()
        
        if not self.permission_manager.current_session.has_permission(str(file_path), 'write'):
            granted = self.permission_manager.request_permission(
                str(file_path), 'write',
                reason="Fast file writing operation"
            )
            if not granted:
                raise PermissionError(f"Write permission denied for {file_path}")
        
        try:
            # Create backup if requested and file exists
            if create_backup and file_path.exists():
                await self._create_backup(file_path)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file with progress for large content
            content_size = len(content.encode('utf-8'))
            if show_progress and content_size > 1024 * 100:  # Show progress for content > 100KB
                await self._write_file_with_progress(file_path, content)
            else:
                await self._write_file_simple(file_path, content)
            
            # Invalidate cache
            self.cache.invalidate(file_path)
            
            # Record operation
            self._record_operation('write', file_path, content_size)
            
            return True
            
        except Exception as e:
            console.print(f"❌ Error writing {file_path}: {e}")
            raise
    
    async def _write_file_simple(self, file_path: Path, content: str):
        """Simple file writing for small files"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        console.print(f"✅ Wrote {file_path.name} ({self._format_size(len(content.encode('utf-8')))})")
    
    async def _write_file_with_progress(self, file_path: Path, content: str):
        """Write large files with progress indication"""
        content_bytes = content.encode('utf-8')
        total_size = len(content_bytes)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task(f"Writing {file_path.name}", total=total_size)
            
            with open(file_path, 'wb') as f:
                bytes_written = 0
                chunk_size = 8192
                
                for i in range(0, total_size, chunk_size):
                    chunk = content_bytes[i:i + chunk_size]
                    f.write(chunk)
                    bytes_written += len(chunk)
                    progress.update(task, completed=bytes_written)
            
            console.print(f"✅ Wrote {file_path.name} ({self._format_size(total_size)})")
    
    async def _create_backup(self, file_path: Path):
        """Create backup of existing file"""
        backup_path = file_path.with_suffix(f"{file_path.suffix}.backup.{int(time.time())}")
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            console.print(f"💾 Backup created: {backup_path.name}")
        except Exception as e:
            console.print(f"⚠️ Backup failed: {e}")
    
    async def batch_read_files(self, file_paths: List[Union[str, Path]], 
                              max_workers: int = 4) -> Dict[str, str]:
        """Read multiple files concurrently"""
        results = {}
        failed_files = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Reading files", total=len(file_paths))
            
            async def read_single_file(file_path):
                try:
                    content = await self.read_file_fast(file_path, show_progress=False)
                    results[str(file_path)] = content
                    progress.update(task, advance=1)
                except Exception as e:
                    failed_files.append((str(file_path), str(e)))
                    progress.update(task, advance=1)
            
            # Process files in batches to avoid overwhelming the system
            batch_size = max_workers
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i + batch_size]
                tasks = [read_single_file(fp) for fp in batch]
                await asyncio.gather(*tasks, return_exceptions=True)
        
        if failed_files:
            console.print(f"⚠️ {len(failed_files)} files failed to read:")
            for file_path, error in failed_files[:5]:  # Show first 5 failures
                console.print(f"  ❌ {file_path}: {error}")
            if len(failed_files) > 5:
                console.print(f"  ... and {len(failed_files) - 5} more")
        
        console.print(f"✅ Successfully read {len(results)}/{len(file_paths)} files")
        return results
    
    def _record_operation(self, operation: str, file_path: Path, size: int):
        """Record file operation for statistics"""
        self.operation_history.append({
            'operation': operation,
            'file_path': str(file_path),
            'size': size,
            'timestamp': time.time()
        })
        
        # Keep only last 100 operations
        if len(self.operation_history) > 100:
            self.operation_history = self.operation_history[-100:]
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_operation_stats(self) -> Dict:
        """Get statistics about file operations"""
        if not self.operation_history:
            return {}
        
        stats = {
            'total_operations': len(self.operation_history),
            'read_operations': len([op for op in self.operation_history if op['operation'] == 'read']),
            'write_operations': len([op for op in self.operation_history if op['operation'] == 'write']),
            'total_bytes_read': sum(op['size'] for op in self.operation_history if op['operation'] == 'read'),
            'total_bytes_written': sum(op['size'] for op in self.operation_history if op['operation'] == 'write'),
            'cache_hits': len(self.cache.read_cache),
            'recent_files': list(set(op['file_path'] for op in self.operation_history[-10:]))
        }
        
        return stats
    
    def show_performance_report(self):
        """Display performance statistics"""
        stats = self.get_operation_stats()
        
        if not stats:
            console.print("📊 No file operations recorded yet")
            return
        
        console.print(Panel.fit("📊 File Operation Performance Report", style="bold blue"))
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Operations", str(stats['total_operations']))
        table.add_row("Read Operations", str(stats['read_operations']))
        table.add_row("Write Operations", str(stats['write_operations']))
        table.add_row("Total Bytes Read", self._format_size(stats['total_bytes_read']))
        table.add_row("Total Bytes Written", self._format_size(stats['total_bytes_written']))
        table.add_row("Cache Entries", str(stats['cache_hits']))
        
        console.print(table)
        
        if stats['recent_files']:
            console.print("\n🔄 Recent Files:")
            for file_path in stats['recent_files'][-5:]:
                console.print(f"  • {Path(file_path).name}")
    
    def clear_cache(self):
        """Clear file operation cache"""
        cache_size = len(self.cache.read_cache)
        self.cache.read_cache.clear()
        self.cache.metadata_cache.clear()
        console.print(f"🗑️ Cleared {cache_size} cache entries")


# Global instance for easy access
_global_file_handler: Optional[EnhancedFileHandler] = None

def get_enhanced_file_handler(permission_manager: SessionPermissionManager = None) -> EnhancedFileHandler:
    """Get or create global enhanced file handler"""
    global _global_file_handler
    
    if _global_file_handler is None:
        if permission_manager is None:
            from .permission_manager import get_session_permission_manager
            permission_manager = get_session_permission_manager()
        _global_file_handler = EnhancedFileHandler(permission_manager)
    
    return _global_file_handler