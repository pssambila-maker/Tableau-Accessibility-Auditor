# Steps to Compliance: Tableau Accessibility Checklist

This guide outlines the mandatory steps for ensuring your Tableau workbooks meet the accessibility standards defined by Upstate and WCAG 2.1.

## Phase 1: Planning & Setup
Before you build a single chart, set these foundations:

1.  **Set Fixed Dashboard Size (WCAG 1.4.4):**
    - Avoid "Automatic" or "Range" sizing.
    - **Step:** In the Dashboard pane, set Size to **Fixed Size**. This prevents elements from overlapping when a user zooms in to 200%.
2.  **Enable Sheet Tabs (WCAG 2.4.1):**
    - **Step:** When publishing, ensure **"Show sheets as tabs"** is checked. This allows keyboard users to bypass blocks of content and navigate between views easily.
3.  **Use Accessible Palettes (WCAG 1.4.1):**
    - **Step:** Prioritize "Color Blind" palettes. Never use color as the *only* way to convey meaning.
    - **Pro Tip:** If a specific color indicates "Danger", also use a shape (like an 'X') or a heavy border to distinguish it.

## Phase 2: Building Visualizations
Follow these rules while creating worksheets:

4.  **Add Alt Text & Captions (WCAG 1.1.1):**
    - **Step:** Every worksheet needs a description. Go to **Worksheet > Accessibility > Edit Alt Text** or use the **Caption** feature to describe the data's "so-what".
5.  **Clean up Labels & Headers:**
    - **Step:** Rename fields to plain English (e.g., change `SUM(Sales_Amt)` to `Total Sales`).
    - **Step:** Ensure filter labels are positioned **Above** or to the **Left** of the entry box.
6.  **Avoid Prohibited Interactions (WCAG 1.4.13):**
    - **Step:** Go to **Dashboard > Actions**. Ensure no actions are triggered by **"Hover"**. Use **"Select"** or **"Menu"** triggers instead.
7.  **Enable "Apply" Buttons (WCAG 3.2.2):**
    - **Step:** For multi-select filters, click the filter dropdown > **Customize** > **Show "Apply" Button**. This prevents the screen from refreshing constantly as a user makes selections.

## Phase 3: Layout & Sequencing
How the pieces fit together on the dashboard:

8.  **Use Tiled Containers (WCAG 1.3.2):**
    - **Step:** Do not use "Floating" objects. Use **Tiled** containers to ensure a logical flow.
9.  **Validate Focus Order (WCAG 2.4.3):**
    - **Step:** Elements should be added to the dashboard in the order you want a user to "Tab" through them (typically top-left to bottom-right).
10. **Check Contrast Ratios (WCAG 1.4.3):**
    - **Step:** Use a tool (like the **TabAccess Scanner**) to verify that your text color vs. background color ratio is at least **4.5:1**.

## Phase 4: Verification
11. **Run the TabAccess Audit:**
    - **Step:** Before publishing, upload your `.twbx` to the **TabAccess Auditor** to catch any missed structural issues.
12. **The "Keyboard Only" Test:**
    - **Step:** Unplug your mouse. Try to navigate your entire dashboard using only the **Tab**, **Enter**, and **Arrow** keys. If you get stuck, it's not compliant.
