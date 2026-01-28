import streamlit as st
import os
from core.parser import TableauParser
from core.scanner import DashboardScanner
import tempfile

st.set_page_config(page_title="TabAccess Auditor", page_icon="♿", layout="wide")

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .status-pass { color: #28a745; font-weight: bold; }
    .status-fail { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("♿ TabAccess: Tableau Accessibility Auditor")
st.markdown("Ensure your dashboards are inclusive and compliant with WCAG standards.")

sidebar = st.sidebar
sidebar.header("Navigation")
page = sidebar.radio("Go to", ["Auditor", "Compliance Checklist"])

if page == "Compliance Checklist":
    st.header("📋 Steps to Compliance")
    with open("checklist.md", "r") as f:
        st.markdown(f.read())
    st.stop()

sidebar.divider()
sidebar.header("Auditor Configuration")
audit_type = sidebar.radio("Audit Source", ["Local File (.twb/.twbx)", "Tableau Server (URL)"])

if audit_type == "Local File (.twb/.twbx)":
    uploaded_file = st.file_uploader("Upload Workbook", type=["twb", "twbx"])
    
    if uploaded_file and st.button("Run Audit"):
        with st.spinner("Analyzing workbook structure..."):
            # Save to temp
            temp_path = os.path.join("temp", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            parser = TableauParser(temp_path)
            tree = parser.parse()
            
            if tree is not None:
                # Run all checks
                focus_results = parser.check_focus_order(tree)
                alt_results = parser.check_alt_text(tree)
                sizing_results = parser.check_dashboard_sizing(tree)
                container_results = parser.check_container_types(tree)
                tab_results = parser.check_show_tabs(tree)
                action_results = parser.check_action_triggers(tree)
                filter_results = parser.check_filter_controls(tree)

                st.subheader("🔍 Complete Audit Results")
                
                tab1, tab2, tab3 = st.tabs(["🏗️ Structure & Dashboard", "🖱️ Interactivity", "🎨 Visuals & Content"])

                with tab1:
                    st.markdown("### Dashboard & Container Logic")
                    # Sizing
                    for res in sizing_results:
                        icon = "✅" if res['status'] == "Pass" else "❌"
                        st.markdown(f"{icon} **{res['dashboard']}**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])
                    
                    # Containers
                    for res in container_results:
                        icon = "✅" if res['status'] == "Pass" else "⚠️"
                        st.markdown(f"{icon} **{res['dashboard']}**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])
                    
                    # Tabs
                    for res in tab_results:
                        icon = "✅" if res['status'] == "Pass" else "❌"
                        st.markdown(f"{icon} **Workbook**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])

                    # Focus Order
                    st.markdown("---")
                    st.markdown("### Navigation Sequence")
                    for res in focus_results:
                        icon = "✅" if res['status'] == "Pass" else "❌"
                        st.markdown(f"{icon} **{res['dashboard']}**: {res['metric']} ({res['wcag_id'] if 'wcag_id' in res else '2.4.3'})")
                        st.caption(res['details'])

                with tab2:
                    st.markdown("### Actions & Filters")
                    # Actions
                    for res in action_results:
                        icon = "✅" if res['status'] == "Pass" else "❌"
                        st.markdown(f"{icon} **{res.get('action', 'Action')}**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])
                    
                    # Filters
                    st.markdown("---")
                    st.markdown("### Filter Controls")
                    for res in filter_results:
                        icon = "✅" if res['status'] == "Pass" else "⚠️"
                        st.markdown(f"{icon} **{res['filter']}**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])

                with tab3:
                    st.markdown("### Visualizations & Descriptions")
                    for res in alt_results:
                        icon = "✅" if res['status'] == "Pass" else "❌"
                        st.markdown(f"{icon} **{res['worksheet']}**: {res['metric']} ({res['wcag_id']})")
                        st.caption(res['details'])
                    
                    st.info("💡 **Manual Review Tip:** Check if visualizations use shapes/patterns in addition to color (WCAG 1.4.1).")

                # Overall Score Heuristic
                all_results = focus_results + alt_results + sizing_results + container_results + tab_results + action_results + filter_results
                passes = sum(1 for r in all_results if r['status'] == "Pass")
                total = len(all_results)
                score = (passes / total * 100) if total > 0 else 0
                
                st.sidebar.divider()
                st.sidebar.metric("Accessibility Score", f"{int(score)}/100")
                if score < 100:
                    st.sidebar.warning(f"Auditor found {total-passes} potential issues.")
                else:
                    st.sidebar.success("Auditor found no major issues!")
            else:
                st.error("Failed to parse the workbook XML.")

else:
    st.info("Scanner mode requires Tableau Server connectivity.")
    server_url = st.text_input("Server URL", "https://tableau.yourcompany.com")
    token_name = st.text_input("PAT Name")
    token_value = st.text_input("PAT Value", type="password")
    view_id = st.text_input("View ID (LUID)")
    
    if st.button("Run Visual Audit"):
        scanner = DashboardScanner(server_url, token_name, token_value)
        with st.spinner("Fetching screenshot and analyzing colors..."):
            success, result = scanner.fetch_screenshot(view_id)
            if success:
                st.image(result, caption="Dashboard Screenshot", use_column_width=True)
                colors = scanner.extract_dominant_colors(result)
                audit = scanner.audit_contrast(colors)
                
                st.subheader("🎨 Visual Analysis")
                st.metric("Contrast Ratio", f"{audit['ratio']}:1", delta=None)
                
                if audit['status'] == "Pass":
                    st.success(f"✅ {audit['details']}")
                else:
                    st.error(f"❌ {audit['details']}")
                    
                st.write("Dominant Palette:")
                c_cols = st.columns(len(colors))
                for i, col in enumerate(colors):
                    c_cols[i].markdown(f'<div style="background-color:rgb{col}; height:50px; border-radius:5px;"></div>', unsafe_allow_html=True)
                    c_cols[i].caption(f"RGB{col}")
            else:
                st.error(f"Error: {result}")

st.sidebar.divider()
st.sidebar.caption("TabAccess Auditor v1.0")
