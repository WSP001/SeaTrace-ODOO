"""
🛡️ DEFENSIVE LAYER 8: ROLE-BASED ACCESS CONTROL (RBAC)
Blocks: Privilege Escalation, Unauthorized Access
For the Commons Good!
"""

from enum import Enum
from functools import wraps
from typing import Set, Callable
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class Role(Enum):
    """User roles (least privilege principle)"""
    FREE_USER = "free"          # PUL license (Public Use License)
    PAID_USER = "paid"          # PL license (Paid License)
    ADMIN = "admin"             # Internal admin
    SUPER_ADMIN = "super"       # God mode (use sparingly!)

class Permission(Enum):
    """Granular permissions"""
    # Data permissions
    READ_DATA = "read:data"
    WRITE_DATA = "write:data"
    DELETE_DATA = "delete:data"
    
    # User permissions
    READ_USERS = "read:users"
    MANAGE_USERS = "manage:users"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view:analytics"
    EXPORT_ANALYTICS = "export:analytics"
    
    # Admin permissions
    MANAGE_LICENSES = "manage:licenses"
    VIEW_LOGS = "view:logs"
    MANAGE_SYSTEM = "manage:system"

# Role → Permission mapping (least privilege)
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.FREE_USER: {
        Permission.READ_DATA,
    },
    Role.PAID_USER: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.VIEW_ANALYTICS,
    },
    Role.ADMIN: {
        Permission.READ_DATA,
        Permission.WRITE_DATA,
        Permission.DELETE_DATA,
        Permission.READ_USERS,
        Permission.MANAGE_USERS,
        Permission.VIEW_ANALYTICS,
        Permission.EXPORT_ANALYTICS,
        Permission.MANAGE_LICENSES,
        Permission.VIEW_LOGS,
    },
    Role.SUPER_ADMIN: set(Permission),  # All permissions
}

def has_permission(role: Role, permission: Permission) -> bool:
    """
    Check if role has permission
    
    Args:
        role: User role
        permission: Required permission
        
    Returns:
        True if role has permission, False otherwise
    """
    allowed_permissions = ROLE_PERMISSIONS.get(role, set())
    return permission in allowed_permissions

def require_permission(permission: Permission):
    """
    Decorator to require specific permission
    
    Usage:
        @require_permission(Permission.WRITE_DATA)
        async def create_item(current_user: User):
            ...
    
    Args:
        permission: Required permission
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            
            if current_user is None:
                logger.error(f"No current_user provided to {func.__name__}")
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            # Get user role
            user_role = getattr(current_user, 'role', None)
            if user_role is None:
                logger.error(f"User {current_user} has no role")
                raise HTTPException(
                    status_code=403,
                    detail="User has no assigned role"
                )
            
            # Convert string role to Role enum if needed
            if isinstance(user_role, str):
                try:
                    user_role = Role(user_role)
                except ValueError:
                    logger.error(f"Invalid role: {user_role}")
                    raise HTTPException(
                        status_code=403,
                        detail=f"Invalid role: {user_role}"
                    )
            
            # Check permission
            if not has_permission(user_role, permission):
                logger.warning(
                    f"Permission denied: {current_user} (role={user_role.value}) "
                    f"attempted {permission.value} on {func.__name__}"
                )
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "permission_denied",
                        "message": f"Permission denied: {permission.value}",
                        "required_permission": permission.value,
                        "user_role": user_role.value
                    }
                )
            
            # Permission granted, execute function
            logger.debug(f"Permission granted: {user_role.value} → {permission.value}")
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(role: Role):
    """
    Decorator to require specific role
    
    Usage:
        @require_role(Role.ADMIN)
        async def admin_only_endpoint(current_user: User):
            ...
    
    Args:
        role: Required role
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            
            if current_user is None:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            # Get user role
            user_role = getattr(current_user, 'role', None)
            if isinstance(user_role, str):
                user_role = Role(user_role)
            
            # Check role
            if user_role != role:
                logger.warning(
                    f"Role check failed: {current_user} (role={user_role.value}) "
                    f"attempted to access {func.__name__} (requires {role.value})"
                )
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "insufficient_role",
                        "message": f"This endpoint requires {role.value} role",
                        "required_role": role.value,
                        "user_role": user_role.value
                    }
                )
            
            # Role check passed
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
