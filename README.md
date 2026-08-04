# Salon Multi-Tenant Vertical  SaaS Platform (Backend  Engine)

A robust, cloud-native, multi-tenant Software-as-a-Service (SaaS) platform built specifically for barbershops, beauty salons, and spa management. This unified backend engine allows multiple independent businesses (Tenants) to register, manage their unique staff schedules, process bookings, track sales, and access isolated dashboards under a single system architecture.

---

## 🏗️ Architectural Core: Logical Multi-Tenancy

To ensure maximum performance and clean data isolation, this platform implements a **Logical Multi-Tenancy Architecture using Shared Database with Row-Level Isolation**. 



Every single table in our system (except the `tenants` directory itself) contains a foreign key tracking field (`tenant_id`). When a request hits our system, custom middleware intercepts the authentication token, extracts the verified tenant identity, and dynamically filters all database transactions so that Salon A can never see data belonging to Salon B.

---

## 🚀 Key Platform Features

* **Tenant Onboarding & Routing:** Automated tenant workspace creation with unique slugs (e.g., `salon-platform.com/api/v1/glam-barbers`).
* **RBAC Authentication (Role-Based Access Control):** Granular authorization permissions for System Admins, Salon Owners, Staff/Stylists, and Customers.
* **Dynamic Smart Scheduling:** Real-time booking system that cross-references stylist working hours, service durations, and existing slot availability.
* **Point of Sale (POS) & Checkout:** Checkout flows designed to log service sales, product inventories, and process digital payments.
* **Scalable Cloud Storage:** Powered by a high-availability serverless PostgreSQL database layer with automatic connection pooling.

---

## 🛠️ The Tech Stack

* **Language & Core Framework:** Python 3.14 + FastAPI *(Asynchronous, auto-generating Swagger open-API docs)*
* **Database Engine:** PostgreSQL hosted on **Neon Serverless DB**
* **Object-Relational Mapping (ORM):** SQLAlchemy 2.0 + Pydantic v2 *(Strict runtime data parsing and type safety validation)*
* **Authentication Engine:** JWT (JSON Web Tokens) via `python-jose` + password encryption using `passlib[bcrypt]`

---

## 📂 Active Core Entities Mapped

* **`tenants`**: The standalone business profiles (Salon names, unique routing slugs, active subscription configurations).
* **`users` / `staff`**: The human actors within a workspace (Owner, administrative staff, master barbers, beauty experts).
* **`customers`**: Isolated client databases specific to each tenant's business history.
* **`services` / `products`**: Custom treatment catalogs (Pricing, duration requirements) and physical retail inventories.
* **`bookings` / `sales`**: The primary operational transactional tables monitoring salon calendars and daily cash registers
