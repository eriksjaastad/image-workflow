#!/usr/bin/env python3
"""
Flask API Response Utilities
=============================
Provides standardized response formats for Flask API endpoints.

Security Note: Never pass raw exception messages (str(e)) to error_response
as this can expose internal details to clients. Use generic messages instead.
"""

import logging
from datetime import datetime
from typing import Any

from flask import jsonify

logger = logging.getLogger(__name__)


def error_response(
    message: str, code: int = 400, details: Any = None
) -> tuple[Any, int]:
    """Create a standardized error response.

    Security: Do not pass raw exception messages. Use generic messages like
    "An internal error occurred" for 500 errors to avoid information exposure.

    Args:
        message: Human-readable error message (should not contain sensitive info)
        code: HTTP status code (default: 400 Bad Request)
        details: Optional additional error details (use only for safe, non-sensitive data)

    Returns:
        Tuple of (Flask Response, status code)

    Examples:
        >>> error_response("Project not found", 404)
        ({'error': {'message': 'Project not found', 'code': 404, ...}}, 404)

        >>> error_response("Invalid input", 400, {"field": "port"})
        ({'error': {'message': 'Invalid input', 'code': 400, 'details': {...}, ...}}, 400)
    """
    error_obj = {
        "message": message,
        "code": code,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # Only include details if provided and for non-5xx errors (to avoid info exposure)
    if details is not None and code < 500:
        error_obj["details"] = details

    return jsonify({"error": error_obj}), code


def success_response(data: Any, code: int = 200) -> tuple[Any, int]:
    """Create a standardized success response.

    Args:
        data: Response data (will be JSON-serialized)
        code: HTTP status code (default: 200 OK)

    Returns:
        Tuple of (Flask Response, status code)
    """
    return jsonify(data), code
