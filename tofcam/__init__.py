"""
TOFcam - Time-of-Flight Camera Analysis Library
=============================================

A professional library for real-time depth analysis and navigation
using Time-of-Flight cameras with advanced AI algorithms.

Modules:
    core: Core analysis engine and camera management
    web: Web interface and API server
    depth: Depth estimation using MiDaS and custom algorithms
    nav: Navigation algorithms (strategic and reactive)
    types: Data structures and type definitions
    
Author: Marcelo Lavor
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Marcelo Lavor"
__license__ = "MIT"

# Core imports for easy access
from .core import TOFAnalyzer, AnalysisConfig
from .web import TOFcamWebViewer

__all__ = [
    'TOFAnalyzer',
    'AnalysisConfig',
    'TOFcamWebViewer'
]