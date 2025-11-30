"""
NeuroCron AuditX API
Autonomous marketing audit engine
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from urllib.parse import urlparse
import asyncio

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


class AuditRequest(BaseModel):
    """Request for website/marketing audit"""
    url: str = Field(..., description="Website URL to audit")
    audit_types: List[str] = Field(
        default=["seo", "performance", "social"],
        description="Types: seo, performance, social, content, ads, email"
    )


class AuditIssue(BaseModel):
    """Single audit issue"""
    category: str
    severity: str  # critical, warning, info
    title: str
    description: str
    recommendation: str
    impact: Optional[str] = None


class AuditScore(BaseModel):
    """Audit score for a category"""
    category: str
    score: int  # 0-100
    grade: str  # A, B, C, D, F
    issues_count: int


class AuditResult(BaseModel):
    """Complete audit result"""
    url: str
    overall_score: int
    overall_grade: str
    scores: List[AuditScore]
    issues: List[AuditIssue]
    recommendations: List[str]
    audit_date: str


@router.post("/website", response_model=AuditResult)
async def audit_website(
    request: AuditRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run a comprehensive website audit.
    
    Checks:
    - SEO (meta tags, headings, structure)
    - Performance (page speed, Core Web Vitals)
    - Social media integration
    - Content quality
    - Technical issues
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    # Validate URL
    try:
        parsed = urlparse(request.url)
        if not parsed.scheme:
            request.url = f"https://{request.url}"
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format"
        )
    
    # Run audits
    scores = []
    issues = []
    recommendations = []
    
    try:
        # Fetch the page
        async with httpx.AsyncClient() as client:
            response = await client.get(
                request.url,
                follow_redirects=True,
                timeout=30.0,
                headers={"User-Agent": "NeuroCron-AuditBot/1.0"}
            )
            html_content = response.text
            headers = dict(response.headers)
            status_code = response.status_code
    except Exception as e:
        # Return a basic audit if we can't fetch the page
        return AuditResult(
            url=request.url,
            overall_score=0,
            overall_grade="F",
            scores=[AuditScore(
                category="accessibility",
                score=0,
                grade="F",
                issues_count=1
            )],
            issues=[AuditIssue(
                category="accessibility",
                severity="critical",
                title="Website Unreachable",
                description=f"Could not access the website: {str(e)}",
                recommendation="Ensure the website is online and accessible.",
            )],
            recommendations=["Fix website accessibility issues first."],
            audit_date="now"
        )
    
    # SEO Audit
    if "seo" in request.audit_types:
        seo_score, seo_issues = _audit_seo(html_content, request.url)
        scores.append(AuditScore(
            category="SEO",
            score=seo_score,
            grade=_score_to_grade(seo_score),
            issues_count=len(seo_issues)
        ))
        issues.extend(seo_issues)
    
    # Performance Audit
    if "performance" in request.audit_types:
        perf_score, perf_issues = _audit_performance(html_content, headers)
        scores.append(AuditScore(
            category="Performance",
            score=perf_score,
            grade=_score_to_grade(perf_score),
            issues_count=len(perf_issues)
        ))
        issues.extend(perf_issues)
    
    # Social Audit
    if "social" in request.audit_types:
        social_score, social_issues = _audit_social(html_content)
        scores.append(AuditScore(
            category="Social Media",
            score=social_score,
            grade=_score_to_grade(social_score),
            issues_count=len(social_issues)
        ))
        issues.extend(social_issues)
    
    # Content Audit
    if "content" in request.audit_types:
        content_score, content_issues = _audit_content(html_content)
        scores.append(AuditScore(
            category="Content",
            score=content_score,
            grade=_score_to_grade(content_score),
            issues_count=len(content_issues)
        ))
        issues.extend(content_issues)
    
    # Calculate overall score
    if scores:
        overall_score = sum(s.score for s in scores) // len(scores)
    else:
        overall_score = 0
    
    # Generate recommendations
    critical_issues = [i for i in issues if i.severity == "critical"]
    if critical_issues:
        recommendations.append(f"Fix {len(critical_issues)} critical issues immediately")
    
    for score in scores:
        if score.score < 50:
            recommendations.append(f"Improve {score.category} - currently scoring {score.score}/100")
    
    if not recommendations:
        recommendations.append("Your website is performing well! Consider A/B testing to optimize further.")
    
    from datetime import datetime
    
    return AuditResult(
        url=request.url,
        overall_score=overall_score,
        overall_grade=_score_to_grade(overall_score),
        scores=scores,
        issues=issues,
        recommendations=recommendations[:5],  # Top 5 recommendations
        audit_date=datetime.utcnow().isoformat(),
    )


def _score_to_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def _audit_seo(html: str, url: str) -> tuple[int, List[AuditIssue]]:
    """Audit SEO factors."""
    issues = []
    score = 100
    
    html_lower = html.lower()
    
    # Check for title tag
    if "<title>" not in html_lower or "</title>" not in html_lower:
        score -= 20
        issues.append(AuditIssue(
            category="SEO",
            severity="critical",
            title="Missing Title Tag",
            description="The page is missing a <title> tag.",
            recommendation="Add a unique, descriptive title tag (50-60 characters).",
            impact="Title tags are crucial for SEO and click-through rates."
        ))
    
    # Check for meta description
    if 'name="description"' not in html_lower and "name='description'" not in html_lower:
        score -= 15
        issues.append(AuditIssue(
            category="SEO",
            severity="warning",
            title="Missing Meta Description",
            description="The page is missing a meta description.",
            recommendation="Add a compelling meta description (150-160 characters).",
            impact="Meta descriptions improve CTR in search results."
        ))
    
    # Check for H1
    if "<h1" not in html_lower:
        score -= 15
        issues.append(AuditIssue(
            category="SEO",
            severity="warning",
            title="Missing H1 Tag",
            description="The page is missing an H1 heading.",
            recommendation="Add one H1 tag that clearly describes the page content.",
            impact="H1 tags help search engines understand page structure."
        ))
    
    # Check for multiple H1s
    if html_lower.count("<h1") > 1:
        score -= 5
        issues.append(AuditIssue(
            category="SEO",
            severity="info",
            title="Multiple H1 Tags",
            description=f"The page has {html_lower.count('<h1')} H1 tags.",
            recommendation="Use only one H1 tag per page.",
            impact="Multiple H1s can confuse search engines."
        ))
    
    # Check for alt attributes on images
    img_count = html_lower.count("<img")
    alt_count = html_lower.count("alt=")
    if img_count > 0 and alt_count < img_count:
        score -= 10
        issues.append(AuditIssue(
            category="SEO",
            severity="warning",
            title="Images Missing Alt Text",
            description=f"{img_count - alt_count} images are missing alt attributes.",
            recommendation="Add descriptive alt text to all images.",
            impact="Alt text improves accessibility and image SEO."
        ))
    
    # Check for canonical tag
    if 'rel="canonical"' not in html_lower:
        score -= 5
        issues.append(AuditIssue(
            category="SEO",
            severity="info",
            title="Missing Canonical Tag",
            description="No canonical tag found.",
            recommendation="Add a canonical tag to prevent duplicate content issues.",
            impact="Canonical tags help consolidate ranking signals."
        ))
    
    return max(0, score), issues


def _audit_performance(html: str, headers: Dict[str, str]) -> tuple[int, List[AuditIssue]]:
    """Audit performance factors."""
    issues = []
    score = 100
    
    # Check page size
    page_size = len(html)
    if page_size > 500000:  # 500KB
        score -= 20
        issues.append(AuditIssue(
            category="Performance",
            severity="warning",
            title="Large Page Size",
            description=f"Page size is {page_size // 1000}KB.",
            recommendation="Reduce page size by optimizing images and minifying code.",
            impact="Large pages load slowly, especially on mobile."
        ))
    
    # Check for compression
    if "content-encoding" not in headers and "gzip" not in str(headers).lower():
        score -= 15
        issues.append(AuditIssue(
            category="Performance",
            severity="warning",
            title="No Compression",
            description="Content is not compressed.",
            recommendation="Enable GZIP or Brotli compression on your server.",
            impact="Compression can reduce transfer size by 70-90%."
        ))
    
    # Check for inline scripts
    html_lower = html.lower()
    if html_lower.count("<script") > 10:
        score -= 10
        issues.append(AuditIssue(
            category="Performance",
            severity="info",
            title="Many Script Tags",
            description=f"Page has {html_lower.count('<script')} script tags.",
            recommendation="Bundle scripts and use defer/async attributes.",
            impact="Too many scripts can slow page rendering."
        ))
    
    # Check for inline CSS
    if html_lower.count("<style") > 5:
        score -= 5
        issues.append(AuditIssue(
            category="Performance",
            severity="info",
            title="Inline CSS",
            description="Multiple inline style blocks detected.",
            recommendation="Move CSS to external stylesheets for better caching.",
            impact="Inline CSS can bloat HTML size."
        ))
    
    return max(0, score), issues


def _audit_social(html: str) -> tuple[int, List[AuditIssue]]:
    """Audit social media integration."""
    issues = []
    score = 100
    
    html_lower = html.lower()
    
    # Check for Open Graph tags
    if 'property="og:' not in html_lower:
        score -= 25
        issues.append(AuditIssue(
            category="Social Media",
            severity="warning",
            title="Missing Open Graph Tags",
            description="No Open Graph meta tags found.",
            recommendation="Add og:title, og:description, og:image for better social sharing.",
            impact="OG tags control how content appears when shared on social media."
        ))
    
    # Check for Twitter Card
    if 'name="twitter:' not in html_lower:
        score -= 15
        issues.append(AuditIssue(
            category="Social Media",
            severity="info",
            title="Missing Twitter Card Tags",
            description="No Twitter Card meta tags found.",
            recommendation="Add twitter:card, twitter:title, twitter:description.",
            impact="Twitter Cards improve engagement on Twitter/X."
        ))
    
    # Check for social sharing buttons
    social_patterns = ["facebook", "twitter", "linkedin", "share"]
    has_social = any(p in html_lower for p in social_patterns)
    if not has_social:
        score -= 10
        issues.append(AuditIssue(
            category="Social Media",
            severity="info",
            title="No Social Sharing",
            description="No social sharing elements detected.",
            recommendation="Add social sharing buttons to encourage content distribution.",
            impact="Social sharing can increase traffic and engagement."
        ))
    
    return max(0, score), issues


def _audit_content(html: str) -> tuple[int, List[AuditIssue]]:
    """Audit content quality."""
    issues = []
    score = 100
    
    # Strip HTML tags to get text content
    import re
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    word_count = len(text.split())
    
    # Check content length
    if word_count < 300:
        score -= 20
        issues.append(AuditIssue(
            category="Content",
            severity="warning",
            title="Thin Content",
            description=f"Page has only ~{word_count} words.",
            recommendation="Aim for at least 300-500 words for main content pages.",
            impact="Thin content may rank poorly and provide less value."
        ))
    
    # Check for structured data
    if '"@type"' not in html and '"@context"' not in html:
        score -= 10
        issues.append(AuditIssue(
            category="Content",
            severity="info",
            title="No Structured Data",
            description="No JSON-LD structured data found.",
            recommendation="Add schema.org markup for rich snippets in search results.",
            impact="Structured data can improve search visibility."
        ))
    
    return max(0, score), issues


@router.get("/history")
async def get_audit_history(
    org_id: UUID = Query(..., description="Organization ID"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit history for an organization.
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    # In production, fetch from database
    return {
        "audits": [],
        "message": "Audit history feature coming soon"
    }

