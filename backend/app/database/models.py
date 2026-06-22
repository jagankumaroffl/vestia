from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    body_type = Column(String(20), default="regular")   # slim | athletic | regular | plus
    gender = Column(String(20), default="unisex")
    preferred_style = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    clothing_items = relationship("ClothingItem", back_populates="user", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    outfit_history = relationship("OutfitHistory", back_populates="user", cascade="all, delete-orphan")
    wardrobe_stats = relationship("WardrobeStatistic", back_populates="user", uselist=False, cascade="all, delete-orphan")


class ClothingItem(Base):
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Storage
    image_path = Column(String(255), nullable=False)

    # CV-extracted metadata
    category = Column(String(50), nullable=False)        # topwear | bottomwear | footwear | accessory | outerwear
    subcategory = Column(String(50), nullable=False)     # t-shirt | jeans | oxford shirt | …
    primary_color = Column(String(50), nullable=False)
    secondary_color = Column(String(50), nullable=True)
    pattern = Column(String(50), default="solid")        # solid | striped | checked | printed | floral | graphic
    style = Column(String(50), nullable=False)           # casual | formal | business_casual | smart_casual | party
    season = Column(String(20), default="all_season")    # summer | winter | rainy | all_season
    gender = Column(String(20), default="unisex")

    # FashionCLIP embedding stored as JSON array string
    embedding = Column(Text, nullable=True)

    # User tags for manual overrides
    tags = Column(JSON, default=list)

    # Lifecycle
    is_active = Column(Boolean, default=True)
    wear_count = Column(Integer, default=0)
    last_worn = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="clothing_items")
    outfit_items = relationship("OutfitItem", back_populates="clothing_item", cascade="all, delete-orphan")


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=True)
    occasion = Column(String(50), nullable=False)
    season = Column(String(20), nullable=False)

    # Scores from the rules engine
    total_score = Column(Float, default=0.0)
    color_score = Column(Float, default=0.0)
    style_score = Column(Float, default=0.0)
    occasion_score = Column(Float, default=0.0)
    season_score = Column(Float, default=0.0)
    repetition_score = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    recommendations = relationship("OutfitRecommendation", back_populates="outfit")
    history = relationship("OutfitHistory", back_populates="outfit")


class OutfitItem(Base):
    """Junction table linking clothing items to an outfit with position info."""
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    clothing_item_id = Column(Integer, ForeignKey("clothing_items.id"), nullable=False)
    position = Column(String(30), nullable=False)        # top | bottom | shoes | outerwear | accessory

    outfit = relationship("Outfit", back_populates="items")
    clothing_item = relationship("ClothingItem", back_populates="outfit_items")


class OutfitRecommendation(Base):
    __tablename__ = "outfit_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    occasion = Column(String(50), nullable=False)
    season = Column(String(20), nullable=False)
    score = Column(Float, default=0.0)
    recommended_date = Column(DateTime(timezone=True), nullable=True)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    outfit = relationship("Outfit", back_populates="recommendations")


class OccasionType(Base):
    __tablename__ = "occasion_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    required_categories = Column(JSON, default=list)     # e.g. ["topwear", "bottomwear", "footwear"]
    optional_categories = Column(JSON, default=list)     # e.g. ["outerwear", "accessory"]
    description = Column(Text, nullable=True)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferred_occasions = Column(JSON, default=list)
    preferred_styles = Column(JSON, default=list)
    preferred_colors = Column(JSON, default=list)
    avoid_colors = Column(JSON, default=list)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="preferences")


class OutfitHistory(Base):
    __tablename__ = "outfit_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    worn_date = Column(DateTime(timezone=True), nullable=False)
    occasion = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="outfit_history")
    outfit = relationship("Outfit", back_populates="history")


class WardrobeStatistic(Base):
    __tablename__ = "wardrobe_statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_items = Column(Integer, default=0)
    category_breakdown = Column(JSON, default=dict)   # {"topwear": 12, "bottomwear": 8, …}
    color_breakdown = Column(JSON, default=dict)       # {"navy blue": 5, "white": 4, …}
    most_worn_items = Column(JSON, default=list)       # [{"id": 1, "name": "…", "count": 10}, …]
    least_worn_items = Column(JSON, default=list)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="wardrobe_stats")
