const { chromium } = require('playwright');
const path = require('path');

const ARTIFACTS = 'C:\\Users\\naren\\.gemini\\antigravity\\brain\\a7854384-4629-493e-b912-1389b94dd8bf';
const BASE = 'http://localhost:7125';
const API = 'http://localhost:8080';

async function loginAs(page, role) {
  // Hit demo login API directly
  const res = await page.request.post(`${API}/api/auth/demo-login`, {
    data: { role },
    headers: { 'Content-Type': 'application/json' },
  });
  const body = await res.json();
  if (body.access_token) {
    await page.evaluate((token) => {
      localStorage.setItem('access_token', token);
    }, body.access_token);
  }
  // Also set cookie
  await page.context().addCookies([{
    name: 'demo_role', value: role, domain: 'localhost', path: '/'
  }]);
}

async function screenshotPage(page, urlPath, filename, waitMs = 3000) {
  const url = `${BASE}${urlPath}`;
  console.log(`  → ${urlPath}`);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForTimeout(waitMs);
    await page.screenshot({ path: path.join(ARTIFACTS, filename), fullPage: true });
    return 'OK';
  } catch (e) {
    console.log(`    WARN: ${e.message.slice(0, 80)}`);
    try { await page.screenshot({ path: path.join(ARTIFACTS, filename), fullPage: true }); } catch {}
    return 'WARN';
  }
}

(async () => {
  console.log('Starting comprehensive VidyaOS demo verification...\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const results = [];

  // ── DEMO GATEWAY ──
  console.log('[Demo Gateway]');
  results.push({ page: '/demo', status: await screenshotPage(page, '/demo', 'v_demo_gateway.png') });

  // ── STUDENT ROLE ──
  console.log('\n[Student Role]');
  await loginAs(page, 'student');
  const studentPages = [
    ['/student/overview', 'v_student_overview.png'],
    ['/student/ai', 'v_student_ai.png'],
    ['/student/ai-studio', 'v_student_ai_studio.png'],
    ['/student/tools', 'v_student_tools.png'],
    ['/student/assignments', 'v_student_assignments.png'],
    ['/student/results', 'v_student_results.png'],
    ['/student/attendance', 'v_student_attendance.png'],
    ['/student/timetable', 'v_student_timetable.png'],
    ['/student/leaderboard', 'v_student_leaderboard.png'],
    ['/student/mind-map', 'v_student_mindmap.png'],
    ['/student/upload', 'v_student_upload.png'],
    ['/student/profile', 'v_student_profile.png'],
  ];
  for (const [p, f] of studentPages) {
    results.push({ page: p, status: await screenshotPage(page, p, f) });
  }

  // ── TEACHER ROLE ──
  console.log('\n[Teacher Role]');
  await loginAs(page, 'teacher');
  const teacherPages = [
    ['/teacher/dashboard', 'v_teacher_dashboard.png'],
    ['/teacher/classes', 'v_teacher_classes.png'],
    ['/teacher/attendance', 'v_teacher_attendance.png'],
    ['/teacher/marks', 'v_teacher_marks.png'],
    ['/teacher/assignments', 'v_teacher_assignments.png'],
    ['/teacher/upload', 'v_teacher_upload.png'],
    ['/teacher/insights', 'v_teacher_insights.png'],
  ];
  for (const [p, f] of teacherPages) {
    results.push({ page: p, status: await screenshotPage(page, p, f) });
  }

  // ── ADMIN ROLE ──
  console.log('\n[Admin Role]');
  await loginAs(page, 'admin');
  const adminPages = [
    ['/admin/dashboard', 'v_admin_dashboard.png', 5000],
    ['/admin/users', 'v_admin_users.png'],
    ['/admin/classes', 'v_admin_classes.png'],
    ['/admin/timetable', 'v_admin_timetable.png'],
    ['/admin/ai-usage', 'v_admin_ai_usage.png'],
    ['/admin/settings', 'v_admin_settings.png'],
    ['/admin/reports', 'v_admin_reports.png'],
    ['/admin/billing', 'v_admin_billing.png'],
    ['/admin/feature-flags', 'v_admin_feature_flags.png'],
  ];
  for (const [p, f, w] of adminPages) {
    results.push({ page: p, status: await screenshotPage(page, p, f, w || 3000) });
  }

  // ── PARENT ROLE ──
  console.log('\n[Parent Role]');
  await loginAs(page, 'parent');
  const parentPages = [
    ['/parent/dashboard', 'v_parent_dashboard.png'],
    ['/parent/attendance', 'v_parent_attendance.png'],
    ['/parent/results', 'v_parent_results.png'],
  ];
  for (const [p, f] of parentPages) {
    results.push({ page: p, status: await screenshotPage(page, p, f) });
  }

  // ── SUMMARY ──
  console.log('\n══════════════════════════════════════');
  console.log('VERIFICATION SUMMARY');
  console.log('══════════════════════════════════════');
  const ok = results.filter(r => r.status === 'OK').length;
  const warn = results.filter(r => r.status === 'WARN').length;
  console.log(`Total: ${results.length} | OK: ${ok} | WARN: ${warn}`);
  for (const r of results) {
    console.log(`  [${r.status}] ${r.page}`);
  }

  await browser.close();
  console.log('\nDone. Screenshots saved to artifacts.');
})();
