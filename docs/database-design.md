# Database Design

## Project

**Multi-Tenant CRM**

---

# Database Architecture

The application follows a multi-tenant architecture with Role-Based Access Control (RBAC).

## Applications

| App | Responsibility |
|-----|----------------|
| accounts | Authentication and user management |
| tenants | Tenant management and user membership |
| authorization | Roles and permissions |
| customer | Customer management |
| vendor | Vendor management |
| inventory | Inventory management |
| sales | Sales management |
| purchase | Purchase management |

---

# High-Level ER Diagram

```text
User
 │
 ▼
Membership
 │
 ├──────────────► Tenant
 │
 ▼
Role ───────────► Tenant
 │
 ▼
RolePermission
 │
 ▼
Permission
 │
 ├────────► Resource
 │
 └────────► PermissionType
```

---

# Core Modules

## User

Stores application users.

---

## Tenant

Represents an organization using the CRM.

---

## Membership

Associates a user with a tenant and assigns a role.

---

## PermissionType

Defines the action that can be performed.

Examples:
- View
- Create
- Update
- Delete
- Download

---

## Resource

Represents an application module.

Examples:
- Customer
- Vendor
- Inventory
- Purchase Order

---

## Permission

Represents a combination of a Resource and a PermissionType.

Example:

```
Customer + View
```

---

## Role

Represents a tenant-specific role.

Examples:
- Admin
- Manager
- Sales Executive

---

## RolePermission

Assigns permissions to roles.

---

# Design Decisions

## Multi-Tenancy

- One user can belong to multiple tenants.
- Each tenant manages its own roles.
- Business data is isolated per tenant.

## Authorization

- Resources are global.
- Permission types are global.
- Permissions are generated from Resource + PermissionType.
- Roles are tenant-specific.
- Permissions are assigned to roles (RBAC).

## Normalization

- No duplicate resources.
- No duplicate permission types.
- Unique Resource + PermissionType combinations.
- Unique Role + Permission combinations.

---

# Future Modules

- Customer Management
- Vendor Management
- Product Management
- Inventory Management
- Purchase Management
- Sales Management
- Warehouse Management
- AI Assistant

---

**Status:** Architecture Frozen (Version 1.0)