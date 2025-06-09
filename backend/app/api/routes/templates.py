import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import func, select, or_

from app import crud
from app.api.deps import SessionDep
from app.models import (
    TripTemplate, TripTemplatePublic, TripTemplatesPublic,
    TemplateStatus, Creator
)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/discover", response_model=TripTemplatesPublic)
def discover_templates(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search in title and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_duration: Optional[int] = Query(None, description="Minimum duration in days"),
    max_duration: Optional[int] = Query(None, description="Maximum duration in days"),
) -> Any:
    """
    Discover published trip templates with filtering and search.
    """
    # Base query for published templates only
    count_statement = (
        select(func.count())
        .select_from(TripTemplate)
        .where(TripTemplate.status == TemplateStatus.PUBLISHED)
    )
    
    statement = (
        select(TripTemplate)
        .where(TripTemplate.status == TemplateStatus.PUBLISHED)
        .join(Creator)
    )
    
    # Apply search filter
    if search:
        search_filter = or_(
            TripTemplate.title.icontains(search),
            TripTemplate.description.icontains(search)
        )
        count_statement = count_statement.where(search_filter)
        statement = statement.where(search_filter)
    
    # Apply category filter (if stored in core_experience)
    if category:
        # This would need to be adjusted based on your JSON structure
        # For now, we'll skip this filter
        pass
    
    # Apply duration filters (if stored in core_experience)
    if min_duration or max_duration:
        # This would need to be adjusted based on your JSON structure
        # For now, we'll skip these filters
        pass
    
    # Get count and results
    count = session.exec(count_statement).one()
    
    templates = session.exec(
        statement
        .offset(skip)
        .limit(limit)
        .order_by(TripTemplate.created_at.desc())
    ).all()
    
    return TripTemplatesPublic(data=templates, count=count)


@router.get("/{template_id}", response_model=TripTemplatePublic)
def get_template(*, session: SessionDep, template_id: uuid.UUID) -> TripTemplate:
    """
    Get specific published template by ID.
    """
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    if template.status != TemplateStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Increment views count
    template.views_count += 1
    session.add(template)
    session.commit()
    session.refresh(template)
    
    return template


@router.get("/by-affiliate/{link_code}", response_model=TripTemplatePublic)
def get_template_by_affiliate(*, session: SessionDep, link_code: str) -> TripTemplate:
    """
    Get template via affiliate link and track click.
    """
    affiliate_link = crud.get_affiliate_link_by_code(session=session, link_code=link_code)
    
    if not affiliate_link:
        raise HTTPException(status_code=404, detail="Affiliate link not found")
    
    template = crud.get_trip_template_by_id(session=session, template_id=affiliate_link.template_id)
    
    if not template or template.status != TemplateStatus.PUBLISHED:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Track affiliate link click
    crud.increment_affiliate_link_clicks(session=session, db_link=affiliate_link)
    
    # Increment template views
    template.views_count += 1
    session.add(template)
    session.commit()
    session.refresh(template)
    
    return template