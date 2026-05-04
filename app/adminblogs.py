# app/adminblogs.py
import os
import re
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Security, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from bson import ObjectId
from app.database import blogs_collection, db

# ---------- Config ----------
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "your-secret-key-change-this")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# ---------- Pydantic models ----------
class AdminLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class BlogPostCreateAdmin(BaseModel):
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

# ---------- JWT helpers ----------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, ADMIN_SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, ADMIN_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

security = HTTPBearer()

# ---------- Admin FastAPI app ----------
admin_app = FastAPI(title="Admin Blog API")

@admin_app.post("/login", response_model=TokenResponse)
async def admin_login(login: AdminLogin):
    if login.username == ADMIN_USERNAME and login.password == ADMIN_PASSWORD:
        token = create_access_token(
            data={"sub": login.username, "role": "admin"},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@admin_app.post("/blogs", response_model=dict)
async def create_blog_admin(
    blog: BlogPostCreateAdmin,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    slug = re.sub(r'[^a-z0-9-]', '', blog.title.lower().replace(" ", "-").replace("/", "-"))
    blog_dict = blog.model_dump()
    blog_dict["slug"] = slug
    blog_dict["views"] = 0
    blog_dict["likes"] = 0
    blog_dict["is_published"] = True
    blog_dict["created_at"] = datetime.utcnow()
    blog_dict["updated_at"] = datetime.utcnow()
    
    result = blogs_collection.insert_one(blog_dict)
    return {"id": str(result.inserted_id), "slug": slug, "message": "Blog created"}

@admin_app.put("/blogs/{blog_id}")
async def update_blog_admin(
    blog_id: str,
    blog: BlogPostCreateAdmin,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = blog.model_dump()
    update_data["updated_at"] = datetime.utcnow()
    if "title" in update_data:
        update_data["slug"] = re.sub(r'[^a-z0-9-]', '', update_data["title"].lower().replace(" ", "-"))
    
    result = blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog updated"}

@admin_app.delete("/blogs/{blog_id}")
async def delete_blog_admin(
    blog_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = blogs_collection.delete_one({"_id": ObjectId(blog_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Blog not found")
    return {"message": "Blog deleted"}

@admin_app.post("/blogs/{blog_id}/publish")
async def publish_blog(
    blog_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    blog = blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    new_status = not blog.get("is_published", True)
    blogs_collection.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": {"is_published": new_status, "updated_at": datetime.utcnow()}}
    )
    return {"is_published": new_status, "message": f"Blog {'published' if new_status else 'unpublished'}"}

@admin_app.get("/blogs")
async def get_all_blogs_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    payload = verify_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    skip = (page - 1) * limit
    total = blogs_collection.count_documents({})
    blogs = list(blogs_collection.find({}).sort("created_at", -1).skip(skip).limit(limit))
    for blog in blogs:
        blog["_id"] = str(blog["_id"])
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit,
        "results": blogs
    }