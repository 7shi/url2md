#!/usr/bin/env python3
"""
TSV file management functionality

Provides common TSV file operations for cache implementations.
"""

from pathlib import Path
from typing import List


def sanitize_tsv_field(value: str) -> str:
    """Sanitize field value for TSV format
    
    Args:
        value: Field value to sanitize
        
    Returns:
        str: Sanitized value with tabs and newlines replaced by spaces
    """
    return value.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')


class TSVManager:
    """TSV file management"""
    
    def __init__(self, tsv_path: Path):
        """Initialize TSV manager
        
        Args:
            tsv_path: Path to the TSV file
        """
        self._tsv_path = tsv_path
        self.header: List[str] = []
        self.data: List[List[str]] = []
    
    @property
    def tsv_path(self) -> Path:
        """Path to TSV file"""
        return self._tsv_path
    
    def load(self) -> None:
        """Load data from TSV file"""
        if not self.tsv_path.exists():
            self.header = []
            self.data = []
            return
        
        with open(self.tsv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse header and data
        if lines:
            self.header = lines[0].strip().split('\t')
            self.data = []
            for line in lines[1:]:
                line = line.strip()
                if line:
                    self.data.append(line.split('\t'))
        else:
            self.header = []
            self.data = []
    
    def save(self) -> None:
        """Save data to TSV file"""
        # Save to temporary file
        temp_path = self.tsv_path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            # Write header
            if self.header:
                sanitized_header = [sanitize_tsv_field(field) for field in self.header]
                f.write('\t'.join(sanitized_header) + '\n')
            
            # Write data
            for row in self.data:
                sanitized_row = [sanitize_tsv_field(field) for field in row]
                f.write('\t'.join(sanitized_row) + '\n')
        
        # Atomic operation with rename
        if self.tsv_path.exists():
            self.tsv_path.unlink()
        temp_path.rename(self.tsv_path)