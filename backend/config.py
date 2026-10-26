import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure stable thread allocation on Windows with PyTorch / OpenBLAS / NumPy
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Load .env file from the backend directory
load_dotenv(Path(__file__).parent / ".env")


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Google Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")

    # Groq
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Embeddings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # OCR Configuration
    TESSDATA_DIR: Path = Path(os.getenv("TESSDATA_DIR", Path(__file__).resolve().parent / "tessdata"))
    OCR_ENABLED: bool = os.getenv("OCR_ENABLED", "true").lower() in ("true", "1", "yes")
    OCR_DPI: int = int(os.getenv("OCR_DPI", "150"))

    # Storage
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    VECTOR_STORE_DIR: Path = Path(os.getenv("VECTOR_STORE_DIR", "vector_store"))

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    ]

    # JWT
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "changeme-use-a-real-secret-in-production-at-least-32-chars",
    )
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 h default

    @property
    def ocr_available(self) -> bool:
        return (self.TESSDATA_DIR / "eng.traineddata").exists()

    @property
    def llm_configured(self) -> bool:
        if self.LLM_PROVIDER == "openai":
            return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_openai_api_key_here")
        if self.LLM_PROVIDER == "google":
            return bool(self.GOOGLE_API_KEY and self.GOOGLE_API_KEY != "your_google_api_key_here")
        if self.LLM_PROVIDER == "groq":
            return bool(self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here")
        return False


settings = Settings()

# Ensure TESSDATA_PREFIX is set globally before PyMuPDF is imported anywhere
if settings.TESSDATA_DIR.exists():
    os.environ["TESSDATA_PREFIX"] = str(settings.TESSDATA_DIR.resolve())
