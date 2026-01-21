import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, JSON, Column


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    creator: Optional["Creator"] = Relationship(back_populates="user", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# Enums for the Creator system
class CreatorStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class TemplateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


# Creator models
class CreatorBase(SQLModel):
    username: str = Field(min_length=3, max_length=50, unique=True, index=True)
    display_name: str = Field(min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=1000)
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    commission_rate: float = Field(default=0.1, ge=0, le=1)


class CreatorCreate(CreatorBase):
    social_media_links: Optional[dict] = Field(default=None)
    payout_info: Optional[dict] = Field(default=None)


class CreatorUpdate(SQLModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = Field(default=None, max_length=1000)
    profile_image_url: Optional[str] = Field(default=None, max_length=500)
    social_media_links: Optional[dict] = Field(default=None)
    payout_info: Optional[dict] = Field(default=None)
    commission_rate: Optional[float] = Field(default=None, ge=0, le=1)


class Creator(CreatorBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    social_media_links: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    payout_info: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: CreatorStatus = Field(default=CreatorStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: Optional[User] = Relationship(back_populates="creator")
    templates: list["TripTemplate"] = Relationship(back_populates="creator", cascade_delete=True)
    affiliate_links: list["AffiliateLink"] = Relationship(back_populates="creator", cascade_delete=True)


class CreatorPublic(CreatorBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: CreatorStatus
    social_media_links: Optional[dict]
    created_at: datetime


class CreatorsPublic(SQLModel):
    data: list[CreatorPublic]
    count: int


# Trip Template models
class TripTemplateBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=2000)
    creator_notes: Optional[str] = Field(default=None, max_length=2000)


class TripTemplateCreate(TripTemplateBase):
    core_experience: dict = Field(description="Immutable core experience data")
    flexible_logistics: dict = Field(description="Customizable logistics options")
    affiliate_settings: Optional[dict] = Field(default=None)


class TripTemplateUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    creator_notes: Optional[str] = Field(default=None, max_length=2000)
    core_experience: Optional[dict] = Field(default=None)
    flexible_logistics: Optional[dict] = Field(default=None)
    affiliate_settings: Optional[dict] = Field(default=None)


class TripTemplate(TripTemplateBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="creator.id", nullable=False, ondelete="CASCADE")
    core_experience: dict = Field(sa_column=Column(JSON))
    flexible_logistics: dict = Field(sa_column=Column(JSON))
    affiliate_settings: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    status: TemplateStatus = Field(default=TemplateStatus.DRAFT)
    views_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: Optional[Creator] = Relationship(back_populates="templates")
    affiliate_links: list["AffiliateLink"] = Relationship(back_populates="template", cascade_delete=True)


class TripTemplatePublic(TripTemplateBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    core_experience: dict
    flexible_logistics: dict
    status: TemplateStatus
    views_count: int
    created_at: datetime
    creator: Optional[CreatorPublic] = None


class TripTemplatesPublic(SQLModel):
    data: list[TripTemplatePublic]
    count: int


# Affiliate Link models
class AffiliateLinkBase(SQLModel):
    link_code: str = Field(min_length=8, max_length=32, unique=True, index=True)


class AffiliateLinkCreate(SQLModel):
    template_id: uuid.UUID


class AffiliateLink(AffiliateLinkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    template_id: uuid.UUID = Field(foreign_key="triptemplate.id", nullable=False, ondelete="CASCADE")
    creator_id: uuid.UUID = Field(foreign_key="creator.id", nullable=False, ondelete="CASCADE")
    clicks: int = Field(default=0)
    conversions: int = Field(default=0)
    revenue_generated: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    template: Optional[TripTemplate] = Relationship(back_populates="affiliate_links")
    creator: Optional[Creator] = Relationship(back_populates="affiliate_links")


class AffiliateLinkPublic(AffiliateLinkBase):
    id: uuid.UUID
    template_id: uuid.UUID
    creator_id: uuid.UUID
    clicks: int
    conversions: int
    revenue_generated: float
    created_at: datetime


class AffiliateLinksPublic(SQLModel):
    data: list[AffiliateLinkPublic]
    count: int
