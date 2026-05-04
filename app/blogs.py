import os
import logging
import re
from contextlib import asynccontextmanager
from typing import Optional, List, Tuple
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from dotenv import load_dotenv


load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB  = os.getenv("MONGODB_DB",  "nyayaai")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("nyayaai.blogs")


# ── MongoDB ────────────────────────────────────────────────────────────────────
class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(MONGODB_URL)
            cls._instance.db     = cls._instance.client[MONGODB_DB]
            cls._instance.blogs  = cls._instance.db.blogs
            cls._instance.categories = cls._instance.db.categories

            cls._instance.blogs.create_index([("title", TEXT), ("content", TEXT), ("tags", TEXT)])
            cls._instance.blogs.create_index([("category", ASCENDING)])
            cls._instance.blogs.create_index([("author",   ASCENDING)])
            cls._instance.blogs.create_index([("created_at", DESCENDING)])
            cls._instance.blogs.create_index([("views",    DESCENDING)])
            cls._instance.blogs.create_index([("likes",    DESCENDING)])
            log.info(f"Connected to MongoDB: {MONGODB_DB}")
        return cls._instance


# ── Pydantic Models ────────────────────────────────────────────────────────────
class BlogPost(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    slug: str
    content: str
    excerpt: str
    category: str
    sub_category: Optional[str] = None
    tags: List[str] = []
    author: str
    author_avatar: Optional[str] = None
    read_time: int = 5
    views: int = 0
    likes: int = 0
    is_published: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None
    references: List[str] = []
    related_laws: List[str] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True


class BlogPostCreate(BaseModel):
    title: str
    content: str
    excerpt: str
    category: str
    sub_category: Optional[str] = None
    tags: List[str] = []
    author: str
    author_avatar: Optional[str] = None
    read_time: int = 5
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None
    references: List[str] = []
    related_laws: List[str] = []

    @field_validator("title")
    def validate_title(cls, v):
        if len(v) < 5:
            raise ValueError("Title must be at least 5 characters")
        return v

    @field_validator("content")
    def validate_content(cls, v):
        if len(v) < 50:
            raise ValueError("Content must be at least 50 characters")
        return v


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    meta_description: Optional[str] = None
    featured_image: Optional[str] = None
    references: Optional[List[str]] = None
    related_laws: Optional[List[str]] = None


# ── Sample seed data ───────────────────────────────────────────────────────────
SAMPLE_BLOGS = [
    {
        "title": "Complete Guide to Driving License in India",
        "slug": "driving-license-guide-india",
        "content": """# Complete Guide to Getting and Renewing Driving License in India

## Introduction
A driving license is an official document that authorizes an individual to operate motor vehicles on public roads. In India, the Motor Vehicles Act, 1988 governs the issuance and regulation of driving licenses.

## Types of Driving Licenses

### 1. Learner's License
- Valid for 6 months
- Requires passing a written test
- Must display 'L' plate on vehicle
- Cannot drive alone (accompanied by licensed driver)

### 2. Permanent Driving License
- Issued after 30 days of learner's license
- Requires passing driving test at RTO
- Valid for 20 years or until age 50
- Renewal required every 5 years after age 50

### 3. Commercial Driving License
- For transport vehicles (trucks, buses, taxis)
- Requires additional medical certificate
- Age requirement: 20-45 years
- Includes badge endorsement

## Documents Required

### For Learner's License
- Age proof (Birth certificate, Passport, 10th marksheet)
- Address proof (Aadhaar, Voter ID, Passport)
- Passport size photographs (3-4)
- Medical certificate (Form 1A for commercial vehicles)

### For Permanent License
- Learner's license (original)
- Learner's license completion certificate
- Driving test application (Form 4)
- Fee payment receipt

## Penalties for Violations

| Offense | Penalty |
|---------|---------|
| Driving without license | ₹5,000 fine |
| Driving with expired license | ₹1,000 fine |
| No 'L' plate on learner's vehicle | ₹1,000 fine |
| Learner driving alone | ₹2,000 fine |
| Underage driving | ₹25,000 fine + license at 25 years |

## Latest Updates (2024)
- Digital license now mandatory for new licenses
- Online driving test introduced in major cities
- QR code on license contains all vehicle owner details
- AI-based tracking of traffic violations
""",
        "excerpt": "Complete step-by-step guide to obtain, renew, and replace driving license in India. Learn about documents, fees, online process, penalties, and latest updates.",
        "category": "Motor Vehicle Laws",
        "sub_category": "Driving License",
        "tags": ["driving license", "RTO", "learner license", "permanent license", "traffic rules", "motor vehicles act"],
        "author": "Advocate Rajesh Sharma",
        "author_avatar": "https://ui-avatars.com/api/?name=Rajesh+Sharma&background=0D9488&color=fff",
        "read_time": 12,
        "meta_description": "Complete guide to Indian driving license - types, documents, process, fees, penalties, renewal, and duplicate license. Updated for 2024.",
        "related_laws": ["Motor Vehicles Act, 1988", "Central Motor Vehicles Rules, 1989"],
        "references": ["Motor Vehicles Act, 1988", "parivahan.gov.in", "Supreme Court judgments on digital license"]
    },
    {
        "title": "Consumer Protection Act 2019: Your Rights as a Consumer",
        "slug": "consumer-protection-act-2019-rights",
        "content": """# Consumer Protection Act, 2019: Complete Guide to Your Rights

## Overview
The Consumer Protection Act, 2019 replaced the 1986 Act, strengthening consumer rights and introducing modern provisions for e-commerce, product liability, and mediation.

## Six Consumer Rights

### 1. Right to Safety
Protection against goods and services hazardous to life and health.

### 2. Right to Information
Full disclosure about quality, quantity, potency, purity, standard, and price.

### 3. Right to Choose
Access to variety of goods and services at competitive prices.

### 4. Right to be Heard
Consumer interests will receive due consideration in appropriate forums.

### 5. Right to Redressal
Claim settlement against unfair trade practices or exploitation.

### 6. Right to Consumer Education
Knowledge about rights and remedies available.

## Filing a Complaint

### Enhanced Pecuniary Jurisdiction
- District Commission: Up to ₹1 crore
- State Commission: ₹1 crore to ₹10 crore
- National Commission: Above ₹10 crore

## Penalties for Violations

| Violation | Penalty |
|-----------|---------|
| Defective goods | Replacement/refund + compensation |
| Deficient service | Compensation + litigation costs |
| Misleading ad | ₹10 lakh fine (manufacturer/endorser) |
| Frivolous complaint | ₹50,000 fine |
""",
        "excerpt": "Complete guide to Consumer Protection Act 2019: Know your 6 consumer rights, filing complaints, e-commerce rules, penalties, and landmark judgments.",
        "category": "Consumer Law",
        "sub_category": "Consumer Rights",
        "tags": ["consumer rights", "consumer court", "defective product", "refund", "compensation", "e-commerce"],
        "author": "Advocate Priya Singh",
        "author_avatar": "https://ui-avatars.com/api/?name=Priya+Singh&background=0D9488&color=fff",
        "read_time": 15,
        "meta_description": "Consumer Protection Act 2019 explained - rights, complaint process, e-commerce rules, penalties, and landmark judgments.",
        "related_laws": ["Consumer Protection Act, 2019", "Legal Metrology Act, 2009"],
        "references": ["Consumer Protection Act 2019", "Ministry of Consumer Affairs"]
    },
    {
        "title": "Domestic Violence Act 2005: Protection and Remedies",
        "slug": "domestic-violence-act-2005-protection",
        "content": """# Protection of Women from Domestic Violence Act, 2005

## Introduction
The Protection of Women from Domestic Violence Act, 2005 (PWDVA) is a landmark legislation that provides comprehensive protection to women against domestic violence.

## Types of Abuse Covered

### Physical Abuse
- Assault, battery, physical injury
- Forced sexual intercourse
- Denial of medical facilities

### Emotional and Verbal Abuse
- Insults, ridicule, humiliation
- Threats of physical violence

### Economic Abuse
- Denial of household necessities
- Prohibiting employment
- Forced to hand over earnings

## Rights Under the Act

### 1. Right to Residence
- Cannot be evicted from shared household
- Right to live in matrimonial home

### 2. Right to Protection Orders
- Protection from further violence
- Respondent restrained from contacting

### 3. Right to Monetary Relief
- Maintenance for self and children
- Compensation for injuries/loss

## Penalties

| Violation | Penalty |
|-----------|---------|
| Breach of protection order | Imprisonment up to 1 year + ₹20,000 fine |
| Multiple violations | Imprisonment up to 3 years + fine |

## Important Helplines

| Service | Number |
|---------|--------|
| Women Helpline | 181 |
| National Commission for Women | 7827170170 |
| Police (Emergency) | 100 |
""",
        "excerpt": "Complete guide to Domestic Violence Act 2005: Rights, protection orders, monetary relief, custody, and how to file complaint.",
        "category": "Family Law",
        "sub_category": "Domestic Violence",
        "tags": ["domestic violence", "women protection", "protection order", "maintenance", "shelter", "abuse"],
        "author": "Advocate Meera Desai",
        "author_avatar": "https://ui-avatars.com/api/?name=Meera+Desai&background=0D9488&color=fff",
        "read_time": 12,
        "meta_description": "Protection of Women from Domestic Violence Act 2005 explained - rights, protection orders, monetary relief, custody, complaint process, and helplines.",
        "related_laws": ["Indian Penal Code (Section 498A)", "Dowry Prohibition Act, 1961"],
        "references": ["Protection of Women from Domestic Violence Act 2005", "Supreme Court judgments"]
    },
    {
        "title": "Rights of Arrested Person under CrPC",
        "slug": "rights-of-arrested-person-crpc",
        "content": """# Rights of Arrested Person under Code of Criminal Procedure

## Fundamental Rights
The Constitution of India and CrPC provide several rights to protect arrested persons from arbitrary arrest and detention.

## Key Rights of Arrested Person

### 1. Right to Know Grounds of Arrest (Article 22(1))
- Must be informed of grounds immediately
- Details in writing if arrest with warrant

### 2. Right to Consult Lawyer (Article 22(1))
- Can consult lawyer of choice
- Lawyer can be present during interrogation
- Legal Aid for poor (Article 39A)

### 3. Right to be Produced Before Magistrate (Article 22(2))
- Within 24 hours of arrest
- Excluding travel time from place of arrest

### 4. Right to Medical Examination
- At time of arrest
- Female arrested examined by female doctor

## Important Judgments

### D.K. Basu v. State of West Bengal (1997)
Laid down guidelines for arrest and custody:
- Police must wear name tag/ID
- Memo of arrest prepared
- Relatives informed
- Medical examination done

## What to Do If Arrested

**DO:**
- Cooperate with police
- Ask for arrest memo
- Apply for bail immediately

**DON'T:**
- Sign statements under pressure
- Destroy evidence
- Make extra-judicial confession
""",
        "excerpt": "Complete guide to rights of arrested person under CrPC and Constitution. Know your rights - legal aid, bail, medical exam, and more.",
        "category": "Criminal Law",
        "sub_category": "Arrest and Bail",
        "tags": ["arrest rights", "CrPC", "bail", "legal aid", "police custody", "fundamental rights"],
        "author": "Advocate Vikram Reddy",
        "author_avatar": "https://ui-avatars.com/api/?name=Vikram+Reddy&background=0D9488&color=fff",
        "read_time": 10,
        "meta_description": "Rights of arrested person under CrPC - right to lawyer, medical exam, bail, speedy trial, and DK Basu guidelines.",
        "related_laws": ["Constitution of India (Articles 20-22)", "Code of Criminal Procedure, 1973"],
        "references": ["Supreme Court judgments on arrest", "CrPC Sections 50-60"]
    }
]


# ── Repository ─────────────────────────────────────────────────────────────────
class BlogRepository:
    def __init__(self):
        self.db     = MongoDB().db
        self.blogs  = self.db.blogs
        self.categories = self.db.categories

    def seed_initial_data(self):
        if self.blogs.count_documents({}) == 0:
            for blog in SAMPLE_BLOGS:
                blog["created_at"]  = datetime.utcnow()
                blog["updated_at"]  = datetime.utcnow()
                blog["views"]       = 0
                blog["likes"]       = 0
                blog["is_published"] = True
                self.blogs.insert_one(blog)
            log.info(f"Seeded {len(SAMPLE_BLOGS)} sample blog posts")

    def create_blog(self, blog_data: dict) -> str:
        blog_data["created_at"] = datetime.utcnow()
        blog_data["updated_at"] = datetime.utcnow()
        blog_data["views"] = 0
        blog_data["likes"] = 0
        result = self.blogs.insert_one(blog_data)
        return str(result.inserted_id)

    def get_blog(self, blog_id: str) -> Optional[dict]:
        try:
            return self.blogs.find_one({"_id": ObjectId(blog_id), "is_published": True})
        except Exception:
            return None

    def get_blog_by_slug(self, slug: str) -> Optional[dict]:
        return self.blogs.find_one({"slug": slug, "is_published": True})

    def search_blogs(
        self, query: str, category: str = None, tag: str = None,
        author: str = None, page: int = 1, limit: int = 10,
        sort_by: str = "created_at", sort_order: str = "desc"
    ) -> Tuple[List[dict], int]:
        filter_query = {"is_published": True}
        if query:
            filter_query["$text"] = {"$search": query}
        if category and category != "All":
            filter_query["category"] = category
        if tag:
            filter_query["tags"] = tag
        if author:
            filter_query["author"] = author
        sort_direction = DESCENDING if sort_order == "desc" else ASCENDING
        total = self.blogs.count_documents(filter_query)
        skip  = (page - 1) * limit
        cursor = self.blogs.find(filter_query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        return list(cursor), total

    def get_categories(self) -> List[dict]:
        pipeline = [
            {"$match": {"is_published": True}},
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        return [{"name": r["_id"], "count": r["count"]} for r in self.blogs.aggregate(pipeline)]

    def get_tags(self) -> List[dict]:
        pipeline = [
            {"$match": {"is_published": True}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        return [{"name": r["_id"], "count": r["count"]} for r in self.blogs.aggregate(pipeline)]

    def get_authors(self) -> List[dict]:
        pipeline = [
            {"$match": {"is_published": True}},
            {"$group": {"_id": "$author", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        return [{"name": r["_id"], "count": r["count"]} for r in self.blogs.aggregate(pipeline)]

    def increment_views(self, blog_id: str):
        self.blogs.update_one({"_id": ObjectId(blog_id)}, {"$inc": {"views": 1}})

    def like_blog(self, blog_id: str) -> bool:
        result = self.blogs.update_one({"_id": ObjectId(blog_id)}, {"$inc": {"likes": 1}})
        return result.modified_count > 0

    def update_blog(self, blog_id: str, update_data: dict) -> bool:
        update_data["updated_at"] = datetime.utcnow()
        result = self.blogs.update_one({"_id": ObjectId(blog_id)}, {"$set": update_data})
        return result.modified_count > 0

    def delete_blog(self, blog_id: str) -> bool:
        result = self.blogs.update_one(
            {"_id": ObjectId(blog_id)},
            {"$set": {"is_published": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    def get_related_blogs(self, blog_id: str, tags: List[str], limit: int = 3) -> List[dict]:
        return list(self.blogs.find(
            {"_id": {"$ne": ObjectId(blog_id)}, "is_published": True, "tags": {"$in": tags}}
        ).sort("views", -1).limit(limit))


blog_repo = BlogRepository()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("NyayaAI Blog App starting — seeding data if needed...")
    blog_repo.seed_initial_data()
    yield
    log.info("NyayaAI Blog App shutting down.")


blogs_app = FastAPI(
    title="NyayaAI — Blog Knowledge Base",
    description="Blog CRUD API with MongoDB",
    version="2.1.0",
    lifespan=lifespan,
)

blogs_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@blogs_app.get("/")
async def blogs_root():
    return {"service": "NyayaAI Blog API", "version": "2.1.0", "status": "operational"}


@blogs_app.get("/blogs/search")
async def search_blogs(
    q: str = Query(""),
    category: str = Query(None),
    tag: str = Query(None),
    author: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    blogs, total = blog_repo.search_blogs(q, category, tag, author, page, limit, sort_by, sort_order)
    for blog in blogs:
        blog["_id"] = str(blog["_id"])
    return {"total": total, "page": page, "limit": limit, "total_pages": (total + limit - 1) // limit, "results": blogs}


@blogs_app.get("/blogs/slug/{slug}")
async def get_blog_by_slug(slug: str):
    blog = blog_repo.get_blog_by_slug(slug)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog_repo.increment_views(str(blog["_id"]))
    blog["_id"] = str(blog["_id"])
    related = blog_repo.get_related_blogs(blog["_id"], blog.get("tags", []))
    for rel in related:
        rel["_id"] = str(rel["_id"])
    return {"blog": blog, "related": related}


@blogs_app.get("/blogs/{blog_id}")
async def get_blog(blog_id: str):
    blog = blog_repo.get_blog(blog_id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    blog_repo.increment_views(blog_id)
    blog["_id"] = str(blog["_id"])
    related = blog_repo.get_related_blogs(blog_id, blog.get("tags", []))
    for rel in related:
        rel["_id"] = str(rel["_id"])
    return {"blog": blog, "related": related}


@blogs_app.post("/blogs/{blog_id}/like")
async def like_blog(blog_id: str):
    success = blog_repo.like_blog(blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog liked successfully"}


@blogs_app.get("/categories")
async def get_categories():
    return {"categories": blog_repo.get_categories()}


@blogs_app.get("/tags")
async def get_tags():
    return {"tags": blog_repo.get_tags()}


@blogs_app.get("/authors")
async def get_authors():
    return {"authors": blog_repo.get_authors()}


@blogs_app.post("/blogs")
async def create_blog(blog: BlogPostCreate):
    slug = blog.title.lower().replace(" ", "-").replace("/", "-")
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    blog_dict = blog.model_dump()
    blog_dict["slug"] = slug
    blog_id = blog_repo.create_blog(blog_dict)
    return {"id": blog_id, "message": "Blog created successfully"}


@blogs_app.put("/blogs/{blog_id}")
async def update_blog(blog_id: str, blog: BlogPostUpdate):
    update_data = {k: v for k, v in blog.model_dump().items() if v is not None}
    success = blog_repo.update_blog(blog_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog updated successfully"}


@blogs_app.delete("/blogs/{blog_id}")
async def delete_blog(blog_id: str):
    success = blog_repo.delete_blog(blog_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted (unpublished) successfully"}


@blogs_app.get("/analytics/popular")
async def get_popular_blogs(limit: int = 6):
    blogs, _ = blog_repo.search_blogs("", limit=limit, sort_by="views", sort_order="desc")
    for blog in blogs:
        blog["_id"] = str(blog["_id"])
    return {"results": blogs}


@blogs_app.get("/analytics/recent")
async def get_recent_blogs(limit: int = 6):
    blogs, _ = blog_repo.search_blogs("", limit=limit, sort_by="created_at", sort_order="desc")
    for blog in blogs:
        blog["_id"] = str(blog["_id"])
    return {"results": blogs}

app2 = FastAPI(title="App Two")

@app2.get("/")
async def root():
    return {"message": "Hello from App Two"}

@app2.get("/health")
async def health():
    return {"app": "App Two", "health": "ok"}