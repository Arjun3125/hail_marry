import { Page } from "@playwright/test";

export interface AuthUser {
    role: "student" | "teacher" | "parent" | "admin";
    userId: string;
    name: string;
}

// Mock authentication data for different roles
const mockUsers: Record<string, AuthUser> = {
    student: {
        role: "student",
        userId: "student-001",
        name: "Test Student",
    },
    teacher: {
        role: "teacher",
        userId: "teacher-001",
        name: "Test Teacher",
    },
    parent: {
        role: "parent",
        userId: "parent-001",
        name: "Test Parent",
    },
    admin: {
        role: "admin",
        userId: "admin-001",
        name: "Test Admin",
    },
};

export async function authenticateAs(page: Page, role: "student" | "teacher" | "parent" | "admin") {
    const user = mockUsers[role];

    if (!user) {
        throw new Error(`Unknown role: ${role}`);
    }

    // Set authentication token in localStorage
    await page.addInitScript(({ token, user: userData }) => {
        window.localStorage.setItem("vidyaos_access_token", token);
        window.localStorage.setItem("vidyaos_user", JSON.stringify(userData));
        
        // Comprehensive tour and onboarding bypasses for all roles
        window.localStorage.setItem("student-tour", "completed");
        window.localStorage.setItem("teacher-tour", "completed");
        window.localStorage.setItem("admin-tour", "completed");
        window.localStorage.setItem("parent-tour", "completed");

        const onboardingCompleted = JSON.stringify({
            "profile-ready": true,
            "upload-material": true,
            "ask-ai": true,
            "read-timetable": true,
            "setup-identity": true,
            "setup-structure": true,
            "onboard-teachers": true
        });

        window.localStorage.setItem("student-onboarding", onboardingCompleted);
        window.localStorage.setItem("teacher-onboarding", onboardingCompleted);
        window.localStorage.setItem("admin-onboarding", onboardingCompleted);
        window.localStorage.setItem("parent-onboarding", onboardingCompleted);

        // Skip AI Studio intent selector so workspace renders directly (sidebar visible)
        if (userData.role === "student") {
            window.localStorage.setItem("student-ai-studio-intent", "understand_topic");
        }
        
    }, {
        token: `mock-token-${role}`,
        user,
    });

    // Stub the auth API endpoints
    await page.route("**/api/auth/me", (route) => {
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify(user),
        });
    });

    // Stub branding API
    await page.route("**/api/branding/config", (route) => {
        route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
                name: "VidyaOS",
                logo_url: null,
                primary_color: "#2563eb",
                secondary_color: "#0f172a",
                accent_color: "#f59e0b",
                font_family: "Inter",
                theme_style: "modern",
            }),
        });
    });

    // Stub personalization events
    await page.route("**/api/personalization/events", (route) => {
        route.fulfill({
            status: 202,
            contentType: "application/json",
            body: JSON.stringify({ ok: true }),
        });
    });
}

export async function expectNoHorizontalScroll(page: Page) {
    const overflow = await page.evaluate(() => {
        const width = window.innerWidth;
        const scrollWidth = document.documentElement.scrollWidth;
        return {
            hasOverflow: scrollWidth > width,
            diff: scrollWidth - width,
        };
    });

    if (overflow.hasOverflow) {
        throw new Error(
            `Page has horizontal scrollbar (overflow: ${overflow.diff}px)`
        );
    }
}

export async function expectTouchTargetSizes(page: Page) {
    const smallTargets = await page.evaluate(() => {
        const buttons = document.querySelectorAll("button, a, [role='button']");
        const smallButtons: {
            text: string;
            width: number;
            height: number;
        }[] = [];

        buttons.forEach((btn) => {
            const rect = btn.getBoundingClientRect();
            // Minimum recommended touch target size is 44x44px
            if (rect.width < 44 || rect.height < 44) {
                smallButtons.push({
                    text: btn.textContent?.substring(0, 20) || "unknown",
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                });
            }
        });

        return smallButtons;
    });

    if (smallTargets.length > 0) {
        console.warn(
            `Found ${smallTargets.length} touch targets smaller than 44x44px:`,
            smallTargets
        );
    }
}

export async function expectReadableText(page: Page, minFontSize = 12) {
    const smallText = await page.evaluate((minSize) => {
        const allElements = document.querySelectorAll("*");
        const tinyText: string[] = [];

        allElements.forEach((el) => {
            if (el.children.length === 0) {
                // Leaf node
                const fontSize = window.getComputedStyle(el).fontSize;
                const fontSizeValue = parseFloat(fontSize);

                if (fontSizeValue < minSize && el.textContent?.trim().length) {
                    tinyText.push(el.textContent.substring(0, 30));
                }
            }
        });

        return tinyText.slice(0, 5); // Return first 5 examples
    }, minFontSize);

    if (smallText.length > 0) {
        console.warn(`Found text smaller than ${minFontSize}px:`, smallText);
    }
}

export async function expectKeyboardNavigation(page: Page) {
    // Verify that interactive elements are reachable via Tab key
    const focusableElements = await page.evaluate(() => {
        const elements = document.querySelectorAll(
            "button, a, input, select, textarea, [tabindex]"
        );
        return elements.length;
    });

    if (focusableElements === 0) {
        console.warn("No focusable elements found on page");
    }

    // Try tabbing through a few elements
    await page.keyboard.press("Tab");
    const focusedElement1 = await page.evaluate(() =>
        document.activeElement?.tagName
    );

    await page.keyboard.press("Tab");
    const focusedElement2 = await page.evaluate(() =>
        document.activeElement?.tagName
    );

    if (!focusedElement1 && !focusedElement2) {
        console.warn("Tab navigation not working properly");
    }
}

export async function testResponsiveSidebar(page: Page) {
    // Check if sidebar is visible or has a toggle on mobile
    const hasSidebar = await page.locator('[data-testid="sidebar"]').count();
    const hasSidebarToggle = await page.locator(
        'button[aria-label*="menu" i], button[aria-label*="sidebar" i]'
    ).count();

    return {
        sidebarVisible: hasSidebar > 0,
        toggleAvailable: hasSidebarToggle > 0,
    };
}
