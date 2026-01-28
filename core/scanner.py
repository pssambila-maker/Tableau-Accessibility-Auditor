import cv2
import numpy as np
from sklearn.cluster import KMeans
from core.contrast import get_contrast_ratio, check_compliance
import tableauserverclient as TSC

class DashboardScanner:
    def __init__(self, server_url=None, token_name=None, token_value=None, site_id=''):
        self.server_url = server_url
        self.token_name = token_name
        self.token_value = token_value
        self.site_id = site_id

    def fetch_screenshot(self, view_id, output_path="temp/dashboard_scan.png"):
        """
        Authenticates and downloads a high-res PNG of a view.
        """
        if not all([self.server_url, self.token_name, self.token_value]):
            return False, "Missing credentials"

        try:
            tableau_auth = TSC.PersonalAccessTokenAuth(self.token_name, self.token_value, site_id=self.site_id)
            server = TSC.Server(self.server_url, use_server_version=True)
            
            with server.auth.sign_in(tableau_auth):
                view = server.views.get_by_id(view_id)
                server.views.populate_image(view)
                with open(output_path, "wb") as f:
                    f.write(view.image)
            return True, output_path
        except Exception as e:
            return False, str(e)

    def extract_dominant_colors(self, image_path, k=5):
        """
        Extracts k dominant colors from an image using K-Means.
        """
        image = cv2.imread(image_path)
        if image is None:
            return []
            
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pixels = image.reshape(-1, 3)
        
        # Perform K-Means to find dominant colors
        kmeans = KMeans(n_clusters=k, n_init=10)
        kmeans.fit(pixels)
        
        colors = kmeans.cluster_centers_.astype(int)
        return [tuple(c) for c in colors]

    def audit_contrast(self, colors):
        """
        Analyzes the palette for contrast compliance.
        Heuristic: Compare the lightest color (BG) with the darkest color (Text).
        """
        if len(colors) < 2:
            return {"status": "Inconclusive", "details": "Not enough colors found"}

        # Sort by luminance
        from core.contrast import get_relative_luminance
        sorted_colors = sorted(colors, key=get_relative_luminance)
        
        darkest = sorted_colors[0]
        lightest = sorted_colors[-1]
        
        passed, ratio = check_compliance(darkest, lightest)
        
        return {
            "status": "Pass" if passed else "Fail",
            "ratio": round(ratio, 2),
            "darkest": darkest,
            "lightest": lightest,
            "details": f"Contrast Ratio {round(ratio, 2)}:1 between dominant dark/light colors."
        }
