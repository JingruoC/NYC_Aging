from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from .db import Base


class Recipe(Base):
    __tablename__ = "recipes"

    recipe_id = Column(Integer, primary_key=True, index=True)
    recipe_name = Column(String(255), nullable=False, index=True)
    meal_type = Column(String(50), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    calories = Column(Float, nullable=False)
    sodium_mg = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    fiber_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    tags = Column(JSON, nullable=False, default=list)
    is_approved = Column(Boolean, nullable=False, default=True, index=True)
    ingredients = Column(JSON, nullable=False, default=list)
    instructions = Column(JSON, nullable=False, default=list)
    serving_size = Column(String(100), nullable=True)
    yield_servings = Column(Integer, nullable=False, default=50)
    scale_note = Column(Text, nullable=True)
    contributed_by = Column(String(255), nullable=True)
    created_on = Column(Date, nullable=True)
    is_public = Column(Boolean, nullable=False, default=True, index=True)
    is_favorite = Column(Boolean, nullable=False, default=False, index=True)
    is_dead = Column(Boolean, nullable=False, default=False, index=True)
    nutrient_claims = Column(JSON, nullable=False, default=list)
    vitamin_c_mg = Column(Float, nullable=False, default=0)
    calcium_mg = Column(Float, nullable=False, default=0)
    saturated_fat_g = Column(Float, nullable=False, default=0)
    trans_fat_g = Column(Float, nullable=False, default=0)
    cholesterol_mg = Column(Float, nullable=False, default=0)
    carbohydrates_g = Column(Float, nullable=False, default=0)
    total_sugars_g = Column(Float, nullable=False, default=0)
    added_sugars_g = Column(Float, nullable=False, default=0)
    vitamin_d_mcg = Column(Float, nullable=False, default=0)
    iron_mg = Column(Float, nullable=False, default=0)
    potassium_mg = Column(Float, nullable=False, default=0)


class RecipeAttachment(Base):
    __tablename__ = "recipe_attachments"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(150), nullable=False, default="application/octet-stream")
    file_kind = Column(String(100), nullable=False, default="supporting_document", index=True)
    file_size = Column(Integer, nullable=False, default=0)
    content = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class RecipeComment(Base):
    __tablename__ = "recipe_comments"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(100), nullable=False)
    author = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    visibility = Column(String(100), nullable=False, default="Admin and provider")
    badge_class = Column(String(50), nullable=False, default="brand")
    is_user_comment = Column(Boolean, nullable=False, default=True)
    target_type = Column(String(50), nullable=False, default="recipe", index=True)
    target_label = Column(String(255), nullable=True)
    nutrient_key = Column(String(100), nullable=True)
    review_status = Column(String(50), nullable=False, default="open", index=True)


class HomeUpdate(Base):
    __tablename__ = "home_updates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    update_type = Column(String(50), nullable=False, default="Announcement", index=True)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    published_on = Column(Date, nullable=False, default=date.today, index=True)
    image_source = Column(Text, nullable=True)


class ResourceFile(Base):
    __tablename__ = "resource_files"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    audience = Column(String(100), nullable=False, default="Staff + Providers", index=True)
    last_updated = Column(Date, nullable=False, default=date.today, index=True)
    uploaded_by = Column(String(255), nullable=False, default="NYC Aging Nutrition Unit")
    file_name = Column(String(255), nullable=False)
    content_type = Column(String(150), nullable=False, default="application/octet-stream")
    file_size = Column(Integer, nullable=False, default=0)
    content = Column(LargeBinary, nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class RecipeHomeCategorySetting(Base):
    __tablename__ = "recipe_home_category_settings"

    category_key = Column(String(100), primary_key=True)
    is_visible = Column(Boolean, nullable=False, default=True)
    display_label = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contract_name = Column(String(255), nullable=True, index=True)
    program_type = Column(String(100), nullable=True, index=True)
    meal_type = Column(String(100), nullable=True, index=True)
    menu_coverage = Column(String(100), nullable=True)
    diet_type = Column(String(100), nullable=True, index=True)
    menu_format = Column(String(100), nullable=True)
    menu_duration_type = Column(String(100), nullable=True)
    meal_served_format = Column(String(150), nullable=True)
    menu_tags = Column(JSON, nullable=False, default=list)
    cycle = Column(String(100), nullable=True, index=True)
    cycle_start_date = Column(Date, nullable=True)
    cycle_end_date = Column(Date, nullable=True)
    contracts = Column(JSON, nullable=False, default=list)
    sample_menu_id = Column(Integer, nullable=True)
    completed_weeks = Column(JSON, nullable=False, default=list)
    submitted_programs = Column(JSON, nullable=False, default=list)
    status = Column(String(50), nullable=False, default="Draft", index=True)
    status_date = Column(Date, nullable=True)
    submitted_to = Column(String(255), nullable=True)
    submitted_to_nyc_aging_on = Column(Date, nullable=True)
    nutrition_advisor = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=True)
    service_date = Column(Date, nullable=False, default=date.today)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    days_per_week = Column(Integer, nullable=False, default=5)
    cycle_week = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    returned_comments = Column(Text, nullable=True)
    approval_notes = Column(Text, nullable=True)
    is_favorite = Column(Boolean, nullable=False, default=False, index=True)

    items = relationship("MenuItem", cascade="all, delete-orphan", back_populates="menu")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    day_index = Column(Integer, nullable=False, default=0)
    meal_slot = Column(String(50), nullable=True)
    component_key = Column(String(50), nullable=True)
    is_alternate = Column(Boolean, nullable=False, default=False)
    source_type = Column(String(50), nullable=False, default="manual")

    menu = relationship("Menu", back_populates="items")


class MenuComment(Base):
    __tablename__ = "menu_comments"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    action = Column(String(100), nullable=False)
    author = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    visibility = Column(String(100), nullable=False, default="Admin and provider")
    badge_class = Column(String(50), nullable=False, default="brand")
    is_user_comment = Column(Boolean, nullable=False, default=True)
    target_type = Column(String(50), nullable=False, default="menu", index=True)
    target_label = Column(String(255), nullable=True)
    day_index = Column(Integer, nullable=True)
    meal_slot = Column(String(100), nullable=True)
    component_key = Column(String(100), nullable=True)
    recipe_id = Column(Integer, nullable=True)
    nutrient_key = Column(String(100), nullable=True)
    review_status = Column(String(50), nullable=False, default="open", index=True)


class HistoricalMenu(Base):
    __tablename__ = "historical_menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    service_date = Column(Date, nullable=False)
    program_type = Column(String(100), nullable=True, index=True)
    meal_type = Column(String(100), nullable=True, index=True)
    menu_coverage = Column(String(100), nullable=True)
    diet_type = Column(String(100), nullable=True, index=True)
    menu_duration_type = Column(String(100), nullable=True)
    meal_served_format = Column(String(150), nullable=True)
    menu_tags = Column(JSON, nullable=False, default=list)
    cycle = Column(String(100), nullable=True, index=True)
    days_per_week = Column(Integer, nullable=False, default=5)
    contracts = Column(JSON, nullable=False, default=list)
    sample_category = Column(String(100), nullable=True)
    passes_nutrition = Column(Boolean, nullable=False, default=True, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    items = relationship("HistoricalMenuItem", cascade="all, delete-orphan", back_populates="menu")


class HistoricalMenuItem(Base):
    __tablename__ = "historical_menu_items"

    id = Column(Integer, primary_key=True, index=True)
    historical_menu_id = Column(Integer, ForeignKey("historical_menus.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id"), nullable=False, index=True)
    position = Column(Integer, nullable=False, default=0)
    day_index = Column(Integer, nullable=False, default=0)
    meal_slot = Column(String(50), nullable=True)
    component_key = Column(String(50), nullable=True)
    is_alternate = Column(Boolean, nullable=False, default=False)
    source_type = Column(String(50), nullable=False, default="sample")

    menu = relationship("HistoricalMenu", back_populates="items")


class NutrientThreshold(Base):
    __tablename__ = "nutrient_thresholds"

    id = Column(Integer, primary_key=True, index=True)
    nutrient_key = Column(String(50), nullable=False, unique=True, index=True)
    low_fail = Column(Float, nullable=True)
    low_warn = Column(Float, nullable=True)
    high_warn = Column(Float, nullable=True)
    high_fail = Column(Float, nullable=True)
    unit = Column(String(20), nullable=False, default="")


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    endpoint = Column(String(100), nullable=False)
    selected_recipe_ids = Column(JSON, nullable=False, default=list)
    result_count = Column(Integer, nullable=False, default=0)
    details = Column("metadata", JSON, nullable=False, default=dict)
