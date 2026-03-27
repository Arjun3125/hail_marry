# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
- Wire doc watch scheduler and weekly digest pipeline.

## [0.2.0] - 2026-03-25
### Added
- Feature Management System with 61-feature catalog, AI intensity classification, and ERP module mapping.
- System Configuration Profiles: AI Tutor, AI Helper, Full ERP (one-click bulk toggle).
- Runtime `require_feature()` API guard for route-level feature gating.
- White-Label Branding Engine with logo upload and automated `colorthief` palette extraction.
- WCAG 2.1 contrast validation for brand colors.
- Dynamic CSS variable injection via `BrandingProvider` React context.
- Admin Feature Flags dashboard at `/admin/feature-flags` with intensity badges.
- Admin Branding dashboard at `/admin/branding` with live iframe preview.
- Docs chatbot API endpoints.
- Clickable citations with document viewer links.
- OpenAPI and quickstart documentation.

## [0.1.0] - 2026-03-12
### Added
- Core ERP modules (attendance, marks, assignments, timetable, complaints).
- AI assistant with RAG retrieval and citations.
- Multi-tenant auth, RBAC, audit logging, and rate limiting.
- Redis-backed AI queue, AI service, and worker.
