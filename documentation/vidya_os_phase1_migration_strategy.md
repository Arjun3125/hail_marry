# Phase 1 Migration Strategy

This document records the migration and rollback plan for the Phase 1
shared-data-layer changes introduced during the Vidya OS transformation.

Scope:

- `backend/src/domains/academic/models/student_profile.py`
- `backend/src/domains/academic/models/parent_link.py`
- `backend/src/domains/academic/models/core.py`
- `backend/src/domains/academic/models/batch.py`
- `backend/src/domains/administrative/models/fee.py`
- `backend/src/domains/academic/models/test_series.py`

## Objectives

Add the following schema guarantees without breaking existing tenant data:

- learner-profile context fields:
  - `current_class_id`
  - `current_batch_id`
  - `primary_parent_id`
  - `guardian_count`
- parent-link uniqueness per tenant
- enrollment uniqueness per tenant/student/class/academic year
- batch-enrollment uniqueness per tenant/batch/student
- fee invoice duplicate prevention and amount guards
- fee payment positive-amount guard
- explicit assessment lifecycle columns for test series

## Migration Order

1. Additive columns first

- add nullable learner-profile context columns
- add test-series lifecycle columns with safe defaults:
  - `assessment_kind='mock_test'`
  - `grading_mode='manual_review'`
  - `status='draft'`
  - `opens_at=NULL`
  - `closes_at=NULL`
  - `published_at=NULL`

2. Backfill learner profile context

- for each student profile row:
  - resolve latest enrollment by `tenant_id + student_id`
  - resolve latest active/trial batch enrollment
  - resolve earliest parent link for `primary_parent_id`
  - set `guardian_count`
- for students without an existing `student_profiles` row:
  - create a shell profile row before analytics backfills

3. Deduplicate before uniqueness constraints

- parent links:
  - collapse duplicate rows with the same `tenant_id + parent_id + child_id`
  - keep the oldest row by `created_at` or `id`
- enrollments:
  - collapse duplicate rows with the same
    `tenant_id + student_id + class_id + academic_year`
- batch enrollments:
  - collapse duplicate rows with the same
    `tenant_id + batch_id + student_id`
- fee invoices:
  - collapse duplicate rows with the same
    `tenant_id + student_id + fee_structure_id + due_date`

4. Validate amount constraints before check constraints

- reject or repair:
  - fee structures with `amount < 0`
  - fee invoices with `amount_due < 0`
  - fee invoices with `amount_paid < 0`
  - fee payments with `amount <= 0`

5. Add unique/check constraints last

- apply uniqueness only after dedupe queries return zero remaining collisions
- apply check constraints only after negative/invalid amounts are resolved

## Data Repair Queries To Run Before Constraint Migration

Required preflight reports:

- duplicate parent links by tenant/parent/child
- duplicate enrollments by tenant/student/class/year
- duplicate batch enrollments by tenant/batch/student
- duplicate fee invoices by tenant/student/structure/due date
- negative fee structure / invoice / payment amounts
- student profiles missing `user_id` or orphaned from users

These reports should be saved with counts before the migration is applied.

## Rollout Notes

- deploy additive columns first
- run backfill job/script
- run preflight duplicate and invalid-value reports
- repair data until reports are clean
- apply unique/check constraints
- deploy application code that assumes the stronger guarantees

## Rollback Notes

If the migration fails before constraints are added:

- roll back the migration transaction
- keep application code pinned to the pre-migration release

If additive columns were added but backfill or validation fails:

- leave new nullable columns in place
- disable code paths that depend on them
- rerun backfill after data repair

If uniqueness/check constraints fail during deployment:

- revert only the failing constraint migration
- preserve dedupe/backfill artifacts for the next attempt
- do not delete the additive columns unless a full schema rollback is required

If application behavior regresses after deployment:

- revert the application release first
- keep the additive schema changes if they are backward compatible
- only remove constraints or columns in a separate controlled rollback migration

## Program Status

This migration strategy satisfies the Phase 1 planning requirement to record
schema-change and rollback intent before full migration delivery.

It does not replace actual Alembic or SQL migration scripts, which still need
to be written and executed when Phase 1 moves from model-contract work to
database rollout.
