# src/__init__.py

"""
GlimmerGrabber Application Source Package.

This package contains the core logic, application-specific modules, and utility
functions for the GlimmerGrabber application.
Sub-packages include:
- app: Handles application-level concerns like CLI, configuration, and data fetching.
- core: Contains core processing logic like image segmentation and processing.
- utils: Provides common utility functions used across the application.
"""

# This file primarily serves to mark the 'src' directory as a Python package.
# It can also be used to make specific components of submodules available at the 'src' package level,
# though this is often not necessary for applications structured with app/core/utils subpackages.

# Example of exposing a function from a submodule:
# from .app.cli import main

# By default, Python does not automatically import submodules or their contents when a package is imported.
# If you need to control what `from src import *` does, you can define `__all__`.
# However, using `import *` is generally discouraged in favor of explicit imports.
# Example:
# __all__ = ["app", "core", "utils"] # This would try to import these names if they were modules.
                                   # For subpackages, this doesn't automatically expose their contents.
