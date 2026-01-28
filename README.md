# TabAccess: Tableau Accessibility Auditor

TabAccess is a Python-based tool designed to audit Tableau dashboards for accessibility compliance against WCAG 2.1 standards. It provides automated structural analysis of workbook files and visual contrast checks using computer vision.

## 🚀 Features

### 🏗️ Structural Analysis (Module A)
- **Focus Order Validation (WCAG 2.4.3):** Ensures dashboard elements follow a logical, sequential sequence.
- **Alt Text & Caption Audit (WCAG 1.1.1):** Verifies the presence of descriptive text for all visualizations.
- **Dashboard Sizing (WCAG 1.4.4):** Flags "Automatic" sizing and recommends "Fixed Size" to maintain layout integrity.
- **Container Hygiene (WCAG 2.4.3):** Detects floating containers and encourages the use of "Tiled" layouts.
- **Navigation Check (WCAG 2.4.1):** Ensures "Show Sheets as Tabs" is enabled for keyboard accessibility.

### 🖱️ Interactivity Audit
- **Action Triggers (WCAG 1.4.13):** Prohibits "Hover" triggers in dashboard actions, preferring "Select" or "Menu".
- **Filter Controls (WCAG 3.2.2):** Recommends the use of "Apply" buttons for multi-select filters to reduce disruptive page refreshes.

### 🎨 Visual Analysis (Module B)
- **Contrast Scanner:** Uses OpenCV K-Means clustering to extract dominant colors from dashboard screenshots.
- **WCAG Math:** Calculates relative luminance to ensure a contrast ratio of at least 4.5:1.

## 📋 Comprehensive Checklist
The app includes a built-in **Steps to Compliance** guide that provides a step-by-step roadmap for developers to remediate common accessibility hurdles in Tableau.

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pssambila-maker/Tableau-Accessibility-Auditor.git
   cd Tableau-Accessibility-Auditor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 🖥️ Usage

- **Local Audit:** Upload a `.twb` or `.twbx` file to scan the workbook structure.
- **Visual Audit:** Provide your Tableau Server URL and credentials (Personal Access Token) along with a View ID to perform a contrast scan on a live dashboard screenshot.

## 📝 Technologies Used
- **Streamlit:** Modern web interface.
- **lxml:** High-performance XML parsing for Tableau Workbooks.
- **OpenCV & scikit-learn:** Computer vision for color analysis.
- **Tableau Server Client (TSC):** Integration with Tableau Server APIs.

---
Built with ❤️ for accessible data storytelling.
