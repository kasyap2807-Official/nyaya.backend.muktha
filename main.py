# # # # # # # # # from fastapi import FastAPI, HTTPException
# # # # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # # # from fastapi.staticfiles import StaticFiles
# # # # # # # # # from fastapi.responses import FileResponse
# # # # # # # # # from pydantic import BaseModel
# # # # # # # # # from mistralai import Mistral
# # # # # # # # # import os

# # # # # # # # # app = FastAPI(
# # # # # # # # #     title="LexAI - Legal Analysis API",
# # # # # # # # #     description="AI-powered legal scenario analysis using Mistral",
# # # # # # # # #     version="1.0.0"
# # # # # # # # # )

# # # # # # # # # app.add_middleware(
# # # # # # # # #     CORSMiddleware,
# # # # # # # # #     allow_origins=["*"],
# # # # # # # # #     allow_credentials=True,
# # # # # # # # #     allow_methods=["*"],
# # # # # # # # #     allow_headers=["*"],
# # # # # # # # # )

# # # # # # # # # # Mount static files
# # # # # # # # # app.mount("/static", StaticFiles(directory="static"), name="static")


# # # # # # # # # class ScenarioRequest(BaseModel):
# # # # # # # # #     scenario: str
# # # # # # # # #     jurisdiction: str = "India"  # Default jurisdiction
# # # # # # # # #     api_key: str  # User provides their Mistral API key


# # # # # # # # # class LegalAnalysis(BaseModel):
# # # # # # # # #     applicable_laws: list
# # # # # # # # #     consequences: list
# # # # # # # # #     recommendations: list
# # # # # # # # #     severity: str
# # # # # # # # #     summary: str
# # # # # # # # #     disclaimer: str


# # # # # # # # # SYSTEM_PROMPT = """You are LexAI, an expert legal analyst with deep knowledge of laws across multiple jurisdictions. 
# # # # # # # # # When given a scenario, you must analyze it thoroughly and respond ONLY with a valid JSON object in this exact format:

# # # # # # # # # {
# # # # # # # # #   "applicable_laws": [
# # # # # # # # #     {
# # # # # # # # #       "name": "Law/Act/Section Name",
# # # # # # # # #       "section": "Specific section or article number",
# # # # # # # # #       "description": "What this law covers and why it applies",
# # # # # # # # #       "jurisdiction": "Country/State this applies to"
# # # # # # # # #     }
# # # # # # # # #   ],
# # # # # # # # #   "consequences": [
# # # # # # # # #     {
# # # # # # # # #       "type": "Civil / Criminal / Administrative / Financial",
# # # # # # # # #       "description": "Detailed description of the consequence",
# # # # # # # # #       "severity": "Minor / Moderate / Severe / Critical",
# # # # # # # # #       "penalty": "Specific penalty if applicable (fine amount, jail term, etc.)"
# # # # # # # # #     }
# # # # # # # # #   ],
# # # # # # # # #   "recommendations": [
# # # # # # # # #     {
# # # # # # # # #       "action": "Recommended action",
# # # # # # # # #       "priority": "Immediate / Short-term / Long-term",
# # # # # # # # #       "description": "Why this is recommended"
# # # # # # # # #     }
# # # # # # # # #   ],
# # # # # # # # #   "severity": "Low / Medium / High / Critical",
# # # # # # # # #   "summary": "A comprehensive 3-5 sentence summary of the legal situation",
# # # # # # # # #   "disclaimer": "This analysis is for informational purposes only and does not constitute legal advice. Please consult a qualified attorney."
# # # # # # # # # }

# # # # # # # # # Be thorough, cite specific laws, sections, and provide realistic penalties. If the jurisdiction is India, cite Indian Penal Code, specific Acts, etc. Always include the disclaimer."""


# # # # # # # # # @app.get("/")
# # # # # # # # # async def serve_frontend():
# # # # # # # # #     return FileResponse("static/index.html")


# # # # # # # # # @app.post("/analyze", response_model=dict)
# # # # # # # # # async def analyze_scenario(request: ScenarioRequest):
# # # # # # # # #     if not request.scenario.strip():
# # # # # # # # #         raise HTTPException(status_code=400, detail="Scenario cannot be empty")
    
# # # # # # # # #     if len(request.scenario) < 20:
# # # # # # # # #         raise HTTPException(status_code=400, detail="Please provide a more detailed scenario (at least 20 characters)")

# # # # # # # # #     try:
# # # # # # # # #         client = Mistral(api_key=request.api_key)
        
# # # # # # # # #         user_message = f"""Jurisdiction: {request.jurisdiction}

# # # # # # # # # Legal Scenario:
# # # # # # # # # {request.scenario}

# # # # # # # # # Analyze this scenario and identify all applicable laws, consequences, and recommendations."""

# # # # # # # # #         response = client.chat.complete(
# # # # # # # # #             model="mistral-large-latest",
# # # # # # # # #             messages=[
# # # # # # # # #                 {"role": "system", "content": SYSTEM_PROMPT},
# # # # # # # # #                 {"role": "user", "content": user_message}
# # # # # # # # #             ],
# # # # # # # # #             temperature=0.2,
# # # # # # # # #             max_tokens=4000,
# # # # # # # # #         )

# # # # # # # # #         content = response.choices[0].message.content.strip()
        
# # # # # # # # #         # Clean up markdown code blocks if present
# # # # # # # # #         if content.startswith("```"):
# # # # # # # # #             content = content.split("```")[1]
# # # # # # # # #             if content.startswith("json"):
# # # # # # # # #                 content = content[4:]
# # # # # # # # #         if content.endswith("```"):
# # # # # # # # #             content = content[:-3]
        
# # # # # # # # #         import json
# # # # # # # # #         analysis = json.loads(content.strip())
# # # # # # # # #         return analysis

# # # # # # # # #     except json.JSONDecodeError:
# # # # # # # # #         raise HTTPException(status_code=500, detail="Failed to parse legal analysis. Please try again.")
# # # # # # # # #     except Exception as e:
# # # # # # # # #         error_msg = str(e)
# # # # # # # # #         if "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
# # # # # # # # #             raise HTTPException(status_code=401, detail="Invalid Mistral API key. Please check your key.")
# # # # # # # # #         elif "429" in error_msg:
# # # # # # # # #             raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait before trying again.")
# # # # # # # # #         else:
# # # # # # # # #             raise HTTPException(status_code=500, detail=f"Analysis failed: {error_msg}")


# # # # # # # # # @app.get("/health")
# # # # # # # # # async def health_check():
# # # # # # # # #     return {"status": "healthy", "service": "LexAI Legal Analysis API", "version": "1.0.0"}


# # # # # # # # # @app.get("/jurisdictions")
# # # # # # # # # async def get_jurisdictions():
# # # # # # # # #     return {
# # # # # # # # #         "jurisdictions": [
# # # # # # # # #             "India", "United States", "United Kingdom", "Australia",
# # # # # # # # #             "Canada", "European Union", "Singapore", "UAE"
# # # # # # # # #         ]
# # # # # # # # #     }


# # # # # # # # # if __name__ == "__main__":
# # # # # # # # #     import uvicorn
# # # # # # # # #     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


# # # # # # # # import os
# # # # # # # # import json
# # # # # # # # import logging
# # # # # # # # import time
# # # # # # # # from contextlib import asynccontextmanager
# # # # # # # # from typing import Optional

# # # # # # # # from fastapi import FastAPI, HTTPException, Request
# # # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # # from fastapi.staticfiles import StaticFiles
# # # # # # # # from fastapi.responses import FileResponse, JSONResponse
# # # # # # # # from pydantic import BaseModel, field_validator
# # # # # # # # from dotenv import load_dotenv

# # # # # # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # # # # # load_dotenv()

# # # # # # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # # # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # # # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # # # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # # # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # # # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # # # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # # # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # # # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "false").lower() == "true"
# # # # # # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # # # # # logging.basicConfig(
# # # # # # # #     level=logging.INFO,
# # # # # # # #     format="%(asctime)s  %(levelname)-8s  %(message)s",
# # # # # # # #     datefmt="%H:%M:%S",
# # # # # # # # )
# # # # # # # # log = logging.getLogger("lexai")

# # # # # # # # # ── Mistral client import (handles v1 and v2 SDK layouts) ────────────────────
# # # # # # # # try:
# # # # # # # #     from mistralai import Mistral          # mistralai >= 1.x
# # # # # # # #     log.info("Using mistralai >= 1.x import path")
# # # # # # # # except ImportError:
# # # # # # # #     try:
# # # # # # # #         from mistralai.client import Mistral  # mistralai 2.x alternate path
# # # # # # # #         log.info("Using mistralai.client import path")
# # # # # # # #     except ImportError:
# # # # # # # #         from mistralai.client import MistralClient as Mistral  # mistralai 0.x
# # # # # # # #         log.info("Using legacy MistralClient import")


# # # # # # # # # ── Lifespan: startup / shutdown messages ────────────────────────────────────
# # # # # # # # @asynccontextmanager
# # # # # # # # async def lifespan(app: FastAPI):
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     log.info("  LexAI Legal Intelligence API  v1.0.0")
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     log.info(f"  Model      : {MISTRAL_MODEL}")
# # # # # # # #     log.info(f"  Server key : {'✓ configured' if MISTRAL_API_KEY else '✗ not set (user must supply)'}")
# # # # # # # #     log.info(f"  User key   : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # # # # # #     log.info(f"  Jurisdiction: {DEFAULT_JURISDICTION}")
# # # # # # # #     log.info(f"  Docs       : http://{HOST}:{PORT}/docs")
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     yield
# # # # # # # #     log.info("LexAI shutting down.")


# # # # # # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # # # # # app = FastAPI(
# # # # # # # #     title="LexAI — Legal Intelligence API",
# # # # # # # #     description=(
# # # # # # # #         "AI-powered legal scenario analysis using Mistral.\n\n"
# # # # # # # #         "Submit a scenario and receive applicable laws, consequences, "
# # # # # # # #         "severity level, and recommended actions."
# # # # # # # #     ),
# # # # # # # #     version="1.0.0",
# # # # # # # #     lifespan=lifespan,
# # # # # # # #     docs_url="/docs",
# # # # # # # #     redoc_url="/redoc",
# # # # # # # # )

# # # # # # # # app.add_middleware(
# # # # # # # #     CORSMiddleware,
# # # # # # # #     allow_origins=["*"],
# # # # # # # #     allow_credentials=True,
# # # # # # # #     allow_methods=["*"],
# # # # # # # #     allow_headers=["*"],
# # # # # # # # )

# # # # # # # # app.mount("/static", StaticFiles(directory="static"), name="static")


# # # # # # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # # # # # VALID_JURISDICTIONS = [
# # # # # # # #     "India", "United States", "United Kingdom",
# # # # # # # #     "Australia", "Canada", "European Union", "Singapore", "UAE",
# # # # # # # # ]

# # # # # # # # class ScenarioRequest(BaseModel):
# # # # # # # #     scenario: str
# # # # # # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # # # # # #     api_key: str = ""          # only used when ALLOW_USER_API_KEY=true

# # # # # # # #     @field_validator("scenario")
# # # # # # # #     @classmethod
# # # # # # # #     def scenario_not_empty(cls, v: str) -> str:
# # # # # # # #         v = v.strip()
# # # # # # # #         if not v:
# # # # # # # #             raise ValueError("Scenario cannot be empty.")
# # # # # # # #         if len(v) < 20:
# # # # # # # #             raise ValueError("Scenario is too short — please provide at least 20 characters.")
# # # # # # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # # # # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
# # # # # # # #         return v

# # # # # # # #     @field_validator("jurisdiction")
# # # # # # # #     @classmethod
# # # # # # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # # # # # #         if v not in VALID_JURISDICTIONS:
# # # # # # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # # # # # #         return v


# # # # # # # # # ── System prompt ─────────────────────────────────────────────────────────────
# # # # # # # # SYSTEM_PROMPT = """You are LexAI, an expert legal analyst with deep knowledge of laws across multiple jurisdictions.

# # # # # # # # When given a legal scenario, analyze it thoroughly and respond ONLY with a valid JSON object using this exact structure:

# # # # # # # # {
# # # # # # # #   "applicable_laws": [
# # # # # # # #     {
# # # # # # # #       "name": "Full name of the Act / Code / Regulation",
# # # # # # # #       "section": "Specific section, article, or clause number",
# # # # # # # #       "description": "What this law covers and exactly why it applies to this scenario",
# # # # # # # #       "jurisdiction": "Country or state where this law is in force"
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "consequences": [
# # # # # # # #     {
# # # # # # # #       "type": "Criminal | Civil | Administrative | Financial",
# # # # # # # #       "description": "Detailed description of this consequence and how it arises",
# # # # # # # #       "severity": "Minor | Moderate | Severe | Critical",
# # # # # # # #       "penalty": "Specific penalty: fine amount, imprisonment term, disqualification, etc."
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "recommendations": [
# # # # # # # #     {
# # # # # # # #       "action": "Concise name of the recommended action",
# # # # # # # #       "priority": "Immediate | Short-term | Long-term",
# # # # # # # #       "description": "Why this action is important and what outcome it achieves"
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "severity": "Low | Medium | High | Critical",
# # # # # # # #   "summary": "3-5 sentence plain-language summary of the overall legal situation, key risks, and what the person should know first.",
# # # # # # # #   "disclaimer": "This analysis is for informational purposes only and does not constitute legal advice. Please consult a qualified attorney for advice specific to your situation."
# # # # # # # # }

# # # # # # # # Rules:
# # # # # # # # - Cite specific laws by their official name and section numbers (e.g. IPC Section 420, IT Act 2000 Section 66C).
# # # # # # # # - Include at least 2 applicable laws and at least 2 consequences when they exist.
# # # # # # # # - Severity levels for consequences: Minor = warning/small fine, Moderate = significant fine or civil liability, Severe = criminal charges or large penalty, Critical = imprisonment or major financial ruin.
# # # # # # # # - Overall severity: Low = informational/minor, Medium = civil risk, High = criminal risk, Critical = urgent/life-altering.
# # # # # # # # - Always write the disclaimer exactly as shown.
# # # # # # # # - Return ONLY the JSON — no markdown fences, no preamble, no explanation outside the JSON."""


# # # # # # # # # ── Helpers ───────────────────────────────────────────────────────────────────
# # # # # # # # def resolve_api_key(user_key: str) -> str:
# # # # # # # #     """Return the API key to use, or raise 400/401 if none available."""
# # # # # # # #     if MISTRAL_API_KEY:
# # # # # # # #         # Server key takes priority; user key allowed only if flag is set
# # # # # # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # # # # # #             log.info("Using user-supplied API key (ALLOW_USER_API_KEY=true)")
# # # # # # # #             return user_key.strip()
# # # # # # # #         return MISTRAL_API_KEY
# # # # # # # #     # No server key — require user to supply one
# # # # # # # #     if not user_key.strip():
# # # # # # # #         raise HTTPException(
# # # # # # # #             status_code=400,
# # # # # # # #             detail=(
# # # # # # # #                 "No API key configured on the server. "
# # # # # # # #                 "Set MISTRAL_API_KEY in .env, or pass api_key in your request."
# # # # # # # #             ),
# # # # # # # #         )
# # # # # # # #     return user_key.strip()


# # # # # # # # def clean_json(raw: str) -> str:
# # # # # # # #     """Remove markdown code fences that Mistral sometimes adds."""
# # # # # # # #     text = raw.strip()
# # # # # # # #     if text.startswith("```"):
# # # # # # # #         # Split on ``` and take the inner block
# # # # # # # #         parts = text.split("```")
# # # # # # # #         text = parts[1] if len(parts) >= 2 else text
# # # # # # # #         if text.lower().startswith("json"):
# # # # # # # #             text = text[4:]
# # # # # # # #     if text.endswith("```"):
# # # # # # # #         text = text[:-3]
# # # # # # # #     return text.strip()


# # # # # # # # def call_mistral(api_key: str, user_message: str) -> dict:
# # # # # # # #     """Call Mistral and return parsed JSON dict."""
# # # # # # # #     client = Mistral(api_key=api_key)
# # # # # # # #     response = client.chat.complete(
# # # # # # # #         model=MISTRAL_MODEL,
# # # # # # # #         messages=[
# # # # # # # #             {"role": "system", "content": SYSTEM_PROMPT},
# # # # # # # #             {"role": "user",   "content": user_message},
# # # # # # # #         ],
# # # # # # # #         temperature=TEMPERATURE,
# # # # # # # #         max_tokens=MAX_TOKENS,
# # # # # # # #     )
# # # # # # # #     raw = response.choices[0].message.content or ""
# # # # # # # #     return json.loads(clean_json(raw))


# # # # # # # # # ── Global error handler ──────────────────────────────────────────────────────
# # # # # # # # @app.exception_handler(Exception)
# # # # # # # # async def global_exception_handler(request: Request, exc: Exception):
# # # # # # # #     log.error(f"Unhandled error on {request.url}: {exc}")
# # # # # # # #     return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# # # # # # # # # ── Routes ────────────────────────────────────────────────────────────────────
# # # # # # # # @app.get("/", include_in_schema=False)
# # # # # # # # async def serve_frontend():
# # # # # # # #     return FileResponse("static/index.html")


# # # # # # # # @app.post(
# # # # # # # #     "/analyze",
# # # # # # # #     response_model=dict,
# # # # # # # #     summary="Analyse a legal scenario",
# # # # # # # #     description=(
# # # # # # # #         "Submit a plain-language description of a legal situation. "
# # # # # # # #         "Returns applicable laws, consequences with severity levels, "
# # # # # # # #         "recommended actions, and an overall risk rating."
# # # # # # # #     ),
# # # # # # # #     tags=["Analysis"],
# # # # # # # # )
# # # # # # # # async def analyze_scenario(request: ScenarioRequest):
# # # # # # # #     api_key = resolve_api_key(request.api_key)

# # # # # # # #     user_message = (
# # # # # # # #         f"Jurisdiction: {request.jurisdiction}\n\n"
# # # # # # # #         f"Legal Scenario:\n{request.scenario}\n\n"
# # # # # # # #         "Analyse this scenario thoroughly. Identify all applicable laws, "
# # # # # # # #         "consequences, and recommended actions."
# # # # # # # #     )

# # # # # # # #     start = time.perf_counter()
# # # # # # # #     log.info(f"Analysing scenario | jurisdiction={request.jurisdiction} | length={len(request.scenario)}")

# # # # # # # #     try:
# # # # # # # #         result = call_mistral(api_key, user_message)
# # # # # # # #         elapsed = time.perf_counter() - start
# # # # # # # #         laws_n  = len(result.get("applicable_laws", []))
# # # # # # # #         cons_n  = len(result.get("consequences", []))
# # # # # # # #         sev     = result.get("severity", "?")
# # # # # # # #         log.info(f"Analysis complete  | {elapsed:.1f}s | laws={laws_n} | consequences={cons_n} | severity={sev}")
# # # # # # # #         return result

# # # # # # # #     except json.JSONDecodeError as e:
# # # # # # # #         log.warning(f"JSON parse error: {e}")
# # # # # # # #         raise HTTPException(
# # # # # # # #             status_code=502,
# # # # # # # #             detail="The AI returned an unexpected response format. Please try again.",
# # # # # # # #         )
# # # # # # # #     except HTTPException:
# # # # # # # #         raise
# # # # # # # #     except Exception as e:
# # # # # # # #         msg = str(e)
# # # # # # # #         log.error(f"Mistral API error: {msg}")
# # # # # # # #         if any(k in msg for k in ("401", "Unauthorized", "unauthorized", "authentication")):
# # # # # # # #             raise HTTPException(status_code=401, detail="Invalid Mistral API key. Please verify your key.")
# # # # # # # #         if "429" in msg or "rate" in msg.lower():
# # # # # # # #             raise HTTPException(status_code=429, detail="Mistral rate limit reached. Please wait a moment and try again.")
# # # # # # # #         if "timeout" in msg.lower() or "timed out" in msg.lower():
# # # # # # # #             raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
# # # # # # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {msg}")


# # # # # # # # @app.get(
# # # # # # # #     "/health",
# # # # # # # #     summary="Health check",
# # # # # # # #     tags=["System"],
# # # # # # # # )
# # # # # # # # async def health_check():
# # # # # # # #     return {
# # # # # # # #         "status": "healthy",
# # # # # # # #         "service": "LexAI Legal Intelligence API",
# # # # # # # #         "version": "1.0.0",
# # # # # # # #         "model": MISTRAL_MODEL,
# # # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # # #         "allow_user_key": ALLOW_USER_API_KEY,
# # # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # # #     }


# # # # # # # # @app.get(
# # # # # # # #     "/config",
# # # # # # # #     summary="Frontend configuration",
# # # # # # # #     description="Public-safe config used by the frontend to decide which UI elements to show.",
# # # # # # # #     tags=["System"],
# # # # # # # # )
# # # # # # # # async def get_config():
# # # # # # # #     return {
# # # # # # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # # #         "allow_user_api_key": ALLOW_USER_API_KEY,
# # # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # # #     }


# # # # # # # # @app.get(
# # # # # # # #     "/jurisdictions",
# # # # # # # #     summary="List supported jurisdictions",
# # # # # # # #     tags=["System"],
# # # # # # # # )
# # # # # # # # async def get_jurisdictions():
# # # # # # # #     return {"jurisdictions": VALID_JURISDICTIONS}


# # # # # # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     import uvicorn
# # # # # # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# # # # # # # # import os
# # # # # # # # import json
# # # # # # # # import logging
# # # # # # # # import time
# # # # # # # # from contextlib import asynccontextmanager
# # # # # # # # from typing import Optional

# # # # # # # # from fastapi import FastAPI, HTTPException, Request
# # # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # # from fastapi.staticfiles import StaticFiles
# # # # # # # # from fastapi.responses import FileResponse, JSONResponse
# # # # # # # # from pydantic import BaseModel, field_validator
# # # # # # # # from dotenv import load_dotenv

# # # # # # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # # # # # load_dotenv()

# # # # # # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # # # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # # # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # # # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # # # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # # # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # # # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # # # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # # # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# # # # # # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # # # # # logging.basicConfig(
# # # # # # # #     level=logging.INFO,
# # # # # # # #     format="%(asctime)s  %(levelname)-8s  %(message)s",
# # # # # # # #     datefmt="%H:%M:%S",
# # # # # # # # )
# # # # # # # # log = logging.getLogger("lexai")

# # # # # # # # # ── Mistral client import ─────────────────────────────────────────────────────
# # # # # # # # try:
# # # # # # # #     from mistralai import Mistral
# # # # # # # #     log.info("Using mistralai >= 1.x import path")
# # # # # # # # except ImportError:
# # # # # # # #     try:
# # # # # # # #         from mistralai.client import Mistral
# # # # # # # #         log.info("Using mistralai.client import path")
# # # # # # # #     except ImportError:
# # # # # # # #         from mistralai.client import MistralClient as Mistral
# # # # # # # #         log.info("Using legacy MistralClient import")


# # # # # # # # # ── Lifespan ──────────────────────────────────────────────────────────────────
# # # # # # # # @asynccontextmanager
# # # # # # # # async def lifespan(app: FastAPI):
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     log.info("  LexAI Legal Intelligence API  v1.0.0")
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     log.info(f"  Model       : {MISTRAL_MODEL}")
# # # # # # # #     log.info(f"  Server key  : {'✓ configured' if MISTRAL_API_KEY else '✗ not set (user must supply)'}")
# # # # # # # #     log.info(f"  User key    : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # # # # # #     log.info(f"  Jurisdiction: {DEFAULT_JURISDICTION}")
# # # # # # # #     log.info(f"  UI + API    : http://{HOST}:{PORT}/")
# # # # # # # #     log.info(f"  API Docs    : http://{HOST}:{PORT}/docs")
# # # # # # # #     log.info("━" * 50)
# # # # # # # #     yield
# # # # # # # #     log.info("LexAI shutting down.")


# # # # # # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # # # # # app = FastAPI(
# # # # # # # #     title="LexAI — Legal Intelligence API",
# # # # # # # #     description=(
# # # # # # # #         "AI-powered legal scenario analysis using Mistral.\n\n"
# # # # # # # #         "Submit a scenario and receive applicable laws, consequences, "
# # # # # # # #         "severity level, and recommended actions."
# # # # # # # #     ),
# # # # # # # #     version="1.0.0",
# # # # # # # #     lifespan=lifespan,
# # # # # # # #     docs_url="/docs",
# # # # # # # #     redoc_url="/redoc",
# # # # # # # # )

# # # # # # # # app.add_middleware(
# # # # # # # #     CORSMiddleware,
# # # # # # # #     allow_origins=["*"],
# # # # # # # #     allow_credentials=True,
# # # # # # # #     allow_methods=["*"],
# # # # # # # #     allow_headers=["*"],
# # # # # # # # )


# # # # # # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # # # # # VALID_JURISDICTIONS = [
# # # # # # # #     "India", "United States", "United Kingdom",
# # # # # # # #     "Australia", "Canada", "European Union", "Singapore", "UAE",
# # # # # # # # ]

# # # # # # # # class ScenarioRequest(BaseModel):
# # # # # # # #     scenario: str
# # # # # # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # # # # # #     api_key: str = ""

# # # # # # # #     @field_validator("scenario")
# # # # # # # #     @classmethod
# # # # # # # #     def scenario_not_empty(cls, v: str) -> str:
# # # # # # # #         v = v.strip()
# # # # # # # #         if not v:
# # # # # # # #             raise ValueError("Scenario cannot be empty.")
# # # # # # # #         if len(v) < 20:
# # # # # # # #             raise ValueError("Scenario is too short — please provide at least 20 characters.")
# # # # # # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # # # # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
# # # # # # # #         return v

# # # # # # # #     @field_validator("jurisdiction")
# # # # # # # #     @classmethod
# # # # # # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # # # # # #         if v not in VALID_JURISDICTIONS:
# # # # # # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # # # # # #         return v


# # # # # # # # # ── System prompt ─────────────────────────────────────────────────────────────
# # # # # # # # SYSTEM_PROMPT = """You are LexAI, an expert legal analyst with deep knowledge of laws across multiple jurisdictions.

# # # # # # # # When given a legal scenario, analyze it thoroughly and respond ONLY with a valid JSON object using this exact structure:

# # # # # # # # {
# # # # # # # #   "applicable_laws": [
# # # # # # # #     {
# # # # # # # #       "name": "Full name of the Act / Code / Regulation",
# # # # # # # #       "section": "Specific section, article, or clause number",
# # # # # # # #       "description": "What this law covers and exactly why it applies to this scenario",
# # # # # # # #       "jurisdiction": "Country or state where this law is in force"
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "consequences": [
# # # # # # # #     {
# # # # # # # #       "type": "Criminal | Civil | Administrative | Financial",
# # # # # # # #       "description": "Detailed description of this consequence and how it arises",
# # # # # # # #       "severity": "Minor | Moderate | Severe | Critical",
# # # # # # # #       "penalty": "Specific penalty: fine amount, imprisonment term, disqualification, etc."
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "recommendations": [
# # # # # # # #     {
# # # # # # # #       "action": "Concise name of the recommended action",
# # # # # # # #       "priority": "Immediate | Short-term | Long-term",
# # # # # # # #       "description": "Why this action is important and what outcome it achieves"
# # # # # # # #     }
# # # # # # # #   ],
# # # # # # # #   "severity": "Low | Medium | High | Critical",
# # # # # # # #   "summary": "3-5 sentence plain-language summary of the overall legal situation, key risks, and what the person should know first.",
# # # # # # # #   "disclaimer": "This analysis is for informational purposes only and does not constitute legal advice. Please consult a qualified attorney for advice specific to your situation."
# # # # # # # # }

# # # # # # # # Rules:
# # # # # # # # - Cite specific laws by their official name and section numbers (e.g. IPC Section 420, IT Act 2000 Section 66C).
# # # # # # # # - Include at least 2 applicable laws and at least 2 consequences when they exist.
# # # # # # # # - Severity levels for consequences: Minor = warning/small fine, Moderate = significant fine or civil liability, Severe = criminal charges or large penalty, Critical = imprisonment or major financial ruin.
# # # # # # # # - Overall severity: Low = informational/minor, Medium = civil risk, High = criminal risk, Critical = urgent/life-altering.
# # # # # # # # - Always write the disclaimer exactly as shown.
# # # # # # # # - Return ONLY the JSON — no markdown fences, no preamble, no explanation outside the JSON."""


# # # # # # # # # ── Helpers ───────────────────────────────────────────────────────────────────
# # # # # # # # def resolve_api_key(user_key: str) -> str:
# # # # # # # #     if MISTRAL_API_KEY:
# # # # # # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # # # # # #             log.info("Using user-supplied API key")
# # # # # # # #             return user_key.strip()
# # # # # # # #         return MISTRAL_API_KEY
# # # # # # # #     if not user_key.strip():
# # # # # # # #         raise HTTPException(
# # # # # # # #             status_code=400,
# # # # # # # #             detail=(
# # # # # # # #                 "No API key configured on the server. "
# # # # # # # #                 "Set MISTRAL_API_KEY in .env, or pass api_key in your request."
# # # # # # # #             ),
# # # # # # # #         )
# # # # # # # #     return user_key.strip()


# # # # # # # # def clean_json(raw: str) -> str:
# # # # # # # #     text = raw.strip()
# # # # # # # #     if text.startswith("```"):
# # # # # # # #         parts = text.split("```")
# # # # # # # #         text = parts[1] if len(parts) >= 2 else text
# # # # # # # #         if text.lower().startswith("json"):
# # # # # # # #             text = text[4:]
# # # # # # # #     if text.endswith("```"):
# # # # # # # #         text = text[:-3]
# # # # # # # #     return text.strip()


# # # # # # # # def call_mistral(api_key: str, user_message: str) -> dict:
# # # # # # # #     client = Mistral(api_key=api_key)
# # # # # # # #     response = client.chat.complete(
# # # # # # # #         model=MISTRAL_MODEL,
# # # # # # # #         messages=[
# # # # # # # #             {"role": "system", "content": SYSTEM_PROMPT},
# # # # # # # #             {"role": "user",   "content": user_message},
# # # # # # # #         ],
# # # # # # # #         temperature=TEMPERATURE,
# # # # # # # #         max_tokens=MAX_TOKENS,
# # # # # # # #     )
# # # # # # # #     raw = response.choices[0].message.content or ""
# # # # # # # #     return json.loads(clean_json(raw))


# # # # # # # # # ── Global error handler ──────────────────────────────────────────────────────
# # # # # # # # @app.exception_handler(Exception)
# # # # # # # # async def global_exception_handler(request: Request, exc: Exception):
# # # # # # # #     log.error(f"Unhandled error on {request.url}: {exc}")
# # # # # # # #     return JSONResponse(status_code=500, content={"detail": "Internal server error."})


# # # # # # # # # ── API Routes ────────────────────────────────────────────────────────────────
# # # # # # # # @app.post(
# # # # # # # #     "/analyze",
# # # # # # # #     response_model=dict,
# # # # # # # #     summary="Analyse a legal scenario",
# # # # # # # #     tags=["Analysis"],
# # # # # # # # )
# # # # # # # # async def analyze_scenario(request: ScenarioRequest):
# # # # # # # #     api_key = resolve_api_key(request.api_key)

# # # # # # # #     user_message = (
# # # # # # # #         f"Jurisdiction: {request.jurisdiction}\n\n"
# # # # # # # #         f"Legal Scenario:\n{request.scenario}\n\n"
# # # # # # # #         "Analyse this scenario thoroughly. Identify all applicable laws, "
# # # # # # # #         "consequences, and recommended actions."
# # # # # # # #     )

# # # # # # # #     start = time.perf_counter()
# # # # # # # #     log.info(f"Analysing | jurisdiction={request.jurisdiction} | length={len(request.scenario)}")

# # # # # # # #     try:
# # # # # # # #         result = call_mistral(api_key, user_message)
# # # # # # # #         elapsed = time.perf_counter() - start
# # # # # # # #         log.info(
# # # # # # # #             f"Done | {elapsed:.1f}s | laws={len(result.get('applicable_laws', []))} "
# # # # # # # #             f"| consequences={len(result.get('consequences', []))} "
# # # # # # # #             f"| severity={result.get('severity', '?')}"
# # # # # # # #         )
# # # # # # # #         return result

# # # # # # # #     except json.JSONDecodeError as e:
# # # # # # # #         log.warning(f"JSON parse error: {e}")
# # # # # # # #         raise HTTPException(status_code=502, detail="The AI returned an unexpected response format. Please try again.")
# # # # # # # #     except HTTPException:
# # # # # # # #         raise
# # # # # # # #     except Exception as e:
# # # # # # # #         msg = str(e)
# # # # # # # #         log.error(f"Mistral API error: {msg}")
# # # # # # # #         if any(k in msg for k in ("401", "Unauthorized", "unauthorized", "authentication")):
# # # # # # # #             raise HTTPException(status_code=401, detail="Invalid Mistral API key.")
# # # # # # # #         if "429" in msg or "rate" in msg.lower():
# # # # # # # #             raise HTTPException(status_code=429, detail="Rate limit reached. Please wait a moment.")
# # # # # # # #         if "timeout" in msg.lower() or "timed out" in msg.lower():
# # # # # # # #             raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
# # # # # # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {msg}")


# # # # # # # # @app.get("/health", summary="Health check", tags=["System"])
# # # # # # # # async def health_check():
# # # # # # # #     return {
# # # # # # # #         "status": "healthy",
# # # # # # # #         "service": "LexAI Legal Intelligence API",
# # # # # # # #         "version": "1.0.0",
# # # # # # # #         "model": MISTRAL_MODEL,
# # # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # # #         "allow_user_key": ALLOW_USER_API_KEY,
# # # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # # #     }


# # # # # # # # @app.get("/config", summary="Frontend configuration", tags=["System"])
# # # # # # # # async def get_config():
# # # # # # # #     return {
# # # # # # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # # #         "allow_user_api_key": ALLOW_USER_API_KEY,
# # # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # # #         "valid_jurisdictions": VALID_JURISDICTIONS,
# # # # # # # #     }


# # # # # # # # @app.get("/jurisdictions", summary="List supported jurisdictions", tags=["System"])
# # # # # # # # async def get_jurisdictions():
# # # # # # # #     return {"jurisdictions": VALID_JURISDICTIONS}


# # # # # # # # # ── Static frontend (must be LAST so API routes take priority) ────────────────
# # # # # # # # # Mount static assets (JS, CSS, images) under /assets
# # # # # # # # # The catch-all serves index.html for all unmatched routes (SPA routing)
# # # # # # # # import os as _os

# # # # # # # # _STATIC_DIR = _os.path.join(_os.path.dirname(__file__), "static")

# # # # # # # # if _os.path.isdir(_STATIC_DIR):
# # # # # # # #     app.mount("/assets", StaticFiles(directory=_os.path.join(_STATIC_DIR, "assets")), name="assets")

# # # # # # # #     @app.get("/{full_path:path}", include_in_schema=False)
# # # # # # # #     async def serve_spa(full_path: str):
# # # # # # # #         index = _os.path.join(_STATIC_DIR, "index.html")
# # # # # # # #         return FileResponse(index)
# # # # # # # # else:
# # # # # # # #     @app.get("/", include_in_schema=False)
# # # # # # # #     async def root():
# # # # # # # #         return {"message": "LexAI API is running. Place your built frontend in ./static/"}


# # # # # # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # # # # # if __name__ == "__main__":
# # # # # # # #     import uvicorn
# # # # # # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)


# # # # # # # import os
# # # # # # # import json
# # # # # # # import logging
# # # # # # # import time
# # # # # # # import asyncio
# # # # # # # from contextlib import asynccontextmanager
# # # # # # # from typing import Optional, List, Dict, Any
# # # # # # # from functools import wraps
# # # # # # # from enum import Enum
# # # # # # # from datetime import datetime

# # # # # # # from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# # # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # # from fastapi.staticfiles import StaticFiles
# # # # # # # from fastapi.responses import FileResponse, JSONResponse
# # # # # # # from fastapi.encoders import jsonable_encoder
# # # # # # # from pydantic import BaseModel, field_validator, Field
# # # # # # # from dotenv import load_dotenv
# # # # # # # from tenacity import (
# # # # # # #     retry, stop_after_attempt, wait_exponential, 
# # # # # # #     retry_if_exception_type, before_sleep_log
# # # # # # # )
# # # # # # # from cachetools import TTLCache
# # # # # # # import re

# # # # # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # # # # load_dotenv()

# # # # # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# # # # # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # # # # New configuration options
# # # # # # # CACHE_TTL            = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
# # # # # # # MAX_RETRIES          = int(os.getenv("MAX_RETRIES", "3"))
# # # # # # # RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# # # # # # # ENABLE_CACHE         = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# # # # # # # FILTER_PROFANITY     = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# # # # # # # REDACT_PII           = os.getenv("REDACT_PII", "true").lower() == "true"
# # # # # # # VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")  # low, medium, high

# # # # # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # # # # logging.basicConfig(
# # # # # # #     level=logging.INFO,
# # # # # # #     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
# # # # # # #     datefmt="%H:%M:%S",
# # # # # # # )
# # # # # # # log = logging.getLogger("lexai")

# # # # # # # # ── Mistral client import ─────────────────────────────────────────────────────
# # # # # # # try:
# # # # # # #     from mistralai import Mistral
# # # # # # #     log.info("Using mistralai >= 1.x import path")
# # # # # # # except ImportError:
# # # # # # #     try:
# # # # # # #         from mistralai.client import Mistral
# # # # # # #         log.info("Using mistralai.client import path")
# # # # # # #     except ImportError:
# # # # # # #         from mistralai.client import MistralClient as Mistral
# # # # # # #         log.info("Using legacy MistralClient import")

# # # # # # # # ── 2023 Indian Criminal Law Framework ────────────────────────────────────────
# # # # # # # class IndianLaw2023:
# # # # # # #     """Reference data for 2023 Indian Criminal Laws"""
    
# # # # # # #     # New Criminal Codes (effective July 1, 2024)
# # # # # # #     BNS = "Bharatiya Nyaya Sanhita, 2023"  # Replaces IPC
# # # # # # #     BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"  # Replaces CrPC
# # # # # # #     BSA = "Bharatiya Sakshya Adhiniyam, 2023"  # Replaces Evidence Act
    
# # # # # # #     # Major offense categories under BNS 2023
# # # # # # #     OFFENSES = {
# # # # # # #         "offenses_against_body": {
# # # # # # #             "sections": "101-153",
# # # # # # #             "includes": ["murder", "attempt to murder", "culpable homicide", "hurt", "grievous hurt", "assault"]
# # # # # # #         },
# # # # # # #         "offenses_against_property": {
# # # # # # #             "sections": "154-215",
# # # # # # #             "includes": ["theft", "extortion", "robbery", "dacoity", "criminal misappropriation", "criminal breach of trust"]
# # # # # # #         },
# # # # # # #         "offenses_against_women_and_children": {
# # # # # # #             "sections": "67-88, 216-234",
# # # # # # #             "includes": ["rape", "sexual harassment", "eve teasing", "trafficking", "cruelty by husband"]
# # # # # # #         },
# # # # # # #         "offenses_against_state": {
# # # # # # #             "sections": "235-267",
# # # # # # #             "includes": ["sedition", "waging war", "terrorist acts", "unlawful activities"]
# # # # # # #         },
# # # # # # #         "economic_offenses": {
# # # # # # #             "sections": "268-289",
# # # # # # #             "includes": ["counterfeiting", "money laundering", "cyber crimes", "financial fraud"]
# # # # # # #         },
# # # # # # #         "cyber_crimes": {
# # # # # # #             "sections": "330-338 (BNS) + IT Act 2000",
# # # # # # #             "includes": ["identity theft", "phishing", "hacking", "data theft", "cyber stalking"]
# # # # # # #         }
# # # # # # #     }
    
# # # # # # #     # Major Acts in Indian Legal System 2023
# # # # # # #     SPECIAL_LAWS = {
# # # # # # #         "it_act": "Information Technology Act, 2000 (Amended 2008)",
# # # # # # #         "posco": "Protection of Children from Sexual Offences Act, 2012",
# # # # # # #         "nda": "Narcotic Drugs and Psychotropic Substances Act, 1985",
# # # # # # #         "prevention_of_money_laundering": "Prevention of Money Laundering Act, 2002",
# # # # # # #         "citizenship": "Citizenship Amendment Act, 2019",
# # # # # # #         "fema": "Foreign Exchange Management Act, 1999",
# # # # # # #         "arbitration": "Arbitration and Conciliation Act, 1996",
# # # # # # #         "consumer_protection": "Consumer Protection Act, 2019",
# # # # # # #         "rti": "Right to Information Act, 2005"
# # # # # # #     }
    
# # # # # # #     @classmethod
# # # # # # #     def get_offense_category(cls, scenario_text: str) -> List[str]:
# # # # # # #         """Categorize offense based on keywords"""
# # # # # # #         categories = []
# # # # # # #         scenario_lower = scenario_text.lower()
        
# # # # # # #         for category, info in cls.OFFENSES.items():
# # # # # # #             if any(keyword in scenario_lower for keyword in info["includes"]):
# # # # # # #                 categories.append(category)
        
# # # # # # #         return categories if categories else ["general_offenses"]
    
# # # # # # #     @classmethod
# # # # # # #     def get_relevant_laws(cls, categories: List[str]) -> List[Dict[str, str]]:
# # # # # # #         """Get relevant laws for identified categories"""
# # # # # # #         laws = [{"name": cls.BNS, "description": "Principal criminal code of India (replaces IPC 1860)"}]
        
# # # # # # #         for category in categories:
# # # # # # #             if "women" in category:
# # # # # # #                 laws.append({"name": cls.BNS + " Chapter V", "description": "Offenses against women and children"})
# # # # # # #             elif "property" in category:
# # # # # # #                 laws.append({"name": cls.BNS + " Chapter XVII", "description": "Offenses against property"})
# # # # # # #             elif "cyber" in category:
# # # # # # #                 laws.append({"name": cls.SPECIAL_LAWS["it_act"], "description": "Cyber crimes and electronic evidence"})
        
# # # # # # #         laws.append({"name": cls.BNSS, "description": "Criminal procedure and trial process"})
# # # # # # #         laws.append({"name": cls.BSA, "description": "Evidence admissibility and proof"})
        
# # # # # # #         return laws

# # # # # # # # ── Cache Setup ───────────────────────────────────────────────────────────────
# # # # # # # if ENABLE_CACHE:
# # # # # # #     response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
# # # # # # #     log.info(f"Response cache enabled with TTL={CACHE_TTL}s")
# # # # # # # else:
# # # # # # #     response_cache = None
# # # # # # #     log.info("Response cache disabled")

# # # # # # # # ── Rate Limiting ─────────────────────────────────────────────────────────────
# # # # # # # class RateLimiter:
# # # # # # #     def __init__(self, requests_per_minute: int):
# # # # # # #         self.requests_per_minute = requests_per_minute
# # # # # # #         self.requests: Dict[str, List[float]] = {}
    
# # # # # # #     def can_proceed(self, client_id: str = "default") -> bool:
# # # # # # #         now = time.time()
# # # # # # #         window_start = now - 60  # Last minute
        
# # # # # # #         if client_id not in self.requests:
# # # # # # #             self.requests[client_id] = []
        
# # # # # # #         # Clean old requests
# # # # # # #         self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
# # # # # # #         if len(self.requests[client_id]) >= self.requests_per_minute:
# # # # # # #             return False
        
# # # # # # #         self.requests[client_id].append(now)
# # # # # # #         return True

# # # # # # # rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# # # # # # # # ── PII Detection Patterns (Indian Context) ───────────────────────────────────
# # # # # # # PII_PATTERNS = [
# # # # # # #     (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),  # Indian mobile number
# # # # # # #     (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
# # # # # # #     (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),  # Aadhaar number
# # # # # # #     (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
# # # # # # #     (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),  # PAN Card
# # # # # # #     (re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b'), '[AADHAAR]'),  # Aadhaar with spaces
# # # # # # #     (re.compile(r'\b\d{2}[A-Z]{2}\d{5}\b'), '[DRIVING_LICENSE]'),  # Driving license
# # # # # # #     (re.compile(r'\b[A-Z]{3}[0-9]{7}\b'), '[PASSPORT]'),  # Passport number
# # # # # # # ]

# # # # # # # PROFANITY_WORDS = [
# # # # # # #     'fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 
# # # # # # #     'damn', 'piss', 'dick', 'cock', 'pussy'
# # # # # # # ]

# # # # # # # # ── Lifespan ──────────────────────────────────────────────────────────────────
# # # # # # # @asynccontextmanager
# # # # # # # async def lifespan(app: FastAPI):
# # # # # # #     log.info("━" * 70)
# # # # # # #     log.info("  LexAI Legal Intelligence API v2.0.0 - 2023 Indian Criminal Law System")
# # # # # # #     log.info("━" * 70)
# # # # # # #     log.info(f"  Model           : {MISTRAL_MODEL}")
# # # # # # #     log.info(f"  Server key      : {'✓ configured' if MISTRAL_API_KEY else '✗ not set'}")
# # # # # # #     log.info(f"  User key        : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # # # # #     log.info(f"  Jurisdiction    : {DEFAULT_JURISDICTION}")
# # # # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # # # #     log.info("  LEGAL FRAMEWORK (Effective July 1, 2024):")
# # # # # # #     log.info(f"    • {IndianLaw2023.BNS} (replaces IPC)")
# # # # # # #     log.info(f"    • {IndianLaw2023.BNSS} (replaces CrPC)")
# # # # # # #     log.info(f"    • {IndianLaw2023.BSA} (replaces Evidence Act)")
# # # # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # # # #     log.info(f"  Features        : Cache={ENABLE_CACHE} | RateLimit={RATE_LIMIT_PER_MINUTE}/min")
# # # # # # #     log.info(f"  UI + API        : http://{HOST}:{PORT}/")
# # # # # # #     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
# # # # # # #     log.info("━" * 70)
# # # # # # #     yield
# # # # # # #     log.info("LexAI shutting down.")

# # # # # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # # # # app = FastAPI(
# # # # # # #     title="LexAI — Legal Intelligence API (2023 Indian Criminal Law System)",
# # # # # # #     description=(
# # # # # # #         "AI-powered legal scenario analysis using India's new criminal codes (2023):\n"
# # # # # # #         "• Bharatiya Nyaya Sanhita (BNS) - Replaces IPC\n"
# # # # # # #         "• Bharatiya Nagarik Suraksha Sanhita (BNSS) - Replaces CrPC\n"
# # # # # # #         "• Bharatiya Sakshya Adhiniyam (BSA) - Replaces Evidence Act\n\n"
# # # # # # #         "Features: Caching, Rate Limiting, Retries, PII Redaction, Profanity Filtering"
# # # # # # #     ),
# # # # # # #     version="2.0.0",
# # # # # # #     lifespan=lifespan,
# # # # # # #     docs_url="/docs",
# # # # # # #     redoc_url="/redoc",
# # # # # # # )

# # # # # # # app.add_middleware(
# # # # # # #     CORSMiddleware,
# # # # # # #     allow_origins=["*"],
# # # # # # #     allow_credentials=True,
# # # # # # #     allow_methods=["*"],
# # # # # # #     allow_headers=["*"],
# # # # # # # )

# # # # # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # # # # VALID_JURISDICTIONS = [
# # # # # # #     "India", "United States", "United Kingdom",
# # # # # # #     "Australia", "Canada", "European Union", "Singapore", "UAE",
# # # # # # # ]

# # # # # # # # Specific Indian states with different local laws
# # # # # # # INDIAN_STATES = [
# # # # # # #     "Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh",
# # # # # # #     "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"
# # # # # # # ]

# # # # # # # class ScenarioRequest(BaseModel):
# # # # # # #     scenario: str
# # # # # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # # # # #     state: Optional[str] = None  # For India-specific state laws
# # # # # # #     api_key: str = ""
    
# # # # # # #     class Config:
# # # # # # #         json_schema_extra = {
# # # # # # #             "example": {
# # # # # # #                 "scenario": "Someone forged my signature on a property document...",
# # # # # # #                 "jurisdiction": "India",
# # # # # # #                 "state": "Maharashtra",
# # # # # # #                 "api_key": ""
# # # # # # #             }
# # # # # # #         }

# # # # # # #     @field_validator("scenario")
# # # # # # #     @classmethod
# # # # # # #     def scenario_not_empty(cls, v: str) -> str:
# # # # # # #         v = v.strip()
# # # # # # #         if not v:
# # # # # # #             raise ValueError("Scenario cannot be empty.")
# # # # # # #         if len(v) < 20:
# # # # # # #             raise ValueError("Scenario is too short — please provide at least 20 characters.")
# # # # # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # # # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        
# # # # # # #         # PII Redaction
# # # # # # #         if REDACT_PII:
# # # # # # #             v = cls.redact_pii(v)
        
# # # # # # #         # Profanity Filter
# # # # # # #         if FILTER_PROFANITY:
# # # # # # #             v = cls.filter_profanity(v)
        
# # # # # # #         return v
    
# # # # # # #     @classmethod
# # # # # # #     def redact_pii(cls, text: str) -> str:
# # # # # # #         for pattern, replacement in PII_PATTERNS:
# # # # # # #             text = pattern.sub(replacement, text)
# # # # # # #         return text
    
# # # # # # #     @classmethod
# # # # # # #     def filter_profanity(cls, text: str) -> str:
# # # # # # #         for word in PROFANITY_WORDS:
# # # # # # #             pattern = re.compile(re.escape(word), re.IGNORECASE)
# # # # # # #             text = pattern.sub('***', text)
# # # # # # #         return text

# # # # # # #     @field_validator("jurisdiction")
# # # # # # #     @classmethod
# # # # # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # # # # #         if v not in VALID_JURISDICTIONS:
# # # # # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # # # # #         return v
    
# # # # # # #     @field_validator("state")
# # # # # # #     @classmethod
# # # # # # #     def state_valid(cls, v: Optional[str], info) -> Optional[str]:
# # # # # # #         if v and info.data.get("jurisdiction") == "India":
# # # # # # #             if v not in INDIAN_STATES:
# # # # # # #                 raise ValueError(f"Invalid state. Supported states: {', '.join(INDIAN_STATES)}")
# # # # # # #         return v

# # # # # # # # FIXED: Removed underscore from field name
# # # # # # # class AnalysisResult(BaseModel):
# # # # # # #     applicable_laws: List[Dict[str, str]]
# # # # # # #     consequences: List[Dict[str, str]]
# # # # # # #     recommendations: List[Dict[str, str]]
# # # # # # #     severity: str
# # # # # # #     summary: str
# # # # # # #     disclaimer: str
# # # # # # #     metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, exclude=True)  # Fixed field name

# # # # # # # # ── Enhanced System prompt for 2023 Indian Laws ───────────────────────────────
# # # # # # # SYSTEM_PROMPT = """You are LexAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws that came into effect on July 1, 2024.

# # # # # # # CRITICAL: You MUST use ONLY the NEW 2023 laws:
# # # # # # # - Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES the Indian Penal Code (IPC)
# # # # # # # - Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES the CrPC
# # # # # # # - Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES the Indian Evidence Act

# # # # # # # REFERENCE MAPPING (Old IPC -> New BNS):
# # # # # # # - IPC 299-304 (Culpable Homicide/Murder) -> BNS 101-104
# # # # # # # - IPC 378-382 (Theft) -> BNS 154-157
# # # # # # # - IPC 383-389 (Extortion) -> BNS 158-163
# # # # # # # - IPC 390-402 (Robbery/Dacoity) -> BNS 164-171
# # # # # # # - IPC 403-409 (Criminal Misappropriation/Breach of Trust) -> BNS 172-178
# # # # # # # - IPC 415-420 (Cheating) -> BNS 179-182
# # # # # # # - IPC 499-502 (Defamation) -> BNS 263-264
# # # # # # # - IPC 121-130 (Offenses Against State) -> BNS 235-244
# # # # # # # - IPC 354 (Assault on Woman) -> BNS 74-76
# # # # # # # - IPC 375-376 (Rape) -> BNS 63-65
# # # # # # # - IPC 497 (Adultery - Decriminalized) -> Not an offense under BNS

# # # # # # # When analyzing Indian legal scenarios, follow this structure:
# # # # # # # 1. Identify the BNS section that applies (not IPC)
# # # # # # # 2. Reference BNSS for procedural aspects
# # # # # # # 3. Reference BSA for evidentiary rules
# # # # # # # 4. Note any enhanced penalties or new provisions in the 2023 laws

# # # # # # # Response Format - Return ONLY valid JSON with this exact structure:

# # # # # # # {
# # # # # # #   "applicable_laws": [
# # # # # # #     {
# # # # # # #       "name": "Full name of the Act (must use BNS/BNSS/BSA for Indian law)",
# # # # # # #       "section": "Specific section number from BNS/BNSS/BSA",
# # # # # # #       "description": "What this law covers and why it applies",
# # # # # # #       "jurisdiction": "India or specific state"
# # # # # # #     }
# # # # # # #   ],
# # # # # # #   "consequences": [
# # # # # # #     {
# # # # # # #       "type": "Criminal | Civil | Administrative | Financial",
# # # # # # #       "description": "Detailed consequences under new BNS provisions",
# # # # # # #       "severity": "Minor | Moderate | Severe | Critical",
# # # # # # #       "penalty": "Specific penalty: imprisonment term (specify years/months), fine amount, community service, etc."
# # # # # # #     }
# # # # # # #   ],
# # # # # # #   "recommendations": [
# # # # # # #     {
# # # # # # #       "action": "Concise name of recommended action",
# # # # # # #       "priority": "Immediate | Short-term | Long-term",
# # # # # # #       "description": "Specific steps including filing FIR under BNSS, gathering evidence under BSA, etc."
# # # # # # #     }
# # # # # # #   ],
# # # # # # #   "severity": "Low | Medium | High | Critical",
# # # # # # #   "summary": "3-5 sentence plain-language summary focusing on BNS provisions and their implications",
# # # # # # #   "disclaimer": "This analysis is based on the Bharatiya Nyaya Sanhita (BNS) 2023 and related codes. For legal advice specific to your situation, consult a qualified advocate."
# # # # # # # }

# # # # # # # CRITICAL RULES FOR INDIAN LAW:
# # # # # # # 1. NEVER cite IPC sections - use ONLY BNS sections
# # # # # # # 2. For procedure, cite BNSS (not CrPC)
# # # # # # # 3. For evidence, cite BSA (not Evidence Act)
# # # # # # # 4. Note that community service is a NEW punishment under BNS
# # # # # # # 5. Sedition is replaced with "acts endangering sovereignty" under BNS 235
# # # # # # # 6. Adultery is decriminalized
# # # # # # # 7. Gay sex is decriminalized (Navtej Singh Johar case)
# # # # # # # 8. Enhanced penalties for crimes against women and children
# # # # # # # 9. New offense of "mob lynching" under BNS
# # # # # # # 10. Electronic evidence has enhanced admissibility under BSA

# # # # # # # Return ONLY the JSON — no markdown fences, no preamble, no explanation outside the JSON."""

# # # # # # # # ── Helpers ───────────────────────────────────────────────────────────────────
# # # # # # # def resolve_api_key(user_key: str) -> str:
# # # # # # #     if MISTRAL_API_KEY:
# # # # # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # # # # #             log.info("Using user-supplied API key")
# # # # # # #             return user_key.strip()
# # # # # # #         return MISTRAL_API_KEY
# # # # # # #     if not user_key.strip():
# # # # # # #         raise HTTPException(
# # # # # # #             status_code=400,
# # # # # # #             detail=(
# # # # # # #                 "No API key configured on the server. "
# # # # # # #                 "Set MISTRAL_API_KEY in .env, or pass api_key in your request."
# # # # # # #             ),
# # # # # # #         )
# # # # # # #     return user_key.strip()

# # # # # # # def clean_json(raw: str) -> str:
# # # # # # #     text = raw.strip()
    
# # # # # # #     # Remove markdown code fences
# # # # # # #     if text.startswith("```"):
# # # # # # #         parts = text.split("```")
# # # # # # #         text = parts[1] if len(parts) >= 2 else text
# # # # # # #         if text.lower().startswith("json"):
# # # # # # #             text = text[4:]
# # # # # # #     if text.endswith("```"):
# # # # # # #         text = text[:-3]
    
# # # # # # #     # Remove trailing commas
# # # # # # #     text = re.sub(r',\s*}', '}', text)
# # # # # # #     text = re.sub(r',\s*]', ']', text)
    
# # # # # # #     return text.strip()

# # # # # # # def validate_and_enhance_response(data: dict, request: ScenarioRequest = None) -> dict:
# # # # # # #     """Validate and enhance response with Indian law context"""
    
# # # # # # #     # Check for IPC references and warn/convert (post-processing)
# # # # # # #     if request and request.jurisdiction == "India":
# # # # # # #         for law in data.get('applicable_laws', []):
# # # # # # #             law_name = law.get('name', '')
# # # # # # #             if 'IPC' in law_name or 'Indian Penal Code' in law_name:
# # # # # # #                 law['name'] = law['name'].replace('IPC', 'BNS').replace('Indian Penal Code', 'Bharatiya Nyaya Sanhita')
# # # # # # #                 law['description'] += " (Note: BNS 2023 replaces IPC)"
# # # # # # #                 log.warning(f"Converted IPC reference to BNS in response")
    
# # # # # # #     # Required fields validation
# # # # # # #     required_fields = ['applicable_laws', 'consequences', 'recommendations', 'severity', 'summary', 'disclaimer']
# # # # # # #     for field in required_fields:
# # # # # # #         if field not in data:
# # # # # # #             if VALIDATION_STRICTNESS == 'high':
# # # # # # #                 raise ValueError(f"Missing required field: {field}")
# # # # # # #             else:
# # # # # # #                 data[field] = [] if field in ['applicable_laws', 'consequences', 'recommendations'] else "Information not available"
    
# # # # # # #     # Validate severity levels
# # # # # # #     valid_severity = ['Low', 'Medium', 'High', 'Critical']
# # # # # # #     if data.get('severity') not in valid_severity:
# # # # # # #         data['severity'] = 'Medium'
    
# # # # # # #     # Add Indian law context note if applicable (using metadata instead of _metadata)
# # # # # # #     if request and request.jurisdiction == "India":
# # # # # # #         if 'metadata' not in data:
# # # # # # #             data['metadata'] = {}
# # # # # # #         data['metadata']['legal_framework'] = {
# # # # # # #             'criminal_code': IndianLaw2023.BNS,
# # # # # # #             'procedure_code': IndianLaw2023.BNSS,
# # # # # # #             'evidence_act': IndianLaw2023.BSA,
# # # # # # #             'effective_date': 'July 1, 2024'
# # # # # # #         }
    
# # # # # # #     return data

# # # # # # # # ── Retry decorator for Mistral calls ─────────────────────────────────────────
# # # # # # # def retry_mistral_call():
# # # # # # #     def decorator(func):
# # # # # # #         @wraps(func)
# # # # # # #         async def wrapper(*args, **kwargs):
# # # # # # #             retry_decorator = retry(
# # # # # # #                 stop=stop_after_attempt(MAX_RETRIES),
# # # # # # #                 wait=wait_exponential(multiplier=1, min=2, max=10),
# # # # # # #                 retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
# # # # # # #                 before_sleep=before_sleep_log(log, logging.WARNING),
# # # # # # #                 reraise=True
# # # # # # #             )
# # # # # # #             return await retry_decorator(func)(*args, **kwargs)
# # # # # # #         return wrapper
# # # # # # #     return decorator

# # # # # # # def get_cache_key(request: ScenarioRequest) -> str:
# # # # # # #     """Generate cache key from request parameters"""
# # # # # # #     scenario_hash = hash(request.scenario)
# # # # # # #     return f"{request.jurisdiction}:{request.state or 'none'}:{scenario_hash}"

# # # # # # # @retry_mistral_call()
# # # # # # # async def call_mistral(api_key: str, user_message: str) -> dict:
# # # # # # #     """Call Mistral API with retries and error handling"""
# # # # # # #     client = Mistral(api_key=api_key)
    
# # # # # # #     response = await asyncio.to_thread(
# # # # # # #         client.chat.complete,
# # # # # # #         model=MISTRAL_MODEL,
# # # # # # #         messages=[
# # # # # # #             {"role": "system", "content": SYSTEM_PROMPT},
# # # # # # #             {"role": "user", "content": user_message},
# # # # # # #         ],
# # # # # # #         temperature=TEMPERATURE,
# # # # # # #         max_tokens=MAX_TOKENS,
# # # # # # #     )
    
# # # # # # #     raw = response.choices[0].message.content or ""
    
# # # # # # #     # Multiple parsing attempts
# # # # # # #     try:
# # # # # # #         return json.loads(clean_json(raw))
# # # # # # #     except json.JSONDecodeError as e:
# # # # # # #         log.warning(f"First parse attempt failed: {e}")
# # # # # # #         cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
# # # # # # #         try:
# # # # # # #             return json.loads(clean_json(cleaned))
# # # # # # #         except json.JSONDecodeError:
# # # # # # #             json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
# # # # # # #             if json_match:
# # # # # # #                 try:
# # # # # # #                     return json.loads(json_match.group())
# # # # # # #                 except json.JSONDecodeError:
# # # # # # #                     pass
# # # # # # #             raise

# # # # # # # # ── Global error handler ──────────────────────────────────────────────────────
# # # # # # # @app.exception_handler(Exception)
# # # # # # # async def global_exception_handler(request: Request, exc: Exception):
# # # # # # #     log.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
# # # # # # #     return JSONResponse(status_code=500, content={"detail": "Internal server error."})

# # # # # # # # ── API Routes ────────────────────────────────────────────────────────────────
# # # # # # # @app.get("/", include_in_schema=False)
# # # # # # # async def root():
# # # # # # #     return {
# # # # # # #         "service": "LexAI Legal Intelligence API",
# # # # # # #         "version": "2.0.0",
# # # # # # #         "legal_framework": {
# # # # # # #             "india": {
# # # # # # #                 "criminal_code": IndianLaw2023.BNS,
# # # # # # #                 "procedure_code": IndianLaw2023.BNSS,
# # # # # # #                 "evidence_act": IndianLaw2023.BSA,
# # # # # # #                 "effective_from": "July 1, 2024"
# # # # # # #             }
# # # # # # #         },
# # # # # # #         "status": "operational",
# # # # # # #         "documentation": "/docs"
# # # # # # #     }

# # # # # # # @app.post(
# # # # # # #     "/analyze",
# # # # # # #     response_model=dict,
# # # # # # #     summary="Analyse a legal scenario (2023 Indian Laws)",
# # # # # # #     tags=["Analysis"],
# # # # # # # )
# # # # # # # async def analyze_scenario(
# # # # # # #     request: ScenarioRequest,
# # # # # # #     background_tasks: BackgroundTasks,
# # # # # # #     client_id: Optional[str] = None
# # # # # # # ):
# # # # # # #     """Analyze legal scenario using 2023 Indian criminal laws (BNS/BNSS/BSA)"""
    
# # # # # # #     # Rate limiting
# # # # # # #     client_identifier = client_id or request.api_key[:8] if request.api_key else "anonymous"
# # # # # # #     if not rate_limiter.can_proceed(client_identifier):
# # # # # # #         raise HTTPException(
# # # # # # #             status_code=429,
# # # # # # #             detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_PER_MINUTE} requests per minute."
# # # # # # #         )
    
# # # # # # #     api_key = resolve_api_key(request.api_key)
    
# # # # # # #     # Check cache
# # # # # # #     cache_key = get_cache_key(request)
# # # # # # #     if ENABLE_CACHE and cache_key in response_cache:
# # # # # # #         log.info(f"Cache hit for {cache_key}")
# # # # # # #         cached_response = response_cache[cache_key]
# # # # # # #         background_tasks.add_task(log.info, f"Cache hit served for {cache_key}")
# # # # # # #         return cached_response
    
# # # # # # #     # Build enhanced user message with Indian law context
# # # # # # #     user_message = f"""Jurisdiction: {request.jurisdiction}
# # # # # # # {'State: ' + request.state if request.state else ''}
# # # # # # # Legal Scenario: {request.scenario}

# # # # # # # IMPORTANT: For Indian jurisdiction, you MUST analyze using:
# # # # # # # - Bharatiya Nyaya Sanhita (BNS) 2023 (NOT IPC)
# # # # # # # - Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 (NOT CrPC)
# # # # # # # - Bharatiya Sakshya Adhiniyam (BSA) 2023 (NOT Evidence Act)

# # # # # # # Analyze this scenario thoroughly under the NEW 2023 criminal laws. Identify all applicable BNS sections, consequences under BNSS procedures, and evidentiary requirements under BSA."""
    
# # # # # # #     start = time.perf_counter()
# # # # # # #     log.info(f"Analysing | jurisdiction={request.jurisdiction} | state={request.state} | length={len(request.scenario)}")
    
# # # # # # #     try:
# # # # # # #         result = await call_mistral(api_key, user_message)
# # # # # # #         result = validate_and_enhance_response(result, request)
        
# # # # # # #         elapsed = time.perf_counter() - start
# # # # # # #         log.info(
# # # # # # #             f"Done | {elapsed:.1f}s | laws={len(result.get('applicable_laws', []))} "
# # # # # # #             f"| consequences={len(result.get('consequences', []))} "
# # # # # # #             f"| severity={result.get('severity', '?')}"
# # # # # # #         )
        
# # # # # # #         # Remove metadata before caching if it exists (to keep cache clean)
# # # # # # #         response_to_cache = result.copy()
# # # # # # #         response_to_cache.pop('metadata', None)
        
# # # # # # #         if ENABLE_CACHE:
# # # # # # #             response_cache[cache_key] = response_to_cache
# # # # # # #             log.info(f"Cached response for {cache_key}")
        
# # # # # # #         return result
    
# # # # # # #     except json.JSONDecodeError as e:
# # # # # # #         log.error(f"JSON parse error: {e}")
# # # # # # #         raise HTTPException(
# # # # # # #             status_code=502, 
# # # # # # #             detail="The AI returned an unexpected response format. Please try again."
# # # # # # #         )
# # # # # # #     except HTTPException:
# # # # # # #         raise
# # # # # # #     except Exception as e:
# # # # # # #         msg = str(e)
# # # # # # #         log.error(f"Mistral API error: {msg}")
        
# # # # # # #         if any(k in msg.lower() for k in ("401", "unauthorized", "authentication")):
# # # # # # #             raise HTTPException(status_code=401, detail="Invalid Mistral API key.")
# # # # # # #         if any(k in msg.lower() for k in ("429", "rate", "quota")):
# # # # # # #             raise HTTPException(status_code=429, detail="Rate limit or quota exceeded.")
# # # # # # #         if any(k in msg.lower() for k in ("timeout", "timed out")):
# # # # # # #             raise HTTPException(status_code=504, detail="Request timed out. Please try again.")
        
# # # # # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {msg}")

# # # # # # # @app.post("/analyze/batch", summary="Batch analyze multiple scenarios", tags=["Analysis"])
# # # # # # # async def batch_analyze(requests: List[ScenarioRequest]):
# # # # # # #     """Analyze multiple scenarios in batch (respects rate limits)"""
# # # # # # #     results = []
# # # # # # #     errors = []
    
# # # # # # #     for i, req in enumerate(requests):
# # # # # # #         try:
# # # # # # #             # Respect rate limits between requests
# # # # # # #             await asyncio.sleep(1)  # Simple delay between batch items
# # # # # # #             result = await analyze_scenario(req)
# # # # # # #             results.append({"index": i, "success": True, "data": result})
# # # # # # #         except Exception as e:
# # # # # # #             results.append({"index": i, "success": False, "error": str(e)})
# # # # # # #             errors.append(f"Request {i}: {str(e)}")
    
# # # # # # #     return {
# # # # # # #         "total": len(requests),
# # # # # # #         "successful": len([r for r in results if r.get("success")]),
# # # # # # #         "failed": len([r for r in results if not r.get("success")]),
# # # # # # #         "results": results,
# # # # # # #         "errors": errors if errors else None
# # # # # # #     }

# # # # # # # @app.get("/legal-framework/india", summary="Get Indian legal framework information", tags=["Legal Reference"])
# # # # # # # async def get_indian_legal_framework():
# # # # # # #     """Get information about India's 2023 criminal laws"""
# # # # # # #     return {
# # # # # # #         "effective_date": "July 1, 2024",
# # # # # # #         "criminal_code": {
# # # # # # #             "name": IndianLaw2023.BNS,
# # # # # # #             "replaces": "Indian Penal Code (IPC), 1860",
# # # # # # #             "sections": "565 sections (vs 511 in IPC)",
# # # # # # #             "key_changes": [
# # # # # # #                 "Community service introduced as punishment",
# # # # # # #                 "Sedition replaced with 'acts endangering sovereignty'",
# # # # # # #                 "Mob lynching specifically criminalized",
# # # # # # #                 "Enhanced penalties for crimes against women",
# # # # # # #                 "Timelines mandated for judgments",
# # # # # # #                 "Sexual intercourse with wife under 18 is rape"
# # # # # # #             ]
# # # # # # #         },
# # # # # # #         "procedure_code": {
# # # # # # #             "name": IndianLaw2023.BNSS,
# # # # # # #             "replaces": "Code of Criminal Procedure (CrPC), 1973",
# # # # # # #             "key_changes": [
# # # # # # #                 "Zero FIR mandatory",
# # # # # # #                 "Timelines for judgment delivery",
# # # # # # #                 "Video recording of searches",
# # # # # # #                 "Handcuffing regulated",
# # # # # # #                 "Trial in absentia for absconders"
# # # # # # #             ]
# # # # # # #         },
# # # # # # #         "evidence_act": {
# # # # # # #             "name": IndianLaw2023.BSA,
# # # # # # #             "replaces": "Indian Evidence Act, 1872",
# # # # # # #             "key_changes": [
# # # # # # #                 "Electronic evidence admissibility enhanced",
# # # # # # #                 "Secondary evidence rules modernized",
# # # # # # #                 "Joint trials permitted",
# # # # # # #                 "Expert testimony provisions updated"
# # # # # # #             ]
# # # # # # #         },
# # # # # # #         "offense_categories": IndianLaw2023.OFFENSES
# # # # # # #     }

# # # # # # # @app.get("/bns-sections", summary="BNS section lookup", tags=["Legal Reference"])
# # # # # # # async def lookup_bns_section(offense_type: Optional[str] = None):
# # # # # # #     """Lookup BNS sections by offense type"""
# # # # # # #     bns_mapping = {
# # # # # # #         "murder": "BNS 101-104",
# # # # # # #         "culpable_homicide": "BNS 101",
# # # # # # #         "attempt_to_murder": "BNS 105",
# # # # # # #         "theft": "BNS 154-157",
# # # # # # #         "extortion": "BNS 158-163",
# # # # # # #         "robbery": "BNS 164-167",
# # # # # # #         "dacoity": "BNS 168-171",
# # # # # # #         "criminal_breach_of_trust": "BNS 172-178",
# # # # # # #         "cheating": "BNS 179-182",
# # # # # # #         "rape": "BNS 63-65",
# # # # # # #         "sexual_harassment": "BNS 74-76",
# # # # # # #         "defamation": "BNS 263-264",
# # # # # # #         "criminal_intimidation": "BNS 260-262",
# # # # # # #         "mob_lynching": "BNS 103(2)",
# # # # # # #         "offenses_against_state": "BNS 235-244"
# # # # # # #     }
    
# # # # # # #     if offense_type and offense_type.lower() in bns_mapping:
# # # # # # #         return {"offense": offense_type, "bns_section": bns_mapping[offense_type.lower()]}
# # # # # # #     return {"bns_mapping": bns_mapping}

# # # # # # # @app.get("/health", summary="Health check", tags=["System"])
# # # # # # # async def health_check():
# # # # # # #     return {
# # # # # # #         "status": "healthy",
# # # # # # #         "service": "LexAI Legal Intelligence API",
# # # # # # #         "version": "2.0.0",
# # # # # # #         "legal_framework": "2023 Indian Criminal Laws (BNS/BNSS/BSA)",
# # # # # # #         "model": MISTRAL_MODEL,
# # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # #         "allow_user_key": ALLOW_USER_API_KEY,
# # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # #         "cache_enabled": ENABLE_CACHE,
# # # # # # #         "cache_size": len(response_cache) if response_cache else 0,
# # # # # # #         "rate_limit": RATE_LIMIT_PER_MINUTE,
# # # # # # #     }

# # # # # # # @app.get("/config", summary="Frontend configuration", tags=["System"])
# # # # # # # async def get_config():
# # # # # # #     return {
# # # # # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # # # #         "allow_user_api_key": ALLOW_USER_API_KEY,
# # # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # # #         "valid_jurisdictions": VALID_JURISDICTIONS,
# # # # # # #         "indian_states": INDIAN_STATES,
# # # # # # #         "legal_framework": {
# # # # # # #             "india_2023": {
# # # # # # #                 "bns": IndianLaw2023.BNS,
# # # # # # #                 "bnss": IndianLaw2023.BNSS,
# # # # # # #                 "bsa": IndianLaw2023.BSA
# # # # # # #             }
# # # # # # #         },
# # # # # # #         "features": {
# # # # # # #             "caching": ENABLE_CACHE,
# # # # # # #             "pii_redaction": REDACT_PII,
# # # # # # #             "profanity_filter": FILTER_PROFANITY,
# # # # # # #             "rate_limiting": RATE_LIMIT_PER_MINUTE,
# # # # # # #             "retries": MAX_RETRIES
# # # # # # #         }
# # # # # # #     }

# # # # # # # @app.get("/jurisdictions", summary="List supported jurisdictions", tags=["System"])
# # # # # # # async def get_jurisdictions():
# # # # # # #     return {
# # # # # # #         "jurisdictions": VALID_JURISDICTIONS,
# # # # # # #         "indian_states": INDIAN_STATES
# # # # # # #     }

# # # # # # # @app.delete("/cache", summary="Clear response cache", tags=["System"])
# # # # # # # async def clear_cache(admin_key: str):
# # # # # # #     """Clear the response cache (requires admin_key from env)"""
# # # # # # #     ADMIN_KEY = os.getenv("ADMIN_KEY", "")
# # # # # # #     if not ADMIN_KEY or admin_key != ADMIN_KEY:
# # # # # # #         raise HTTPException(status_code=403, detail="Invalid admin key")
    
# # # # # # #     if response_cache:
# # # # # # #         old_size = len(response_cache)
# # # # # # #         response_cache.clear()
# # # # # # #         log.info(f"Cache cleared by admin (had {old_size} entries)")
# # # # # # #         return {"message": "Cache cleared", "cleared_entries": old_size}
# # # # # # #     return {"message": "Cache not enabled"}

# # # # # # # # ── Static frontend ──────────────────────────────────────────────────────────
# # # # # # # import os as _os

# # # # # # # _STATIC_DIR = _os.path.join(_os.path.dirname(__file__), "static")

# # # # # # # if _os.path.isdir(_STATIC_DIR):
# # # # # # #     app.mount("/assets", StaticFiles(directory=_os.path.join(_STATIC_DIR, "assets")), name="assets")

# # # # # # #     @app.get("/{full_path:path}", include_in_schema=False)
# # # # # # #     async def serve_spa(full_path: str):
# # # # # # #         if full_path.startswith(("docs", "redoc", "openapi.json")):
# # # # # # #             raise HTTPException(status_code=404)
# # # # # # #         index = _os.path.join(_STATIC_DIR, "index.html")
# # # # # # #         return FileResponse(index)
# # # # # # # else:
# # # # # # #     @app.get("/", include_in_schema=False)
# # # # # # #     async def root_info():
# # # # # # #         return {"message": "LexAI API is running. Place your built frontend in ./static/"}

# # # # # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # # # # if __name__ == "__main__":
# # # # # # #     import uvicorn
# # # # # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# # # # # # import os
# # # # # # import json
# # # # # # import logging
# # # # # # import time
# # # # # # import asyncio
# # # # # # from contextlib import asynccontextmanager
# # # # # # from typing import Optional, List, Dict, Any, Tuple
# # # # # # from functools import wraps
# # # # # # from enum import Enum
# # # # # # from datetime import datetime

# # # # # # from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# # # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # # from fastapi.staticfiles import StaticFiles
# # # # # # from fastapi.responses import FileResponse, JSONResponse
# # # # # # from fastapi.encoders import jsonable_encoder
# # # # # # from pydantic import BaseModel, field_validator, Field
# # # # # # from dotenv import load_dotenv
# # # # # # from tenacity import (
# # # # # #     retry, stop_after_attempt, wait_exponential, 
# # # # # #     retry_if_exception_type, before_sleep_log
# # # # # # )
# # # # # # from cachetools import TTLCache
# # # # # # import re

# # # # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # # # load_dotenv()

# # # # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# # # # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # # # New configuration options
# # # # # # CACHE_TTL            = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
# # # # # # MAX_RETRIES          = int(os.getenv("MAX_RETRIES", "3"))
# # # # # # RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# # # # # # ENABLE_CACHE         = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# # # # # # FILTER_PROFANITY     = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# # # # # # REDACT_PII           = os.getenv("REDACT_PII", "true").lower() == "true"
# # # # # # VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")

# # # # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # # # logging.basicConfig(
# # # # # #     level=logging.INFO,
# # # # # #     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
# # # # # #     datefmt="%H:%M:%S",
# # # # # # )
# # # # # # log = logging.getLogger("lexai")

# # # # # # # ── Mistral client import ─────────────────────────────────────────────────────
# # # # # # try:
# # # # # #     from mistralai import Mistral
# # # # # #     log.info("Using mistralai >= 1.x import path")
# # # # # # except ImportError:
# # # # # #     try:
# # # # # #         from mistralai.client import Mistral
# # # # # #         log.info("Using mistralai.client import path")
# # # # # #     except ImportError:
# # # # # #         from mistralai.client import MistralClient as Mistral
# # # # # #         log.info("Using legacy MistralClient import")

# # # # # # # ── Query Classifier ──────────────────────────────────────────────────────────
# # # # # # class QueryClassifier:
# # # # # #     """Classifies whether a query is a legal scenario or general conversation"""
    
# # # # # #     # Legal keywords that indicate a legal scenario
# # # # # #     LEGAL_KEYWORDS = [
# # # # # #         # Criminal keywords
# # # # # #         'murder', 'kill', 'death', 'homicide', 'assault', 'battery', 'robbery', 
# # # # # #         'theft', 'burglary', 'dacoity', 'extortion', 'fraud', 'cheating', 
# # # # # #         'forgery', 'counterfeit', 'rape', 'sexual', 'harassment', 'stalking',
# # # # # #         'kidnap', 'abduction', 'dowry', 'domestic violence', 'cruelty',
        
# # # # # #         # Legal terms
# # # # # #         'fir', 'complaint', 'police', 'case', 'court', 'judge', 'lawyer',
# # # # # #         'advocate', 'legal', 'violation', 'offense', 'crime', 'criminal',
# # # # # #         'sentence', 'punishment', 'fine', 'imprisonment', 'arrest', 'bail',
        
# # # # # #         # Civil terms
# # # # # #         'contract', 'agreement', 'property', 'ownership', 'title', 'deed',
# # # # # #         'landlord', 'tenant', 'rent', 'eviction', 'divorce', 'maintenance',
# # # # # #         'custody', 'inheritance', 'will', 'testament', 'debt', 'loan',
        
# # # # # #         # Cyber crimes
# # # # # #         'hacking', 'phishing', 'cyber', 'online fraud', 'identity theft',
# # # # # #         'data breach', 'privacy violation', 'digital arrest',
        
# # # # # #         # Constitutional
# # # # # #         'fundamental rights', 'constitution', 'article', 'writ', 'petition',
        
# # # # # #         # Business
# # # # # #         'company', 'corporate', 'director', 'shareholder', 'insolvency',
# # # # # #         'bankruptcy', 'trademark', 'copyright', 'patent'
# # # # # #     ]
    
# # # # # #     # Greeting and casual conversation patterns (non-legal)
# # # # # #     GREETING_PATTERNS = [
# # # # # #         r'^(hi|hello|hey|greetings)[\s\!]*$',
# # # # # #         r'^good (morning|afternoon|evening)[\s\!]*$',
# # # # # #         r'^how are you[\s\?]*$',
# # # # # #         r'^what\'?s up[\s\?]*$',
# # # # # #         r'^nice to meet you',
# # # # # #         r'^i am \w+$',  # "I am Krishna" pattern
# # # # # #         r'^my name is \w+$',
# # # # # #         r'^who are you[\s\?]*$',
# # # # # #         r'^what is your name[\s\?]*$',
# # # # # #         r'^tell me about yourself',
# # # # # #         r'^thanks?[\s\!]*$',
# # # # # #         r'^thank you[\s\!]*$',
# # # # # #         r'^bye|goodbye|see you',
# # # # # #         r'^ok|okay'
# # # # # #     ]
    
# # # # # #     # Query patterns that are clearly non-legal
# # # # # #     NON_LEGAL_PATTERNS = [
# # # # # #         r'weather|temperature',
# # # # # #         r'cricket|football|sports',
# # # # # #         r'movie|song|music|film',
# # # # # #         r'recipe|cooking|food',
# # # # # #         r'joke|funny|humor',
# # # # # #         r'game|play|fun',
# # # # # #         r'love|relationship (?!law|legal)',
# # # # # #         r'^what is (ai|artificial intelligence|machine learning)',
# # # # # #         r'^how to (cook|bake|make)'
# # # # # #     ]
    
# # # # # #     @classmethod
# # # # # #     def is_legal_scenario(cls, text: str) -> Tuple[bool, str]:
# # # # # #         """
# # # # # #         Classify if text is a legal scenario.
# # # # # #         Returns: (is_legal, reason)
# # # # # #         """
# # # # # #         text_lower = text.lower().strip()
        
# # # # # #         # Check for greeting patterns first (quick filter)
# # # # # #         for pattern in cls.GREETING_PATTERNS:
# # # # # #             if re.match(pattern, text_lower, re.IGNORECASE):
# # # # # #                 return False, "greeting_or_introduction"
        
# # # # # #         # Check for non-legal patterns
# # # # # #         for pattern in cls.NON_LEGAL_PATTERNS:
# # # # # #             if re.search(pattern, text_lower, re.IGNORECASE):
# # # # # #                 return False, "non_legal_conversation"
        
# # # # # #         # For very short queries (less than 15 chars), likely not legal
# # # # # #         if len(text) < 15 and not any(kw in text_lower for kw in cls.LEGAL_KEYWORDS):
# # # # # #             return False, "query_too_short"
        
# # # # # #         # Check for legal keywords
# # # # # #         legal_keyword_count = sum(1 for kw in cls.LEGAL_KEYWORDS if kw in text_lower)
        
# # # # # #         # If at least 2 legal keywords OR 1 legal keyword with sufficient length
# # # # # #         if legal_keyword_count >= 2:
# # # # # #             return True, f"contains_legal_keywords ({legal_keyword_count} keywords)"
# # # # # #         elif legal_keyword_count == 1 and len(text) > 30:
# # # # # #             return True, "contains_legal_context"
        
# # # # # #         # Default to non-legal for casual queries
# # # # # #         return False, "no_legal_context"
    
# # # # # #     @classmethod
# # # # # #     def get_non_legal_response(cls, query: str, classification_reason: str) -> dict:
# # # # # #         """Generate appropriate response for non-legal queries"""
        
# # # # # #         responses = {
# # # # # #             "greeting_or_introduction": {
# # # # # #                 "response": f"👋 Hello! I'm LexAI, your legal intelligence assistant. I specialize in analyzing legal scenarios under the Bharatiya Nyaya Sanhita (BNS) 2023 and other Indian laws.\n\nPlease describe a legal situation or problem you'd like me to analyze (e.g., 'Someone forged my signature on a property document'), and I'll provide applicable laws, consequences, and recommendations.",
# # # # # #                 "type": "greeting"
# # # # # #             },
# # # # # #             "non_legal_conversation": {
# # # # # #                 "response": f"I'm LexAI, a legal analysis AI. I'm designed to help with legal scenarios under Indian criminal laws (BNS 2023, BNSS, BSA).\n\nI notice your query isn't about a legal issue. Could you please describe a legal situation you need help with? For example: 'Someone stole my phone and is using my UPI apps' or 'My employer hasn't paid me for 3 months'.",
# # # # # #                 "type": "clarification"
# # # # # #             },
# # # # # #             "query_too_short": {
# # # # # #                 "response": f"I need more details to provide a legal analysis. Please describe your legal situation in more detail (minimum 20 characters).\n\nFor example: 'A shopkeeper sold me expired medicine and now I'm sick'.",
# # # # # #                 "type": "insufficient_info"
# # # # # #             },
# # # # # #             "no_legal_context": {
# # # # # #                 "response": f"I'm a legal analysis assistant. I can help with:\n\n• Criminal matters (theft, fraud, assault, etc.)\n• Property disputes\n• Contract violations\n• Cyber crimes\n• Family law issues\n\nPlease share the legal problem you're facing, what happened, and which jurisdiction (state/country) it occurred in.",
# # # # # #                 "type": "guidance"
# # # # # #             }
# # # # # #         }
        
# # # # # #         response_data = responses.get(classification_reason, responses["no_legal_context"])
        
# # # # # #         # Structure response like legal analysis for consistency
# # # # # #         return {
# # # # # #             "is_legal_query": False,
# # # # # #             "classification_reason": classification_reason,
# # # # # #             "message": response_data["response"],
# # # # # #             "type": response_data["type"],
# # # # # #             "applicable_laws": [],
# # # # # #             "consequences": [{
# # # # # #                 "type": "None",
# # # # # #                 "description": "This is not a legal query requiring analysis under BNS, BNSS, or BSA.",
# # # # # #                 "severity": "None",
# # # # # #                 "penalty": "Not applicable"
# # # # # #             }],
# # # # # #             "recommendations": [{
# # # # # #                 "action": "Provide a legal scenario",
# # # # # #                 "priority": "Immediate",
# # # # # #                 "description": response_data["response"]
# # # # # #             }],
# # # # # #             "severity": "Low",
# # # # # #             "summary": response_data["response"],
# # # # # #             "disclaimer": "This is an informational response. For actual legal analysis, please provide a specific legal scenario."
# # # # # #         }

# # # # # # # ── 2023 Indian Criminal Law Framework ────────────────────────────────────────
# # # # # # class IndianLaw2023:
# # # # # #     """Reference data for 2023 Indian Criminal Laws"""
    
# # # # # #     # New Criminal Codes (effective July 1, 2024)
# # # # # #     BNS = "Bharatiya Nyaya Sanhita, 2023"
# # # # # #     BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"
# # # # # #     BSA = "Bharatiya Sakshya Adhiniyam, 2023"
    
# # # # # #     @classmethod
# # # # # #     def is_relevant_law(cls, scenario: str) -> bool:
# # # # # #         """Check if scenario might involve any legal provisions"""
# # # # # #         scenario_lower = scenario.lower()
# # # # # #         # If scenario contains any legal context, it's relevant
# # # # # #         legal_indicators = ['fir', 'police', 'case', 'court', 'legal', 'offense', 
# # # # # #                            'crime', 'criminal', 'sue', 'complaint', 'violation']
# # # # # #         return any(indicator in scenario_lower for indicator in legal_indicators)

# # # # # # # ── Cache Setup ───────────────────────────────────────────────────────────────
# # # # # # if ENABLE_CACHE:
# # # # # #     response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
# # # # # #     log.info(f"Response cache enabled with TTL={CACHE_TTL}s")
# # # # # # else:
# # # # # #     response_cache = None
# # # # # #     log.info("Response cache disabled")

# # # # # # # ── Rate Limiting ─────────────────────────────────────────────────────────────
# # # # # # class RateLimiter:
# # # # # #     def __init__(self, requests_per_minute: int):
# # # # # #         self.requests_per_minute = requests_per_minute
# # # # # #         self.requests: Dict[str, List[float]] = {}
    
# # # # # #     def can_proceed(self, client_id: str = "default") -> bool:
# # # # # #         now = time.time()
# # # # # #         window_start = now - 60
        
# # # # # #         if client_id not in self.requests:
# # # # # #             self.requests[client_id] = []
        
# # # # # #         self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
# # # # # #         if len(self.requests[client_id]) >= self.requests_per_minute:
# # # # # #             return False
        
# # # # # #         self.requests[client_id].append(now)
# # # # # #         return True

# # # # # # rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# # # # # # # ── PII Detection Patterns ───────────────────────────────────────────────────
# # # # # # PII_PATTERNS = [
# # # # # #     (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),
# # # # # #     (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
# # # # # #     (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),
# # # # # #     (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
# # # # # #     (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),
# # # # # # ]

# # # # # # PROFANITY_WORDS = ['fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 'damn', 'piss']

# # # # # # # ── Lifespan ──────────────────────────────────────────────────────────────────
# # # # # # @asynccontextmanager
# # # # # # async def lifespan(app: FastAPI):
# # # # # #     log.info("━" * 70)
# # # # # #     log.info("  LexAI Legal Intelligence API v2.0.0 - 2023 Indian Criminal Law System")
# # # # # #     log.info("━" * 70)
# # # # # #     log.info(f"  Model           : {MISTRAL_MODEL}")
# # # # # #     log.info(f"  Server key      : {'✓ configured' if MISTRAL_API_KEY else '✗ not set'}")
# # # # # #     log.info(f"  User key        : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # # # #     log.info(f"  Jurisdiction    : {DEFAULT_JURISDICTION}")
# # # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # # #     log.info("  LEGAL FRAMEWORK (Effective July 1, 2024):")
# # # # # #     log.info(f"    • {IndianLaw2023.BNS} (replaces IPC)")
# # # # # #     log.info(f"    • {IndianLaw2023.BNSS} (replaces CrPC)")
# # # # # #     log.info(f"    • {IndianLaw2023.BSA} (replaces Evidence Act)")
# # # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # # #     log.info(f"  Features        : Cache={ENABLE_CACHE} | RateLimit={RATE_LIMIT_PER_MINUTE}/min")
# # # # # #     log.info(f"  Query Classifier: Enabled (prevents hallucination)")
# # # # # #     log.info(f"  UI + API        : http://{HOST}:{PORT}/")
# # # # # #     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
# # # # # #     log.info("━" * 70)
# # # # # #     yield
# # # # # #     log.info("LexAI shutting down.")

# # # # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # # # app = FastAPI(
# # # # # #     title="LexAI — Legal Intelligence API (2023 Indian Criminal Law System)",
# # # # # #     description="AI-powered legal scenario analysis with query classification to prevent hallucination",
# # # # # #     version="2.1.0",
# # # # # #     lifespan=lifespan,
# # # # # #     docs_url="/docs",
# # # # # #     redoc_url="/redoc",
# # # # # # )

# # # # # # app.add_middleware(
# # # # # #     CORSMiddleware,
# # # # # #     allow_origins=["*"],
# # # # # #     allow_credentials=True,
# # # # # #     allow_methods=["*"],
# # # # # #     allow_headers=["*"],
# # # # # # )

# # # # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # # # VALID_JURISDICTIONS = ["India", "United States", "United Kingdom", "Australia", "Canada", "European Union", "Singapore", "UAE"]
# # # # # # INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"]

# # # # # # class ScenarioRequest(BaseModel):
# # # # # #     scenario: str
# # # # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # # # #     state: Optional[str] = None
# # # # # #     api_key: str = ""
    
# # # # # #     class Config:
# # # # # #         json_schema_extra = {
# # # # # #             "example": {
# # # # # #                 "scenario": "Someone forged my signature on a property document in Maharashtra",
# # # # # #                 "jurisdiction": "India",
# # # # # #                 "state": "Maharashtra",
# # # # # #                 "api_key": ""
# # # # # #             }
# # # # # #         }

# # # # # #     @field_validator("scenario")
# # # # # #     @classmethod
# # # # # #     def scenario_not_empty(cls, v: str) -> str:
# # # # # #         v = v.strip()
# # # # # #         if not v:
# # # # # #             raise ValueError("Scenario cannot be empty.")
        
# # # # # #         # Don't block short queries, but they'll be classified as non-legal
# # # # # #         if len(v) < 5:
# # # # # #             raise ValueError("Please provide at least 5 characters.")
        
# # # # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        
# # # # # #         if REDACT_PII:
# # # # # #             for pattern, replacement in PII_PATTERNS:
# # # # # #                 v = pattern.sub(replacement, v)
        
# # # # # #         if FILTER_PROFANITY:
# # # # # #             for word in PROFANITY_WORDS:
# # # # # #                 pattern = re.compile(re.escape(word), re.IGNORECASE)
# # # # # #                 v = pattern.sub('***', v)
        
# # # # # #         return v

# # # # # #     @field_validator("jurisdiction")
# # # # # #     @classmethod
# # # # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # # # #         if v not in VALID_JURISDICTIONS:
# # # # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # # # #         return v
    
# # # # # #     @field_validator("state")
# # # # # #     @classmethod
# # # # # #     def state_valid(cls, v: Optional[str], info) -> Optional[str]:
# # # # # #         if v and info.data.get("jurisdiction") == "India":
# # # # # #             if v not in INDIAN_STATES:
# # # # # #                 raise ValueError(f"Invalid state. Supported states: {', '.join(INDIAN_STATES)}")
# # # # # #         return v

# # # # # # class AnalysisResult(BaseModel):
# # # # # #     applicable_laws: List[Dict[str, str]]
# # # # # #     consequences: List[Dict[str, str]]
# # # # # #     recommendations: List[Dict[str, str]]
# # # # # #     severity: str
# # # # # #     summary: str
# # # # # #     disclaimer: str
# # # # # #     metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, exclude=True)

# # # # # # # ── Enhanced System Prompt for Legal Analysis Only ───────────────────────────
# # # # # # LEGAL_SYSTEM_PROMPT = """You are LexAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws.

# # # # # # IMPORTANT: Only analyze queries that describe actual legal scenarios or legal problems. If the user asks a greeting, introduces themselves, or asks non-legal questions, respond naturally without forcing legal analysis.

# # # # # # For LEGAL scenarios, you MUST use ONLY the NEW 2023 laws:
# # # # # # - Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES IPC
# # # # # # - Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES CrPC
# # # # # # - Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES Evidence Act

# # # # # # Response Format - Return ONLY valid JSON with this structure:

# # # # # # {
# # # # # #   "applicable_laws": [
# # # # # #     {
# # # # # #       "name": "Full name of the Act",
# # # # # #       "section": "Specific section number",
# # # # # #       "description": "Why this law applies",
# # # # # #       "jurisdiction": "India or specific state"
# # # # # #     }
# # # # # #   ],
# # # # # #   "consequences": [
# # # # # #     {
# # # # # #       "type": "Criminal | Civil | Administrative | Financial",
# # # # # #       "description": "Detailed consequences",
# # # # # #       "severity": "Minor | Moderate | Severe | Critical",
# # # # # #       "penalty": "Specific penalty details"
# # # # # #     }
# # # # # #   ],
# # # # # #   "recommendations": [
# # # # # #     {
# # # # # #       "action": "Recommended action",
# # # # # #       "priority": "Immediate | Short-term | Long-term",
# # # # # #       "description": "Why this action helps"
# # # # # #     }
# # # # # #   ],
# # # # # #   "severity": "Low | Medium | High | Critical",
# # # # # #   "summary": "Plain-language summary",
# # # # # #   "disclaimer": "This analysis is based on BNS 2023 and related codes."
# # # # # # }

# # # # # # CRITICAL RULES:
# # # # # # 1. NEVER analyze non-legal queries as legal cases
# # # # # # 2. For greetings/questions like "who are you", respond conversationally
# # # # # # 3. ONLY apply BNS/BNSS/BSA when actual legal issues are described
# # # # # # 4. If no crime is described, state clearly that no legal violation occurred"""

# # # # # # # ── Helper Functions ──────────────────────────────────────────────────────────
# # # # # # def resolve_api_key(user_key: str) -> str:
# # # # # #     if MISTRAL_API_KEY:
# # # # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # # # #             log.info("Using user-supplied API key")
# # # # # #             return user_key.strip()
# # # # # #         return MISTRAL_API_KEY
# # # # # #     if not user_key.strip():
# # # # # #         raise HTTPException(
# # # # # #             status_code=400,
# # # # # #             detail="No API key configured. Set MISTRAL_API_KEY in .env, or pass api_key."
# # # # # #         )
# # # # # #     return user_key.strip()

# # # # # # def clean_json(raw: str) -> str:
# # # # # #     text = raw.strip()
# # # # # #     if text.startswith("```"):
# # # # # #         parts = text.split("```")
# # # # # #         text = parts[1] if len(parts) >= 2 else text
# # # # # #         if text.lower().startswith("json"):
# # # # # #             text = text[4:]
# # # # # #     if text.endswith("```"):
# # # # # #         text = text[:-3]
# # # # # #     text = re.sub(r',\s*}', '}', text)
# # # # # #     text = re.sub(r',\s*]', ']', text)
# # # # # #     return text.strip()

# # # # # # def get_cache_key(request: ScenarioRequest) -> str:
# # # # # #     scenario_hash = hash(request.scenario)
# # # # # #     return f"{request.jurisdiction}:{request.state or 'none'}:{scenario_hash}"

# # # # # # @retry(retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
# # # # # #        stop=stop_after_attempt(MAX_RETRIES),
# # # # # #        wait=wait_exponential(multiplier=1, min=2, max=10),
# # # # # #        before_sleep=before_sleep_log(log, logging.WARNING))
# # # # # # async def call_mistral(api_key: str, user_message: str) -> dict:
# # # # # #     """Call Mistral API with retries"""
# # # # # #     client = Mistral(api_key=api_key)
    
# # # # # #     response = await asyncio.to_thread(
# # # # # #         client.chat.complete,
# # # # # #         model=MISTRAL_MODEL,
# # # # # #         messages=[
# # # # # #             {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
# # # # # #             {"role": "user", "content": user_message},
# # # # # #         ],
# # # # # #         temperature=TEMPERATURE,
# # # # # #         max_tokens=MAX_TOKENS,
# # # # # #     )
    
# # # # # #     raw = response.choices[0].message.content or ""
    
# # # # # #     try:
# # # # # #         return json.loads(clean_json(raw))
# # # # # #     except json.JSONDecodeError as e:
# # # # # #         log.warning(f"JSON parse failed: {e}")
# # # # # #         cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
# # # # # #         json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
# # # # # #         if json_match:
# # # # # #             return json.loads(json_match.group())
# # # # # #         raise

# # # # # # # ── API Routes ────────────────────────────────────────────────────────────────
# # # # # # @app.get("/", include_in_schema=False)
# # # # # # async def root():
# # # # # #     return {
# # # # # #         "service": "LexAI Legal Intelligence API",
# # # # # #         "version": "2.1.0",
# # # # # #         "features": ["Query Classification", "Anti-Hallucination", "BNS 2023"],
# # # # # #         "status": "operational",
# # # # # #         "documentation": "/docs"
# # # # # #     }

# # # # # # @app.post("/analyze", response_model=dict, summary="Analyze a legal scenario", tags=["Analysis"])
# # # # # # async def analyze_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks, client_id: Optional[str] = None):
# # # # # #     """Analyze legal scenario with automatic query classification to prevent hallucination"""
    
# # # # # #     # Rate limiting
# # # # # #     client_identifier = client_id or request.api_key[:8] if request.api_key else "anonymous"
# # # # # #     if not rate_limiter.can_proceed(client_identifier):
# # # # # #         raise HTTPException(status_code=429, detail=f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute")
    
# # # # # #     # CLASSIFY QUERY FIRST - Prevents hallucination
# # # # # #     is_legal, reason = QueryClassifier.is_legal_scenario(request.scenario)
# # # # # #     log.info(f"Query classified: is_legal={is_legal}, reason={reason}, query='{request.scenario[:50]}...'")
    
# # # # # #     # Handle non-legal queries immediately without calling AI
# # # # # #     if not is_legal:
# # # # # #         log.info(f"Returning non-legal response for: {request.scenario[:50]}")
# # # # # #         non_legal_response = QueryClassifier.get_non_legal_response(request.scenario, reason)
# # # # # #         return non_legal_response
    
# # # # # #     # For legal queries, proceed with AI analysis
# # # # # #     api_key = resolve_api_key(request.api_key)
    
# # # # # #     # Check cache
# # # # # #     cache_key = get_cache_key(request)
# # # # # #     if ENABLE_CACHE and cache_key in response_cache:
# # # # # #         log.info(f"Cache hit for legal query: {cache_key}")
# # # # # #         return response_cache[cache_key]
    
# # # # # #     # Build legal analysis prompt
# # # # # #     user_message = f"""Jurisdiction: {request.jurisdiction}
# # # # # # {'State: ' + request.state if request.state else ''}
# # # # # # Legal Scenario: {request.scenario}

# # # # # # Analyze this scenario under the NEW 2023 criminal laws. Identify applicable BNS sections, consequences, and recommendations."""
    
# # # # # #     start = time.perf_counter()
# # # # # #     log.info(f"Analyzing legal scenario | jurisdiction={request.jurisdiction} | length={len(request.scenario)}")
    
# # # # # #     try:
# # # # # #         result = await call_mistral(api_key, user_message)
        
# # # # # #         elapsed = time.perf_counter() - start
# # # # # #         log.info(f"Analysis complete | {elapsed:.1f}s | severity={result.get('severity', '?')}")
        
# # # # # #         # Add metadata to response
# # # # # #         result["metadata"] = {
# # # # # #             "query_classified": True,
# # # # # #             "is_legal_query": True,
# # # # # #             "classification_reason": reason,
# # # # # #             "analysis_timestamp": time.time()
# # # # # #         }
        
# # # # # #         # Cache response (without metadata to save space)
# # # # # #         response_to_cache = result.copy()
# # # # # #         response_to_cache.pop('metadata', None)
# # # # # #         if ENABLE_CACHE:
# # # # # #             response_cache[cache_key] = response_to_cache
        
# # # # # #         return result
    
# # # # # #     except json.JSONDecodeError as e:
# # # # # #         log.error(f"JSON parse error: {e}")
# # # # # #         raise HTTPException(status_code=502, detail="AI returned invalid response format.")
# # # # # #     except Exception as e:
# # # # # #         log.error(f"Analysis error: {e}")
# # # # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# # # # # # @app.get("/health", summary="Health check", tags=["System"])
# # # # # # async def health_check():
# # # # # #     return {
# # # # # #         "status": "healthy",
# # # # # #         "service": "LexAI API",
# # # # # #         "version": "2.1.0",
# # # # # #         "features": {
# # # # # #             "query_classification": "enabled",
# # # # # #             "anti_hallucination": "active",
# # # # # #             "legal_framework": "BNS/BNSS/BSA 2023"
# # # # # #         },
# # # # # #         "cache_enabled": ENABLE_CACHE,
# # # # # #         "rate_limit": RATE_LIMIT_PER_MINUTE
# # # # # #     }

# # # # # # @app.get("/config", summary="Configuration", tags=["System"])
# # # # # # async def get_config():
# # # # # #     return {
# # # # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # # #         "valid_jurisdictions": VALID_JURISDICTIONS,
# # # # # #         "query_classification": True,
# # # # # #         "features": {
# # # # # #             "caching": ENABLE_CACHE,
# # # # # #             "rate_limiting": RATE_LIMIT_PER_MINUTE,
# # # # # #             "pii_redaction": REDACT_PII,
# # # # # #             "profanity_filter": FILTER_PROFANITY
# # # # # #         }
# # # # # #     }

# # # # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # # # if __name__ == "__main__":
# # # # # #     import uvicorn
# # # # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# # # # # import os
# # # # # import json
# # # # # import logging
# # # # # import time
# # # # # import asyncio
# # # # # from contextlib import asynccontextmanager
# # # # # from typing import Optional, List, Dict, Any, Tuple
# # # # # from functools import wraps
# # # # # from enum import Enum
# # # # # from datetime import datetime

# # # # # from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# # # # # from fastapi.middleware.cors import CORSMiddleware
# # # # # from fastapi.staticfiles import StaticFiles
# # # # # from fastapi.responses import FileResponse, JSONResponse
# # # # # from fastapi.encoders import jsonable_encoder
# # # # # from pydantic import BaseModel, field_validator, Field
# # # # # from dotenv import load_dotenv
# # # # # from tenacity import (
# # # # #     retry, stop_after_attempt, wait_exponential, 
# # # # #     retry_if_exception_type, before_sleep_log
# # # # # )
# # # # # from cachetools import TTLCache
# # # # # import re

# # # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # # load_dotenv()

# # # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# # # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # # New configuration options
# # # # # CACHE_TTL            = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
# # # # # MAX_RETRIES          = int(os.getenv("MAX_RETRIES", "3"))
# # # # # RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# # # # # ENABLE_CACHE         = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# # # # # FILTER_PROFANITY     = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# # # # # REDACT_PII           = os.getenv("REDACT_PII", "true").lower() == "true"
# # # # # VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")

# # # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # # logging.basicConfig(
# # # # #     level=logging.INFO,
# # # # #     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
# # # # #     datefmt="%H:%M:%S",
# # # # # )
# # # # # log = logging.getLogger("lexai")

# # # # # # ── Mistral client import ─────────────────────────────────────────────────────
# # # # # try:
# # # # #     from mistralai import Mistral
# # # # #     log.info("Using mistralai >= 1.x import path")
# # # # # except ImportError:
# # # # #     try:
# # # # #         from mistralai.client import Mistral
# # # # #         log.info("Using mistralai.client import path")
# # # # #     except ImportError:
# # # # #         from mistralai.client import MistralClient as Mistral
# # # # #         log.info("Using legacy MistralClient import")

# # # # # # ── Query Classifier ──────────────────────────────────────────────────────────
# # # # # class QueryClassifier:
# # # # #     """Classifies whether a query is a legal scenario or general conversation"""
    
# # # # #     # Legal keywords that indicate a legal scenario
# # # # #     LEGAL_KEYWORDS = [
# # # # #         # Criminal keywords
# # # # #         'murder', 'kill', 'death', 'homicide', 'assault', 'battery', 'robbery', 
# # # # #         'theft', 'burglary', 'dacoity', 'extortion', 'fraud', 'cheating', 
# # # # #         'forgery', 'counterfeit', 'rape', 'sexual', 'harassment', 'stalking',
# # # # #         'kidnap', 'abduction', 'dowry', 'domestic violence', 'cruelty',
        
# # # # #         # Legal terms
# # # # #         'fir', 'complaint', 'police', 'case', 'court', 'judge', 'lawyer',
# # # # #         'advocate', 'legal', 'violation', 'offense', 'crime', 'criminal',
# # # # #         'sentence', 'punishment', 'fine', 'imprisonment', 'arrest', 'bail',
        
# # # # #         # Civil terms
# # # # #         'contract', 'agreement', 'property', 'ownership', 'title', 'deed',
# # # # #         'landlord', 'tenant', 'rent', 'eviction', 'divorce', 'maintenance',
# # # # #         'custody', 'inheritance', 'will', 'testament', 'debt', 'loan',
        
# # # # #         # Cyber crimes
# # # # #         'hacking', 'phishing', 'cyber', 'online fraud', 'identity theft',
# # # # #         'data breach', 'privacy violation', 'digital arrest',
        
# # # # #         # Constitutional
# # # # #         'fundamental rights', 'constitution', 'article', 'writ', 'petition',
        
# # # # #         # Business
# # # # #         'company', 'corporate', 'director', 'shareholder', 'insolvency',
# # # # #         'bankruptcy', 'trademark', 'copyright', 'patent'
# # # # #     ]
    
# # # # #     # Greeting and casual conversation patterns (non-legal)
# # # # #     GREETING_PATTERNS = [
# # # # #         r'^(hi|hello|hey|greetings)[\s\!]*$',
# # # # #         r'^good (morning|afternoon|evening)[\s\!]*$',
# # # # #         r'^how are you[\s\?]*$',
# # # # #         r'^what\'?s up[\s\?]*$',
# # # # #         r'^nice to meet you',
# # # # #         r'^i am \w+$',  # "I am Krishna" pattern
# # # # #         r'^my name is \w+$',
# # # # #         r'^who are you[\s\?]*$',
# # # # #         r'^what is your name[\s\?]*$',
# # # # #         r'^tell me about yourself',
# # # # #         r'^thanks?[\s\!]*$',
# # # # #         r'^thank you[\s\!]*$',
# # # # #         r'^bye|goodbye|see you',
# # # # #         r'^ok|okay'
# # # # #     ]
    
# # # # #     # Query patterns that are clearly non-legal
# # # # #     NON_LEGAL_PATTERNS = [
# # # # #         r'weather|temperature',
# # # # #         r'cricket|football|sports',
# # # # #         r'movie|song|music|film',
# # # # #         r'recipe|cooking|food',
# # # # #         r'joke|funny|humor',
# # # # #         r'game|play|fun',
# # # # #         r'love|relationship (?!law|legal)',
# # # # #         r'^what is (ai|artificial intelligence|machine learning)',
# # # # #         r'^how to (cook|bake|make)'
# # # # #     ]
    
# # # # #     @classmethod
# # # # #     def is_legal_scenario(cls, text: str) -> Tuple[bool, str]:
# # # # #         """
# # # # #         Classify if text is a legal scenario.
# # # # #         Returns: (is_legal, reason)
# # # # #         """
# # # # #         text_lower = text.lower().strip()
        
# # # # #         # Check for greeting patterns first (quick filter)
# # # # #         for pattern in cls.GREETING_PATTERNS:
# # # # #             if re.match(pattern, text_lower, re.IGNORECASE):
# # # # #                 return False, "greeting_or_introduction"
        
# # # # #         # Check for non-legal patterns
# # # # #         for pattern in cls.NON_LEGAL_PATTERNS:
# # # # #             if re.search(pattern, text_lower, re.IGNORECASE):
# # # # #                 return False, "non_legal_conversation"
        
# # # # #         # For very short queries (less than 15 chars), likely not legal
# # # # #         if len(text) < 15 and not any(kw in text_lower for kw in cls.LEGAL_KEYWORDS):
# # # # #             return False, "query_too_short"
        
# # # # #         # Check for legal keywords
# # # # #         legal_keyword_count = sum(1 for kw in cls.LEGAL_KEYWORDS if kw in text_lower)
        
# # # # #         # If at least 2 legal keywords OR 1 legal keyword with sufficient length
# # # # #         if legal_keyword_count >= 2:
# # # # #             return True, f"contains_legal_keywords ({legal_keyword_count} keywords)"
# # # # #         elif legal_keyword_count == 1 and len(text) > 30:
# # # # #             return True, "contains_legal_context"
        
# # # # #         # Default to non-legal for casual queries
# # # # #         return False, "no_legal_context"
    
# # # # #     @classmethod
# # # # #     def get_non_legal_response(cls, query: str, classification_reason: str) -> dict:
# # # # #         """Generate appropriate response for non-legal queries"""
        
# # # # #         responses = {
# # # # #             "greeting_or_introduction": {
# # # # #                 "response": f"👋 Hello! I'm LexAI, your legal intelligence assistant. I specialize in analyzing legal scenarios under the Bharatiya Nyaya Sanhita (BNS) 2023 and other Indian laws.\n\nPlease describe a legal situation or problem you'd like me to analyze (e.g., 'Someone forged my signature on a property document'), and I'll provide applicable laws, consequences, and recommendations.",
# # # # #                 "type": "greeting"
# # # # #             },
# # # # #             "non_legal_conversation": {
# # # # #                 "response": f"I'm LexAI, a legal analysis AI. I'm designed to help with legal scenarios under Indian criminal laws (BNS 2023, BNSS, BSA).\n\nI notice your query isn't about a legal issue. Could you please describe a legal situation you need help with? For example: 'Someone stole my phone and is using my UPI apps' or 'My employer hasn't paid me for 3 months'.",
# # # # #                 "type": "clarification"
# # # # #             },
# # # # #             "query_too_short": {
# # # # #                 "response": f"I need more details to provide a legal analysis. Please describe your legal situation in more detail (minimum 20 characters).\n\nFor example: 'A shopkeeper sold me expired medicine and now I'm sick'.",
# # # # #                 "type": "insufficient_info"
# # # # #             },
# # # # #             "no_legal_context": {
# # # # #                 "response": f"I'm a legal analysis assistant. I can help with:\n\n• Criminal matters (theft, fraud, assault, etc.)\n• Property disputes\n• Contract violations\n• Cyber crimes\n• Family law issues\n\nPlease share the legal problem you're facing, what happened, and which jurisdiction (state/country) it occurred in.",
# # # # #                 "type": "guidance"
# # # # #             }
# # # # #         }
        
# # # # #         response_data = responses.get(classification_reason, responses["no_legal_context"])
        
# # # # #         # Structure response like legal analysis for consistency
# # # # #         return {
# # # # #             "is_legal_query": False,
# # # # #             "classification_reason": classification_reason,
# # # # #             "message": response_data["response"],
# # # # #             "type": response_data["type"],
# # # # #             "applicable_laws": [],
# # # # #             "consequences": [{
# # # # #                 "type": "None",
# # # # #                 "description": "This is not a legal query requiring analysis under BNS, BNSS, or BSA.",
# # # # #                 "severity": "None",
# # # # #                 "penalty": "Not applicable"
# # # # #             }],
# # # # #             "recommendations": [{
# # # # #                 "action": "Provide a legal scenario",
# # # # #                 "priority": "Immediate",
# # # # #                 "description": response_data["response"]
# # # # #             }],
# # # # #             "severity": "Low",
# # # # #             "summary": response_data["response"],
# # # # #             "disclaimer": "This is an informational response. For actual legal analysis, please provide a specific legal scenario."
# # # # #         }

# # # # # # ── 2023 Indian Criminal Law Framework ────────────────────────────────────────
# # # # # class IndianLaw2023:
# # # # #     """Reference data for 2023 Indian Criminal Laws"""
    
# # # # #     # New Criminal Codes (effective July 1, 2024)
# # # # #     BNS = "Bharatiya Nyaya Sanhita, 2023"
# # # # #     BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"
# # # # #     BSA = "Bharatiya Sakshya Adhiniyam, 2023"
    
# # # # #     @classmethod
# # # # #     def is_relevant_law(cls, scenario: str) -> bool:
# # # # #         """Check if scenario might involve any legal provisions"""
# # # # #         scenario_lower = scenario.lower()
# # # # #         # If scenario contains any legal context, it's relevant
# # # # #         legal_indicators = ['fir', 'police', 'case', 'court', 'legal', 'offense', 
# # # # #                            'crime', 'criminal', 'sue', 'complaint', 'violation']
# # # # #         return any(indicator in scenario_lower for indicator in legal_indicators)

# # # # # # ── Cache Setup ───────────────────────────────────────────────────────────────
# # # # # if ENABLE_CACHE:
# # # # #     response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
# # # # #     log.info(f"Response cache enabled with TTL={CACHE_TTL}s")
# # # # # else:
# # # # #     response_cache = None
# # # # #     log.info("Response cache disabled")

# # # # # # ── Rate Limiting ─────────────────────────────────────────────────────────────
# # # # # class RateLimiter:
# # # # #     def __init__(self, requests_per_minute: int):
# # # # #         self.requests_per_minute = requests_per_minute
# # # # #         self.requests: Dict[str, List[float]] = {}
    
# # # # #     def can_proceed(self, client_id: str = "default") -> bool:
# # # # #         now = time.time()
# # # # #         window_start = now - 60
        
# # # # #         if client_id not in self.requests:
# # # # #             self.requests[client_id] = []
        
# # # # #         self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
# # # # #         if len(self.requests[client_id]) >= self.requests_per_minute:
# # # # #             return False
        
# # # # #         self.requests[client_id].append(now)
# # # # #         return True

# # # # # rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# # # # # # ── PII Detection Patterns ───────────────────────────────────────────────────
# # # # # PII_PATTERNS = [
# # # # #     (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),
# # # # #     (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
# # # # #     (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),
# # # # #     (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
# # # # #     (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),
# # # # # ]

# # # # # PROFANITY_WORDS = ['fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 'damn', 'piss']

# # # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # # VALID_JURISDICTIONS = ["India", "United States", "United Kingdom", "Australia", "Canada", "European Union", "Singapore", "UAE"]
# # # # # INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"]

# # # # # class ConversationMessage(BaseModel):
# # # # #     """Model for conversation history messages"""
# # # # #     role: str  # "user" or "ai"
# # # # #     content: str
    
# # # # #     @field_validator("role")
# # # # #     @classmethod
# # # # #     def validate_role(cls, v: str) -> str:
# # # # #         if v not in ["user", "ai", "assistant"]:
# # # # #             raise ValueError("Role must be 'user', 'ai', or 'assistant'")
# # # # #         return v

# # # # # # Update the ScenarioRequest model in main.py (around line 250-270)

# # # # # class ScenarioRequest(BaseModel):
# # # # #     scenario: str
# # # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # # #     state: Optional[str] = None
# # # # #     api_key: str = ""
# # # # #     conversation_history: Optional[List[Dict[str, str]]] = None  # Changed from ConversationMessage to Dict
    
# # # # #     class Config:
# # # # #         json_schema_extra = {
# # # # #             "example": {
# # # # #                 "scenario": "Someone forged my signature on a property document in Maharashtra",
# # # # #                 "jurisdiction": "India",
# # # # #                 "state": "Maharashtra",
# # # # #                 "api_key": "",
# # # # #                 "conversation_history": [
# # # # #                     {"role": "user", "content": "My property documents were forged"},
# # # # #                     {"role": "assistant", "content": "Based on your scenario..."}
# # # # #                 ]
# # # # #             }
# # # # #         }
# # # # #         # Allow extra fields to be ignored
# # # # #         extra = "ignore"

# # # # #     @field_validator("scenario")
# # # # #     @classmethod
# # # # #     def scenario_not_empty(cls, v: str) -> str:
# # # # #         v = v.strip()
# # # # #         if not v:
# # # # #             raise ValueError("Scenario cannot be empty.")
        
# # # # #         if len(v) < 5:
# # # # #             raise ValueError("Please provide at least 5 characters.")
        
# # # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        
# # # # #         if REDACT_PII:
# # # # #             for pattern, replacement in PII_PATTERNS:
# # # # #                 v = pattern.sub(replacement, v)
        
# # # # #         if FILTER_PROFANITY:
# # # # #             for word in PROFANITY_WORDS:
# # # # #                 pattern = re.compile(re.escape(word), re.IGNORECASE)
# # # # #                 v = pattern.sub('***', v)
        
# # # # #         return v

# # # # #     @field_validator("jurisdiction")
# # # # #     @classmethod
# # # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # # #         if v not in VALID_JURISDICTIONS:
# # # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # # #         return v
    
# # # # #     @field_validator("state")
# # # # #     @classmethod
# # # # #     def state_valid(cls, v: Optional[str], info) -> Optional[str]:
# # # # #         if v and info.data.get("jurisdiction") == "India":
# # # # #             if v not in INDIAN_STATES:
# # # # #                 # Don't raise error, just warn and allow
# # # # #                 log.warning(f"State '{v}' not in supported list, but allowing")
# # # # #                 return v
# # # # #         return v

# # # # # class AnalysisResult(BaseModel):
# # # # #     applicable_laws: List[Dict[str, str]]
# # # # #     consequences: List[Dict[str, str]]
# # # # #     recommendations: List[Dict[str, str]]
# # # # #     severity: str
# # # # #     summary: str
# # # # #     disclaimer: str
# # # # #     metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, exclude=True)

# # # # # # ── Enhanced System Prompt for Legal Analysis Only ───────────────────────────
# # # # # LEGAL_SYSTEM_PROMPT = """You are LexAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws.

# # # # # IMPORTANT: 
# # # # # - If this is a follow-up question with conversation history provided, use the previous context to answer naturally.
# # # # # - Maintain consistency with previous answers about the same legal scenario.
# # # # # - If the user asks for more details, clarification, or next steps, provide specific actionable advice.

# # # # # For LEGAL scenarios, you MUST use ONLY the NEW 2023 laws:
# # # # # - Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES IPC
# # # # # - Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES CrPC
# # # # # - Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES Evidence Act

# # # # # Response Format - Return ONLY valid JSON with this structure:

# # # # # {
# # # # #   "applicable_laws": [
# # # # #     {
# # # # #       "name": "Full name of the Act",
# # # # #       "section": "Specific section number",
# # # # #       "description": "Why this law applies",
# # # # #       "jurisdiction": "India or specific state"
# # # # #     }
# # # # #   ],
# # # # #   "consequences": [
# # # # #     {
# # # # #       "type": "Criminal | Civil | Administrative | Financial",
# # # # #       "description": "Detailed consequences",
# # # # #       "severity": "Minor | Moderate | Severe | Critical",
# # # # #       "penalty": "Specific penalty details"
# # # # #     }
# # # # #   ],
# # # # #   "recommendations": [
# # # # #     {
# # # # #       "action": "Recommended action",
# # # # #       "priority": "Immediate | Short-term | Long-term",
# # # # #       "description": "Why this action helps"
# # # # #     }
# # # # #   ],
# # # # #   "severity": "Low | Medium | High | Critical",
# # # # #   "summary": "Plain-language summary that directly answers the user's question",
# # # # #   "disclaimer": "This analysis is based on BNS 2023 and related codes."
# # # # # }

# # # # # CRITICAL RULES:
# # # # # 1. For follow-up questions, provide answers that reference the conversation history
# # # # # 2. NEVER analyze non-legal queries as legal cases
# # # # # 3. For greetings/questions like "who are you", respond conversationally
# # # # # 4. ONLY apply BNS/BNSS/BSA when actual legal issues are described
# # # # # 5. If the user asks for clarification on a previous point, provide more detailed information
# # # # # 6. If the user asks "what evidence do I need", provide specific document types and evidence requirements
# # # # # 7. If the user asks about timeline, give realistic estimates based on legal procedures"""

# # # # # # ── Helper Functions ──────────────────────────────────────────────────────────
# # # # # def resolve_api_key(user_key: str) -> str:
# # # # #     if MISTRAL_API_KEY:
# # # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # # #             log.info("Using user-supplied API key")
# # # # #             return user_key.strip()
# # # # #         return MISTRAL_API_KEY
# # # # #     if not user_key.strip():
# # # # #         raise HTTPException(
# # # # #             status_code=400,
# # # # #             detail="No API key configured. Set MISTRAL_API_KEY in .env, or pass api_key."
# # # # #         )
# # # # #     return user_key.strip()

# # # # # def clean_json(raw: str) -> str:
# # # # #     text = raw.strip()
# # # # #     if text.startswith("```"):
# # # # #         parts = text.split("```")
# # # # #         text = parts[1] if len(parts) >= 2 else text
# # # # #         if text.lower().startswith("json"):
# # # # #             text = text[4:]
# # # # #     if text.endswith("```"):
# # # # #         text = text[:-3]
# # # # #     text = re.sub(r',\s*}', '}', text)
# # # # #     text = re.sub(r',\s*]', ']', text)
# # # # #     return text.strip()

# # # # # def get_cache_key(request: ScenarioRequest) -> str:
# # # # #     scenario_hash = hash(request.scenario)
# # # # #     return f"{request.jurisdiction}:{request.state or 'none'}:{scenario_hash}"

# # # # # @retry(retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
# # # # #        stop=stop_after_attempt(MAX_RETRIES),
# # # # #        wait=wait_exponential(multiplier=1, min=2, max=10),
# # # # #        before_sleep=before_sleep_log(log, logging.WARNING))
# # # # # async def call_mistral(api_key: str, user_message: str) -> dict:
# # # # #     """Call Mistral API with retries"""
# # # # #     client = Mistral(api_key=api_key)
    
# # # # #     response = await asyncio.to_thread(
# # # # #         client.chat.complete,
# # # # #         model=MISTRAL_MODEL,
# # # # #         messages=[
# # # # #             {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
# # # # #             {"role": "user", "content": user_message},
# # # # #         ],
# # # # #         temperature=TEMPERATURE,
# # # # #         max_tokens=MAX_TOKENS,
# # # # #     )
    
# # # # #     raw = response.choices[0].message.content or ""
    
# # # # #     try:
# # # # #         return json.loads(clean_json(raw))
# # # # #     except json.JSONDecodeError as e:
# # # # #         log.warning(f"JSON parse failed: {e}")
# # # # #         cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
# # # # #         json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
# # # # #         if json_match:
# # # # #             return json.loads(json_match.group())
# # # # #         raise

# # # # # # ── Lifespan ──────────────────────────────────────────────────────────────────
# # # # # @asynccontextmanager
# # # # # async def lifespan(app: FastAPI):
# # # # #     log.info("━" * 70)
# # # # #     log.info("  LexAI Legal Intelligence API v2.1.0 - 2023 Indian Criminal Law System")
# # # # #     log.info("━" * 70)
# # # # #     log.info(f"  Model           : {MISTRAL_MODEL}")
# # # # #     log.info(f"  Server key      : {'✓ configured' if MISTRAL_API_KEY else '✗ not set'}")
# # # # #     log.info(f"  User key        : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # # #     log.info(f"  Jurisdiction    : {DEFAULT_JURISDICTION}")
# # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # #     log.info("  LEGAL FRAMEWORK (Effective July 1, 2024):")
# # # # #     log.info(f"    • {IndianLaw2023.BNS} (replaces IPC)")
# # # # #     log.info(f"    • {IndianLaw2023.BNSS} (replaces CrPC)")
# # # # #     log.info(f"    • {IndianLaw2023.BSA} (replaces Evidence Act)")
# # # # #     log.info("  ──────────────────────────────────────────────────────")
# # # # #     log.info(f"  Features        : Cache={ENABLE_CACHE} | RateLimit={RATE_LIMIT_PER_MINUTE}/min")
# # # # #     log.info(f"  Query Classifier: Enabled (prevents hallucination)")
# # # # #     log.info(f"  Follow-up Support: Enabled (conversation history)")
# # # # #     log.info(f"  UI + API        : http://{HOST}:{PORT}/")
# # # # #     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
# # # # #     log.info("━" * 70)
# # # # #     yield
# # # # #     log.info("LexAI shutting down.")

# # # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # # app = FastAPI(
# # # # #     title="LexAI — Legal Intelligence API (2023 Indian Criminal Law System)",
# # # # #     description="AI-powered legal scenario analysis with query classification and follow-up support",
# # # # #     version="2.1.0",
# # # # #     lifespan=lifespan,
# # # # #     docs_url="/docs",
# # # # #     redoc_url="/redoc",
# # # # # )

# # # # # app.add_middleware(
# # # # #     CORSMiddleware,
# # # # #     allow_origins=["*"],
# # # # #     allow_credentials=True,
# # # # #     allow_methods=["*"],
# # # # #     allow_headers=["*"],
# # # # # )

# # # # # # ── API Routes ────────────────────────────────────────────────────────────────
# # # # # @app.get("/", include_in_schema=False)
# # # # # async def root():
# # # # #     return {
# # # # #         "service": "LexAI Legal Intelligence API",
# # # # #         "version": "2.1.0",
# # # # #         "features": ["Query Classification", "Anti-Hallucination", "BNS 2023", "Follow-up Support"],
# # # # #         "status": "operational",
# # # # #         "documentation": "/docs"
# # # # #     }

# # # # # # Update the analyze_scenario function (around line 450-500)

# # # # # @app.post("/analyze", response_model=dict, summary="Analyze a legal scenario", tags=["Analysis"])
# # # # # async def analyze_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks, client_id: Optional[str] = None):
# # # # #     """Analyze legal scenario with automatic query classification and follow-up support"""
    
# # # # #     # Rate limiting
# # # # #     client_identifier = client_id or request.api_key[:8] if request.api_key else "anonymous"
# # # # #     if not rate_limiter.can_proceed(client_identifier):
# # # # #         raise HTTPException(status_code=429, detail=f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute")
    
# # # # #     # CLASSIFY QUERY FIRST - Prevents hallucination
# # # # #     is_legal, reason = QueryClassifier.is_legal_scenario(request.scenario)
# # # # #     log.info(f"Query classified: is_legal={is_legal}, reason={reason}, query='{request.scenario[:50]}...'")
    
# # # # #     # Handle non-legal queries immediately without calling AI
# # # # #     if not is_legal:
# # # # #         log.info(f"Returning non-legal response for: {request.scenario[:50]}")
# # # # #         non_legal_response = QueryClassifier.get_non_legal_response(request.scenario, reason)
# # # # #         return non_legal_response
    
# # # # #     # For legal queries, proceed with AI analysis
# # # # #     api_key = resolve_api_key(request.api_key)
    
# # # # #     # Check cache (skip caching for follow-ups with conversation history)
# # # # #     cache_key = get_cache_key(request) if not request.conversation_history else None
# # # # #     if ENABLE_CACHE and cache_key and cache_key in response_cache:
# # # # #         log.info(f"Cache hit for legal query: {cache_key}")
# # # # #         return response_cache[cache_key]
    
# # # # #     # Build legal analysis prompt with conversation history if available
# # # # #     user_message = f"""Jurisdiction: {request.jurisdiction}
# # # # # {'State: ' + request.state if request.state else ''}
# # # # # Legal Scenario: {request.scenario}"""

# # # # #     # Add conversation context for follow-ups
# # # # #     if request.conversation_history and len(request.conversation_history) > 0:
# # # # #         user_message += "\n\nPrevious conversation:\n"
# # # # #         # Include last 6 messages for context (3 exchanges)
# # # # #         for msg in request.conversation_history[-6:]:
# # # # #             role = msg.get("role", "unknown")
# # # # #             content = msg.get("content", "")
# # # # #             role_label = "USER" if role.lower() in ["user", "human"] else "ASSISTANT"
# # # # #             user_message += f"{role_label}: {content}\n"
# # # # #         user_message += "\nPlease answer this follow-up question based on the previous context. Maintain consistency with previous answers."
    
# # # # #     start = time.perf_counter()
# # # # #     log.info(f"Analyzing legal scenario | jurisdiction={request.jurisdiction} | length={len(request.scenario)} | has_history={bool(request.conversation_history)}")
    
# # # # #     try:
# # # # #         result = await call_mistral(api_key, user_message)
        
# # # # #         elapsed = time.perf_counter() - start
# # # # #         log.info(f"Analysis complete | {elapsed:.1f}s | severity={result.get('severity', '?')}")
        
# # # # #         # Add metadata to response
# # # # #         result["metadata"] = {
# # # # #             "query_classified": True,
# # # # #             "is_legal_query": True,
# # # # #             "classification_reason": reason,
# # # # #             "analysis_timestamp": time.time(),
# # # # #             "has_conversation_history": bool(request.conversation_history),
# # # # #             "conversation_depth": len(request.conversation_history) if request.conversation_history else 0
# # # # #         }
        
# # # # #         # Cache response (without metadata to save space)
# # # # #         if ENABLE_CACHE and cache_key:
# # # # #             response_to_cache = result.copy()
# # # # #             response_to_cache.pop('metadata', None)
# # # # #             response_cache[cache_key] = response_to_cache
        
# # # # #         return result
    
# # # # #     except json.JSONDecodeError as e:
# # # # #         log.error(f"JSON parse error: {e}")
# # # # #         raise HTTPException(status_code=502, detail="AI returned invalid response format.")
# # # # #     except Exception as e:
# # # # #         log.error(f"Analysis error: {e}")
# # # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# # # # # @app.get("/health", summary="Health check", tags=["System"])
# # # # # async def health_check():
# # # # #     return {
# # # # #         "status": "healthy",
# # # # #         "service": "LexAI API",
# # # # #         "version": "2.1.0",
# # # # #         "features": {
# # # # #             "query_classification": "enabled",
# # # # #             "anti_hallucination": "active",
# # # # #             "legal_framework": "BNS/BNSS/BSA 2023",
# # # # #             "follow_up_support": "enabled"
# # # # #         },
# # # # #         "cache_enabled": ENABLE_CACHE,
# # # # #         "rate_limit": RATE_LIMIT_PER_MINUTE
# # # # #     }

# # # # # @app.get("/config", summary="Configuration", tags=["System"])
# # # # # async def get_config():
# # # # #     return {
# # # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # # #         "valid_jurisdictions": VALID_JURISDICTIONS,
# # # # #         "query_classification": True,
# # # # #         "follow_up_support": True,
# # # # #         "features": {
# # # # #             "caching": ENABLE_CACHE,
# # # # #             "rate_limiting": RATE_LIMIT_PER_MINUTE,
# # # # #             "pii_redaction": REDACT_PII,
# # # # #             "profanity_filter": FILTER_PROFANITY
# # # # #         },
# # # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # # #         "allow_user_api_key": ALLOW_USER_API_KEY
# # # # #     }

# # # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # # if __name__ == "__main__":
# # # # #     import uvicorn
# # # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# # # # import os
# # # # import json
# # # # import logging
# # # # import time
# # # # import asyncio
# # # # from contextlib import asynccontextmanager
# # # # from typing import Optional, List, Dict, Any, Tuple
# # # # from functools import wraps
# # # # from enum import Enum
# # # # from datetime import datetime

# # # # from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# # # # from fastapi.middleware.cors import CORSMiddleware
# # # # from fastapi.staticfiles import StaticFiles
# # # # from fastapi.responses import FileResponse, JSONResponse
# # # # from fastapi.encoders import jsonable_encoder
# # # # from pydantic import BaseModel, field_validator, Field
# # # # from dotenv import load_dotenv
# # # # from tenacity import (
# # # #     retry, stop_after_attempt, wait_exponential, 
# # # #     retry_if_exception_type, before_sleep_log
# # # # )
# # # # from cachetools import TTLCache
# # # # import re

# # # # # ── Load .env ─────────────────────────────────────────────────────────────────
# # # # load_dotenv()

# # # # # ── Config from environment ───────────────────────────────────────────────────
# # # # MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# # # # MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# # # # MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# # # # TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# # # # HOST                 = os.getenv("HOST", "0.0.0.0")
# # # # PORT                 = int(os.getenv("PORT", "8000"))
# # # # DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# # # # ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# # # # MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # # # # New configuration options
# # # # CACHE_TTL            = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
# # # # MAX_RETRIES          = int(os.getenv("MAX_RETRIES", "3"))
# # # # RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# # # # ENABLE_CACHE         = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# # # # FILTER_PROFANITY     = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# # # # REDACT_PII           = os.getenv("REDACT_PII", "true").lower() == "true"
# # # # VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")

# # # # # ── Logging ───────────────────────────────────────────────────────────────────
# # # # logging.basicConfig(
# # # #     level=logging.INFO,
# # # #     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
# # # #     datefmt="%H:%M:%S",
# # # # )
# # # # log = logging.getLogger("lexai")

# # # # # ── Mistral client import ─────────────────────────────────────────────────────
# # # # try:
# # # #     from mistralai import Mistral
# # # #     log.info("Using mistralai >= 1.x import path")
# # # # except ImportError:
# # # #     try:
# # # #         from mistralai.client import Mistral
# # # #         log.info("Using mistralai.client import path")
# # # #     except ImportError:
# # # #         from mistralai.client import MistralClient as Mistral
# # # #         log.info("Using legacy MistralClient import")

# # # # # ── Query Classifier ──────────────────────────────────────────────────────────
# # # # class QueryClassifier:
# # # #     """Classifies whether a query is a legal scenario or general conversation"""
    
# # # #     # Legal keywords that indicate a legal scenario
# # # #     LEGAL_KEYWORDS = [
# # # #         # Criminal keywords
# # # #         'murder', 'kill', 'death', 'homicide', 'assault', 'battery', 'robbery', 
# # # #         'theft', 'burglary', 'dacoity', 'extortion', 'fraud', 'cheating', 
# # # #         'forgery', 'counterfeit', 'rape', 'sexual', 'harassment', 'stalking',
# # # #         'kidnap', 'abduction', 'dowry', 'domestic violence', 'cruelty',
        
# # # #         # Legal terms
# # # #         'fir', 'complaint', 'police', 'case', 'court', 'judge', 'lawyer',
# # # #         'advocate', 'legal', 'violation', 'offense', 'crime', 'criminal',
# # # #         'sentence', 'punishment', 'fine', 'imprisonment', 'arrest', 'bail',
        
# # # #         # Civil terms
# # # #         'contract', 'agreement', 'property', 'ownership', 'title', 'deed',
# # # #         'landlord', 'tenant', 'rent', 'eviction', 'divorce', 'maintenance',
# # # #         'custody', 'inheritance', 'will', 'testament', 'debt', 'loan',
        
# # # #         # Cyber crimes
# # # #         'hacking', 'phishing', 'cyber', 'online fraud', 'identity theft',
# # # #         'data breach', 'privacy violation', 'digital arrest',
        
# # # #         # Constitutional
# # # #         'fundamental rights', 'constitution', 'article', 'writ', 'petition',
        
# # # #         # Business
# # # #         'company', 'corporate', 'director', 'shareholder', 'insolvency',
# # # #         'bankruptcy', 'trademark', 'copyright', 'patent'
# # # #     ]
    
# # # #     # Legal short forms and abbreviations
# # # #     LEGAL_SHORT_FORMS = {
# # # #         'fir': 'First Information Report',
# # # #         'ipc': 'Indian Penal Code (now replaced by BNS 2023)',
# # # #         'crpc': 'Code of Criminal Procedure (now replaced by BNSS 2023)',
# # # #         'bnss': 'Bharatiya Nagarik Suraksha Sanhita',
# # # #         'bns': 'Bharatiya Nyaya Sanhita',
# # # #         'bsa': 'Bharatiya Sakshya Adhiniyam',
# # # #         'rti': 'Right to Information',
# # # #         'gst': 'Goods and Services Tax',
# # # #         'cyber': 'Cyber crime',
# # # #         'divorce': 'Divorce and family law',
# # # #         'rent': 'Rental and tenancy laws',
# # # #         'property': 'Property laws',
# # # #         'contract': 'Contract laws'
# # # #     }
    
# # # #     # Greeting and casual conversation patterns (non-legal)
# # # #     GREETING_PATTERNS = [
# # # #         r'^(hi|hello|hey|greetings)[\s\!]*$',
# # # #         r'^good (morning|afternoon|evening)[\s\!]*$',
# # # #         r'^how are you[\s\?]*$',
# # # #         r'^what\'?s up[\s\?]*$',
# # # #         r'^nice to meet you',
# # # #         r'^i am \w+$',
# # # #         r'^my name is \w+$',
# # # #         r'^who are you[\s\?]*$',
# # # #         r'^what is your name[\s\?]*$',
# # # #         r'^tell me about yourself',
# # # #         r'^thanks?[\s\!]*$',
# # # #         r'^thank you[\s\!]*$',
# # # #         r'^bye|goodbye|see you',
# # # #         r'^ok|okay$'
# # # #     ]
    
# # # #     # Query patterns that are clearly non-legal
# # # #     NON_LEGAL_PATTERNS = [
# # # #         r'weather|temperature',
# # # #         r'cricket|football|sports',
# # # #         r'movie|song|music|film',
# # # #         r'recipe|cooking|food',
# # # #         r'joke|funny|humor',
# # # #         r'game|play|fun'
# # # #     ]
    
# # # #     @classmethod
# # # #     def is_legal_scenario(cls, text: str) -> Tuple[bool, str]:
# # # #         """
# # # #         Classify if text is a legal scenario.
# # # #         Returns: (is_legal, reason)
# # # #         """
# # # #         text_lower = text.lower().strip()
        
# # # #         # Check for legal short forms first
# # # #         for short_form in cls.LEGAL_SHORT_FORMS.keys():
# # # #             if text_lower == short_form or text_lower.startswith(f"{short_form} "):
# # # #                 return True, f"legal_abbreviation_{short_form}"
        
# # # #         # Check for greeting patterns first (quick filter)
# # # #         for pattern in cls.GREETING_PATTERNS:
# # # #             if re.match(pattern, text_lower, re.IGNORECASE):
# # # #                 return False, "greeting_or_introduction"
        
# # # #         # Check for non-legal patterns
# # # #         for pattern in cls.NON_LEGAL_PATTERNS:
# # # #             if re.search(pattern, text_lower, re.IGNORECASE):
# # # #                 return False, "non_legal_conversation"
        
# # # #         # Check for legal keywords (no minimum length restriction)
# # # #         legal_keyword_count = sum(1 for kw in cls.LEGAL_KEYWORDS if kw in text_lower)
        
# # # #         # For very short queries, check if they're legal short forms or questions
# # # #         if len(text) < 15:
# # # #             # Check if it's a question about law
# # # #             if '?' in text and any(word in text_lower for word in ['law', 'legal', 'right', 'police', 'court']):
# # # #                 return True, "short_legal_question"
# # # #             # Check if it contains any legal keywords
# # # #             if legal_keyword_count >= 1:
# # # #                 return True, f"contains_legal_keywords ({legal_keyword_count} keywords)"
# # # #             # Default for short non-legal queries
# # # #             return False, "short_non_legal_query"
        
# # # #         # If at least 1 legal keyword, consider it legal
# # # #         if legal_keyword_count >= 1:
# # # #             return True, f"contains_legal_keywords ({legal_keyword_count} keywords)"
        
# # # #         # Check for legal question patterns
# # # #         legal_question_patterns = [
# # # #             r'^(what|how|why|when|where|can|is|are|do|does|did) (is|are|my|the|a|an)?.*?(right|law|legal|police|court|case)',
# # # #             r'.*?(lawyer|advocate|sue|complaint|criminal|civil).*?\?$'
# # # #         ]
        
# # # #         for pattern in legal_question_patterns:
# # # #             if re.search(pattern, text_lower, re.IGNORECASE):
# # # #                 return True, "legal_question_pattern"
        
# # # #         # Default to non-legal for casual queries
# # # #         return False, "no_legal_context"
    
# # # #     @classmethod
# # # #     def get_non_legal_response(cls, query: str, classification_reason: str) -> dict:
# # # #         """Generate appropriate response for non-legal queries"""
        
# # # #         responses = {
# # # #             "greeting_or_introduction": {
# # # #                 "response": "👋 Hello! I'm NyayaAI, your legal intelligence assistant. I specialize in analyzing legal scenarios under the Bharatiya Nyaya Sanhita (BNS) 2023 and other Indian laws.\n\nPlease describe a legal situation or problem you'd like me to analyze (e.g., 'Someone forged my signature on a property document'), and I'll provide applicable laws, consequences, and recommendations.",
# # # #                 "type": "greeting"
# # # #             },
# # # #             "non_legal_conversation": {
# # # #                 "response": "I'm NyayaAI, a legal analysis AI. I'm designed to help with legal scenarios under Indian criminal laws (BNS 2023, BNSS, BSA).\n\nI notice your query isn't about a legal issue. Could you please describe a legal situation you need help with? For example: 'Someone stole my phone and is using my UPI apps' or 'My employer hasn't paid me for 3 months'.",
# # # #                 "type": "clarification"
# # # #             },
# # # #             "short_non_legal_query": {
# # # #                 "response": "I'm here to help with legal questions! Could you please provide more details about your legal situation? For example:\n\n• 'My landlord is not returning my security deposit'\n• 'Someone is blackmailing me online'\n• 'I got a fake job offer and lost money'\n\nWhat legal issue are you facing?",
# # # #                 "type": "clarification"
# # # #             },
# # # #             "no_legal_context": {
# # # #                 "response": "I'm a legal analysis assistant. I can help with:\n\n• Criminal matters (theft, fraud, assault, etc.)\n• Property disputes\n• Contract violations\n• Cyber crimes\n• Family law issues\n\nPlease share the legal problem you're facing, what happened, and which jurisdiction (state/country) it occurred in.",
# # # #                 "type": "guidance"
# # # #             }
# # # #         }
        
# # # #         response_data = responses.get(classification_reason, responses["no_legal_context"])
        
# # # #         # Structure response like legal analysis for consistency
# # # #         return {
# # # #             "is_legal_query": False,
# # # #             "classification_reason": classification_reason,
# # # #             "message": response_data["response"],
# # # #             "type": response_data["type"],
# # # #             "applicable_laws": [],
# # # #             "consequences": [{
# # # #                 "type": "None",
# # # #                 "description": "This is not a legal query requiring analysis under BNS, BNSS, or BSA.",
# # # #                 "severity": "None",
# # # #                 "penalty": "Not applicable"
# # # #             }],
# # # #             "recommendations": [{
# # # #                 "action": "Provide a legal scenario",
# # # #                 "priority": "Immediate",
# # # #                 "description": "Please describe your legal situation in more detail for a proper legal analysis."
# # # #             }],
# # # #             "severity": "Low",
# # # #             "summary": response_data["response"],
# # # #             "disclaimer": "This is an informational response. For actual legal analysis, please provide a specific legal scenario."
# # # #         }

# # # # # ── 2023 Indian Criminal Law Framework ────────────────────────────────────────
# # # # class IndianLaw2023:
# # # #     """Reference data for 2023 Indian Criminal Laws"""
    
# # # #     # New Criminal Codes (effective July 1, 2024)
# # # #     BNS = "Bharatiya Nyaya Sanhita, 2023"
# # # #     BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"
# # # #     BSA = "Bharatiya Sakshya Adhiniyam, 2023"
    
# # # #     @classmethod
# # # #     def is_relevant_law(cls, scenario: str) -> bool:
# # # #         """Check if scenario might involve any legal provisions"""
# # # #         scenario_lower = scenario.lower()
# # # #         # If scenario contains any legal context, it's relevant
# # # #         legal_indicators = ['fir', 'police', 'case', 'court', 'legal', 'offense', 
# # # #                            'crime', 'criminal', 'sue', 'complaint', 'violation', 'law', 'right']
# # # #         return any(indicator in scenario_lower for indicator in legal_indicators)

# # # # # ── Cache Setup ───────────────────────────────────────────────────────────────
# # # # if ENABLE_CACHE:
# # # #     response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
# # # #     log.info(f"Response cache enabled with TTL={CACHE_TTL}s")
# # # # else:
# # # #     response_cache = None
# # # #     log.info("Response cache disabled")

# # # # # ── Rate Limiting ─────────────────────────────────────────────────────────────
# # # # class RateLimiter:
# # # #     def __init__(self, requests_per_minute: int):
# # # #         self.requests_per_minute = requests_per_minute
# # # #         self.requests: Dict[str, List[float]] = {}
    
# # # #     def can_proceed(self, client_id: str = "default") -> bool:
# # # #         now = time.time()
# # # #         window_start = now - 60
        
# # # #         if client_id not in self.requests:
# # # #             self.requests[client_id] = []
        
# # # #         self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
# # # #         if len(self.requests[client_id]) >= self.requests_per_minute:
# # # #             return False
        
# # # #         self.requests[client_id].append(now)
# # # #         return True

# # # # rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# # # # # ── PII Detection Patterns ───────────────────────────────────────────────────
# # # # PII_PATTERNS = [
# # # #     (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),
# # # #     (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
# # # #     (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),
# # # #     (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
# # # #     (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),
# # # # ]

# # # # PROFANITY_WORDS = ['fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 'damn', 'piss']

# # # # # ── Request / Response models ─────────────────────────────────────────────────
# # # # VALID_JURISDICTIONS = ["India", "United States", "United Kingdom", "Australia", "Canada", "European Union", "Singapore", "UAE"]
# # # # INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"]

# # # # class ScenarioRequest(BaseModel):
# # # #     scenario: str
# # # #     jurisdiction: str = DEFAULT_JURISDICTION
# # # #     state: Optional[str] = None
# # # #     api_key: str = ""
# # # #     conversation_history: Optional[List[Dict[str, str]]] = None
    
# # # #     class Config:
# # # #         json_schema_extra = {
# # # #             "example": {
# # # #                 "scenario": "Someone forged my signature on a property document in Maharashtra",
# # # #                 "jurisdiction": "India",
# # # #                 "state": "Maharashtra",
# # # #                 "api_key": "",
# # # #                 "conversation_history": [
# # # #                     {"role": "user", "content": "My property documents were forged"},
# # # #                     {"role": "assistant", "content": "Based on your scenario..."}
# # # #                 ]
# # # #             }
# # # #         }
# # # #         extra = "ignore"

# # # #     @field_validator("scenario")
# # # #     @classmethod
# # # #     def scenario_not_empty(cls, v: str) -> str:
# # # #         v = v.strip()
# # # #         if not v:
# # # #             raise ValueError("Scenario cannot be empty.")
        
# # # #         # Increased max length, removed minimum length restriction
# # # #         if len(v) > MAX_SCENARIO_LENGTH:
# # # #             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        
# # # #         if REDACT_PII:
# # # #             for pattern, replacement in PII_PATTERNS:
# # # #                 v = pattern.sub(replacement, v)
        
# # # #         if FILTER_PROFANITY:
# # # #             for word in PROFANITY_WORDS:
# # # #                 pattern = re.compile(re.escape(word), re.IGNORECASE)
# # # #                 v = pattern.sub('***', v)
        
# # # #         return v

# # # #     @field_validator("jurisdiction")
# # # #     @classmethod
# # # #     def jurisdiction_valid(cls, v: str) -> str:
# # # #         if v not in VALID_JURISDICTIONS:
# # # #             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
# # # #         return v
    
# # # #     @field_validator("state")
# # # #     @classmethod
# # # #     def state_valid(cls, v: Optional[str], info) -> Optional[str]:
# # # #         if v and info.data.get("jurisdiction") == "India":
# # # #             if v not in INDIAN_STATES:
# # # #                 log.warning(f"State '{v}' not in supported list, but allowing")
# # # #                 return v
# # # #         return v

# # # # # ── Enhanced System Prompt for Legal Analysis ───────────────────────────────
# # # # LEGAL_SYSTEM_PROMPT = """You are NyayaAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws.

# # # # IMPORTANT INSTRUCTIONS:
# # # # 1. For short queries (even single words like "divorce", "fir", "theft"), provide relevant legal information based on the context.
# # # # 2. If the query is ambiguous, ask clarifying questions politely.
# # # # 3. For follow-up questions, use conversation history to maintain context.
# # # # 4. Always provide specific, actionable legal guidance when possible.

# # # # For LEGAL scenarios, use the NEW 2023 laws:
# # # # - Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES IPC
# # # # - Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES CrPC
# # # # - Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES Evidence Act

# # # # For GENERAL queries that are not legal scenarios but related to law:
# # # # - Provide helpful information without forcing a legal analysis structure
# # # # - Explain what information would be needed for proper legal analysis

# # # # Response Format - Return JSON. For legal scenarios, use this structure:
# # # # {
# # # #   "applicable_laws": [...],
# # # #   "consequences": [...],
# # # #   "recommendations": [...],
# # # #   "severity": "Low | Medium | High | Critical",
# # # #   "summary": "Clear answer to the query",
# # # #   "disclaimer": "Legal disclaimer"
# # # # }

# # # # For ambiguous or short queries, provide helpful guidance instead of error messages."""

# # # # # ── Helper Functions ──────────────────────────────────────────────────────────
# # # # def resolve_api_key(user_key: str) -> str:
# # # #     if MISTRAL_API_KEY:
# # # #         if ALLOW_USER_API_KEY and user_key.strip():
# # # #             log.info("Using user-supplied API key")
# # # #             return user_key.strip()
# # # #         return MISTRAL_API_KEY
# # # #     if not user_key.strip():
# # # #         raise HTTPException(
# # # #             status_code=400,
# # # #             detail="No API key configured. Set MISTRAL_API_KEY in .env, or pass api_key."
# # # #         )
# # # #     return user_key.strip()

# # # # def clean_json(raw: str) -> str:
# # # #     text = raw.strip()
# # # #     if text.startswith("```"):
# # # #         parts = text.split("```")
# # # #         text = parts[1] if len(parts) >= 2 else text
# # # #         if text.lower().startswith("json"):
# # # #             text = text[4:]
# # # #     if text.endswith("```"):
# # # #         text = text[:-3]
# # # #     text = re.sub(r',\s*}', '}', text)
# # # #     text = re.sub(r',\s*]', ']', text)
# # # #     return text.strip()

# # # # def get_cache_key(request: ScenarioRequest) -> str:
# # # #     scenario_hash = hash(request.scenario)
# # # #     return f"{request.jurisdiction}:{request.state or 'none'}:{scenario_hash}"

# # # # @retry(retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
# # # #        stop=stop_after_attempt(MAX_RETRIES),
# # # #        wait=wait_exponential(multiplier=1, min=2, max=10),
# # # #        before_sleep=before_sleep_log(log, logging.WARNING))
# # # # async def call_mistral(api_key: str, user_message: str) -> dict:
# # # #     """Call Mistral API with retries"""
# # # #     client = Mistral(api_key=api_key)
    
# # # #     response = await asyncio.to_thread(
# # # #         client.chat.complete,
# # # #         model=MISTRAL_MODEL,
# # # #         messages=[
# # # #             {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
# # # #             {"role": "user", "content": user_message},
# # # #         ],
# # # #         temperature=TEMPERATURE,
# # # #         max_tokens=MAX_TOKENS,
# # # #     )
    
# # # #     raw = response.choices[0].message.content or ""
    
# # # #     try:
# # # #         return json.loads(clean_json(raw))
# # # #     except json.JSONDecodeError as e:
# # # #         log.warning(f"JSON parse failed: {e}")
# # # #         cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
# # # #         json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
# # # #         if json_match:
# # # #             return json.loads(json_match.group())
# # # #         # Return a fallback response
# # # #         return {
# # # #             "applicable_laws": [],
# # # #             "consequences": [],
# # # #             "recommendations": [{
# # # #                 "action": "Rephrase your question",
# # # #                 "priority": "Immediate",
# # # #                 "description": "Could you please provide more details about your legal situation?"
# # # #             }],
# # # #             "severity": "Low",
# # # #             "summary": "I understand you have a legal question. Could you please provide more details so I can give you a proper legal analysis?",
# # # #             "disclaimer": "This is an automated response."
# # # #         }

# # # # # ── Lifespan ──────────────────────────────────────────────────────────────────
# # # # @asynccontextmanager
# # # # async def lifespan(app: FastAPI):
# # # #     log.info("━" * 70)
# # # #     log.info("  NyayaAI Legal Intelligence API v2.1.0 - 2023 Indian Criminal Law System")
# # # #     log.info("━" * 70)
# # # #     log.info(f"  Model           : {MISTRAL_MODEL}")
# # # #     log.info(f"  Server key      : {'✓ configured' if MISTRAL_API_KEY else '✗ not set'}")
# # # #     log.info(f"  User key        : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
# # # #     log.info(f"  Jurisdiction    : {DEFAULT_JURISDICTION}")
# # # #     log.info("  ──────────────────────────────────────────────────────")
# # # #     log.info("  LEGAL FRAMEWORK (Effective July 1, 2024):")
# # # #     log.info(f"    • {IndianLaw2023.BNS} (replaces IPC)")
# # # #     log.info(f"    • {IndianLaw2023.BNSS} (replaces CrPC)")
# # # #     log.info(f"    • {IndianLaw2023.BSA} (replaces Evidence Act)")
# # # #     log.info("  ──────────────────────────────────────────────────────")
# # # #     log.info(f"  Features        : Cache={ENABLE_CACHE} | RateLimit={RATE_LIMIT_PER_MINUTE}/min")
# # # #     log.info(f"  Query Classifier: Enabled (handles short queries gracefully)")
# # # #     log.info(f"  Follow-up Support: Enabled (conversation history)")
# # # #     log.info(f"  UI + API        : http://{HOST}:{PORT}/")
# # # #     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
# # # #     log.info("━" * 70)
# # # #     yield
# # # #     log.info("NyayaAI shutting down.")

# # # # # ── App ───────────────────────────────────────────────────────────────────────
# # # # app = FastAPI(
# # # #     title="NyayaAI — Legal Intelligence API (2023 Indian Criminal Law System)",
# # # #     description="AI-powered legal scenario analysis with query classification and follow-up support",
# # # #     version="2.1.0",
# # # #     lifespan=lifespan,
# # # #     docs_url="/docs",
# # # #     redoc_url="/redoc",
# # # # )

# # # # app.add_middleware(
# # # #     CORSMiddleware,
# # # #     allow_origins=["*"],
# # # #     allow_credentials=True,
# # # #     allow_methods=["*"],
# # # #     allow_headers=["*"],
# # # # )

# # # # # ── API Routes ────────────────────────────────────────────────────────────────
# # # # @app.get("/", include_in_schema=False)
# # # # async def root():
# # # #     return {
# # # #         "service": "NyayaAI Legal Intelligence API",
# # # #         "version": "2.1.0",
# # # #         "features": ["Query Classification", "Anti-Hallucination", "BNS 2023", "Follow-up Support"],
# # # #         "status": "operational",
# # # #         "documentation": "/docs"
# # # #     }

# # # # @app.post("/analyze", response_model=dict, summary="Analyze a legal scenario", tags=["Analysis"])
# # # # async def analyze_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks, client_id: Optional[str] = None):
# # # #     """Analyze legal scenario with automatic query classification and follow-up support"""
    
# # # #     # Rate limiting
# # # #     client_identifier = client_id or request.api_key[:8] if request.api_key else "anonymous"
# # # #     if not rate_limiter.can_proceed(client_identifier):
# # # #         raise HTTPException(status_code=429, detail=f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute")
    
# # # #     # CLASSIFY QUERY FIRST - Prevents hallucination
# # # #     is_legal, reason = QueryClassifier.is_legal_scenario(request.scenario)
# # # #     log.info(f"Query classified: is_legal={is_legal}, reason={reason}, query='{request.scenario[:50]}...'")
    
# # # #     # For short queries that might be legal, let the AI handle them
# # # #     # Only return non-legal response for clearly non-legal queries
# # # #     if not is_legal and reason not in ["short_non_legal_query", "short_legal_question"]:
# # # #         log.info(f"Returning non-legal response for: {request.scenario[:50]}")
# # # #         non_legal_response = QueryClassifier.get_non_legal_response(request.scenario, reason)
# # # #         return non_legal_response
    
# # # #     # For legal queries or ambiguous short queries, proceed with AI analysis
# # # #     api_key = resolve_api_key(request.api_key)
    
# # # #     # Check cache (skip caching for follow-ups with conversation history)
# # # #     cache_key = get_cache_key(request) if not request.conversation_history else None
# # # #     if ENABLE_CACHE and cache_key and cache_key in response_cache:
# # # #         log.info(f"Cache hit for legal query: {cache_key}")
# # # #         return response_cache[cache_key]
    
# # # #     # Build prompt with conversation history if available
# # # #     user_message = f"""Jurisdiction: {request.jurisdiction}
# # # # {'State: ' + request.state if request.state else ''}
# # # # Query: {request.scenario}"""

# # # #     # Add context about query being short/ambiguous
# # # #     if len(request.scenario) < 20:
# # # #         user_message += "\n\nNote: This is a short query. If it's ambiguous, provide helpful information about what the user might be asking, or ask clarifying questions."

# # # #     # Add conversation context for follow-ups
# # # #     if request.conversation_history and len(request.conversation_history) > 0:
# # # #         user_message += "\n\nPrevious conversation:\n"
# # # #         for msg in request.conversation_history[-6:]:
# # # #             role = msg.get("role", "unknown")
# # # #             content = msg.get("content", "")
# # # #             role_label = "USER" if role.lower() in ["user", "human"] else "ASSISTANT"
# # # #             user_message += f"{role_label}: {content}\n"
# # # #         user_message += "\nPlease answer based on the above conversation context."
    
# # # #     start = time.perf_counter()
# # # #     log.info(f"Analyzing query | jurisdiction={request.jurisdiction} | length={len(request.scenario)} | has_history={bool(request.conversation_history)}")
    
# # # #     try:
# # # #         result = await call_mistral(api_key, user_message)
        
# # # #         elapsed = time.perf_counter() - start
# # # #         log.info(f"Analysis complete | {elapsed:.1f}s | severity={result.get('severity', '?')}")
        
# # # #         # Add metadata to response
# # # #         result["is_legal_query"] = True
# # # #         result["classification_reason"] = reason
        
# # # #         # Cache response (without metadata to save space)
# # # #         if ENABLE_CACHE and cache_key:
# # # #             response_to_cache = result.copy()
# # # #             response_cache[cache_key] = response_to_cache
        
# # # #         return result
    
# # # #     except json.JSONDecodeError as e:
# # # #         log.error(f"JSON parse error: {e}")
# # # #         # Return a graceful fallback response
# # # #         return {
# # # #             "applicable_laws": [],
# # # #             "consequences": [],
# # # #             "recommendations": [{
# # # #                 "action": "Provide more details",
# # # #                 "priority": "Immediate",
# # # #                 "description": "Could you please provide more information about your legal situation? I'm here to help."
# # # #             }],
# # # #             "severity": "Low",
# # # #             "summary": "I understand you have a legal question. Could you please provide more details so I can give you a proper legal analysis?",
# # # #             "disclaimer": "This is an automated response. Please provide more details for a complete legal analysis.",
# # # #             "is_legal_query": True
# # # #         }
# # # #     except Exception as e:
# # # #         log.error(f"Analysis error: {e}")
# # # #         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# # # # @app.get("/health", summary="Health check", tags=["System"])
# # # # async def health_check():
# # # #     return {
# # # #         "status": "healthy",
# # # #         "service": "NyayaAI API",
# # # #         "version": "2.1.0",
# # # #         "features": {
# # # #             "query_classification": "enabled",
# # # #             "anti_hallucination": "active",
# # # #             "legal_framework": "BNS/BNSS/BSA 2023",
# # # #             "follow_up_support": "enabled",
# # # #             "short_query_handling": "enabled"
# # # #         },
# # # #         "cache_enabled": ENABLE_CACHE,
# # # #         "rate_limit": RATE_LIMIT_PER_MINUTE
# # # #     }

# # # # @app.get("/config", summary="Configuration", tags=["System"])
# # # # async def get_config():
# # # #     return {
# # # #         "default_jurisdiction": DEFAULT_JURISDICTION,
# # # #         "max_scenario_length": MAX_SCENARIO_LENGTH,
# # # #         "valid_jurisdictions": VALID_JURISDICTIONS,
# # # #         "query_classification": True,
# # # #         "follow_up_support": True,
# # # #         "short_query_handling": True,
# # # #         "features": {
# # # #             "caching": ENABLE_CACHE,
# # # #             "rate_limiting": RATE_LIMIT_PER_MINUTE,
# # # #             "pii_redaction": REDACT_PII,
# # # #             "profanity_filter": FILTER_PROFANITY
# # # #         },
# # # #         "server_key_configured": bool(MISTRAL_API_KEY),
# # # #         "allow_user_api_key": ALLOW_USER_API_KEY
# # # #     }

# # # # # ── Entry point ───────────────────────────────────────────────────────────────
# # # # if __name__ == "__main__":
# # # #     import uvicorn
# # # #     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# import os
# import json
# import logging
# import time
# import asyncio
# from contextlib import asynccontextmanager
# from typing import Optional, List, Dict, Any, Tuple
# from functools import wraps
# from enum import Enum
# from datetime import datetime

# from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.encoders import jsonable_encoder
# from pydantic import BaseModel, field_validator, Field
# from dotenv import load_dotenv
# from tenacity import (
#     retry, stop_after_attempt, wait_exponential, 
#     retry_if_exception_type, before_sleep_log
# )
# from cachetools import TTLCache
# import re

# # ── Load .env ─────────────────────────────────────────────────────────────────
# load_dotenv()

# # ── Config from environment ───────────────────────────────────────────────────
# MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# HOST                 = os.getenv("HOST", "0.0.0.0")
# PORT                 = int(os.getenv("PORT", "8000"))
# DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # New configuration options
# CACHE_TTL            = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
# MAX_RETRIES          = int(os.getenv("MAX_RETRIES", "3"))
# RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# ENABLE_CACHE         = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# FILTER_PROFANITY     = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# REDACT_PII           = os.getenv("REDACT_PII", "true").lower() == "true"
# VALIDATION_STRICTNESS = os.getenv("VALIDATION_STRICTNESS", "medium")

# # ── Logging ───────────────────────────────────────────────────────────────────
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
#     datefmt="%H:%M:%S",
# )
# log = logging.getLogger("lexai")

# # ── Mistral client import ─────────────────────────────────────────────────────
# try:
#     from mistralai import Mistral
#     log.info("Using mistralai >= 1.x import path")
# except ImportError:
#     try:
#         from mistralai.client import Mistral
#         log.info("Using mistralai.client import path")
#     except ImportError:
#         from mistralai.client import MistralClient as Mistral
#         log.info("Using legacy MistralClient import")

# # ── Query Classifier with 100+ Legal Keywords ──────────────────────────────────────────
# class QueryClassifier:
#     """Classifies whether a query is a legal scenario or general conversation"""
    
#     # Comprehensive Legal Keywords (100+ words)
#     LEGAL_KEYWORDS = [
#         # Criminal offenses
#         'murder', 'kill', 'death', 'homicide', 'assault', 'battery', 'robbery', 
#         'theft', 'burglary', 'dacoity', 'extortion', 'fraud', 'cheating', 
#         'forgery', 'counterfeit', 'rape', 'sexual assault', 'harassment', 'stalking',
#         'kidnap', 'abduction', 'dowry', 'domestic violence', 'cruelty', 'attempt to murder',
#         'dowry death', 'eve teasing', 'molestation', 'outraging modesty', 'voyeurism',
#         'cyber stalking', 'online harassment', 'identity theft', 'phishing', 'hacking',
        
#         # Legal procedures and terms
#         'fir', 'complaint', 'police', 'case', 'court', 'judge', 'lawyer', 'advocate',
#         'legal', 'violation', 'offense', 'crime', 'criminal', 'sentence', 'punishment',
#         'fine', 'imprisonment', 'arrest', 'bail', 'custody', 'summons', 'warrant',
#         'charge sheet', 'trial', 'hearing', 'appeal', 'petition', 'affidavit',
#         'summons', 'notice', 'order', 'judgment', 'decree', 'stay order',
        
#         # Civil matters
#         'contract', 'agreement', 'property', 'ownership', 'title', 'deed', 'rent',
#         'lease', 'landlord', 'tenant', 'eviction', 'possession', 'boundary dispute',
#         'succession', 'inheritance', 'will', 'testament', 'probate', 'letters of administration',
#         'debt', 'loan', 'recovery', 'default', 'bankruptcy', 'insolvency', 'liquidation',
#         'specific performance', 'injunction', 'damages', 'compensation', 'tort',
        
#         # Family law
#         'divorce', 'maintenance', 'alimony', 'custody', 'child custody', 'visitation rights',
#         'guardianship', 'adoption', 'annulment', 'judicial separation', 'restitution of conjugal rights',
#         'marriage', 'wedding', 'dowry', 'stridhan', 'family court', 'mediation',
        
#         # Cyber crimes
#         'hacking', 'phishing', 'cyber', 'online fraud', 'identity theft', 'data breach',
#         'privacy violation', 'digital arrest', 'cyber bullying', 'trolling', 'defamation online',
#         'credit card fraud', 'bank fraud', 'upi fraud', 'sim swapping', 'otp fraud',
        
#         # Constitutional & Rights
#         'fundamental rights', 'constitution', 'article', 'writ', 'petition', 'habeas corpus',
#         'mandamus', 'certiorari', 'quo warranto', 'prohibition', 'human rights',
#         'legal aid', 'free legal aid', 'right to information', 'rti', 'right to privacy',
        
#         # Business and Corporate
#         'company', 'corporate', 'director', 'shareholder', 'insolvency', 'bankruptcy',
#         'trademark', 'copyright', 'patent', 'intellectual property', 'merger', 'acquisition',
#         'partnership dispute', 'llp', 'gst', 'income tax', 'tax evasion', 'service tax',
        
#         # Motor vehicle and traffic
#         'driving license', 'learner license', 'driving licence', 'dl', 'registration certificate',
#         'rc', 'insurance', 'motor vehicle', 'traffic challan', 'speeding', 'rash driving',
#         'accident', 'hit and run', 'drink driving', 'drunken driving', 'overloading',
#         'helmet rule', 'seat belt', 'no entry violation', 'red light jumping',
#         'vehicle seizure', 'impound', 'traffic police', 'mvi', 'transport department',
        
#         # Documents and identification
#         'aadhar', 'pan card', 'voter id', 'passport', 'visa', 'pancard', 'aadhaar',
#         'lost document', 'forget document', 'misplaced', 'missing certificate',
#         'birth certificate', 'death certificate', 'marriage certificate', 'domicile',
#         'caste certificate', 'income certificate', 'transfer certificate', 'tc',
        
#         # Common legal issues
#         'lost', 'forget', 'forgot', 'misplaced', 'missing', 'stolen', 'damaged',
#         'destroyed', 'renewal', 'renew', 'apply', 'application', 'process',
#         'procedure', 'documentation', 'required documents', 'eligibility',
#         'fees', 'fine', 'penalty', 'challan', 'pending', 'due', 'overdue',
        
#         # Employment
#         'salary', 'wages', 'employer', 'employee', 'termination', 'retrenchment',
#         'layoff', 'fired', 'resignation', 'notice period', 'gratuity', 'pf', 'provident fund',
#         'esi', 'bonus', 'overtime', 'leave encashment', 'compensation', 'workplace harassment',
#         'sexual harassment at workplace', 'posh act', 'labour law', 'industrial dispute',
        
#         # Consumer issues
#         'consumer complaint', 'defective product', 'deficient service', 'false advertising',
#         'misleading ad', 'unfair trade practice', 'consumer court', 'consumer forum',
#         'replacement', 'refund', 'compensation', 'cheated', 'scam', 'fraudulent',
        
#         # Real estate
#         'flat', 'apartment', 'builder', 'developer', 'possession delayed', 'occupancy certificate',
#         'completion certificate', 'stamp duty', 'registration', 'agreement for sale',
#         'sale deed', 'title deed', 'encumbrance', 'mutation', 'khata', 'property tax',
        
#         # Banking and finance
#         'bank account', 'savings account', 'fixed deposit', 'loan', 'credit card',
#         'emi default', 'np ', 'non-performing asset', 'bank guarantee', 'cheque bounce',
#         'stop payment', 'debit card fraud', 'atm fraud', 'net banking fraud',
        
#         # Education
#         'college', 'university', 'admission', 'capitation fee', 'donation', 'seat blocking',
#         'degree certificate', 'marksheet', 'transcript', 'convocation', 'backlog',
#         'exam results', 'revaluation', 'supplementary exam', 'student rights',
        
#         # Medical and health
#         'medical negligence', 'hospital negligence', 'doctor negligence', 'wrong treatment',
#         'medical error', 'compensation for injury', 'insurance claim', 'health insurance',
#         'medi claim', 'cashless treatment', 'denial of claim',
        
#         # General legal issues
#         'problem', 'issue', 'dispute', 'conflict', 'disagreement', 'unfair', 'illegal',
#         'wrong', 'cheated', 'scammed', 'victim', 'suffering', 'loss', 'damage',
#         'injury', 'hurt', 'wound', 'accuse', 'alleged', 'suspect', 'witness',
#         'caught', 'caught by police', 'detained', 'questioned', 'interrogated',
#         'want to file case', 'want to complain', 'lodge complaint', 'register case',
#         'legal action', 'police action', 'investigation', 'inquiry', 'enquiry',
        
#         # Emergencies
#         'urgent', 'emergency', 'immediate help', 'right now', 'fast', 'quick',
#         'help', 'assist', 'guide', 'advise', 'suggest', 'recommend',
        
#         # Money and financial
#         'cash', 'money', 'payment', 'paid', 'paying', 'paid extra', 'overcharged',
#         'refund', 'return money', 'recover money', 'money back', 'duplicate payment',
#         'wrong transaction', 'reversal', 'chargeback', 'dispute transaction',
#     ]
    
#     # Legal short forms and abbreviations
#     LEGAL_SHORT_FORMS = {
#         'fir': 'First Information Report',
#         'ipc': 'Indian Penal Code (now replaced by BNS 2023)',
#         'crpc': 'Code of Criminal Procedure (now replaced by BNSS 2023)',
#         'bnss': 'Bharatiya Nagarik Suraksha Sanhita',
#         'bns': 'Bharatiya Nyaya Sanhita',
#         'bsa': 'Bharatiya Sakshya Adhiniyam',
#         'rti': 'Right to Information',
#         'gst': 'Goods and Services Tax',
#         'cyber': 'Cyber crime',
#         'divorce': 'Divorce and family law',
#         'rent': 'Rental and tenancy laws',
#         'property': 'Property laws',
#         'contract': 'Contract laws',
#         'dl': 'Driving License',
#         'rc': 'Registration Certificate',
#         'pan': 'Permanent Account Number',
#         'aadhaar': 'Aadhaar Identification',
#         'upi': 'Unified Payments Interface',
#         'posh': 'Prevention of Sexual Harassment',
#         'esi': 'Employees State Insurance',
#         'pf': 'Provident Fund',
#     }
    
#     # Legal question patterns
#     LEGAL_QUESTION_PATTERNS = [
#         r'(what|how|why|when|where|can|is|are|do|does|did|will|would|could|should).*?(law|legal|right|police|court|file|complaint|case|procedure|process)',
#         r'(is|are|does).*?(illegal|legal|criminal|punishable|valid|invalid|allowed|prohibited)',
#         r'(can|how to).*?(file|register|apply|get|obtain|renew|make|lodge)',
#         r'(what to do|what should i|what can i).*?(if|when|after|before)',
#         r'(is this|was this).*?(legal|illegal|criminal|offence|crime)',
#         r'(punishment|penalty|sentence|fine|jail|imprisonment).*?(for|of)',
#         r'(compensation|damages|recovery|refund).*?(for|from)',
#         r'(rights|entitlement|eligible|entitled).*?(under|as per|according to)',
#         r'(forget|forgot|lost|misplaced|missing|stolen).*?(license|licence|document|card|certificate|money|cash)',
#         r'(caught|arrested|detained|questioned).*?(police|customs)',
#     ]
    
#     # Greeting and casual conversation patterns (non-legal)
#     GREETING_PATTERNS = [
#         r'^(hi|hello|hey|greetings)[\s\!]*$',
#         r'^good (morning|afternoon|evening)[\s\!]*$',
#         r'^how are you[\s\?]*$',
#         r'^what\'?s up[\s\?]*$',
#         r'^nice to meet you',
#         r'^i am \w+$',
#         r'^my name is \w+$',
#         r'^who are you[\s\?]*$',
#         r'^what is your name[\s\?]*$',
#         r'^tell me about yourself',
#         r'^thanks?[\s\!]*$',
#         r'^thank you[\s\!]*$',
#         r'^bye|goodbye|see you',
#         r'^ok|okay$'
#     ]
    
#     # Query patterns that are clearly non-legal
#     NON_LEGAL_PATTERNS = [
#         r'weather|temperature|rain|sunny|cloudy',
#         r'cricket|football|sports|game|match|tournament',
#         r'movie|song|music|film|actor|actress|celebrity',
#         r'recipe|cooking|food|restaurant|hotel|meal|dinner|lunch',
#         r'joke|funny|humor|laugh|comedy',
#         r'game|play|fun|entertainment',
#         r'love|relationship|boyfriend|girlfriend|dating',
#         r'^what is (ai|artificial intelligence|machine learning|chatgpt)',
#         r'^how to (cook|bake|make|prepare).*?(food|cake|pizza|burger)',
#     ]
    
#     @classmethod
#     def is_legal_scenario(cls, text: str) -> Tuple[bool, str]:
#         """
#         Classify if text is a legal scenario.
#         Returns: (is_legal, reason)
#         """
#         text_lower = text.lower().strip()
        
#         # Check for legal short forms first
#         for short_form in cls.LEGAL_SHORT_FORMS.keys():
#             if text_lower == short_form or text_lower.startswith(f"{short_form} ") or text_lower.endswith(f" {short_form}"):
#                 return True, f"legal_abbreviation_{short_form}"
        
#         # Check for greeting patterns first (quick filter)
#         for pattern in cls.GREETING_PATTERNS:
#             if re.match(pattern, text_lower, re.IGNORECASE):
#                 return False, "greeting_or_introduction"
        
#         # Check for non-legal patterns
#         for pattern in cls.NON_LEGAL_PATTERNS:
#             if re.search(pattern, text_lower, re.IGNORECASE):
#                 return False, "non_legal_conversation"
        
#         # Check legal question patterns
#         for pattern in cls.LEGAL_QUESTION_PATTERNS:
#             if re.search(pattern, text_lower, re.IGNORECASE):
#                 return True, "legal_question_pattern"
        
#         # Check for legal keywords (count matches)
#         legal_keyword_matches = []
#         for kw in cls.LEGAL_KEYWORDS:
#             if kw in text_lower:
#                 legal_keyword_matches.append(kw)
        
#         legal_keyword_count = len(legal_keyword_matches)
        
#         # If at least 1 legal keyword, consider it legal
#         if legal_keyword_count >= 1:
#             log.debug(f"Legal keywords found: {legal_keyword_matches[:5]}")
#             return True, f"contains_legal_keywords ({legal_keyword_count} keywords)"
        
#         # Check for legal context indicators
#         legal_context_indicators = [
#             'i want to', 'i need to', 'how to', 'what to do', 'help me with',
#             'i have a problem', 'i am facing', 'is it possible', 'can i'
#         ]
        
#         for indicator in legal_context_indicators:
#             if indicator in text_lower and len(text) > 20:
#                 return True, "legal_context_indicator"
        
#         # Default to non-legal for casual queries
#         return False, "no_legal_context"
    
#     @classmethod
#     def get_non_legal_response(cls, query: str, classification_reason: str) -> dict:
#         """Generate appropriate response for non-legal queries"""
        
#         responses = {
#             "greeting_or_introduction": {
#                 "response": "👋 Hello! I'm NyayaAI, your legal intelligence assistant. I specialize in analyzing legal scenarios under the Bharatiya Nyaya Sanhita (BNS) 2023 and other Indian laws.\n\nPlease describe your legal situation or problem. For example:\n• 'I lost my driving license, how do I get a duplicate?'\n• 'Someone forged my signature on a property document'\n• 'My employer hasn't paid my salary for 3 months'",
#                 "type": "greeting"
#             },
#             "non_legal_conversation": {
#                 "response": "I'm NyayaAI, a legal analysis AI. I'm designed to help with legal issues and problems.\n\nI notice your query isn't about a legal issue. Could you please describe a legal situation you need help with? For example:\n• 'I forgot my driving license at home, what's the penalty?'\n• 'Someone stole my phone and is using my UPI apps'\n• 'My landlord is not returning my security deposit'",
#                 "type": "clarification"
#             },
#             "no_legal_context": {
#                 "response": "I'm a legal analysis assistant. I can help with legal issues like:\n\n• Lost documents (license, certificates, ID cards)\n• Criminal matters (theft, fraud, assault)\n• Property disputes\n• Contract violations\n• Cyber crimes\n• Employment issues (salary, termination)\n• Consumer complaints\n• Family law issues (divorce, custody)\n\nPlease describe your specific legal problem or situation.",
#                 "type": "guidance"
#             }
#         }
        
#         response_data = responses.get(classification_reason, responses["no_legal_context"])
        
#         # Structure response like legal analysis for consistency
#         return {
#             "is_legal_query": False,
#             "classification_reason": classification_reason,
#             "message": response_data["response"],
#             "type": response_data["type"],
#             "applicable_laws": [],
#             "consequences": [{
#                 "type": "None",
#                 "description": "This is not a legal query requiring analysis.",
#                 "severity": "None",
#                 "penalty": "Not applicable"
#             }],
#             "recommendations": [{
#                 "action": "Describe your legal situation",
#                 "priority": "Immediate",
#                 "description": "Please provide details about your legal problem or situation so I can help you properly."
#             }],
#             "severity": "Low",
#             "summary": response_data["response"],
#             "disclaimer": "I'm here to help with legal issues. Please describe your specific legal problem."
#         }

# # ── 2023 Indian Criminal Law Framework ────────────────────────────────────────
# class IndianLaw2023:
#     """Reference data for 2023 Indian Criminal Laws"""
    
#     # New Criminal Codes (effective July 1, 2024)
#     BNS = "Bharatiya Nyaya Sanhita, 2023"
#     BNSS = "Bharatiya Nagarik Suraksha Sanhita, 2023"
#     BSA = "Bharatiya Sakshya Adhiniyam, 2023"
    
#     @classmethod
#     def is_relevant_law(cls, scenario: str) -> bool:
#         """Check if scenario might involve any legal provisions"""
#         scenario_lower = scenario.lower()
#         legal_indicators = ['fir', 'police', 'case', 'court', 'legal', 'offense', 
#                            'crime', 'criminal', 'sue', 'complaint', 'violation', 
#                            'law', 'right', 'license', 'licence', 'document', 'lost',
#                            'forget', 'forgot', 'problem', 'issue', 'money', 'cash',
#                            'caught', 'detained', 'arrested']
#         return any(indicator in scenario_lower for indicator in legal_indicators)

# # ── Cache Setup ───────────────────────────────────────────────────────────────
# if ENABLE_CACHE:
#     response_cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)
#     log.info(f"Response cache enabled with TTL={CACHE_TTL}s")
# else:
#     response_cache = None
#     log.info("Response cache disabled")

# # ── Rate Limiting ─────────────────────────────────────────────────────────────
# class RateLimiter:
#     def __init__(self, requests_per_minute: int):
#         self.requests_per_minute = requests_per_minute
#         self.requests: Dict[str, List[float]] = {}
    
#     def can_proceed(self, client_id: str = "default") -> bool:
#         now = time.time()
#         window_start = now - 60
        
#         if client_id not in self.requests:
#             self.requests[client_id] = []
        
#         self.requests[client_id] = [t for t in self.requests[client_id] if t > window_start]
        
#         if len(self.requests[client_id]) >= self.requests_per_minute:
#             return False
        
#         self.requests[client_id].append(now)
#         return True

# rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)

# # ── PII Detection Patterns ───────────────────────────────────────────────────
# PII_PATTERNS = [
#     (re.compile(r'\b\d{10}\b'), '[PHONE_NUMBER]'),
#     (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[EMAIL]'),
#     (re.compile(r'\b\d{12}\b'), '[AADHAAR]'),
#     (re.compile(r'\b\d{16}\b'), '[CREDIT_CARD]'),
#     (re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'), '[PAN]'),
# ]

# PROFANITY_WORDS = ['fuck', 'shit', 'asshole', 'bitch', 'cunt', 'bastard', 'damn', 'piss']

# # ── Request / Response models ─────────────────────────────────────────────────
# VALID_JURISDICTIONS = ["India", "United States", "United Kingdom", "Australia", "Canada", "European Union", "Singapore", "UAE"]
# INDIAN_STATES = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat", "West Bengal", "Rajasthan", "Kerala", "Telangana"]

# class ScenarioRequest(BaseModel):
#     scenario: str
#     jurisdiction: str = DEFAULT_JURISDICTION
#     state: Optional[str] = None
#     api_key: str = ""
#     conversation_history: Optional[List[Dict[str, str]]] = None
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "scenario": "I forgot my driving license somewhere, what should I do?",
#                 "jurisdiction": "India",
#                 "state": "Maharashtra",
#                 "api_key": "",
#                 "conversation_history": []
#             }
#         }
#         extra = "ignore"

#     @field_validator("scenario")
#     @classmethod
#     def scenario_not_empty(cls, v: str) -> str:
#         v = v.strip()
#         if not v:
#             raise ValueError("Scenario cannot be empty.")
        
#         if len(v) > MAX_SCENARIO_LENGTH:
#             raise ValueError(f"Scenario exceeds the {MAX_SCENARIO_LENGTH}-character limit.")
        
#         if REDACT_PII:
#             for pattern, replacement in PII_PATTERNS:
#                 v = pattern.sub(replacement, v)
        
#         if FILTER_PROFANITY:
#             for word in PROFANITY_WORDS:
#                 pattern = re.compile(re.escape(word), re.IGNORECASE)
#                 v = pattern.sub('***', v)
        
#         return v

#     @field_validator("jurisdiction")
#     @classmethod
#     def jurisdiction_valid(cls, v: str) -> str:
#         if v not in VALID_JURISDICTIONS:
#             raise ValueError(f"Unsupported jurisdiction '{v}'. Choose from: {', '.join(VALID_JURISDICTIONS)}")
#         return v
    
#     @field_validator("state")
#     @classmethod
#     def state_valid(cls, v: Optional[str], info) -> Optional[str]:
#         if v and info.data.get("jurisdiction") == "India":
#             if v not in INDIAN_STATES:
#                 log.warning(f"State '{v}' not in supported list, but allowing")
#                 return v
#         return v

# # ── Enhanced System Prompt for Legal Analysis ───────────────────────────────
# LEGAL_SYSTEM_PROMPT = """You are NyayaAI, an expert legal analyst specializing in the NEW 2023 Indian criminal laws.

# IMPORTANT INSTRUCTIONS:
# 1. For queries about lost documents, forgotten items, or legal procedures, provide relevant legal information.
# 2. Always assume the user is seeking legal guidance unless clearly indicated otherwise.
# 3. For ambiguous queries, ask clarifying questions politely.
# 4. Provide specific, actionable legal guidance when possible.

# For LEGAL scenarios, use the NEW 2023 laws:
# - Bharatiya Nyaya Sanhita (BNS), 2023 - REPLACES IPC
# - Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023 - REPLACES CrPC
# - Bharatiya Sakshya Adhiniyam (BSA), 2023 - REPLACES Evidence Act

# Response Format - Return JSON with this structure:
# {
#   "applicable_laws": [
#     {
#       "name": "Full name of the Act",
#       "section": "Specific section number",
#       "description": "Why this law applies",
#       "jurisdiction": "India or specific state"
#     }
#   ],
#   "consequences": [
#     {
#       "type": "Criminal | Civil | Administrative | Financial",
#       "description": "Detailed consequences",
#       "severity": "Minor | Moderate | Severe | Critical",
#       "penalty": "Specific penalty details"
#     }
#   ],
#   "recommendations": [
#     {
#       "action": "Recommended action",
#       "priority": "Immediate | Short-term | Long-term",
#       "description": "Why this action helps"
#     }
#   ],
#   "severity": "Low | Medium | High | Critical",
#   "summary": "Clear, helpful answer to the user's query",
#   "disclaimer": "This is legal information, not legal advice."
# }

# For lost document queries like "I forgot my driving license", provide:
# - Legal requirements for carrying license
# - Penalties for not carrying license
# - Procedure to get duplicate if lost
# - Steps to take if caught without license"""

# # ── Helper Functions ──────────────────────────────────────────────────────────
# def resolve_api_key(user_key: str) -> str:
#     if MISTRAL_API_KEY:
#         if ALLOW_USER_API_KEY and user_key.strip():
#             log.info("Using user-supplied API key")
#             return user_key.strip()
#         return MISTRAL_API_KEY
#     if not user_key.strip():
#         raise HTTPException(
#             status_code=400,
#             detail="No API key configured. Set MISTRAL_API_KEY in .env, or pass api_key."
#         )
#     return user_key.strip()

# def clean_json(raw: str) -> str:
#     text = raw.strip()
#     if text.startswith("```"):
#         parts = text.split("```")
#         text = parts[1] if len(parts) >= 2 else text
#         if text.lower().startswith("json"):
#             text = text[4:]
#     if text.endswith("```"):
#         text = text[:-3]
#     text = re.sub(r',\s*}', '}', text)
#     text = re.sub(r',\s*]', ']', text)
#     return text.strip()

# def get_cache_key(request: ScenarioRequest) -> str:
#     scenario_hash = hash(request.scenario)
#     return f"{request.jurisdiction}:{request.state or 'none'}:{scenario_hash}"

# @retry(retry=retry_if_exception_type((json.JSONDecodeError, ConnectionError, TimeoutError)),
#        stop=stop_after_attempt(MAX_RETRIES),
#        wait=wait_exponential(multiplier=1, min=2, max=10),
#        before_sleep=before_sleep_log(log, logging.WARNING))
# async def call_mistral(api_key: str, user_message: str) -> dict:
#     """Call Mistral API with retries"""
#     client = Mistral(api_key=api_key)
    
#     response = await asyncio.to_thread(
#         client.chat.complete,
#         model=MISTRAL_MODEL,
#         messages=[
#             {"role": "system", "content": LEGAL_SYSTEM_PROMPT},
#             {"role": "user", "content": user_message},
#         ],
#         temperature=TEMPERATURE,
#         max_tokens=MAX_TOKENS,
#     )
    
#     raw = response.choices[0].message.content or ""
    
#     try:
#         return json.loads(clean_json(raw))
#     except json.JSONDecodeError as e:
#         log.warning(f"JSON parse failed: {e}")
#         cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
#         json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
#         if json_match:
#             return json.loads(json_match.group())
#         # Return a helpful fallback response
#         return {
#             "applicable_laws": [],
#             "consequences": [],
#             "recommendations": [{
#                 "action": "Get legal assistance",
#                 "priority": "Immediate",
#                 "description": "Please provide more details about your legal situation for specific guidance."
#             }],
#             "severity": "Low",
#             "summary": "I understand you have a legal concern. Could you please provide more details so I can give you proper legal guidance?",
#             "disclaimer": "This is an automated response. For specific legal advice, please consult a lawyer."
#         }

# # ── Lifespan ──────────────────────────────────────────────────────────────────
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     log.info("━" * 70)
#     log.info("  NyayaAI Legal Intelligence API v2.1.0 - 2023 Indian Criminal Law System")
#     log.info("━" * 70)
#     log.info(f"  Model           : {MISTRAL_MODEL}")
#     log.info(f"  Server key      : {'✓ configured' if MISTRAL_API_KEY else '✗ not set'}")
#     log.info(f"  User key        : {'allowed' if ALLOW_USER_API_KEY else 'not allowed'}")
#     log.info(f"  Jurisdiction    : {DEFAULT_JURISDICTION}")
#     log.info("  ──────────────────────────────────────────────────────")
#     log.info("  LEGAL FRAMEWORK (Effective July 1, 2024):")
#     log.info(f"    • {IndianLaw2023.BNS} (replaces IPC)")
#     log.info(f"    • {IndianLaw2023.BNSS} (replaces CrPC)")
#     log.info(f"    • {IndianLaw2023.BSA} (replaces Evidence Act)")
#     log.info("  ──────────────────────────────────────────────────────")
#     log.info(f"  Features        : Cache={ENABLE_CACHE} | RateLimit={RATE_LIMIT_PER_MINUTE}/min")
#     log.info(f"  Query Classifier: Enhanced with 150+ legal keywords")
#     log.info(f"  Follow-up Support: Enabled (conversation history)")
#     log.info(f"  UI + API        : http://{HOST}:{PORT}/")
#     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
#     log.info("━" * 70)
#     yield
#     log.info("NyayaAI shutting down.")

# # ── App ───────────────────────────────────────────────────────────────────────
# app = FastAPI(
#     title="NyayaAI — Legal Intelligence API (2023 Indian Criminal Law System)",
#     description="AI-powered legal scenario analysis with enhanced query classification",
#     version="2.1.0",
#     lifespan=lifespan,
#     docs_url="/docs",
#     redoc_url="/redoc",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── API Routes ────────────────────────────────────────────────────────────────
# @app.get("/", include_in_schema=False)
# async def root():
#     return {
#         "service": "NyayaAI Legal Intelligence API",
#         "version": "2.1.0",
#         "features": [
#             "Query Classification (150+ legal keywords)",
#             "Anti-Hallucination",
#             "BNS 2023 Framework",
#             "Follow-up Support",
#             "Lost Document Guidance"
#         ],
#         "status": "operational",
#         "documentation": "/docs"
#     }

# @app.post("/analyze", response_model=dict, summary="Analyze a legal scenario", tags=["Analysis"])
# async def analyze_scenario(request: ScenarioRequest, background_tasks: BackgroundTasks, client_id: Optional[str] = None):
#     """Analyze legal scenario with automatic query classification"""
    
#     # Rate limiting
#     client_identifier = client_id or request.api_key[:8] if request.api_key else "anonymous"
#     if not rate_limiter.can_proceed(client_identifier):
#         raise HTTPException(status_code=429, detail=f"Rate limit: {RATE_LIMIT_PER_MINUTE} requests/minute")
    
#     # CLASSIFY QUERY FIRST
#     is_legal, reason = QueryClassifier.is_legal_scenario(request.scenario)
#     log.info(f"Query classified: is_legal={is_legal}, reason={reason}, query='{request.scenario[:50]}...'")
    
#     # For non-legal queries, return helpful guidance
#     if not is_legal:
#         log.info(f"Returning non-legal response for: {request.scenario[:50]}")
#         non_legal_response = QueryClassifier.get_non_legal_response(request.scenario, reason)
#         return non_legal_response
    
#     # For legal queries, proceed with AI analysis
#     api_key = resolve_api_key(request.api_key)
    
#     # Build prompt with conversation history if available
#     user_message = f"""Jurisdiction: {request.jurisdiction}
# {'State: ' + request.state if request.state else ''}
# User Query: {request.scenario}"""

#     # Add conversation context for follow-ups
#     if request.conversation_history and len(request.conversation_history) > 0:
#         user_message += "\n\nPrevious conversation:\n"
#         for msg in request.conversation_history[-6:]:
#             role = msg.get("role", "unknown")
#             content = msg.get("content", "")
#             role_label = "USER" if role.lower() in ["user", "human"] else "ASSISTANT"
#             user_message += f"{role_label}: {content}\n"
#         user_message += "\nPlease answer based on the above conversation context."
    
#     start = time.perf_counter()
#     log.info(f"Analyzing query | jurisdiction={request.jurisdiction} | length={len(request.scenario)}")
    
#     try:
#         result = await call_mistral(api_key, user_message)
        
#         elapsed = time.perf_counter() - start
#         log.info(f"Analysis complete | {elapsed:.1f}s | severity={result.get('severity', '?')}")
        
#         # Add metadata to response
#         result["is_legal_query"] = True
#         result["classification_reason"] = reason
        
#         return result
    
#     except json.JSONDecodeError as e:
#         log.error(f"JSON parse error: {e}")
#         return {
#             "applicable_laws": [],
#             "consequences": [],
#             "recommendations": [{
#                 "action": "Provide more details",
#                 "priority": "Immediate",
#                 "description": "Could you please provide more information about your legal situation?"
#             }],
#             "severity": "Low",
#             "summary": "I understand you have a legal question. Could you please provide more details so I can give you proper legal guidance?",
#             "disclaimer": "This is an automated response.",
#             "is_legal_query": True
#         }
#     except Exception as e:
#         log.error(f"Analysis error: {e}")
#         raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# @app.get("/health", summary="Health check", tags=["System"])
# async def health_check():
#     return {
#         "status": "healthy",
#         "service": "NyayaAI API",
#         "version": "2.1.0",
#         "features": {
#             "query_classification": "enabled (150+ keywords)",
#             "anti_hallucination": "active",
#             "legal_framework": "BNS/BNSS/BSA 2023",
#             "follow_up_support": "enabled"
#         },
#         "cache_enabled": ENABLE_CACHE,
#         "rate_limit": RATE_LIMIT_PER_MINUTE
#     }

# @app.get("/config", summary="Configuration", tags=["System"])
# async def get_config():
#     return {
#         "default_jurisdiction": DEFAULT_JURISDICTION,
#         "max_scenario_length": MAX_SCENARIO_LENGTH,
#         "valid_jurisdictions": VALID_JURISDICTIONS,
#         "query_classification": True,
#         "keywords_count": 150,
#         "follow_up_support": True,
#         "features": {
#             "caching": ENABLE_CACHE,
#             "rate_limiting": RATE_LIMIT_PER_MINUTE,
#             "pii_redaction": REDACT_PII,
#             "profanity_filter": FILTER_PROFANITY
#         },
#         "server_key_configured": bool(MISTRAL_API_KEY),
#         "allow_user_api_key": ALLOW_USER_API_KEY
#     }

# # ── Entry point ───────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)


# import os
# import json
# import logging
# import time
# import asyncio
# from contextlib import asynccontextmanager
# from typing import Optional, List, Dict, Any, Tuple
# from datetime import datetime
# from bson import ObjectId
# from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
# from pymongo.errors import DuplicateKeyError

# from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Query
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel, Field, field_validator
# from dotenv import load_dotenv
# import re

# # ── Load .env ─────────────────────────────────────────────────────────────────
# load_dotenv()

# # ── Config from environment ───────────────────────────────────────────────────
# MISTRAL_API_KEY      = os.getenv("MISTRAL_API_KEY", "").strip()
# MISTRAL_MODEL        = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
# MAX_TOKENS           = int(os.getenv("MAX_TOKENS", "4000"))
# TEMPERATURE          = float(os.getenv("TEMPERATURE", "0.2"))
# HOST                 = os.getenv("HOST", "0.0.0.0")
# PORT                 = int(os.getenv("PORT", "8000"))
# DEFAULT_JURISDICTION = os.getenv("DEFAULT_JURISDICTION", "India")
# ALLOW_USER_API_KEY   = os.getenv("ALLOW_USER_API_KEY", "true").lower() == "true"
# MAX_SCENARIO_LENGTH  = int(os.getenv("MAX_SCENARIO_LENGTH", "5000"))

# # MongoDB Configuration
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
# MONGODB_DB = os.getenv("MONGODB_DB", "nyayaai")
# CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
# MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
# RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
# ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
# FILTER_PROFANITY = os.getenv("FILTER_PROFANITY", "true").lower() == "true"
# REDACT_PII = os.getenv("REDACT_PII", "true").lower() == "true"

# # ── Logging ───────────────────────────────────────────────────────────────────
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
#     datefmt="%H:%M:%S",
# )
# log = logging.getLogger("nyayaai")

# # ── MongoDB Connection ─────────────────────────────────────────────────────────
# class MongoDB:
#     _instance = None
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance.client = MongoClient(MONGODB_URL)
#             cls._instance.db = cls._instance.client[MONGODB_DB]
#             cls._instance.blogs = cls._instance.db.blogs
#             cls._instance.categories = cls._instance.db.categories
            
#             # Create indexes
#             cls._instance.blogs.create_index([("title", TEXT), ("content", TEXT), ("tags", TEXT)])
#             cls._instance.blogs.create_index([("category", ASCENDING)])
#             cls._instance.blogs.create_index([("author", ASCENDING)])
#             cls._instance.blogs.create_index([("created_at", DESCENDING)])
#             cls._instance.blogs.create_index([("views", DESCENDING)])
#             cls._instance.blogs.create_index([("likes", DESCENDING)])
            
#             log.info(f"Connected to MongoDB: {MONGODB_DB}")
#         return cls._instance

# # ── Pydantic Models ───────────────────────────────────────────────────────────
# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid objectid")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")

# class BlogPost(BaseModel):
#     id: Optional[str] = Field(default=None, alias="_id")
#     title: str
#     slug: str
#     content: str
#     excerpt: str
#     category: str
#     sub_category: Optional[str] = None
#     tags: List[str] = []
#     author: str
#     author_avatar: Optional[str] = None
#     read_time: int = 5
#     views: int = 0
#     likes: int = 0
#     is_published: bool = True
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     meta_description: Optional[str] = None
#     featured_image: Optional[str] = None
#     references: List[str] = []
#     related_laws: List[str] = []
    
#     class Config:
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         populate_by_name = True

# class BlogPostCreate(BaseModel):
#     title: str
#     content: str
#     excerpt: str
#     category: str
#     sub_category: Optional[str] = None
#     tags: List[str] = []
#     author: str
#     author_avatar: Optional[str] = None
#     read_time: int = 5
#     meta_description: Optional[str] = None
#     featured_image: Optional[str] = None
#     references: List[str] = []
#     related_laws: List[str] = []
    
#     @field_validator("title")
#     def validate_title(cls, v):
#         if len(v) < 5:
#             raise ValueError("Title must be at least 5 characters")
#         return v
    
#     @field_validator("content")
#     def validate_content(cls, v):
#         if len(v) < 50:
#             raise ValueError("Content must be at least 50 characters")
#         return v

# class BlogPostUpdate(BaseModel):
#     title: Optional[str] = None
#     content: Optional[str] = None
#     excerpt: Optional[str] = None
#     category: Optional[str] = None
#     sub_category: Optional[str] = None
#     tags: Optional[List[str]] = None
#     is_published: Optional[bool] = None
#     meta_description: Optional[str] = None
#     featured_image: Optional[str] = None
#     references: Optional[List[str]] = None
#     related_laws: Optional[List[str]] = None

# class SearchQuery(BaseModel):
#     q: str = ""
#     category: Optional[str] = None
#     tag: Optional[str] = None
#     author: Optional[str] = None
#     page: int = 1
#     limit: int = 10
#     sort_by: str = "created_at"
#     sort_order: str = "desc"

# class Category(BaseModel):
#     name: str
#     slug: str
#     description: str
#     icon: str
#     post_count: int = 0

# # ── Sample Blog Data to Seed MongoDB ──────────────────────────────────────────
# SAMPLE_BLOGS = [
#     {
#         "title": "Complete Guide to Driving License in India",
#         "slug": "driving-license-guide-india",
#         "content": """
# # Complete Guide to Getting and Renewing Driving License in India

# ## Introduction
# A driving license is an official document that authorizes an individual to operate motor vehicles on public roads. In India, the Motor Vehicles Act, 1988 governs the issuance and regulation of driving licenses.

# ## Types of Driving Licenses

# ### 1. Learner's License
# - Valid for 6 months
# - Requires passing a written test
# - Must display 'L' plate on vehicle
# - Cannot drive alone (accompanied by licensed driver)

# ### 2. Permanent Driving License
# - Issued after 30 days of learner's license
# - Requires passing driving test at RTO
# - Valid for 20 years or until age 50
# - Renewal required every 5 years after age 50

# ### 3. Commercial Driving License
# - For transport vehicles (trucks, buses, taxis)
# - Requires additional medical certificate
# - Age requirement: 20-45 years
# - Includes badge endorsement

# ## Documents Required

# ### For Learner's License
# - Age proof (Birth certificate, Passport, 10th marksheet)
# - Address proof (Aadhaar, Voter ID, Passport)
# - Passport size photographs (3-4)
# - Medical certificate (Form 1A for commercial vehicles)

# ### For Permanent License
# - Learner's license (original)
# - Learner's license completion certificate
# - Driving test application (Form 4)
# - Fee payment receipt

# ## Step-by-Step Process

# ### Step 1: Apply for Learner's License
# 1. Visit nearest RTO or apply online at parivahan.gov.in
# 2. Fill Form 1 (application for learner's license)
# 3. Submit documents and pay fee (₹150-200)
# 4. Take written/online test
# 5. Pass test to receive learner's license

# ### Step 2: Practice Driving
# - Practice for minimum 30 days with learner's license
# - Always carry learner's license while driving
# - Display 'L' plate clearly on vehicle

# ### Step 3: Apply for Permanent License
# 1. After 30 days, apply for permanent license
# 2. Fill Form 4 online or at RTO
# 3. Schedule driving test appointment
# 4. Pay applicable fees (₹300-500)

# ### Step 4: Take Driving Test
# - Bring your own vehicle for test
# - Demonstrate parking, handling, and road driving
# - Show knowledge of traffic rules
# - Pass test to receive permanent license

# ## Penalties for Violations

# | Offense | Penalty |
# |---------|---------|
# | Driving without license | ₹5,000 fine |
# | Driving with expired license | ₹1,000 fine |
# | No 'L' plate on learner's vehicle | ₹1,000 fine |
# | Learner driving alone | ₹2,000 fine |
# | Underage driving | ₹25,000 fine + license at 25 years |

# ## Renewal Process

# ### Online Renewal
# 1. Visit parivahan.gov.in
# 2. Click on "Driving License Related Services"
# 3. Select your state and RTO
# 4. Choose "Renewal of Driving License"
# 5. Upload documents and pay fee
# 6. Download temporary license immediately

# ### Offline Renewal
# 1. Visit RTO with old license
# 2. Fill Form 9 (renewal application)
# 3. Submit medical certificate (if over 40)
# 4. Pay renewal fee
# 5. Receive new license in 7-10 days

# ## Lost or Damaged License

# ### Duplicate License Process
# 1. File FIR at nearest police station (if stolen)
# 2. Visit RTO with FIR copy
# 3. Fill Form 2 (duplicate license)
# 4. Submit affidavit of loss
# 5. Pay duplicate license fee (₹250-400)
# 6. Get duplicate license within 15 days

# ## Important Tips

# 1. **Always carry license**: Keep original or digital license (DigiLocker/ mParivahan)

# 2. **Check expiration**: Renew 30 days before expiry to avoid penalties

# 3. **International Driving Permit**: Get IDP before traveling abroad (valid for 1 year)

# 4. **Digital license is valid**: Supreme Court recognizes digital license from DigiLocker or mParivahan app

# 5. **Medical checkup**: Required for commercial license and after age 50

# ## Common FAQs

# **Q: Can I drive with a digital license?**
# A: Yes, digital license from DigiLocker or mParivahan app is legally valid.

# **Q: What if I forget my license at home?**
# A: Show digital license from app. If traffic police insists, you have 15 days to produce original license.

# **Q: Is international driving license valid in India?**
# A: Yes, if it's an International Driving Permit (IDP) issued under Geneva Convention 1949.

# **Q: Can I apply for driving license online?**
# A: Yes, complete process from learner's to permanent license is available online at parivahan.gov.in.

# ## Latest Updates (2024)

# - Digital license now mandatory for new licenses
# - Online driving test introduced in major cities
# - QR code on license contains all vehicle owner details
# - AI-based tracking of traffic violations

# ## Conclusion

# Getting a driving license in India is straightforward if you follow the proper procedure. Always ensure you have a valid license while driving to avoid heavy penalties. Use the online portal for faster processing and keep digital copy handy for emergencies.
#         """,
#         "excerpt": "Complete step-by-step guide to obtain, renew, and replace driving license in India. Learn about documents, fees, online process, penalties, and latest updates.",
#         "category": "Motor Vehicle Laws",
#         "sub_category": "Driving License",
#         "tags": ["driving license", "RTO", "learner license", "permanent license", "traffic rules", "motor vehicles act"],
#         "author": "Advocate Rajesh Sharma",
#         "author_avatar": "https://ui-avatars.com/api/?name=Rajesh+Sharma&background=0D9488&color=fff",
#         "read_time": 12,
#         "meta_description": "Complete guide to Indian driving license - types, documents, process, fees, penalties, renewal, and duplicate license. Updated for 2024.",
#         "related_laws": ["Motor Vehicles Act, 1988", "Central Motor Vehicles Rules, 1989"],
#         "references": ["Motor Vehicles Act, 1988", "parivahan.gov.in", "Supreme Court judgments on digital license"]
#     },
#     {
#         "title": "Consumer Protection Act 2019: Your Rights as a Consumer",
#         "slug": "consumer-protection-act-2019-rights",
#         "content": """
# # Consumer Protection Act, 2019: Complete Guide to Your Rights

# ## Overview
# The Consumer Protection Act, 2019 replaced the 1986 Act, strengthening consumer rights and introducing modern provisions for e-commerce, product liability, and mediation.

# ## Key Changes in 2019 Act

# ### 1. Central Consumer Protection Authority (CCPA)
# - Established to regulate consumer rights violations
# - Can impose penalties for false/misleading advertisements
# - Has power to recall unsafe products

# ### 2. Enhanced Pecuniary Jurisdiction
# - District Commission: Up to ₹1 crore
# - State Commission: ₹1 crore to ₹10 crore
# - National Commission: Above ₹10 crore

# ### 3. Product Liability
# - Manufacturer liable for defective products
# - Service provider liable for deficient services
# - Seller can be held liable in some cases

# ### 4. E-commerce Regulations
# - Covers online transactions and marketplaces
# - Sellers cannot refuse returns if product is defective
# - Liability for misleading product descriptions

# ## Six Consumer Rights

# ### 1. Right to Safety
# Protection against goods and services hazardous to life and health.

# ### 2. Right to Information
# Full disclosure about quality, quantity, potency, purity, standard, and price.

# ### 3. Right to Choose
# Access to variety of goods and services at competitive prices.

# ### 4. Right to be Heard
# Consumer interests will receive due consideration in appropriate forums.

# ### 5. Right to Redressal
# Claim settlement against unfair trade practices or exploitation.

# ### 6. Right to Consumer Education
# Knowledge about rights and remedies available.

# ## Filing a Complaint

# ### Step-by-Step Process

# **Step 1: Send Legal Notice**
# - Send notice to opposite party (seller/manufacturer)
# - Give 15-30 days to respond
# - Mention defect/deficiency clearly

# **Step 2: File Complaint**
# - Determine appropriate forum based on claim value
# - Submit complaint with supporting documents
# - Pay nominal court fees (₹100-5000)

# **Step 3: Admission Hearing**
# - Forum admits complaint within 21 days
# - If rejected, reasons must be recorded

# **Step 4: Notice to Opposite Party**
# - Forum issues notice to opposite party
# - 30 days to file written response

# **Step 5: Evidence and Arguments**
# - Parties submit evidence (bills, photos, expert reports)
# - Arguments before commission

# **Step 6: Judgment**
# - Commission passes order within 3-5 months
# - Provides compensation, refund, or replacement

# ## Documents Required

# - Copy of bill/invoice
# - Warranty/guarantee card
# - Proof of payment (credit card statement, bank statement)
# - Photographs/videos of defective product
# - Expert opinion (if needed)
# - Correspondence with seller
# - Legal notice copy

# ## Time Limits

# | Action | Time Limit |
# |--------|------------|
# | Complaint admission | 21 days |
# | Written statement | 30 days (max 45) |
# | Evidence submission | 30 days |
# | Judgment (no expert) | 3 months |
# | Judgment (with expert) | 5 months |
# | Appeal to higher forum | 30 days |
# | Appeal to Supreme Court | 90 days |

# ## Penalties for Violations

# | Violation | Penalty |
# |-----------|---------|
# | Defective goods | Replacement/refund + compensation |
# | Deficient service | Compensation + litigation costs |
# | Unfair trade practice | Compensation + punitive damages |
# | Misleading ad | ₹10 lakh fine (manufacturer/endorser) |
# | Frivolous complaint | ₹50,000 fine |
# | Non-compliance of order | Imprisonment (1-3 years) + fine |

# ## E-commerce Specific Provisions

# ### Responsibilities of E-commerce Entities
# - Display all product details authentically
# - Provide clear refund/return policy
# - Acknowledge order receipt within 24 hours
# - Enable consumer grievance redressal
# - Cannot charge cancellation fees without disclosure

# ### Consumer Rights in Online Shopping
# - Right to cancel order before shipment
# - Right to refund for defective products
# - Right to know seller details
# - Right to product authenticity guarantee

# ## Mediation as Alternative Dispute Resolution

# ### Advantages of Mediation
# - Faster resolution (30-45 days)
# - Less expensive than litigation
# - Voluntary and confidential
# - Preserves business relationships

# ### Mediation Process
# 1. Both parties agree to mediation
# 2. Commission appoints mediator
# 3. Mediation sessions (max 3)
# 4. Settlement agreement signed
# 5. Commission passes order based on agreement

# ## Landmark Judgments

# ### 1. Indian Medical Association v. V.P. Shantha (1995)
# **Significance**: Medical services included under 'service' for consumer complaints.

# ### 2. Lucknow Development Authority v. M.K. Gupta (1994)
# **Significance**: Housing authorities covered under Consumer Act.

# ### 3. Spring Meadows Hospital v. Harjol Ahluwalia (1998)
# **Significance**: Medical negligence against child covered.

# ## Filing Online Complaint

# ### Steps for e-Daakhil Portal
# 1. Visit edaakhil.nic.in
# 2. Register with mobile number and email
# 3. Fill complaint form with details
# 4. Upload documents (PDF format)
# 5. Pay fees online
# 6. Track case status online

# ## Tips for Successful Complaint

# 1. **Preserve evidence**: Keep bills, photos, videos, emails
# 2. **Send legal notice**: Always send notice before filing complaint
# 3. **Choose right forum**: Calculate claim value correctly
# 4. **Be specific**: Clearly mention defect/deficiency
# 5. **Respond promptly**: Reply to court notices on time
# 6. **Consider mediation**: Faster and cheaper for small claims

# ## Conclusion

# The Consumer Protection Act 2019 is a powerful tool for consumers. Understanding your rights and the complaint process can help you get justice for defective products or deficient services. Always keep documentation and approach the correct consumer forum for faster resolution.
#         """,
#         "excerpt": "Complete guide to Consumer Protection Act 2019: Know your 6 consumer rights, filing complaints, e-commerce rules, penalties, and landmark judgments.",
#         "category": "Consumer Law",
#         "sub_category": "Consumer Rights",
#         "tags": ["consumer rights", "consumer court", "defective product", "refund", "compensation", "e-commerce"],
#         "author": "Advocate Priya Singh",
#         "author_avatar": "https://ui-avatars.com/api/?name=Priya+Singh&background=0D9488&color=fff",
#         "read_time": 15,
#         "meta_description": "Consumer Protection Act 2019 explained - rights, complaint process, e-commerce rules, penalties, and landmark judgments. Guide for Indian consumers.",
#         "related_laws": ["Consumer Protection Act, 2019", "Legal Metrology Act, 2009", "Food Safety Act, 2006"],
#         "references": ["Consumer Protection Act 2019", "Ministry of Consumer Affairs", "Supreme Court judgments"]
#     },
#     {
#         "title": "Domestic Violence Act 2005: Protection and Remedies",
#         "slug": "domestic-violence-act-2005-protection",
#         "content": """
# # Protection of Women from Domestic Violence Act, 2005

# ## Introduction
# The Protection of Women from Domestic Violence Act, 2005 (PWDVA) is a landmark legislation that provides comprehensive protection to women against domestic violence. It recognizes domestic violence as a human rights violation.

# ## Definition of Domestic Violence

# ### Physical Abuse
# - Assault, battery, physical injury
# - Forced sexual intercourse
# - Denial of medical facilities

# ### Emotional and Verbal Abuse
# - Insults, ridicule, humiliation
# - Threats of physical violence
# - Verbal aggression

# ### Economic Abuse
# - Denial of household necessities
# - Prohibiting employment
# - Forced to hand over earnings
# - Selling/alienating stridhan

# ### Sexual Abuse
# - Forced sexual activity
# - Demanding dowry
# - Forced pregnancy termination

# ## Who Can File Complaint

# ### Aggrieved Person
# - Any woman in domestic relationship
# - Includes mother, sister, daughter, widow
# - Includes live-in partners

# ### Who Can File on Her Behalf
# - Protection Officer
# - Service provider
# - Magistrate can initiate suo moto

# ## Rights Under the Act

# ### 1. Right to Residence
# - Cannot be evicted from shared household
# - Right to live in matrimonial home
# - Alternative accommodation rights

# ### 2. Right to Protection Orders
# - Protection from further violence
# - Respondent restrained from contacting
# - Cannot enter workplace/school

# ### 3. Right to Monetary Relief
# - Maintenance for self and children
# - Compensation for injuries/loss
# - Medical expense reimbursement

# ### 4. Right to Custody of Children
# - Temporary custody granted
# - Visitation rights for respondent
# - Child's welfare paramount

# ## How to File Complaint

# ### Step 1: Contact Protection Officer
# - Protection Officer appointed by state
# - Free service provided
# - Files Domestic Incident Report

# ### Step 2: Approach Magistrate
# - Magistrate can pass protection orders
# - Can grant interim relief within 3 days
# - Final orders within 60 days

# ### Step 3: Get Protection Order
# - Prohibits respondent from committing violence
# - May include counseling orders
# - Valid until aggrieved applies for discharge

# ## Types of Orders

# ### Protection Orders
# - Prohibits violence and threats
# - Stops communication channels
# - Restricts entry to workplace

# ### Residence Orders
# - Right to stay in shared household
# - Cannot be dispossessed
# - Alternative residence direction

# ### Monetary Relief Orders
# - Monthly maintenance payment
# - Compensation for medical expenses
# - Loss of earnings compensation

# ### Custody Orders
# - Temporary custody of children
# - Visitation rights specified
# - Child's preference considered

# ## Penalties for Violation

# | Violation | Penalty |
# |-----------|---------|
# | Breach of protection order | Imprisonment up to 1 year + ₹20,000 fine |
# | Multiple violations | Imprisonment up to 3 years + fine |
# | False complaint | Magistrate can order compensation |

# ## Support Services

# ### Protection Officers
# - Appointed by state government
# - Free legal aid assistance
# - Maintain confidentiality

# ### Service Providers
# - Registered NGOs recognized
# - Provide shelter and counseling
# - Medical facility access

# ### Shelter Homes
# - Short-stay accommodation
# - Food and medical facilities
# - Legal aid referral

# ## Recent Amendments and Rules

# ### Domestic Violence Rules 2013
# - Faster complaint processing
# - Electronic evidence admissible
# - Mandatory training for Protection Officers

# ### Recent Supreme Court Guidelines
# - Includes live-in relationships
# - Siblings can claim protection
# - Same-sex partners included

# ## Practical Tips for Victims

# 1. **Document Everything**
#    - Take photos of injuries
#    - Save threatening messages/emails
#    - Maintain diary of incidents

# 2. **Get Medical Help**
#    - Visit doctor immediately
#    - Collect medical reports
#    - Preserve treatment records

# 3. **Contact Support Network**
#    - Reach out to family/friends
#    - Contact NGO helplines
#    - Call women helpline (181)

# 4. **Legal Documentation**
#    - File complaint immediately
#    - Get copy of FIR
#    - Record statement before magistrate

# 5. **Financial Independence**
#    - Open separate bank account
#    - Keep important documents safe
#    - Apply for monetary relief

# ## Important Helplines

# | Service | Number |
# |---------|--------|
# | Women Helpline | 181 |
# | National Commission for Women | 7827170170 |
# | Police (Emergency) | 100 |
# | Child Helpline | 1098 |

# ## Landmark Judgments

# ### 1. Indra Sarma v. V.K.V. Sarma (2013)
# **Significance**: Live-in relationships covered under DV Act.

# ### 2. Sandhya Manoj Wankhade v. Manoj Bhimrao Wankhade (2011)
# **Significance**: Economic abuse includes denial of household expenses.

# ### 3. Hiral P. Harsora v. Kusum Narottamdas Harsora (2016)
# **Significance**: Sisters-in-law can be respondents.

# ## International Framework

# - Matches UN Declaration on Violence Against Women
# - Supports CEDAW commitments
# - Modelled on UK Domestic Violence Act

# ## Conclusion

# The Domestic Violence Act 2005 provides comprehensive protection and remedies for women facing abuse. Understanding your rights and the legal process helps in seeking timely justice. Reach out to Protection Officers or NGOs immediately if facing violence.
#         """,
#         "excerpt": "Complete guide to Domestic Violence Act 2005: Rights, protection orders, monetary relief, custody, and how to file complaint. Know your legal remedies.",
#         "category": "Family Law",
#         "sub_category": "Domestic Violence",
#         "tags": ["domestic violence", "women protection", "protection order", "maintenance", "shelter", "abuse"],
#         "author": "Advocate Meera Desai",
#         "author_avatar": "https://ui-avatars.com/api/?name=Meera+Desai&background=0D9488&color=fff",
#         "read_time": 12,
#         "meta_description": "Protection of Women from Domestic Violence Act 2005 explained - rights, protection orders, monetary relief, custody, complaint process, and helplines.",
#         "related_laws": ["Indian Penal Code (Section 498A)", "Dowry Prohibition Act, 1961", "Family Courts Act, 1984"],
#         "references": ["Protection of Women from Domestic Violence Act 2005", "Supreme Court judgments", "NCW guidelines"]
#     },
#     {
#         "title": "Rights of Arrested Person under CrPC",
#         "slug": "rights-of-arrested-person-crpc",
#         "content": """
# # Rights of Arrested Person under Code of Criminal Procedure

# ## Fundamental Rights
# The Constitution of India and CrPC provide several rights to protect arrested persons from arbitrary arrest and detention.

# ## Key Rights of Arrested Person

# ### 1. Right to Know Grounds of Arrest (Article 22(1))
# - Must be informed of grounds immediately
# - Details in writing if arrest with warrant
# - Cannot be kept in dark about accusations

# ### 2. Right to Consult Lawyer (Article 22(1))
# - Can consult lawyer of choice
# - Lawyer can be present during interrogation
# - Legal Aid for poor (Article 39A)

# ### 3. Right to be Produced Before Magistrate (Article 22(2))
# - Within 24 hours of arrest
# - Excluding travel time from place of arrest
# - Magistrate can authorize detention

# ### 4. Right to Medical Examination
# - At time of arrest
# - At request of arrested person
# - Female arrested examined by female doctor

# ### 5. Right to Inform Family/Friend
# - Police must inform relative/friend
# - Immediately after arrest
# - Free legal aid if needed

# ## Arrest Procedure

# ### With Warrant
# 1. Police officer shows warrant
# 2. Touches or confines body
# 3. Informs grounds of arrest
# 4. Produces before magistrate within 24 hours

# ### Without Warrant (Cognizable Offences)
# 1. Police can arrest without warrant
# 2. Must inform grounds
# 3. Right to bail in bailable offences
# 4. Production within 24 hours

# ### Arrest by Private Person
# 1. Can arrest for non-bailable offence
# 2. Must produce before police without delay
# 3. Police may re-arrest if evidence exists

# ## Rights During Interrogation

# ### Right to Silence
# - Cannot be forced to confess
# - Confession before police not admissible
# - Judicial confession has evidentiary value

# ### Right to Lawyer
# - Lawyer can be present during interrogation
# - Not allowed during police custody (only magistrate)
# - Article 20(3) - right against self-incrimination

# ### Right against Double Jeopardy (Article 20(2))
# - Cannot be prosecuted twice for same offence
# - Autrefois convict protection

# ## Rights After Arrest

# ### Right to Bail
# - **Bailable offences**: Bail as right
# - **Non-bailable offences**: Discretionary bail
# - **Anticipatory bail**: Before arrest for non-bailable

# ### Right to Speedy Trial (Article 21)
# - Trial within reasonable time
# - Cannot be detained indefinitely
# - Right to fair investigation

# ### Right to Free Legal Aid (Article 39A)
# - For poor and indigent persons
# - State must provide lawyer
# - At trial and appeal stages

# ## Police Custody vs Judicial Custody

# ### Police Custody
# - Interrogation by police
# - Maximum 15 days initially
# - Extendable to 60-90 days

# ### Judicial Custody
# - Jail custody under magistrate
# - Better facilities
# - Family can meet

# ### Remand Procedure
# - Police seek remand within 24 hours
# - Magistrate authorizes custody
# - Must give reasons in writing

# ## Important Judgments

# ### 1. D.K. Basu v. State of West Bengal (1997)
# **Significance**: Laid down guidelines for arrest and custody:
# - Police must wear name tag/ID
# - Memo of arrest prepared
# - Relatives informed
# - Medical examination done

# ### 2. Joginder Kumar v. State of UP (1994)
# **Significance**: Cannot arrest for minor offences without justification.

# ### 3. Hussainara Khatoon v. State of Bihar (1979)
# **Significance**: Right to speedy trial fundamental under Article 21.

# ## What to Do If Arrested

# ### Immediate Steps
# 1. **Stay calm**: Don't resist arrest physically
# 2. **Ask reason**: Demand to know grounds in writing
# 3. **Call lawyer**: Exercise right immediately
# 4. **Inform family**: Ask police to notify relative
# 5. **Request medical**: Physical examination at arrest
# 6. **Don't sign blank**: Read before signing any document

# ### Dos and Don'ts
# **DO**:
# - Cooperate with police
# - Ask for arrest memo
# - Keep copy of all documents
# - Apply for bail immediately
# - Seek legal aid if poor

# **DON'T**:
# - Sign statements under pressure
# - Destroy evidence
# - Try to escape
# - Attack police officer
# - Make extra-judicial confession

# ## Zero FIR and E-FIR

# ### Zero FIR
# - Can be filed at any police station
# - Transferred to jurisdiction later
# - No delay in registration

# ### E-FIR
# - File online for certain offences
# - Printout submitted within 3 days
# - Valid for cognizable offences

# ## Role of Magistrate

# ### Duties
# - Verify arrest legality
# - Authorize detention beyond 24 hours
# - Grant bail where appropriate
# - Ensure rights are protected

# ### Powers
# - Order medical examination
# - Grant interim bail
# - Direct police investigation
# - Quash illegal arrest

# ## Conclusion

# Understanding your rights as an arrested person is crucial. The law provides strong protections against arbitrary arrest and detention. Always exercise your right to lawyer and medical examination. Remember the DK Basu guidelines that prohibit torture and inhumane treatment in custody.
#         """,
#         "excerpt": "Complete guide to rights of arrested person under CrPC and Constitution. Know your rights - legal aid, bail, medical exam, and more.",
#         "category": "Criminal Law",
#         "sub_category": "Arrest and Bail",
#         "tags": ["arrest rights", "CrPC", "bail", "legal aid", "police custody", "fundamental rights"],
#         "author": "Advocate Vikram Reddy",
#         "author_avatar": "https://ui-avatars.com/api/?name=Vikram+Reddy&background=0D9488&color=fff",
#         "read_time": 10,
#         "meta_description": "Rights of arrested person under CrPC - right to lawyer, medical exam, bail, speedy trial, and DK Basu guidelines. Know your legal rights.",
#         "related_laws": ["Constitution of India (Articles 20-22)", "Code of Criminal Procedure, 1973", "Indian Penal Code"],
#         "references": ["Supreme Court judgments on arrest", "CrPC Sections 50-60", "NCSC guidelines"]
#     }
# ]

# # ── MongoDB Operations ─────────────────────────────────────────────────────────
# class BlogRepository:
#     def __init__(self):
#         self.db = MongoDB().db
#         self.blogs = self.db.blogs
#         self.categories = self.db.categories
    
#     def seed_initial_data(self):
#         """Seed initial blog posts if database is empty"""
#         if self.blogs.count_documents({}) == 0:
#             for blog in SAMPLE_BLOGS:
#                 blog["created_at"] = datetime.utcnow()
#                 blog["updated_at"] = datetime.utcnow()
#                 self.blogs.insert_one(blog)
#             log.info(f"Seeded {len(SAMPLE_BLOGS)} sample blog posts")
    
#     def create_blog(self, blog_data: dict) -> str:
#         """Create a new blog post"""
#         blog_data["created_at"] = datetime.utcnow()
#         blog_data["updated_at"] = datetime.utcnow()
#         blog_data["views"] = 0
#         blog_data["likes"] = 0
#         result = self.blogs.insert_one(blog_data)
#         return str(result.inserted_id)
    
#     def get_blog(self, blog_id: str) -> Optional[dict]:
#         """Get blog by ID"""
#         try:
#             return self.blogs.find_one({"_id": ObjectId(blog_id), "is_published": True})
#         except:
#             return None
    
#     def get_blog_by_slug(self, slug: str) -> Optional[dict]:
#         """Get blog by slug"""
#         return self.blogs.find_one({"slug": slug, "is_published": True})
    
#     def search_blogs(self, query: str, category: str = None, tag: str = None, 
#                      author: str = None, page: int = 1, limit: int = 10,
#                      sort_by: str = "created_at", sort_order: str = "desc") -> Tuple[List[dict], int]:
#         """Search blogs with filters"""
#         filter_query = {"is_published": True}
        
#         # Text search
#         if query:
#             filter_query["$text"] = {"$search": query}
        
#         # Category filter
#         if category and category != "All":
#             filter_query["category"] = category
        
#         # Tag filter
#         if tag:
#             filter_query["tags"] = tag
        
#         # Author filter
#         if author:
#             filter_query["author"] = author
        
#         # Sort order
#         sort_direction = DESCENDING if sort_order == "desc" else ASCENDING
        
#         # Get total count
#         total = self.blogs.count_documents(filter_query)
        
#         # Get paginated results
#         skip = (page - 1) * limit
#         cursor = self.blogs.find(filter_query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        
#         blogs = list(cursor)
#         return blogs, total
    
#     def get_categories(self) -> List[dict]:
#         """Get all categories with post counts"""
#         pipeline = [
#             {"$match": {"is_published": True}},
#             {"$group": {"_id": "$category", "count": {"$sum": 1}}},
#             {"$sort": {"count": -1}}
#         ]
#         results = list(self.blogs.aggregate(pipeline))
#         return [{"name": r["_id"], "count": r["count"]} for r in results]
    
#     def get_tags(self) -> List[dict]:
#         """Get all tags with frequencies"""
#         pipeline = [
#             {"$match": {"is_published": True}},
#             {"$unwind": "$tags"},
#             {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
#             {"$sort": {"count": -1}},
#             {"$limit": 20}
#         ]
#         results = list(self.blogs.aggregate(pipeline))
#         return [{"name": r["_id"], "count": r["count"]} for r in results]
    
#     def get_authors(self) -> List[dict]:
#         """Get all authors with post counts"""
#         pipeline = [
#             {"$match": {"is_published": True}},
#             {"$group": {"_id": "$author", "count": {"$sum": 1}}},
#             {"$sort": {"count": -1}}
#         ]
#         results = list(self.blogs.aggregate(pipeline))
#         return [{"name": r["_id"], "count": r["count"]} for r in results]
    
#     def increment_views(self, blog_id: str):
#         """Increment view count"""
#         self.blogs.update_one({"_id": ObjectId(blog_id)}, {"$inc": {"views": 1}})
    
#     def like_blog(self, blog_id: str):
#         """Increment like count"""
#         self.blogs.update_one({"_id": ObjectId(blog_id)}, {"$inc": {"likes": 1}})
    
#     def update_blog(self, blog_id: str, update_data: dict) -> bool:
#         """Update blog post"""
#         update_data["updated_at"] = datetime.utcnow()
#         result = self.blogs.update_one(
#             {"_id": ObjectId(blog_id)},
#             {"$set": update_data}
#         )
#         return result.modified_count > 0
    
#     def delete_blog(self, blog_id: str) -> bool:
#         """Soft delete blog"""
#         result = self.blogs.update_one(
#             {"_id": ObjectId(blog_id)},
#             {"$set": {"is_published": False, "updated_at": datetime.utcnow()}}
#         )
#         return result.modified_count > 0
    
#     def get_related_blogs(self, blog_id: str, tags: List[str], limit: int = 3) -> List[dict]:
#         """Get related blogs based on tags"""
#         filter_query = {
#             "_id": {"$ne": ObjectId(blog_id)},
#             "is_published": True,
#             "tags": {"$in": tags}
#         }
#         return list(self.blogs.find(filter_query).sort("views", -1).limit(limit))

# # ── FastAPI App Setup ─────────────────────────────────────────────────────────
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     log.info("━" * 70)
#     log.info("  NyayaAI Legal Intelligence API v2.1.0 with MongoDB")
#     log.info("━" * 70)
    
#     # Initialize MongoDB and seed data
#     blog_repo = BlogRepository()
#     blog_repo.seed_initial_data()
    
#     log.info(f"MongoDB connected and seeded")
#     log.info(f"  API Docs        : http://{HOST}:{PORT}/docs")
#     log.info("━" * 70)
#     yield
#     log.info("Shutting down...")

# app = FastAPI(
#     title="NyayaAI — Legal Intelligence API with MongoDB",
#     description="AI-powered legal analysis with blog knowledge base",
#     version="2.1.0",
#     lifespan=lifespan
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── Blog API Endpoints ─────────────────────────────────────────────────────────
# blog_repo = BlogRepository()

# @app.get("/api/blogs/search")
# async def search_blogs(
#     q: str = Query("", description="Search query"),
#     category: str = Query(None, description="Filter by category"),
#     tag: str = Query(None, description="Filter by tag"),
#     author: str = Query(None, description="Filter by author"),
#     page: int = Query(1, ge=1, description="Page number"),
#     limit: int = Query(10, ge=1, le=50, description="Results per page"),
#     sort_by: str = Query("created_at", description="Sort field"),
#     sort_order: str = Query("desc", description="Sort order (asc/desc)")
# ):
#     """Search for blog posts"""
#     blogs, total = blog_repo.search_blogs(q, category, tag, author, page, limit, sort_by, sort_order)
    
#     # Convert ObjectId to string
#     for blog in blogs:
#         blog["_id"] = str(blog["_id"])
    
#     return {
#         "total": total,
#         "page": page,
#         "limit": limit,
#         "total_pages": (total + limit - 1) // limit,
#         "results": blogs
#     }

# @app.get("/api/blogs/{blog_id}")
# async def get_blog(blog_id: str):
#     """Get blog post by ID"""
#     blog = blog_repo.get_blog(blog_id)
#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog not found")
    
#     # Increment view count
#     blog_repo.increment_views(blog_id)
    
#     blog["_id"] = str(blog["_id"])
    
#     # Get related blogs
#     related = blog_repo.get_related_blogs(blog_id, blog.get("tags", []))
#     for rel in related:
#         rel["_id"] = str(rel["_id"])
    
#     return {"blog": blog, "related": related}

# @app.get("/api/blogs/slug/{slug}")
# async def get_blog_by_slug(slug: str):
#     """Get blog post by slug"""
#     blog = blog_repo.get_blog_by_slug(slug)
#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog not found")
    
#     blog_repo.increment_views(str(blog["_id"]))
#     blog["_id"] = str(blog["_id"])
    
#     related = blog_repo.get_related_blogs(str(blog["_id"]), blog.get("tags", []))
#     for rel in related:
#         rel["_id"] = str(rel["_id"])
    
#     return {"blog": blog, "related": related}

# @app.post("/api/blogs/{blog_id}/like")
# async def like_blog(blog_id: str):
#     """Like a blog post"""
#     success = blog_repo.like_blog(blog_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Blog not found")
#     return {"message": "Blog liked successfully"}

# @app.get("/api/categories")
# async def get_categories():
#     """Get all categories with post counts"""
#     categories = blog_repo.get_categories()
#     return {"categories": categories}

# @app.get("/api/tags")
# async def get_tags():
#     """Get all tags with frequencies"""
#     tags = blog_repo.get_tags()
#     return {"tags": tags}

# @app.get("/api/authors")
# async def get_authors():
#     """Get all authors with post counts"""
#     authors = blog_repo.get_authors()
#     return {"authors": authors}

# @app.post("/api/blogs")
# async def create_blog(blog: BlogPostCreate):
#     """Create a new blog post (admin endpoint)"""
#     slug = blog.title.lower().replace(" ", "-").replace("/", "-")
#     blog_dict = blog.model_dump()
#     blog_dict["slug"] = slug
#     blog_dict["views"] = 0
#     blog_dict["likes"] = 0
    
#     blog_id = blog_repo.create_blog(blog_dict)
#     return {"id": blog_id, "message": "Blog created successfully"}

# @app.put("/api/blogs/{blog_id}")
# async def update_blog(blog_id: str, blog: BlogPostUpdate):
#     """Update a blog post (admin endpoint)"""
#     update_data = {k: v for k, v in blog.model_dump().items() if v is not None}
#     success = blog_repo.update_blog(blog_id, update_data)
#     if not success:
#         raise HTTPException(status_code=404, detail="Blog not found")
#     return {"message": "Blog updated successfully"}

# @app.delete("/api/blogs/{blog_id}")
# async def delete_blog(blog_id: str):
#     """Delete a blog post (admin endpoint)"""
#     success = blog_repo.delete_blog(blog_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Blog not found")
#     return {"message": "Blog deleted successfully"}

# # ── Analytics Endpoints ────────────────────────────────────────────────────────
# @app.get("/api/analytics/popular")
# async def get_popular_blogs(limit: int = 6):
#     """Get most viewed blogs"""
#     blogs, _ = blog_repo.search_blogs("", limit=limit, sort_by="views", sort_order="desc")
#     for blog in blogs:
#         blog["_id"] = str(blog["_id"])
#     return {"results": blogs}

# @app.get("/api/analytics/recent")
# async def get_recent_blogs(limit: int = 6):
#     """Get most recent blogs"""
#     blogs, _ = blog_repo.search_blogs("", limit=limit, sort_by="created_at", sort_order="desc")
#     for blog in blogs:
#         blog["_id"] = str(blog["_id"])
#     return {"results": blogs}

# # ── Original Chat Analysis Endpoints ───────────────────────────────────────────
# # (Keep your existing chat analysis endpoints here - /analyze, /health, /config)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host=HOST, port=PORT, reload=True)

# # Add these imports at the top
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from passlib.context import CryptContext
# import jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from pydantic import BaseModel, EmailStr

# # Add these to your config section
# ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "your-secret-key-change-this")
# ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
# ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# # Password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Generate password hash (run once)
# # from passlib.hash import bcrypt
# # print(bcrypt.hash("your-password"))

# class AdminLogin(BaseModel):
#     username: str
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str

# class BlogPostCreateAdmin(BaseModel):
#     title: str
#     content: str
#     excerpt: str
#     category: str
#     sub_category: Optional[str] = None
#     tags: List[str] = []
#     author: str
#     author_avatar: Optional[str] = None
#     read_time: int = 5
#     meta_description: Optional[str] = None
#     featured_image: Optional[str] = None
#     references: List[str] = []
#     related_laws: List[str] = []

# class BlogPostResponse(BaseModel):
#     id: str
#     title: str
#     slug: str
#     excerpt: str
#     category: str
#     tags: List[str]
#     author: str
#     views: int
#     likes: int
#     is_published: bool
#     created_at: datetime
#     updated_at: datetime

# # Helper functions for admin auth
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# def verify_token(token: str):
#     try:
#         payload = jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.PyJWTError:
#         return None

# # Add to your app initialization
# security = HTTPBearer()

# # ─── Admin Authentication Endpoints ───────────────────────────────────────────
# @app.post("/api/admin/login", response_model=TokenResponse)
# async def admin_login(login: AdminLogin):
#     """Admin login endpoint"""
#     # For production, compare with hashed password from DB
#     # For now, simple check (implement proper hashing in production)
#     if login.username == ADMIN_USERNAME and login.password == os.getenv("ADMIN_PASSWORD", "admin123"):
#         access_token = create_access_token(
#             data={"sub": login.username, "role": "admin"},
#             expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         )
#         return {"access_token": access_token, "token_type": "bearer"}
#     raise HTTPException(status_code=401, detail="Invalid credentials")

# @app.post("/api/admin/blogs", response_model=dict)
# async def create_blog_admin(
#     blog: BlogPostCreateAdmin,
#     credentials: HTTPAuthorizationCredentials = Security(security)
# ):
#     """Create new blog post (admin only)"""
#     payload = verify_token(credentials.credentials)
#     if not payload or payload.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     # Generate slug from title
#     slug = blog.title.lower().replace(" ", "-").replace("/", "-").replace(":", "").replace(".", "")
#     slug = re.sub(r'[^a-z0-9-]', '', slug)
    
#     blog_dict = blog.model_dump()
#     blog_dict["slug"] = slug
#     blog_dict["views"] = 0
#     blog_dict["likes"] = 0
#     blog_dict["is_published"] = True
#     blog_dict["created_at"] = datetime.utcnow()
#     blog_dict["updated_at"] = datetime.utcnow()
    
#     result = blog_repo.blogs.insert_one(blog_dict)
#     return {"id": str(result.inserted_id), "slug": slug, "message": "Blog created successfully"}

# @app.put("/api/admin/blogs/{blog_id}")
# async def update_blog_admin(
#     blog_id: str,
#     blog: BlogPostCreateAdmin,
#     credentials: HTTPAuthorizationCredentials = Security(security)
# ):
#     """Update blog post (admin only)"""
#     payload = verify_token(credentials.credentials)
#     if not payload or payload.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     update_data = blog.model_dump()
#     update_data["updated_at"] = datetime.utcnow()
    
#     # Update slug if title changed
#     if "title" in update_data:
#         slug = update_data["title"].lower().replace(" ", "-").replace("/", "-")
#         update_data["slug"] = slug
    
#     result = blog_repo.blogs.update_one(
#         {"_id": ObjectId(blog_id)},
#         {"$set": update_data}
#     )
    
#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Blog not found")
    
#     return {"message": "Blog updated successfully"}

# @app.delete("/api/admin/blogs/{blog_id}")
# async def delete_blog_admin(
#     blog_id: str,
#     credentials: HTTPAuthorizationCredentials = Security(security)
# ):
#     """Delete blog post (admin only)"""
#     payload = verify_token(credentials.credentials)
#     if not payload or payload.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     result = blog_repo.blogs.delete_one({"_id": ObjectId(blog_id)})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Blog not found")
    
#     return {"message": "Blog deleted successfully"}

# @app.post("/api/admin/blogs/{blog_id}/publish")
# async def publish_blog(
#     blog_id: str,
#     credentials: HTTPAuthorizationCredentials = Security(security)
# ):
#     """Publish/unpublish blog post"""
#     payload = verify_token(credentials.credentials)
#     if not payload or payload.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     blog = blog_repo.blogs.find_one({"_id": ObjectId(blog_id)})
#     if not blog:
#         raise HTTPException(status_code=404, detail="Blog not found")
    
#     new_status = not blog.get("is_published", True)
#     result = blog_repo.blogs.update_one(
#         {"_id": ObjectId(blog_id)},
#         {"$set": {"is_published": new_status, "updated_at": datetime.utcnow()}}
#     )
    
#     return {"is_published": new_status, "message": f"Blog {'published' if new_status else 'unpublished'} successfully"}

# @app.get("/api/admin/blogs")
# async def get_all_blogs_admin(
#     page: int = Query(1, ge=1),
#     limit: int = Query(20, ge=1, le=100),
#     credentials: HTTPAuthorizationCredentials = Security(security)
# ):
#     """Get all blogs (admin only) - includes unpublished"""
#     payload = verify_token(credentials.credentials)
#     if not payload or payload.get("role") != "admin":
#         raise HTTPException(status_code=403, detail="Not authorized")
    
#     skip = (page - 1) * limit
#     total = blog_repo.blogs.count_documents({})
#     blogs = list(blog_repo.blogs.find({}).sort("created_at", DESCENDING).skip(skip).limit(limit))
    
#     for blog in blogs:
#         blog["_id"] = str(blog["_id"])
    
#     return {
#         "total": total,
#         "page": page,
#         "limit": limit,
#         "total_pages": (total + limit - 1) // limit,
#         "results": blogs
#     }