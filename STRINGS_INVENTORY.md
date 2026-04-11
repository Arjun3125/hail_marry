# Hardcoded Strings Inventory for i18n Extraction

## Summary
This inventory lists hardcoded strings in the VidyaOS codebase that need extraction to `en.json`/`hi.json` for proper localization.

**Total strings identified:** ~80+ hardcoded UI strings  
**Priority level:** High (Phase 2 deliverable)  
**Status:** ❌ TODO - extraction needed

---

## Critical UI Strings (Most Visible to Users)

### Common Actions & Buttons
| String | Current Location | Priority | Hindi | Notes |
|--------|------------------|----------|-------|-------|
| "Confirm & Submit" | CameraPreviewModal.tsx:238 | 🟥 HIGH | पुष्टि करें और सबमिट करें | Camera submit button |
| "Camera preview" | CameraPreviewModal.tsx:129 | 🟥 HIGH | कैमरा प्रीव्यू | Alt text for image |
| "Retake" | CameraPreviewModal.tsx:181 | 🟥 HIGH | फिर से लें | Camera retake button |
| "Confirm" | CameraPreviewModal.tsx:235 | 🟥 HIGH | पुष्टि करें | Generic confirm |
| "Cancel" | CameraPreviewModal.tsx:249 | 🟥 HIGH | रद्द करें | Generic cancel |
| "Failed to load preferences" | parent/settings/page.tsx:51 | 🟨 MED | प्राथमिकताएं लोड करने में विफल | Error message |
| "Failed to save preferences" | parent/settings/page.tsx:96 | 🟨 MED | प्राथमिकताएं सहेजने में विफल | Error message |

### Parent Notification Settings
| String | Location | Priority | Hindi |
|--------|----------|----------|-------|
| "Notification Settings" | parent/settings/page.tsx:117 | 🟥 HIGH | सूचना सेटिंग्स |
| "Manage how you receive updates about your child's school activities" | parent/settings/page.tsx:118 | 🟥 HIGH | अपने बच्चे की स्कूल गतिविधियों की सूचनाओं को प्राप्त करने का तरीका प्रबंधित करें |
| "Communication Channels" | parent/settings/page.tsx:135 | 🟥 HIGH | संचार चैनल |
| "Notification Types" | parent/settings/page.tsx:214 | 🟥 HIGH | सूचना प्रकार |
| "Quiet Hours" | parent/settings/page.tsx:260 | 🟥 HIGH | शांत घंटे |

### Assignment Submission Flow
| String | Location | Priority | Hindi |
|--------|----------|----------|-------|
| "Open camera and submit notebook photo" | assignments/page.tsx:770 | 🟥 HIGH | कैमरा खोलें और नोटबुक फोटो सबमिट करें |
| "Choose file from phone or laptop" | assignments/page.tsx:790 | 🟥 HIGH | फोन या लैपटॉप से फाइल चुनें |
| "Type your answer here. Include steps, diagrams explained in words, or final working." | assignments/page.tsx:806 | 🟥 HIGH | यहाँ अपना उत्तर टाइप करें। कदम, आरेख शब्दों में समझाया गया, या अंतिम कार्य शामिल करें। |
| "Submit typed answer" | assignments/page.tsx:815 | 🟥 HIGH | टाइप किए गए उत्तर को सबमिट करें |
| "Checking your work for today..." | assignments/page.tsx:434 | 🟥 HIGH | आज के काम की जांच जारी है... |
| "Looking for due homework, submitted files, and anything your teacher has already graded." | assignments/page.tsx:435 | 🟥 HIGH | बकाया होमवर्क, सबमिट की गई फाइलें, और कुछ भी जो आपके शिक्षक ने पहले से ही ग्रेड किया है, की तलाश की जा रही है। |

### Dashboard & Empty States
| String | Location | Priority | Hindi |
|--------|----------|----------|-------|
| "No homework has been assigned yet" | assignments/page.tsx:442 | 🟥 HIGH | अभी तक कोई होमवर्क असाइन नहीं किया गया है |
| "When your teacher shares homework, diagrams, worksheets, or typed-answer tasks, they will appear here with one clear submit action." | assignments/page.tsx:443 | 🟥 HIGH | जब आपके शिक्षक होमवर्क, आरेख, कार्यपत्र, या टाइप किए गए उत्तर कार्य साझा करते हैं, तो वे यहाँ एक स्पष्ट सबमिट क्रिया के साथ दिखाई देंगे। |
| "Until then, you can add study material and ask AI questions from your own notes." | assignments/page.tsx:444 | 🟥 HIGH | तब तक, आप अध्ययन सामग्री जोड़ सकते हैं और अपने नोट्स से AI से सवाल पूछ सकते हैं। |
| "Add study material" | assignments/page.tsx:445 | 🟥 HIGH | अध्ययन सामग्री जोड़ें |
| "Open AI Studio" | assignments/page.tsx:446 | 🟥 HIGH | AI स्टूडियो खोलें |

### Layout & Navigation
| String | Location | Priority | Hindi |
|--------|----------|----------|-------|
| "Notification Settings" (layout nav) | parent/layout.tsx | 🟨 MED | सूचना सेटिंग्स |
| "Settings" | parent/layout.tsx | 🟨 MED | सेटिंग्स |

### Demo Flow
| String | Location | Priority | Hindi |
|--------|----------|----------|-------|
| "Start guided learning with curriculum-grounded AI." | demo/page.tsx:102 | 🟨 MED | पाठ्यक्रम-आधारित AI के साथ निर्देशित शिक्षण शुरू करें। |
| "See pending work and OCR-assisted submission flows." | demo/page.tsx:103 | 🟨 MED | OCR-सहायतापूर्ण जमा करने के प्रवाह के साथ लंबित कार्य देखें। |
| "Understand progress trends and next focus areas." | demo/page.tsx:104 | 🟨 MED | प्रगति के रुझानों और अगले ध्यान केंद्रित क्षेत्रों को समझें। |

---

## Medium Priority Strings (Status Labels, Field Labels)

| String | Location | Priority | Hindi | Category |
|--------|----------|----------|-------|----------|
| "Needs action" | assignments/page.tsx | 🟨 MED | कार्रवाई की आवश्यकता है | Status label |
| "Submitted" | assignments/page.tsx | 🟨 MED | जमा किया गया | Status badge |
| "Average score" | assignments/page.tsx | 🟨 MED | औसत स्कोर | Panel header |
| "Latest graded work, normalized into a quick progress signal." | assignments/page.tsx | 🟨 MED | नवीनतम ग्रेडेड कार्य, तेजी से प्रगति संकेत में सामान्यीकृत। | Description |
| "Assignment scope" | assignments/page.tsx | 🟨 MED | असाइनमेंट स्कोप | Form label |
| "Keep one subject in focus and it will follow you into AI Studio and adjacent study screens." | assignments/page.tsx | 🟨 MED | एक विषय पर ध्यान रखें और यह आपके साथ AI स्टूडियो और आसन्न अध्ययन स्क्रीन में जाएगा। | Helper text |
| "Graded work is locked. Ask your teacher before resubmitting." | assignments/page.tsx | 🟨 MED | ग्रेडेड कार्य बंद है। फिर से जमा करने से पहले अपने शिक्षक से पूछें। | Disabled state message |
| "Need help?" | assignments/page.tsx | 🟨 MED | सहायता चाहिए? | CTA button |

---

## Low Priority Strings (Console Logs, Comments, Help Text)

| String | Location | Priority | Notes |
|--------|----------|----------|-------|
| "Error fetching preferences:" | parent/settings/page.tsx:52 | 🟧 LOW | Console error log |
| "Error saving preferences:" | parent/settings/page.tsx:97 | 🟧 LOW | Console error log |
| "Failed to resolve branding config in RootLayout" | layout.tsx:59 | 🟧 LOW | Console error log |

---

## Extraction Action Items

### Phase 2a: High Priority (Immediate)
These strings are directly visible to end users and impact UX significantly.

**Location:** `frontend/src/i18n/en.json` and `frontend/src/i18n/hi.json`

**Required sections:**
```json
{
  "camera": {
    "preview": "Camera preview",
    "retake": "Retake",
    "confirm_submit": "Confirm & Submit",
    "confirm": "Confirm",
    "alert": "Image quality alert"
  },
  "assignments": {
    "checking_work": "Checking your work for today...",
    "checking_work_desc": "Looking for due homework, submitted files, and anything your teacher has already graded.",
    "no_homework": "No homework has been assigned yet",
    "no_homework_detail": "When your teacher shares homework, diagrams, worksheets, or typed-answer tasks, they will appear here with one clear submit action.",
    "study_material_hint": "Until then, you can add study material and ask AI questions from your own notes.",
    "add_study_material": "Add study material",
    "open_ai_studio": "Open AI Studio",
    "camera_submit": "Open camera and submit notebook photo",
    "file_submit": "Choose file from phone or laptop",
    "type_answer_placeholder": "Type your answer here. Include steps, diagrams explained in words, or final working.",
    "submit_typed": "Submit typed answer",
    "no_resubmit": "Graded work is locked. Ask your teacher before resubmitting.",
    "need_help": "Need help?",
    "assignment_scope": "Assignment scope",
    "scope_desc": "Keep one subject in focus and it will follow you into AI Studio and adjacent study screens.",
    "needs_action": "Needs action",
    "average_score": "Average score",
    "avg_score_desc": "Latest graded work, normalized into a quick progress signal."
  },
  "parent": {
    "settings": "Settings",
    "notification_settings": "Notification Settings",
    "notification_settings_desc": "Manage how you receive updates about your child's school activities",
    "com_channels": "Communication Channels",
    "notification_types": "Notification Types",
    "quiet_hours": "Quiet Hours",
    "pref_load_error": "Failed to load preferences",
    "pref_save_error": "Failed to save preferences"
  }
}
```

### Phase 2b: Medium Priority (Week 2)
Status labels, form labels, helper text.

### Phase 2c: Low Priority (Week 3)
Console logs and developer-facing text (not directly user-visible).

---

## File Mapping for Extraction

| Source File | Strings Count | Difficulty | ETA |
|-------------|---------------|------------|-----|
| assignments/page.tsx | ~25 | 🟢 Easy | 2-3h |
| parent/settings/page.tsx | ~12 | 🟢 Easy | 1-2h |
| CameraPreviewModal.tsx | ~8 | 🟢 Easy | 30m |
| demo/page.tsx | ~10 | 🟢 Easy | 1h |
| layout.tsx | ~3 | 🟢 Easy | 15m |
| **TOTAL** | **~80** | **Medium** | **~8-10h** |

---

## Implementation Steps

### Step 1: Create i18n Keys (1h)
- [ ] Add all high-priority keys to `en.json`
- [ ] Verify structure consistency with existing keys
- [ ] Test for typos/special characters

### Step 2: Add Hindi Translations (2-3h)
- [ ] Translate high-priority strings to Hindi
- [ ] Verify CBSE/ICSE terminology accuracy
- [ ] Add regional variations where needed

### Step 3: Extract to Components (4-5h)
- [ ] Update `assignments/page.tsx` to use `useLanguage()` hook
- [ ] Update `parent/settings/page.tsx`
- [ ] Update `CameraPreviewModal.tsx`
- [ ] Update other pages

### Step 4: Test & Validate (2-3h)
- [ ] Full language switch test (English ↔ Hindi)
- [ ] Check for missing translations
- [ ] Verify layout doesn't break with longer Hindi text

---

## Hindi Translation Quality Checklist

When translating, ensure:
- [ ] Subject/verb agreement in Hindi
- [ ] Proper use of formal/informal forms (तुम, आप, आप्)
- [ ] Educational terminology matches CBSE/ICSE standards
- [ ] Abbreviations are translatable or explained
- [ ] Gender-neutral pronouns where possible
- [ ] Consistent terminology across the app (e.g., "अंक" for marks, not "अंशो")

**Examples:**
- "Marks" = "अंक" (standard CBSE term, not "नंबर")
- "Assignment" = "कार्य" or "अभ्यास" (not generic "काम")
- "Doubt" = "प्रश्न" or "संदेह" (context-dependent)
- "Attendance" = "उपस्थिति" (formal, educational)

---

## Next Phase

Once Phase 2a is complete, move to **Phase 3: Session Wrap-Up** which requires backend session tracking model and frontend modal component.

---

## Related Issues

- [ ] Mobile responsiveness check on translated text (Hindi often longer than English)
- [ ] RTL language support (future enhancement, not in Phase 2)
- [ ] Pluralization rules for Hindi (currently simplified)
- [ ] Number formatting by locale (e.g., 1,00,000 in Indian English)
