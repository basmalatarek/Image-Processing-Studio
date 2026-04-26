import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
import io

import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(
    page_title="✨ Image Processing Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inject_global_styles(theme="Dark"):
    if theme == "Light":
        app_bg = "#f8fafc"
        card_bg = "rgba(255, 255, 255, 0.92)"
        border = "rgba(148, 163, 184, 0.3)"
        text = "#0f172a"
        muted = "#475569"
        accent = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        accent2 = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        highlight = "#0f60d6"
        shadow = "0 20px 50px rgba(15, 23, 42, 0.08)"
        sidebar_bg = "#ffffff"
        sidebar_text = "#0f172a"
        header_bg = "rgba(255, 255, 255, 0.9)"
        tab_bg = "rgba(15, 23, 42, 0.06)"
        section_bg = "rgba(255, 255, 255, 0.92)"
    else:
        app_bg = "#0f172a"
        card_bg = "#1e293b"
        border = "#334155"
        text = "#e2e8f0"
        muted = "#94a3b8"
        accent = "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        accent2 = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        highlight = "#38bdf8"
        shadow = "0 25px 70px rgba(15, 23, 42, 0.45)"
        sidebar_bg = "#111827"
        sidebar_text = "#e2e8f0"
        header_bg = "rgba(15, 23, 42, 0.92)"
        tab_bg = "rgba(255, 255, 255, 0.025)"
        section_bg = "rgba(15, 23, 42, 0.82)"
    st.markdown(f"""
        <style>
        :root {{
            --app-bg: {app_bg};
            --card-bg: {card_bg};
            --card-border: {border};
            --text: {text};
            --muted: {muted};
            --accent: {accent};
            --accent2: {accent2};
            --highlight: {highlight};
            --shadow: {shadow};
            --header-bg: {header_bg};
            --tab-bg: {tab_bg};
            --section-bg: {section_bg};
            --sidebar-bg: {sidebar_bg};
            --sidebar-text: {sidebar_text};
        }}

        html, body {{
            background: var(--app-bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
        }}

        .stApp {{
            background: var(--app-bg) !important;
            color: var(--text) !important;
            min-height: 100vh;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: radial-gradient(circle at 15% 10%, rgba(79, 172, 254, 0.12), transparent 18%),
                        radial-gradient(circle at 85% 20%, rgba(118, 75, 162, 0.1), transparent 22%),
                        radial-gradient(circle at 50% 85%, rgba(16, 185, 129, 0.08), transparent 25%);
            z-index: -1;
        }}

        .main-container {{
            padding: 2rem 2rem 3rem;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .page-header {{
            padding: 2rem 2rem 1.5rem;
            border-radius: 28px;
            background: var(--header-bg) !important;
            border: 1px solid rgba(79, 172, 254, 0.12);
            box-shadow: 0 35px 100px rgba(0, 0, 0, 0.4);
            color: var(--text) !important;
            margin-bottom: 1.5rem;
            animation: floatIn 0.9s ease both;
            backdrop-filter: blur(20px);
        }}

        .page-title {{
            font-size: 3rem;
            font-weight: 900;
            margin: 0;
            letter-spacing: -0.07em;
            text-shadow: 0 15px 30px rgba(0, 0, 0, 0.25);
        }}

        .page-subtitle {{
            margin-top: 0.85rem;
            font-size: 1.05rem;
            color: rgba(226, 232, 240, 0.8);
            max-width: 820px;
            line-height: 1.75;
        }}

        .section-card, .image-card, .image-container, .sidebar-title, .sidebar-category {{
            background: var(--card-bg) !important;
            border: 1px solid var(--card-border) !important;
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.35) !important;
            backdrop-filter: blur(18px) !important;
            -webkit-backdrop-filter: blur(18px) !important;
        }}

        .section-card {{
            border-radius: 26px;
            padding: 1.75rem;
            transition: transform 0.4s ease, border-color 0.4s ease, box-shadow 0.4s ease;
            margin-bottom: 1.75rem;
            animation: floatIn 0.9s ease both;
        }}

        .section-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(79, 172, 254, 0.35);
            box-shadow: 0 35px 95px rgba(0, 0, 0, 0.45);
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            color: var(--text);
        }}

        .section-description {{
            color: rgba(226, 232, 240, 0.75);
            margin-bottom: 1.6rem;
        }}

        .image-card, .image-container {{
            border-radius: 24px;
            padding: 1.1rem;
            border: 1px solid rgba(79, 172, 254, 0.08);
            transition: transform 0.35s ease, box-shadow 0.35s ease;
            animation: floatIn 0.95s ease both;
        }}

        .image-card:hover, .image-container:hover {{
            transform: translateY(-3px);
            box-shadow: 0 35px 90px rgba(0, 0, 0, 0.36);
        }}

        .image-title {{
            margin-bottom: 1rem;
            font-weight: 800;
            color: var(--text);
            letter-spacing: 0.5px;
        }}

        .stButton > button,
        .stDownloadButton > button,
        .stButton button,
        .stDownloadButton button,
        .stTabs [data-baseweb="tab-list"] button,
        .stSidebar button {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 40%, #667eea 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 22px !important;
            min-height: 56px !important;
            padding: 0.9rem 2rem !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            box-shadow: 0 22px 45px rgba(41, 98, 255, 0.22) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            white-space: nowrap !important;
            overflow-wrap: normal !important;
            word-break: normal !important;
            line-height: 1.2 !important;
            transition: transform 0.35s ease, box-shadow 0.35s ease, background-position 0.8s ease, color 0.35s ease !important;
            background-size: 180% 180% !important;
        }}

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stButton button:hover,
        .stDownloadButton button:hover,
        .stTabs [data-baseweb="tab-list"] button:hover,
        .stSidebar button:hover {{
            transform: translateY(-2px) scale(1.08) !important;
            background-position: 100% 0% !important;
            box-shadow: 0 0 30px rgba(79, 172, 254, 0.78) !important;
        }}

        .stButton > button:active,
        .stDownloadButton > button:active,
        .stButton button:active,
        .stDownloadButton button:active,
        .stTabs [data-baseweb="tab-list"] button:active,
        .stSidebar button:active {{
            transform: translateY(0px) scale(0.96) !important;
            box-shadow: 0 12px 26px rgba(0, 0, 0, 0.38) !important;
        }}

        .stSlider [data-testid="stSlider"] input {{
            accent-color: #38bdf8 !important;
        }}

        .stSlider > div {{
            background: rgba(255, 255, 255, 0.04) !important;
            border-radius: 18px !important;
            padding: 0.85rem 1rem !important;
            box-shadow: inset 0 0 0 1px rgba(79, 172, 254, 0.08) !important;
        }}

        .stSlider > div > div {{
            border-radius: 16px !important;
        }}

        .stSelectbox > div > div {{
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(79, 172, 254, 0.18) !important;
            border-radius: 18px !important;
            box-shadow: 0 25px 55px rgba(0, 0, 0, 0.18) !important;
            color: var(--text) !important;
            transition: all 0.35s ease !important;
            padding: 0.85rem 1rem !important;
        }}

        .stSelectbox > div > div:hover {{
            border-color: rgba(79, 172, 254, 0.45) !important;
            background: rgba(79, 172, 254, 0.08) !important;
            transform: translateY(-1px) !important;
        }}

        .stTextInput > div > input, .stNumberInput > div > input {{
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(79, 172, 254, 0.18) !important;
            border-radius: 18px !important;
            color: var(--text) !important;
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04) !important;
            transition: all 0.35s ease !important;
            padding: 0.95rem 1rem !important;
        }}

        .stTextInput > div > input:focus, .stNumberInput > div > input:focus {{
            outline: none !important;
            border-color: rgba(79, 172, 254, 0.45) !important;
            box-shadow: 0 0 0 4px rgba(79, 172, 254, 0.14) !important;
        }}

        .stRadio > div {{
            gap: 0.9rem;
        }}

        .stRadio > div > label {{
            background: rgba(255, 255, 255, 0.03) !important;
            color: var(--text) !important;
            border: 1px solid rgba(79, 172, 254, 0.18) !important;
            border-radius: 18px !important;
            padding: 0.95rem 1.1rem !important;
            transition: all 0.35s ease !important;
            box-shadow: 0 18px 35px rgba(0, 0, 0, 0.18) !important;
            backdrop-filter: blur(10px) !important;
        }}

        .stRadio > div > label:hover {{
            background: rgba(79, 172, 254, 0.12) !important;
            border-color: rgba(79, 172, 254, 0.45) !important;
            transform: translateY(-1px) !important;
        }}

        [data-testid="stSidebar"] .stRadio > div > label:nth-child(-n+4) {{
            background: linear-gradient(135deg, #fb923c 0%, #f97316 100%) !important;
            color: white !important;
            border-color: rgba(249, 115, 22, 0.35) !important;
        }}

        [data-testid="stSidebar"] .stRadio > div > label:nth-child(n+5):nth-child(-n+8) {{
            background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%) !important;
            color: white !important;
            border-color: rgba(124, 58, 237, 0.35) !important;
        }}

        [data-testid="stSidebar"] .stRadio > div > label:nth-child(n+9) {{
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
            color: white !important;
            border-color: rgba(14, 165, 233, 0.35) !important;
        }}

        .sidebar-category {{
            padding: 0.95rem 1rem;
            border-radius: 18px;
            margin-bottom: 1rem;
            color: white;
            font-weight: 700;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: transform 0.35s ease, box-shadow 0.35s ease;
        }}

        .sidebar-category:hover {{
            transform: translateY(-2px);
            box-shadow: 0 30px 75px rgba(0, 0, 0, 0.25);
        }}

        .sidebar-category-basic {{
            background: linear-gradient(135deg, #fb923c 0%, #f97316 100%) !important;
        }}

        .sidebar-category-advanced {{
            background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%) !important;
        }}

        .sidebar-category-analysis {{
            background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
        }}

        .download-btn, .reset-btn {{
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            margin: 0 auto !important;
        }}

        .download-btn .stDownloadButton > button,
        .reset-btn .stButton > button {{
            min-width: 220px !important;
            width: auto !important;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.95) !important;
            color: var(--sidebar-text) !important;
            border-right: 1px solid rgba(79, 172, 254, 0.12);
            box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
        }}

        [data-testid="stSidebar"] .stMarkdown {{
            color: var(--sidebar-text) !important;
        }}

        .sidebar-title {{
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--sidebar-text);
            margin-bottom: 1rem;
            padding-bottom: 0.85rem;
            border-bottom: 1px solid rgba(79, 172, 254, 0.18);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            background: var(--tab-bg) !important;
            border: 1px solid rgba(79, 172, 254, 0.12) !important;
            border-radius: 18px;
            padding: 0.5rem;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2) !important;
        }}

        .stTabs [data-baseweb="tab-list"] [aria-selected="true"] {{
            background: linear-gradient(135deg, #4facfe, #667eea) !important;
            box-shadow: 0 14px 35px rgba(79, 172, 254, 0.35) !important;
            color: white !important;
            border-radius: 14px !important;
        }}

        .stMarkdown h1 {{
            color: var(--text) !important;
            font-weight: 900;
            animation: floatIn 0.6s ease-out;
        }}

        .stMarkdown h2 {{
            color: var(--text) !important;
            font-weight: 800;
            margin-top: 1.4rem;
            animation: floatIn 0.6s ease-out;
        }}

        .stMarkdown h3 {{
            color: var(--muted) !important;
            font-weight: 700;
        }}

        hr {{
            border: none;
            height: 1px;
            background: rgba(79, 172, 254, 0.18);
            margin: 2rem 0;
        }}

        .metric-card {{
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.18), rgba(15, 23, 42, 0.92));
            color: white;
            padding: 1.5rem;
            border-radius: 18px;
            text-align: center;
            animation: floatIn 0.6s ease-out;
            box-shadow: 0 25px 65px rgba(0, 0, 0, 0.3);
        }}

        .stAlert {{
            border-radius: 18px !important;
            padding: 1.4rem !important;
            animation: scaleIn 0.3s ease-out;
        }}

        .section-card {{
            animation: floatIn 0.8s ease-out;
        }}

        .image-card {{
            animation: floatIn 1s ease-out;
        }}

        @keyframes floatIn {{
            from {{ opacity: 0; transform: translateY(18px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes buttonGradient {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        @keyframes scaleIn {{
            from {{ opacity: 0; transform: scale(0.96); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}

        @media (max-width: 768px) {{
            .main-container {{ padding: 1rem 1rem 2rem; }}
            .page-title {{ font-size: 2.2rem; }}
            .section-card {{ padding: 1.25rem; }}
        }}
        </style>
    """, unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def image_to_array(img):
    """Convert PIL Image to numpy array"""
    return np.array(img)

def array_to_image(arr):
    """Convert numpy array to PIL Image"""
    if arr.dtype != np.uint8:
        arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def resize_for_dual(img1, img2):
    """Resize both images to same dimensions"""
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    h, w = min(h1, h2), min(w1, w2)
    return img1[:h, :w], img2[:h, :w]

def display_image_card(image, title="Image", border_color="#6366f1"):
    """Display image in a modern card container"""
    st.markdown(f"""
        <div class="image-card" style="border-color: {border_color};">
            <div class="image-title">📷 {title}</div>
        </div>
    """, unsafe_allow_html=True)
    st.image(image, width="stretch")

def create_gradient_button(label, icon=""):
    """Helper for button styling"""
    return f"🎨 {label}" if icon == "" else f"{icon} {label}"

def render_header():
    """Render beautiful header"""
    st.markdown(
        """
        <div class="page-header">
            <div class="page-title">✨ Image Processing Studio</div>
            <div class="page-subtitle">A premium AI-style image editor with modern filters, live preview, and polished dashboard UI.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def display_images_side_by_side(col1, col2, original, processed, title1="Original", title2="Processed"):
    """Display two images side by side with modern styling"""
    with col1:
        st.markdown(f"""
            <div class="image-card">
                <div class="image-title">📸 {title1}</div>
            </div>
        """, unsafe_allow_html=True)
        st.image(original, width="stretch")
    with col2:
        st.markdown(f"""
            <div class="image-card" style="border-color: #ec4899;">
                <div class="image-title">✨ {title2}</div>
            </div>
        """, unsafe_allow_html=True)
        st.image(processed, width="stretch")

# ==================== UNARY OPERATIONS ====================

class UnaryOps:
    @staticmethod
    def brightness(img, factor):
        """Adjust brightness"""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    @staticmethod
    def contrast(img, factor):
        """Adjust contrast"""
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:, :, 0] = np.clip(lab[:, :, 0] * factor, 0, 255)
        return cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB)

    @staticmethod
    def grayscale(img):
        """Convert to grayscale"""
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    @staticmethod
    def negative(img):
        """Create negative/complement"""
        return 255 - img

    @staticmethod
    def threshold_basic(img, value):
        """Basic thresholding"""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
        _, thresh = cv2.threshold(gray, value, 255, cv2.THRESH_BINARY)
        return thresh

    @staticmethod
    def threshold_otsu(img):
        """Otsu thresholding"""
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    @staticmethod
    def histogram(img):
        """Generate histogram"""
        if len(img.shape) == 2:  # Grayscale
            hist = cv2.calcHist([img], [0], None, [256], [0, 256])
            return hist
        else:  # RGB
            colors = ('r', 'g', 'b')
            hists = [cv2.calcHist([img], [i], None, [256], [0, 256]) for i in range(3)]
            return hists

    @staticmethod
    def salt_pepper_noise(img, amount=0.05):
        """Add salt & pepper noise"""
        output = img.copy()
        num_salt = np.ceil(amount / 2 * img.size)
        num_pepper = np.ceil(amount / 2 * img.size)
        
        coords = [np.random.randint(0, i, int(num_salt)) for i in img.shape]
        output[coords[0], coords[1]] = 255
        
        coords = [np.random.randint(0, i, int(num_pepper)) for i in img.shape]
        output[coords[0], coords[1]] = 0
        return output

    @staticmethod
    def remove_salt_pepper(img, filter_type='median', kernel_size=5):
        """Remove salt & pepper noise"""
        if filter_type == 'median':
            return cv2.medianBlur(img, kernel_size)
        elif filter_type == 'bilateral':
            return cv2.bilateralFilter(img, 9, 75, 75)
        return img

    @staticmethod
    def mean_filter(img, kernel_size=5):
        """Apply mean filter"""
        return cv2.blur(img, (kernel_size, kernel_size))

    @staticmethod
    def median_filter(img, kernel_size=5):
        """Apply median filter"""
        return cv2.medianBlur(img, kernel_size)

    @staticmethod
    def min_filter(img, kernel_size=5):
        """Apply minimum filter"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.erode(img, kernel)

    @staticmethod
    def max_filter(img, kernel_size=5):
        """Apply maximum filter"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.dilate(img, kernel)

    @staticmethod
    def erosion(img, kernel_size=5):
        """Morphological erosion"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.erode(img, kernel)

    @staticmethod
    def dilation(img, kernel_size=5):
        """Morphological dilation"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.dilate(img, kernel)

    @staticmethod
    def opening(img, kernel_size=5):
        """Morphological opening"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    @staticmethod
    def closing(img, kernel_size=5):
        """Morphological closing"""
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    @staticmethod
    def dithering(img):
        """Floyd-Steinberg dithering"""
        pil_img = array_to_image(img) if isinstance(img, np.ndarray) else img
        return pil_img.convert('1')

def plot_histogram(image):
    """Plot histogram using matplotlib"""
    fig, ax = plt.subplots()
    if len(image.shape) == 2:
        ax.hist(image.ravel(), bins=256, color='gray', alpha=0.7)
    else:
        colors = ['r', 'g', 'b']
        for i, color in enumerate(colors):
            ax.hist(image[:, :, i].ravel(), bins=256, color=color, alpha=0.7, label=color.upper())
        ax.legend()
    ax.set_xlabel('Pixel Value')
    ax.set_ylabel('Frequency')
    ax.set_title('Image Histogram')
    return fig

# ==================== BINARY OPERATIONS ====================

class BinaryOps:
    @staticmethod
    def add_images(img1, img2):
        """Add two images"""
        img1, img2 = resize_for_dual(img1, img2)
        return cv2.add(img1, img2)

    @staticmethod
    def weighted_blend(img1, img2, alpha=0.5):
        """Weighted blending"""
        img1, img2 = resize_for_dual(img1, img2)
        return cv2.addWeighted(img1, alpha, img2, 1 - alpha, 0)

    @staticmethod
    def subtract_images(img1, img2, reverse=False):
        """Subtract images"""
        img1, img2 = resize_for_dual(img1, img2)
        if reverse:
            return cv2.subtract(img2, img1)
        return cv2.subtract(img1, img2)

    @staticmethod
    def channel_comparison(img1, img2):
        """RGB channel comparison"""
        img1, img2 = resize_for_dual(img1, img2)
        b1, g1, r1 = cv2.split(img1)
        b2, g2, r2 = cv2.split(img2)
        
        r_diff = cv2.absdiff(r1, r2)
        g_diff = cv2.absdiff(g1, g2)
        b_diff = cv2.absdiff(b1, b2)
        
        return cv2.merge([b_diff, g_diff, r_diff])

# ==================== CONVOLUTION FILTERS ====================

class ConvolutionOps:
    @staticmethod
    def average_filter(img, kernel_size=3):
        """Average filter"""
        return cv2.blur(img, (kernel_size, kernel_size))

    @staticmethod
    def gaussian_filter(img, kernel_size=5, sigma=1.0):
        """Gaussian filter"""
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)

    @staticmethod
    def sharpening(img, strength=1.5):
        """Sharpening filter"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) * strength / 9
        return cv2.filter2D(img, -1, kernel)

    @staticmethod
    def custom_convolution(img, kernel):
        """Apply custom convolution kernel"""
        return cv2.filter2D(img, -1, kernel)

# ==================== UI SECTIONS ====================

def upload_section():
    """Image upload section with modern design"""
    st.sidebar.markdown('<div class="sidebar-title">📁 Upload Image</div>', unsafe_allow_html=True)
    uploaded_file = st.sidebar.file_uploader("Choose an image file", type=['jpg', 'jpeg', 'png', 'bmp', 'avif'], 
                                             label_visibility="collapsed")
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        img_array = np.array(img.convert('RGB'))
        st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
        return img_array
    return None

def upload_dual_section():
    """Dual image upload section with modern design"""
    st.sidebar.markdown('<div class="sidebar-title">📁 Upload Two Images</div>', unsafe_allow_html=True)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        file1 = st.file_uploader("Image 1", type=['jpg', 'jpeg', 'png', 'bmp', 'avif'], key="img1")
    with col2:
        file2 = st.file_uploader("Image 2", type=['jpg', 'jpeg', 'png', 'bmp', 'avif'], key="img2")
    
    if file1 and file2:
        img1 = np.array(Image.open(file1).convert('RGB'))
        img2 = np.array(Image.open(file2).convert('RGB'))
        st.sidebar.success("✅ Both images loaded")
        return img1, img2
    return None, None

def download_button(image, filename="processed_image.png"):
    """Generate download button with modern styling"""
    buf = io.BytesIO()
    if isinstance(image, np.ndarray):
        Image.fromarray(image.astype(np.uint8)).save(buf, format="PNG")
    else:
        image.save(buf, format="PNG")
    buf.seek(0)
    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
    st.download_button(
        label="💾 Download Image",
        data=buf,
        file_name=filename,
        mime="image/png",
        use_container_width=False
    )
    st.markdown('</div>', unsafe_allow_html=True)

def reset_app():
    """Reset the app state and rerun cleanly"""
    st.sidebar.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    reset_pressed = st.sidebar.button("🔄 Reset")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    if reset_pressed:
        st.session_state.clear()
        st.rerun()

# ==================== MAIN APP ====================

def main():
    if "theme" not in st.session_state:
        st.session_state.theme = "Dark"
    st.sidebar.markdown('<div class="sidebar-title">🎨 Theme</div>', unsafe_allow_html=True)
    theme_choice = st.sidebar.radio(
        "Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "Dark" else 1,
        key="theme_toggle",
        label_visibility="collapsed",
    )
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    inject_global_styles(st.session_state.theme)
    st.sidebar.markdown('---')
    reset_app()

    st.sidebar.markdown('---')
    # Render Header
    render_header()
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="sidebar-title">🚀 Navigation</div>', unsafe_allow_html=True)
    
    app_mode = st.sidebar.radio(
        "Select Mode",
        ["🎯 Single Image", "🔗 Dual Images", "🔧 Convolution Filters"],
        label_visibility="collapsed"
    )
    
    # =============== SINGLE IMAGE MODE ===============
    if app_mode == "🎯 Single Image":
        original_img = upload_section()

        if original_img is not None:
            st.sidebar.markdown("---")
            st.sidebar.markdown('<div class="sidebar-title">⚙️ Operations</div>', unsafe_allow_html=True)
            st.sidebar.markdown('<div class="sidebar-category sidebar-category-basic">⚡ Operation categories: Basic • Advanced • Analysis</div>', unsafe_allow_html=True)
            operation = st.sidebar.radio(
                "Select Operation",
                ["🌟 Brightness", "🎚️ Contrast", "🖤 Grayscale", "🔄 Negative", "⚪ Threshold",
                 "📊 Histogram", "🌪️ Salt & Pepper", "🎨 Filters", "🧬 Morphological", "🎭 Dithering"],
                label_visibility="collapsed"
            )

            with st.spinner("Processing..."):
                border_color = "#38bdf8"
                processed = None
                if operation == "🌟 Brightness":
                    factor = st.sidebar.slider("Brightness Factor", 0.5, 2.0, 1.0, 0.1)
                    processed = UnaryOps.brightness(original_img, factor)
                    border_color = "#f59e0b"
                elif operation == "🎚️ Contrast":
                    factor = st.sidebar.slider("Contrast Factor", 0.5, 2.0, 1.0, 0.1)
                    processed = UnaryOps.contrast(original_img, factor)
                    border_color = "#3b82f6"
                elif operation == "🖤 Grayscale":
                    processed = UnaryOps.grayscale(original_img)
                elif operation == "🔄 Negative":
                    processed = UnaryOps.negative(original_img)
                elif operation == "⚪ Threshold":
                    threshold_type = st.sidebar.radio("Threshold Type", ["Basic", "Otsu"], horizontal=True)
                    if threshold_type == "Basic":
                        value = st.sidebar.slider("Threshold Value", 0, 255, 128)
                        processed = UnaryOps.threshold_basic(original_img, value)
                    else:
                        processed = UnaryOps.threshold_otsu(original_img)
                elif operation == "📊 Histogram":
                    processed = original_img
                elif operation == "🌪️ Salt & Pepper":
                    sub_op = st.sidebar.radio("Salt & Pepper", ["Add Noise", "Remove Noise"], horizontal=True)
                    if sub_op == "Add Noise":
                        amount = st.sidebar.slider("Noise Amount", 0.01, 0.2, 0.05, 0.01)
                        gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
                        processed = UnaryOps.salt_pepper_noise(gray, amount)
                    else:
                        filter_type = st.sidebar.radio("Filter Type", ["Median", "Bilateral"], horizontal=True)
                        kernel = st.sidebar.slider("Kernel Size", 3, 15, 5, 2)
                        gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
                        noisy = UnaryOps.salt_pepper_noise(gray, 0.1)
                        processed = UnaryOps.remove_salt_pepper(noisy, filter_type, kernel)
                elif operation == "🎨 Filters":
                    filter_type = st.sidebar.radio("Filter Type", ["Mean", "Median", "Min", "Max"], horizontal=True)
                    kernel_size = st.sidebar.slider("Kernel Size", 3, 15, 5, 2)
                    if filter_type == "Mean":
                        processed = UnaryOps.mean_filter(original_img, kernel_size)
                    elif filter_type == "Median":
                        processed = UnaryOps.median_filter(original_img, kernel_size)
                    elif filter_type == "Min":
                        gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
                        processed = UnaryOps.min_filter(gray, kernel_size)
                    else:
                        gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
                        processed = UnaryOps.max_filter(gray, kernel_size)
                elif operation == "🧬 Morphological":
                    morph_type = st.sidebar.radio(
                        "Morphological Operation",
                        ["Erosion", "Dilation", "Opening", "Closing"],
                        horizontal=True,
                    )
                    kernel_size = st.sidebar.slider("Kernel Size", 3, 15, 5, 2)
                    gray = cv2.cvtColor(original_img, cv2.COLOR_RGB2GRAY)
                    if morph_type == "Erosion":
                        processed = UnaryOps.erosion(gray, kernel_size)
                    elif morph_type == "Dilation":
                        processed = UnaryOps.dilation(gray, kernel_size)
                    elif morph_type == "Opening":
                        processed = UnaryOps.opening(gray, kernel_size)
                    else:
                        processed = UnaryOps.closing(gray, kernel_size)
                elif operation == "🎭 Dithering":
                    processed = UnaryOps.dithering(original_img)

            def display_processed_image(image):
                if isinstance(image, np.ndarray) and image.ndim == 2:
                    st.image(image, width="stretch", channels="GRAY")
                else:
                    st.image(image, width="stretch")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📸 Original Image</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                st.image(original_img, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">✨ Processed Image</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f'<div class="image-card" style="border-color: {border_color};">', unsafe_allow_html=True)
                if operation == "📊 Histogram":
                    fig = plot_histogram(original_img)
                    st.pyplot(fig, use_container_width=True)
                else:
                    display_processed_image(processed)
                st.markdown('</div>', unsafe_allow_html=True)
                if operation != "📊 Histogram":
                    if isinstance(processed, np.ndarray) or hasattr(processed, 'save'):
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            download_button(np.array(processed) if not isinstance(processed, np.ndarray) else processed,
                                            f"{operation.split()[0].lower()}.png")

            info_tabs = st.tabs(["🎚 Controls", "📷 Preview", "📊 Analysis"])
            with info_tabs[0]:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">🎛️ Control Panel</div>
                        <p class="section-description">Use the sidebar to choose your effect and adjust settings. Each filter updates instantly with a smooth preview.</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Current operation:** {operation}")
                if operation == "🌟 Brightness":
                    st.write("Adjust the slider to brighten or darken the image while preserving color balance.")
                elif operation == "🎚️ Contrast":
                    st.write("Boost or soften contrast for richer detail and clearer edges.")
                elif operation == "🖤 Grayscale":
                    st.write("Convert your image to clean grayscale for a timeless monochrome look.")
                elif operation == "🔄 Negative":
                    st.write("Invert the colors to create a dramatic negative effect.")
                elif operation == "⚪ Threshold":
                    st.write("Create high-contrast masks using basic or adaptive thresholding.")
                elif operation == "🌪️ Salt & Pepper":
                    st.write("Add or remove noise for texture testing and denoising effects.")
                elif operation == "🎨 Filters":
                    st.write("Apply mean, median, min, or max filters for smoothing and edge control.")
                elif operation == "🧬 Morphological":
                    st.write("Use morphology tools to clean or highlight structural image elements.")
                elif operation == "🎭 Dithering":
                    st.write("Convert your image to a stylized black-and-white dithered effect.")
                elif operation == "📊 Histogram":
                    st.write("View the pixel distribution of the original image in the analysis tab.")

            with info_tabs[1]:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📷 Side-by-side Preview</div>
                    </div>
                """, unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                display_images_side_by_side(col_a, col_b, original_img, processed, "Original", "Processed")

            with info_tabs[2]:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📊 Image Analysis</div>
                    </div>
                """, unsafe_allow_html=True)
                if operation == "📊 Histogram":
                    st.write("Histogram displayed in the processed image area above.")
                else:
                    fig = plot_histogram(processed if processed is not None else original_img)
                    st.pyplot(fig, use_container_width=True)

    # =============== DUAL IMAGE MODE ===============
    elif app_mode == "🔗 Dual Images":
        img1, img2 = upload_dual_section()
        
        if img1 is not None and img2 is not None:
            st.sidebar.markdown("---")
            st.sidebar.markdown('<div class="sidebar-title">⚙️ Operations</div>', unsafe_allow_html=True)
            st.sidebar.markdown('<div class="sidebar-category sidebar-category-advanced">🔧 Filter types: Average • Gaussian • Sharpen • Custom</div>', unsafe_allow_html=True)
            
            operation = st.sidebar.radio(
                "Select Operation",
                ["➕ Add Images", "🎨 Weighted Blend", "➖ Subtract", "🔍 Channel Comparison"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.markdown("""
                <div class="section-card">
                    <div class="section-title">🔗 Dual Image Operations</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📸 Image 1</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(img1, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">🖼️ Image 2</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(img2, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("""
                <div class="section-card">
                    <div class="section-title">✨ Result</div>
                </div>
            """, unsafe_allow_html=True)
            
            if "➕ Add Images" in operation:
                processed = BinaryOps.add_images(img1, img2)
                st.markdown('<div class="image-container" style="border-color: #10b981;">', unsafe_allow_html=True)
                st.image(processed, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    download_button(processed, "added.png")
            
            elif "🎨 Weighted Blend" in operation:
                alpha = st.slider("Image 1 Weight", 0.0, 1.0, 0.5, 0.05)
                processed = BinaryOps.weighted_blend(img1, img2, alpha)
                st.markdown('<div class="image-container" style="border-color: #ec4899;">', unsafe_allow_html=True)
                st.image(processed, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    download_button(processed, "blended.png")
            
            elif "➖ Subtract" in operation:
                reverse = st.checkbox("Reverse (Image 2 - Image 1)")
                processed = BinaryOps.subtract_images(img1, img2, reverse)
                st.markdown('<div class="image-container" style="border-color: #f59e0b;">', unsafe_allow_html=True)
                st.image(processed, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    download_button(processed, "subtracted.png")
            
            elif "🔍 Channel Comparison" in operation:
                processed = BinaryOps.channel_comparison(img1, img2)
                st.markdown('<div class="image-container" style="border-color: #8b5cf6;">', unsafe_allow_html=True)
                st.image(processed, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    download_button(processed, "channel_diff.png")
    
    # =============== CONVOLUTION MODE ===============
    elif app_mode == "🔧 Convolution Filters":
        original_img = upload_section()
        
        if original_img is not None:
            st.sidebar.markdown("---")
            st.sidebar.markdown('<div class="sidebar-title">⚙️ Filters</div>', unsafe_allow_html=True)
            
            filter_type = st.sidebar.radio(
                "Select Filter",
                ["🌀 Average", "🔷 Gaussian", "⚡ Sharpening", "🎯 Custom Kernel"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.markdown("""
                <div class="section-card">
                    <div class="section-title">🔧 Convolution Filters</div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">📸 Original</div>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.image(original_img, width="stretch")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="section-card">
                        <div class="section-title">✨ Filtered</div>
                    </div>
                """, unsafe_allow_html=True)
                
                if "🌀 Average" in filter_type:
                    kernel_size = st.slider("Kernel Size", 3, 15, 5, 2)
                    processed = ConvolutionOps.average_filter(original_img, kernel_size)
                    st.markdown('<div class="image-container" style="border-color: #3b82f6;">', unsafe_allow_html=True)
                    st.image(processed, width="stretch")
                    st.markdown('</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        download_button(processed, "average_filter.png")
                
                elif "🔷 Gaussian" in filter_type:
                    col_k, col_s = st.columns(2)
                    with col_k:
                        kernel_size = st.slider("Kernel Size", 3, 15, 5, 2)
                    with col_s:
                        sigma = st.slider("Sigma", 0.1, 3.0, 1.0, 0.1)
                    processed = ConvolutionOps.gaussian_filter(original_img, kernel_size, sigma)
                    st.markdown('<div class="image-container" style="border-color: #8b5cf6;">', unsafe_allow_html=True)
                    st.image(processed, width="stretch")
                    st.markdown('</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        download_button(processed, "gaussian_filter.png")
                
                elif "⚡ Sharpening" in filter_type:
                    strength = st.slider("Strength", 0.5, 3.0, 1.5, 0.1)
                    processed = ConvolutionOps.sharpening(original_img, strength)
                    st.markdown('<div class="image-container" style="border-color: #ef4444;">', unsafe_allow_html=True)
                    st.image(processed, width="stretch")
                    st.markdown('</div>', unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        download_button(processed, "sharpened.png")
                
                elif "🎯 Custom Kernel" in filter_type:
                    st.info("📝 Enter 9 values separated by commas for a 3x3 kernel")
                    kernel_input = st.text_area("Custom Kernel", value="0,-1,0,-1,5,-1,0,-1,0", height=80)
                    
                    try:
                        kernel = np.array([float(x.strip()) for x in kernel_input.split(',')]).reshape(3, 3)
                        processed = ConvolutionOps.custom_convolution(original_img, kernel)
                        st.markdown('<div class="image-container" style="border-color: #10b981;">', unsafe_allow_html=True)
                        st.image(processed, width="stretch")
                        st.markdown('</div>', unsafe_allow_html=True)
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            download_button(processed, "custom_kernel.png")
                    except ValueError:
                        st.error("❌ Invalid kernel format! Please enter 9 comma-separated numbers.")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()