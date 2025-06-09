import uuid
import secrets
import string
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import func, select

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Message, Creator, CreatorCreate, CreatorPublic, CreatorsPublic, CreatorUpdate,
    TripTemplate, TripTemplateCreate, TripTemplatePublic, TripTemplatesPublic, TripTemplateUpdate,
    AffiliateLink, AffiliateLinkCreate, AffiliateLinkPublic, AffiliateLinksPublic,
    CreatorStatus, TemplateStatus
)

router = APIRouter(prefix="/creators", tags=["creators"])


def get_current_creator(session: SessionDep, current_user: CurrentUser) -> Creator:
    """Get current user's creator profile, raise 404 if not found."""
    creator = crud.get_creator_by_user_id(session=session, user_id=current_user.id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return creator


def require_active_creator(session: SessionDep, current_user: CurrentUser) -> Creator:
    """Get current user's creator profile and ensure it's active."""
    creator = get_current_creator(session, current_user)
    if creator.status != CreatorStatus.ACTIVE:
        status_msg = {
            CreatorStatus.PENDING: "Your creator account is pending approval. Please wait for admin approval or contact support.",
            CreatorStatus.SUSPENDED: "Your creator account has been suspended. Please contact support for assistance."
        }.get(creator.status, f"Creator account status: {creator.status}")
        raise HTTPException(status_code=403, detail=status_msg)
    return creator


@router.post("/", response_model=CreatorPublic)
def create_creator_profile(
    *, session: SessionDep, current_user: CurrentUser, creator_in: CreatorCreate
) -> Creator:
    """
    Create creator profile for current user.
    """
    # Check if user already has a creator profile
    existing_creator = crud.get_creator_by_user_id(session=session, user_id=current_user.id)
    if existing_creator:
        raise HTTPException(status_code=400, detail="Creator profile already exists")
    
    creator = crud.create_creator(session=session, creator_in=creator_in, user_id=current_user.id)
    
    # Auto-approve creator for demo purposes
    creator.status = CreatorStatus.ACTIVE
    session.add(creator)
    session.commit()
    session.refresh(creator)
    
    return creator


@router.get("/me", response_model=CreatorPublic)
def get_my_creator_profile(session: SessionDep, current_user: CurrentUser) -> Creator:
    """
    Get current user's creator profile.
    """
    return get_current_creator(session, current_user)


@router.put("/me", response_model=CreatorPublic)
def update_my_creator_profile(
    *, session: SessionDep, current_user: CurrentUser, creator_in: CreatorUpdate
) -> Creator:
    """
    Update current user's creator profile.
    """
    creator = get_current_creator(session, current_user)
    creator = crud.update_creator(session=session, db_creator=creator, creator_in=creator_in)
    return creator


# Template management endpoints
@router.get("/templates", response_model=TripTemplatesPublic)
def get_my_templates(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get current creator's templates.
    """
    creator = get_current_creator(session, current_user)
    
    count_statement = (
        select(func.count())
        .select_from(TripTemplate)
        .where(TripTemplate.creator_id == creator.id)
    )
    count = session.exec(count_statement).one()
    
    statement = (
        select(TripTemplate)
        .where(TripTemplate.creator_id == creator.id)
        .offset(skip)
        .limit(limit)
        .order_by(TripTemplate.created_at.desc())
    )
    templates = session.exec(statement).all()
    
    return TripTemplatesPublic(data=templates, count=count)


@router.post("/templates", response_model=TripTemplatePublic)
def create_trip_template(
    *, session: SessionDep, current_user: CurrentUser, template_in: TripTemplateCreate
) -> TripTemplate:
    """
    Create new trip template.
    """
    creator = require_active_creator(session, current_user)
    template = crud.create_trip_template(
        session=session, template_in=template_in, creator_id=creator.id
    )
    return template


@router.get("/templates/{template_id}", response_model=TripTemplatePublic)
def get_my_template(
    *, session: SessionDep, current_user: CurrentUser, template_id: uuid.UUID
) -> TripTemplate:
    """
    Get specific template owned by current creator.
    """
    creator = get_current_creator(session, current_user)
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this template")
    
    return template


@router.put("/templates/{template_id}", response_model=TripTemplatePublic)
def update_my_template(
    *, 
    session: SessionDep, 
    current_user: CurrentUser, 
    template_id: uuid.UUID,
    template_in: TripTemplateUpdate
) -> TripTemplate:
    """
    Update template owned by current creator.
    """
    creator = get_current_creator(session, current_user)
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    
    template = crud.update_trip_template(
        session=session, db_template=template, template_in=template_in
    )
    return template


@router.put("/templates/{template_id}/publish", response_model=TripTemplatePublic)
def publish_template(
    *, session: SessionDep, current_user: CurrentUser, template_id: uuid.UUID
) -> TripTemplate:
    """
    Publish a draft template.
    """
    creator = require_active_creator(session, current_user)
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to publish this template")
    if template.status != TemplateStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only draft templates can be published")
    
    template_update = TripTemplateUpdate(status=TemplateStatus.PUBLISHED)
    template = crud.update_trip_template(
        session=session, db_template=template, template_in=template_update
    )
    return template


@router.delete("/templates/{template_id}")
def delete_my_template(
    *, session: SessionDep, current_user: CurrentUser, template_id: uuid.UUID
) -> Message:
    """
    Delete template owned by current creator.
    """
    creator = get_current_creator(session, current_user)
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    
    crud.delete_trip_template(session=session, db_template=template)
    return Message(message="Template deleted successfully")


# Affiliate link management
def generate_affiliate_code(length: int = 12) -> str:
    """Generate a random affiliate link code."""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


@router.post("/templates/{template_id}/affiliate-links", response_model=AffiliateLinkPublic)
def create_affiliate_link(
    *, session: SessionDep, current_user: CurrentUser, template_id: uuid.UUID
) -> AffiliateLink:
    """
    Create affiliate link for published template.
    """
    creator = require_active_creator(session, current_user)
    template = crud.get_trip_template_by_id(session=session, template_id=template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.creator_id != creator.id:
        raise HTTPException(status_code=403, detail="Not authorized to create affiliate link")
    if template.status != TemplateStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Can only create affiliate links for published templates")
    
    # Generate unique affiliate code
    link_code = generate_affiliate_code()
    while crud.get_affiliate_link_by_code(session=session, link_code=link_code):
        link_code = generate_affiliate_code()
    
    link_in = AffiliateLinkCreate(template_id=template_id)
    affiliate_link = crud.create_affiliate_link(
        session=session, link_in=link_in, creator_id=creator.id, link_code=link_code
    )
    return affiliate_link


@router.get("/affiliate-links", response_model=AffiliateLinksPublic)
def get_my_affiliate_links(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get current creator's affiliate links.
    """
    creator = get_current_creator(session, current_user)
    
    count_statement = (
        select(func.count())
        .select_from(AffiliateLink)
        .where(AffiliateLink.creator_id == creator.id)
    )
    count = session.exec(count_statement).one()
    
    statement = (
        select(AffiliateLink)
        .where(AffiliateLink.creator_id == creator.id)
        .offset(skip)
        .limit(limit)
        .order_by(AffiliateLink.created_at.desc())
    )
    links = session.exec(statement).all()
    
    return AffiliateLinksPublic(data=links, count=count)