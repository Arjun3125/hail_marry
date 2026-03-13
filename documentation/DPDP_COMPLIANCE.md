# DPDP Act 2023 Compliance Review — VidyaOS

## 1. Overview

This document outlines VidyaOS's compliance posture with respect to the **Digital Personal Data Protection (DPDP) Act, 2023** of India. Given that VidyaOS handles student data (including minors), parental data, teacher records, and academic performance metrics, this review is critical before any production pilot.

> **Status**: Draft for legal review  
> **Last Updated**: March 2026  
> **Legal Sign-Off**: ⬜ Pending

---

## 2. Key DPDP Provisions & VidyaOS Compliance

### 2.1 Consent (Section 6)

| Requirement | VidyaOS Status | Action Needed |
|---|---|---|
| Explicit consent before processing personal data | ✅ Registration requires consent checkbox | Add detailed consent text per DPDP template |
| Consent must be free, specific, informed | ⚠️ Generic consent currently | Draft specific consent forms per data category |
| Withdrawal of consent mechanism | ✅ Account deletion request via `/api/compliance/deletion-request` | Add UI toggle for consent withdrawal |

### 2.2 Children's Data (Section 9)

| Requirement | VidyaOS Status | Action Needed |
|---|---|---|
| Verifiable parental consent for <18 | ⚠️ Parent-link model exists but consent flow is manual | Implement digital parental consent via OTP/email |
| No behavioral tracking of children | ✅ No advertising/behavioral targeting | Document in privacy policy |
| No profiling of children | ⚠️ AI performance analytics could be viewed as profiling | Legal opinion needed on academic analytics vs. profiling |

### 2.3 Data Principal Rights (Section 11-14)

| Right | VidyaOS Status | Endpoint |
|---|---|---|
| Right to access personal data | ✅ | `GET /api/compliance/export` |
| Right to correction | ⚠️ Profile edit exists, no formal "correction request" | Add formal correction request API |
| Right to erasure | ✅ | `POST /api/compliance/deletion-request` |
| Right to nominate | 🔴 Not implemented | Add nominee management for parent accounts |
| Grievance redressal | ⚠️ Complaint system exists but not DPDP-specific | Add Data Protection Officer (DPO) contact endpoint |

### 2.4 Data Fiduciary Obligations (Section 8)

| Obligation | VidyaOS Status |
|---|---|
| Purpose limitation | ✅ Data used only for educational purposes |
| Storage limitation | ⚠️ No automatic data expiry policy |
| Data accuracy | ✅ Teachers/admins can correct records |
| Security safeguards | ✅ JWT auth, RBAC, audit logs, encrypted storage |
| Breach notification | ⚠️ Incident system exists but no 72-hour notification workflow |

### 2.5 Cross-Border Data Transfers (Section 16)

| Requirement | VidyaOS Status |
|---|---|
| Government-notified approved countries only | ✅ Self-hosted — data stays in-country |
| Cloud provider compliance | ⚠️ If deployed on AWS/GCP, confirm India region |

---

## 3. Data Categories Processed

| Category | Examples | Legal Basis |
|---|---|---|
| Student identity | Name, email, class, roll number | Legitimate educational purpose + consent |
| Academic records | Marks, attendance, performance | Legitimate educational purpose |
| Parental data | Parent name, email, phone | Consent + parental link for minors |
| Teacher data | Name, email, subjects, attendance | Employment relationship |
| AI interaction logs | Queries, responses, usage metrics | Consent + service improvement |
| Financial data | Fee invoices, payments | Contractual necessity |

---

## 4. Security Measures Already Implemented

- ✅ **Authentication**: JWT with refresh token blacklisting (JTI-based)
- ✅ **Authorization**: Role-based access control (RBAC) — admin/teacher/student/parent
- ✅ **Audit logging**: All admin actions logged with timestamps and actor
- ✅ **Data export**: GDPR/DPDP-style data export endpoint
- ✅ **Deletion requests**: Formal deletion request pipeline with tracking
- ✅ **Tenant isolation**: Multi-tenant architecture with data separation
- ✅ **Incident management**: Incident route + event tracking system

---

## 5. Required Actions Before Pilot

### High Priority
1. **Obtain legal sign-off** on this compliance review
2. **Draft privacy policy** specific to DPDP 2023 requirements
3. **Implement verifiable parental consent** for student (<18) accounts
4. **Add Data Protection Officer (DPO)** contact information endpoint
5. **Implement 72-hour breach notification** workflow in incident system

### Medium Priority
6. **Add data retention policy** with automatic purging of old records
7. **Create formal correction request** API endpoint
8. **Add nominee management** for parent accounts
9. **Document purpose limitation** in terms of service

### Low Priority
10. **Conduct penetration testing** and document results
11. **Create DPDP compliance training** materials for school admins
12. **Set up regular compliance audits** (quarterly)

---

## 6. Sign-Off

| Role | Name | Date | Signature |
|---|---|---|---|
| CTO / Technical Lead | | | ⬜ |
| Legal Counsel | | | ⬜ |
| Data Protection Officer | | | ⬜ |
| School Principal (Pilot) | | | ⬜ |
