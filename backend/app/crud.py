import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item, ItemCreate, User, UserCreate, UserUpdate,
    Creator, CreatorCreate, CreatorUpdate,
    TripTemplate, TripTemplateCreate, TripTemplateUpdate,
    AffiliateLink, AffiliateLinkCreate
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Creator CRUD functions
def create_creator(*, session: Session, creator_in: CreatorCreate, user_id: uuid.UUID) -> Creator:
    db_creator = Creator.model_validate(creator_in, update={"user_id": user_id})
    session.add(db_creator)
    session.commit()
    session.refresh(db_creator)
    return db_creator


def get_creator_by_user_id(*, session: Session, user_id: uuid.UUID) -> Creator | None:
    statement = select(Creator).where(Creator.user_id == user_id)
    return session.exec(statement).first()


def get_creator_by_id(*, session: Session, creator_id: uuid.UUID) -> Creator | None:
    statement = select(Creator).where(Creator.id == creator_id)
    return session.exec(statement).first()


def update_creator(*, session: Session, db_creator: Creator, creator_in: CreatorUpdate) -> Creator:
    creator_data = creator_in.model_dump(exclude_unset=True)
    db_creator.sqlmodel_update(creator_data)
    session.add(db_creator)
    session.commit()
    session.refresh(db_creator)
    return db_creator


# TripTemplate CRUD functions
def create_trip_template(*, session: Session, template_in: TripTemplateCreate, creator_id: uuid.UUID) -> TripTemplate:
    db_template = TripTemplate.model_validate(template_in, update={"creator_id": creator_id})
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


def get_trip_template_by_id(*, session: Session, template_id: uuid.UUID) -> TripTemplate | None:
    statement = select(TripTemplate).where(TripTemplate.id == template_id)
    return session.exec(statement).first()


def update_trip_template(*, session: Session, db_template: TripTemplate, template_in: TripTemplateUpdate) -> TripTemplate:
    template_data = template_in.model_dump(exclude_unset=True)
    db_template.sqlmodel_update(template_data)
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


def delete_trip_template(*, session: Session, db_template: TripTemplate) -> None:
    session.delete(db_template)
    session.commit()


# AffiliateLink CRUD functions
def create_affiliate_link(*, session: Session, link_in: AffiliateLinkCreate, creator_id: uuid.UUID, link_code: str) -> AffiliateLink:
    db_link = AffiliateLink.model_validate(
        link_in, 
        update={"creator_id": creator_id, "link_code": link_code}
    )
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link


def get_affiliate_link_by_code(*, session: Session, link_code: str) -> AffiliateLink | None:
    statement = select(AffiliateLink).where(AffiliateLink.link_code == link_code)
    return session.exec(statement).first()


def increment_affiliate_link_clicks(*, session: Session, db_link: AffiliateLink) -> AffiliateLink:
    db_link.clicks += 1
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link
