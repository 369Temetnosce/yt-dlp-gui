"""Application entry point for yt-dlp GUI Desktop App.

This module initializes the PyQt6 application and launches the main window.
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from .utils import setup_logging
from .main_window import MainWindow


def main() -> int:
    """Main entry point for the application.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Setup logging first
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("yt-dlp GUI v0.1.0 starting...")
    
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("yt-dlp GUI")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("yt-dlp-gui")
    
    # Set application style
    app.setStyle("Fusion")
    
    try:
        # Create and show main window
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Run event loop
        return app.exec()
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
