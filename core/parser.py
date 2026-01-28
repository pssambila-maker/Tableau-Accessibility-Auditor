import zipfile
import os
import shutil
from lxml import etree

class TableauParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = "temp"
        self.twb_content = None
        self.ns = None

    def _extract_twb(self):
        """Extracts .twb from .twbx if necessary."""
        if self.file_path.endswith('.twbx'):
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                # Find the .twb file inside the .twbx
                twb_files = [f for f in zip_ref.namelist() if f.endswith('.twb')]
                if not twb_files:
                    raise FileNotFoundError("No .twb file found in .twbx")
                
                # Extract to temp directory
                extract_path = zip_ref.extract(twb_files[0], self.temp_dir)
                with open(extract_path, 'rb') as f:
                    self.twb_content = f.read()
                
                # Cleanup: we could remove the file, but we'll leave it in temp for now or handle later
        else:
            with open(self.file_path, 'rb') as f:
                self.twb_content = f.read()

    def parse(self):
        """Parses the XML content."""
        self._extract_twb()
        if not self.twb_content:
            return None
        
        try:
            tree = etree.fromstring(self.twb_content)
            return tree
        except etree.XMLSyntaxError as e:
            print(f"XML Syntax Error: {e}")
            return None

    def check_focus_order(self, tree):
        """
        Checks the focus order in the <zones> section.
        Rule: Sequential IDs (1, 2, 3) are good. Random IDs are bad.
        """
        results = []
        # Find all dashboards
        dashboards = tree.xpath("//dashboard")
        for db in dashboards:
            db_name = db.get("name")
            # Find zones in this dashboard
            zones = db.xpath(".//zone")
            ids = []
            for zone in zones:
                zone_id = zone.get("id")
                if zone_id and zone_id.isdigit():
                    ids.append(int(zone_id))
            
            if not ids:
                continue
                
            sorted_ids = sorted(ids)
            is_sequential = all(ids[i] <= ids[i+1] for i in range(len(ids)-1))
            
            results.append({
                "dashboard": db_name,
                "status": "Pass" if is_sequential else "Fail",
                "details": f"IDs found: {ids[:10]}..." if len(ids) > 10 else f"IDs found: {ids}",
                "metric": "Focus Order"
            })
        return results

    def check_alt_text(self, tree):
        """
        Checks for Alt Text/Captions in worksheets.
        """
        results = []
        worksheets = tree.xpath("//worksheet")
        for ws in worksheets:
            ws_name = ws.get("name")
            # In Tableau XML, accessibility descriptions are often in <caption/> or specific <accessibility/> tags (newer versions)
            # We'll check for captions and potentially other tags
            caption_tag = ws.find(".//caption")
            formatted_text = ws.xpath(".//formatted-text/run")
            
            has_caption = False
            if caption_tag is not None:
                # Check if caption has text
                text_runs = caption_tag.xpath(".//run")
                if text_runs:
                    has_caption = any(run.text for run in text_runs if run.text)

            # Some versions use a specific accessibility tag if set manually
            # Example: <accessibility description='...' />
            acc_tag = ws.find(".//accessibility")
            has_acc = acc_tag is not None and acc_tag.get("description")

            status = "Pass" if (has_caption or has_acc) else "Fail"
            results.append({
                "worksheet": ws_name,
                "status": status,
                "details": "Has caption or accessibility description" if status == "Pass" else "Missing caption/alt text",
                "metric": "Alt Text",
                "wcag_id": "1.1.1"
            })
        return results

    def check_dashboard_sizing(self, tree):
        """
        Checks if dashboards are fixed size (WCAG 1.4.4).
        """
        results = []
        dashboards = tree.xpath("//dashboard")
        for db in dashboards:
            db_name = db.get("name")
            size = db.find(".//size")
            is_fixed = False
            if size is not None:
                maxheight = size.get("maxheight")
                minheight = size.get("minheight")
                # If absolute pixel values are set and min==max, it's fixed
                if maxheight and minheight and maxheight == minheight:
                    is_fixed = True
            
            results.append({
                "dashboard": db_name,
                "status": "Pass" if is_fixed else "Fail",
                "details": "Fixed size dashboard" if is_fixed else "Automatic/Range resizing detected (May cause overlap)",
                "metric": "Dashboard Sizing",
                "wcag_id": "1.4.4"
            })
        return results

    def check_container_types(self, tree):
        """
        Checks for floating vs tiled containers (WCAG 1.3.2, 2.4.3).
        """
        results = []
        dashboards = tree.xpath("//dashboard")
        for db in dashboards:
            db_name = db.get("name")
            zones = db.xpath(".//zone")
            floating_zones = [z for z in zones if z.get("is-floating") == "1"]
            
            status = "Pass" if not floating_zones else "Warning"
            results.append({
                "dashboard": db_name,
                "status": status,
                "details": "All containers are tiled" if status == "Pass" else f"Found {len(floating_zones)} floating containers (Tiled preferred for focus order)",
                "metric": "Container Logic",
                "wcag_id": "2.4.3"
            })
        return results

    def check_show_tabs(self, tree):
        """
        Checks if 'Show Sheets as Tabs' is enabled (WCAG 2.4.1).
        """
        results = []
        # show-tabs is typically an attribute on the workbook/repository-location or similar
        # In the .twb XML, it can be in <preferences> or workbook attributes
        show_tabs = tree.get("show-tabs") or "0"
        
        status = "Pass" if show_tabs == "1" else "Fail"
        results.append({
            "workbook": "Overall Workbook",
            "status": status,
            "details": "Sheets as Tabs is ENABLED" if status == "Pass" else "Sheets as Tabs is DISABLED (Harder to navigate via keyboard)",
            "metric": "Navigation Strategy",
            "wcag_id": "2.4.1"
        })
        return results

    def check_action_triggers(self, tree):
        """
        Checks for prohibited 'Hover' actions (WCAG 1.4.13).
        """
        results = []
        actions = tree.xpath("//action")
        hover_actions = [a for a in actions if a.get("trigger") == "hover"]
        
        for action in hover_actions:
            results.append({
                "action": action.get("name"),
                "status": "Fail",
                "details": "Trigger set to 'Hover' (Prohibited)",
                "metric": "Action Trigger",
                "wcag_id": "1.4.13"
            })
        
        if not hover_actions:
            results.append({
                "action": "All Actions",
                "status": "Pass",
                "details": "No hover-triggered actions found",
                "metric": "Action Trigger",
                "wcag_id": "1.4.13"
            })
        return results

    def check_filter_controls(self, tree):
        """
        Checks if 'Apply' buttons are shown for multi-select filters (WCAG 3.2.1, 3.2.2).
        """
        results = []
        # This is often in <filter> tags with specific attributes like 'show-apply'
        filters = tree.xpath("//filter")
        for f in filters:
            f_name = f.get("column") or "Unknown Filter"
            show_apply = f.get("show-apply")
            
            # We specifically care about categorical filters that might trigger multiple refreshes
            if show_apply == "1":
                status = "Pass"
            else:
                status = "Warning"
            
            results.append({
                "filter": f_name,
                "status": status,
                "details": "Show 'Apply' button is ENABLED" if status == "Pass" else "Show 'Apply' button is DISABLED (May cause multiple page refreshes)",
                "metric": "Filter Control",
                "wcag_id": "3.2.2"
            })
        
        if not filters:
            results.append({
                "filter": "All Filters",
                "status": "Pass",
                "details": "No filters requiring 'Apply' buttons found",
                "metric": "Filter Control",
                "wcag_id": "3.2.2"
            })
        return results

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        parser = TableauParser(sys.argv[1])
        t = parser.parse()
        if t is not None:
            print("Focus Order Checks:")
            print(parser.check_focus_order(t))
            print("\nAlt Text Checks:")
            print(parser.check_alt_text(t))
