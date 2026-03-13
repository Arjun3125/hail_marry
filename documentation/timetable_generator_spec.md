# Timetable Generator: Technical Specification (Algorithm Only)

## 1. Purpose and Scope
Generate a weekly timetable for all classes and teachers simultaneously with no collisions.
The schedule must satisfy required weekly periods per class-subject, teacher availability,
teacher load limits, fixed lessons, and strict no back-to-back rules for both classes and teachers.
Optimization target is class balance only.

Scope is limited to class and teacher constraints. Rooms and facilities are out of scope.

## 2. Goals
- Produce a feasible timetable if one exists.
- Optimize class balance across the week for each class-subject.
- Provide a clear conflict report when infeasible.

## 3. Non-Goals
- Room/lab capacity constraints.
- Teacher preference optimization beyond class balance.
- Cross-school multi-campus synchronization.

## 4. Inputs (User-Provided)

### 4.1 Time Grid
- `days_per_week`: integer (e.g., 5 or 6)
- `periods_per_day`: integer (e.g., 7 or 8)
- `breaks`: optional list of blocked `TimeSlot`s

### 4.2 Teachers
Each teacher record contains:
- `id`, `name`
- `availability`: set of allowed `TimeSlot`s
- `max_periods_per_week`: integer
- `max_periods_per_day`: integer
- `qualified_subjects` or `qualified_class_subjects`

### 4.3 Classes
Each class record contains:
- `id`, `name`
- optional `class_constraints` (reserved for future extensions)

### 4.4 Subjects
Each subject record contains:
- `id`, `name`

### 4.5 Requirements
Each requirement record contains:
- `class_id`, `subject_id`
- `required_periods_per_week`
- optional `allowed_teachers` list

### 4.6 Fixed Lessons
Each fixed lesson contains:
- `class_id`, `subject_id`, `teacher_id`, `timeSlot`
Fixed lessons are locked and must be placed exactly as provided.

### 4.7 Global Rules
- `no_back_to_back_classes`: true
- `no_back_to_back_teachers`: true

### 4.8 Optimization Weights
- `class_balance_weight`: numeric (primary and only objective)

## 5. Key Definitions
- `TimeSlot` = `(day, period)` within the weekly grid.
- `Lesson` = one required period of a class-subject.
- `Assignment` = `(class, subject, teacher, timeSlot)`.

Derived sets:
- `S` = all valid `TimeSlot`s excluding breaks.
- `Eligible(c,s,t)` = true if teacher `t` is qualified and available for class `c` subject `s`.
- `EligibleSlots(c,s,t)` = subset of `S` where teacher `t` is available.

## 6. Hard Constraints (Must Hold)
1. Teacher collision: a teacher cannot be assigned to two classes in the same `TimeSlot`.
2. Class collision: a class cannot have two subjects in the same `TimeSlot`.
3. Teacher availability: only schedule within available `TimeSlot`s.
4. Qualification: only assign qualified teachers.
5. Requirement completion: each class-subject meets exact `required_periods_per_week`.
6. Teacher weekly cap: total assigned periods per week <= `max_periods_per_week`.
7. Teacher daily cap: assigned periods per day <= `max_periods_per_day`.
8. Fixed lessons: locked and cannot move.
9. No back-to-back for classes: same subject cannot be scheduled in consecutive periods for a class.
10. No back-to-back for teachers: a teacher cannot be scheduled in consecutive periods.

Notes:
- No back-to-back applies to adjacent periods in the same day.
- A class-subject can appear twice in a day only if separated by at least one other period.
- Fixed lessons must already satisfy no back-to-back; otherwise infeasible.

## 7. Optimization Objective (Class Balance)
Goal: spread each class-subject evenly across days to avoid clustering.

For each class-subject `(c,s)` and day `d`:
- `count[c,s,d] = number of periods of subject s in class c on day d`
- `ideal = required_periods_per_week / days_per_week`

Minimize:
- Sum of absolute deviations: `sum over c,s,d |count[c,s,d] - ideal|`

Equivalent penalties can be used:
- Squared deviation for stronger penalty on uneven distribution.
- Additional penalty when `count[c,s,d] >= 2` to discourage multiple periods in one day.

Only class balance is optimized; all other rules are hard constraints.

## 8. Solver Model (CP-SAT / ILP)
Binary decision variable:
- `x[c,s,t,d,p] = 1` if teacher `t` teaches class `c` subject `s` at day `d` period `p`

Constraints map directly to linear constraints:
- Class collision: for each `c,d,p`, sum over `s,t` of `x[c,s,t,d,p] <= 1`
- Teacher collision: for each `t,d,p`, sum over `c,s` of `x[c,s,t,d,p] <= 1`
- Requirement completion: for each `(c,s)`, sum over `t,d,p` of `x[c,s,t,d,p] = required_periods_per_week`
- Weekly cap: for each `t`, sum over `c,s,d,p` of `x[c,s,t,d,p] <= max_periods_per_week`
- Daily cap: for each `t,d`, sum over `c,s,p` of `x[c,s,t,d,p] <= max_periods_per_day`
- Availability/qualification: set `x[c,s,t,d,p] = 0` where ineligible
- Fixed lessons: set `x[c,s,t,d,p] = 1` for locked slots
- No back-to-back (class): for each `(c,s,d,p)`, sum over `t` of `x[c,s,t,d,p] + x[c,s,t,d,p+1] <= 1`
- No back-to-back (teacher): for each `(t,d,p)`, sum over `c,s` of `x[c,s,t,d,p] + x[c,s,t,d,p+1] <= 1`

Objective:
- Minimize class balance penalty based on `count[c,s,d]`

> **Implementation note (2026-03-12):**
> The current codebase uses a heuristic backtracking solver with class-balance scoring to
> avoid heavy solver dependencies. CP-SAT/ILP remains the recommended upgrade for large
> schools or tighter constraints.

## 9. Algorithm Flow
1. Build the weekly `TimeSlot` grid and remove breaks.
2. Validate fixed lessons (availability, qualification, no collision, no back-to-back).
3. Pre-check feasibility:
   - For each requirement, ensure enough eligible slots exist.
   - For each teacher, ensure required load does not exceed availability and caps.
4. Build the solver model and add all constraints.
5. Solve for the optimal schedule with class balance objective.
6. If infeasible, generate conflict report.
7. If feasible, output per-class and per-teacher timetables with summary metrics.

## 10. Conflict Report (When Infeasible)
The report must identify:
- Requirements with insufficient feasible slots.
- Teachers exceeding capacity or with insufficient availability.
- Fixed lessons causing collisions or no back-to-back violations.
- Days or periods where constraints are over-constrained.

This report is required so users can adjust inputs.

## 11. Output Format (Logical)
- Timetable per class: grid of days x periods.
- Timetable per teacher: grid of days x periods.
- Summary metrics:
  - total periods per teacher
  - daily load per teacher
  - class balance score
- Any soft constraint violations (should be zero if objective optimized fully).

## 12. Example Input (Conceptual, Minimal)
Time grid:
- 5 days, 7 periods, no breaks

Teacher:
- T1 available all slots
- max per week: 20, max per day: 4
- qualified: Math for classes 9A and 9B

Requirement:
- Class 9A Math: 5 periods/week

Fixed lesson:
- 9A Math, T1, Monday period 1

## 13. Edge Cases and Guidance
- If `required_periods_per_week` > `days_per_week`, class balance can still be achieved by
  spreading across days with non-consecutive placement. No back-to-back still enforced.
- If a teacher has very limited availability, feasibility is likely to fail; the conflict
  report must show the shortfall.
- No back-to-back for teachers significantly reduces capacity; users should be warned if
  feasibility fails due to this rule.

## 14. Extensibility
Future constraints can be added as hard or soft rules without altering the model structure:
- Room capacity or lab requirements
- Teacher preferences
- Subject-specific constraints (double periods, morning only, etc.)

## 15. Acceptance Criteria
- All hard constraints are satisfied.
- Class balance objective is optimized.
- Clear conflict report is produced if infeasible.
