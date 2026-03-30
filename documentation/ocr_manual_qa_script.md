# OCR Manual QA Script

**Date:** 2026-03-29  
**Goal:** Validate OCR capture flows from camera and image uploads.

## 1. Camera Capture

1. Open student upload.
2. Use the camera capture option on a mobile device.
3. Capture a page of printed English text.
4. Verify the upload completes and shows OCR completed.
5. Repeat for Hindi and Marathi samples.

## 2. Photo Upload

1. Open teacher upload.
2. Upload a photo of a mixed-language (English + Hindi) note.
3. Confirm OCR review required appears when expected.
4. Upload a low-light photo and confirm a warning appears.

## 3. Structured Imports

1. Open admin setup wizard and select the Teachers step.
2. Upload a roster photo and verify the preview table appears.
3. Edit a name or email and confirm import.
4. Repeat for the Students step with a class roster photo.

## 4. Failure Handling

1. Upload a blurry image and confirm the UI surfaces a useful error.
2. Upload a non-text photo and confirm OCR review or failure messaging.

## 5. Notes

Capture the screenshots and notes from the above steps in the benchmark report.
