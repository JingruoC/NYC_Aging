from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


MealType = Literal["breakfast", "lunch", "dinner", "snack"]


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recipe_id: int
    recipe_name: str
    meal_type: str
    category: str
    calories: float
    sodium_mg: float
    protein_g: float
    fiber_g: float
    fat_g: float
    tags: list[str]
    is_approved: bool
    ingredients: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    serving_size: Optional[str] = None
    yield_servings: int = 50
    scale_note: Optional[str] = None
    contributed_by: Optional[str] = None
    created_on: Optional[date] = None
    is_public: bool = True
    is_favorite: bool = False
    is_dead: bool = False
    nutrient_claims: list[str] = Field(default_factory=list)
    vitamin_c_mg: float = 0
    calcium_mg: float = 0


class RecipeCreate(BaseModel):
    recipe_name: str
    meal_type: str = "lunch"
    category: str = "entree"
    calories: float = 0
    sodium_mg: float = 0
    protein_g: float = 0
    fiber_g: float = 0
    fat_g: float = 0
    tags: list[str] = Field(default_factory=list)
    is_approved: bool = False
    ingredients: list[str] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    serving_size: Optional[str] = None
    yield_servings: int = 1
    scale_note: Optional[str] = None
    contributed_by: Optional[str] = None
    created_on: Optional[date] = None
    is_public: bool = True
    is_favorite: bool = False
    is_dead: bool = False
    nutrient_claims: list[str] = Field(default_factory=list)
    vitamin_c_mg: float = 0
    calcium_mg: float = 0


class RecipeUpdate(BaseModel):
    recipe_name: Optional[str] = None
    meal_type: Optional[str] = None
    category: Optional[str] = None
    calories: Optional[float] = None
    sodium_mg: Optional[float] = None
    protein_g: Optional[float] = None
    fiber_g: Optional[float] = None
    fat_g: Optional[float] = None
    tags: Optional[list[str]] = None
    is_approved: Optional[bool] = None
    ingredients: Optional[list[str]] = None
    instructions: Optional[list[str]] = None
    serving_size: Optional[str] = None
    yield_servings: Optional[int] = None
    scale_note: Optional[str] = None
    contributed_by: Optional[str] = None
    created_on: Optional[date] = None
    is_public: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_dead: Optional[bool] = None
    nutrient_claims: Optional[list[str]] = None
    vitamin_c_mg: Optional[float] = None
    calcium_mg: Optional[float] = None


class RecipeCommentCreate(BaseModel):
    action: str
    author: str
    role: str
    body: str
    visibility: str = "Admin and provider"
    badge_class: str = "brand"
    is_user_comment: bool = True
    target_type: str = "recipe"
    target_label: Optional[str] = None
    nutrient_key: Optional[str] = None
    review_status: str = "open"


class RecipeCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recipe_id: int
    created_at: datetime
    action: str
    author: str
    role: str
    body: str
    visibility: str
    badge_class: str
    is_user_comment: bool
    target_type: str = "recipe"
    target_label: Optional[str] = None
    nutrient_key: Optional[str] = None
    review_status: str = "open"


class MenuItemIn(BaseModel):
    recipe_id: int
    position: int = 0
    day_index: int = 0
    meal_slot: Optional[str] = None
    component_key: Optional[str] = None
    is_alternate: bool = False
    source_type: str = "manual"


class MenuCreate(BaseModel):
    name: str
    contract_name: Optional[str] = None
    program_type: Optional[str] = None
    meal_type: Optional[str] = None
    menu_coverage: Optional[str] = None
    diet_type: Optional[str] = None
    menu_format: Optional[str] = None
    menu_duration_type: Optional[str] = None
    meal_served_format: Optional[str] = None
    menu_tags: list[str] = Field(default_factory=list)
    cycle: Optional[str] = None
    cycle_start_date: Optional[date] = None
    cycle_end_date: Optional[date] = None
    contracts: list[str] = Field(default_factory=list)
    sample_menu_id: Optional[int] = None
    completed_weeks: list[int] = Field(default_factory=list)
    submitted_programs: list[str] = Field(default_factory=list)
    status: str = "Draft"
    status_date: Optional[date] = None
    submitted_to: Optional[str] = None
    submitted_to_nyc_aging_on: Optional[date] = None
    nutrition_advisor: Optional[str] = None
    created_by: Optional[str] = None
    start_date: date = Field(default_factory=date.today)
    end_date: Optional[date] = None
    days_per_week: int = 5
    cycle_week: int = 1
    notes: Optional[str] = None
    returned_comments: Optional[str] = None
    approval_notes: Optional[str] = None
    is_favorite: bool = False
    items: list[MenuItemIn] = Field(default_factory=list)
    recipe_ids: list[int] = Field(default_factory=list)


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    recipe_id: int
    position: int
    day_index: int = 0
    meal_slot: Optional[str] = None
    component_key: Optional[str] = None
    is_alternate: bool = False
    source_type: str = "manual"
    recipe: RecipeOut | None = None


class MenuOut(BaseModel):
    id: int
    name: str
    contract_name: Optional[str] = None
    program_type: Optional[str] = None
    meal_type: Optional[str] = None
    menu_coverage: Optional[str] = None
    diet_type: Optional[str] = None
    menu_format: Optional[str] = None
    menu_duration_type: Optional[str] = None
    meal_served_format: Optional[str] = None
    menu_tags: list[str] = Field(default_factory=list)
    cycle: Optional[str] = None
    cycle_start_date: Optional[date] = None
    cycle_end_date: Optional[date] = None
    contracts: list[str] = Field(default_factory=list)
    sample_menu_id: Optional[int] = None
    completed_weeks: list[int] = Field(default_factory=list)
    submitted_programs: list[str] = Field(default_factory=list)
    status: str = "Draft"
    status_date: Optional[date] = None
    submitted_to: Optional[str] = None
    submitted_to_nyc_aging_on: Optional[date] = None
    nutrition_advisor: Optional[str] = None
    created_by: Optional[str] = None
    service_date: date
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days_per_week: int = 5
    cycle_week: int = 1
    created_at: datetime
    notes: Optional[str] = None
    returned_comments: Optional[str] = None
    approval_notes: Optional[str] = None
    is_favorite: bool = False
    items: list[MenuItemOut]


class MenuSummaryOut(BaseModel):
    id: int
    name: str
    contract_name: Optional[str] = None
    program_type: Optional[str] = None
    meal_type: Optional[str] = None
    menu_coverage: Optional[str] = None
    diet_type: Optional[str] = None
    menu_format: Optional[str] = None
    menu_duration_type: Optional[str] = None
    meal_served_format: Optional[str] = None
    menu_tags: list[str] = Field(default_factory=list)
    cycle: Optional[str] = None
    cycle_start_date: Optional[date] = None
    cycle_end_date: Optional[date] = None
    contracts: list[str] = Field(default_factory=list)
    sample_menu_id: Optional[int] = None
    completed_weeks: list[int] = Field(default_factory=list)
    submitted_programs: list[str] = Field(default_factory=list)
    status: str = "Draft"
    status_date: Optional[date] = None
    submitted_to: Optional[str] = None
    submitted_to_nyc_aging_on: Optional[date] = None
    nutrition_advisor: Optional[str] = None
    created_by: Optional[str] = None
    service_date: date
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days_per_week: int = 5
    cycle_week: int = 1
    created_at: datetime
    notes: Optional[str] = None
    returned_comments: Optional[str] = None
    approval_notes: Optional[str] = None
    is_favorite: bool = False
    item_count: int = 0
    recipe_names: list[str] = Field(default_factory=list)


class MenuCommentCreate(BaseModel):
    action: str
    author: str
    role: str
    body: str
    visibility: str = "Admin and provider"
    badge_class: str = "brand"
    is_user_comment: bool = True
    target_type: str = "menu"
    target_label: Optional[str] = None
    day_index: Optional[int] = None
    meal_slot: Optional[str] = None
    component_key: Optional[str] = None
    recipe_id: Optional[int] = None
    nutrient_key: Optional[str] = None
    review_status: str = "open"


class MenuCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_id: int
    created_at: datetime
    action: str
    author: str
    role: str
    body: str
    visibility: str
    badge_class: str
    is_user_comment: bool
    target_type: str = "menu"
    target_label: Optional[str] = None
    day_index: Optional[int] = None
    meal_slot: Optional[str] = None
    component_key: Optional[str] = None
    recipe_id: Optional[int] = None
    nutrient_key: Optional[str] = None
    review_status: str = "open"


class HistoricalMenuSummaryOut(BaseModel):
    id: int
    name: str
    service_date: date
    program_type: Optional[str] = None
    meal_type: Optional[str] = None
    menu_coverage: Optional[str] = None
    diet_type: Optional[str] = None
    menu_duration_type: Optional[str] = None
    meal_served_format: Optional[str] = None
    menu_tags: list[str] = Field(default_factory=list)
    cycle: Optional[str] = None
    days_per_week: int = 5
    contracts: list[str] = Field(default_factory=list)
    sample_category: Optional[str] = None
    passes_nutrition: bool
    notes: Optional[str] = None
    item_count: int = 0
    recipe_names: list[str] = Field(default_factory=list)


class HistoricalMenuItemOut(BaseModel):
    recipe_id: int
    position: int
    meal_slot: Optional[str] = None
    component_key: Optional[str] = None
    is_alternate: bool = False
    source_type: str = "sample"
    recipe: RecipeOut


class HistoricalMenuDetailOut(BaseModel):
    id: int
    name: str
    service_date: date
    program_type: Optional[str] = None
    meal_type: Optional[str] = None
    menu_coverage: Optional[str] = None
    diet_type: Optional[str] = None
    menu_duration_type: Optional[str] = None
    meal_served_format: Optional[str] = None
    menu_tags: list[str] = Field(default_factory=list)
    cycle: Optional[str] = None
    days_per_week: int = 5
    contracts: list[str] = Field(default_factory=list)
    sample_category: Optional[str] = None
    passes_nutrition: bool
    notes: Optional[str] = None
    items: list[HistoricalMenuItemOut] = Field(default_factory=list)


class ThresholdOut(BaseModel):
    nutrient_key: str
    low_fail: Optional[float] = None
    low_warn: Optional[float] = None
    high_warn: Optional[float] = None
    high_fail: Optional[float] = None
    unit: str


class NutrientStatus(BaseModel):
    nutrient_key: str
    total: float
    unit: str
    status: Literal["pass", "warning", "fail"]
    message: str


class MenuAnalysisRequest(BaseModel):
    recipe_ids: list[int]
    items: list[MenuItemIn] = Field(default_factory=list)
    thresholds: Optional[dict[str, ThresholdOut]] = None


class MenuAnalysisOut(BaseModel):
    totals: dict[str, float]
    statuses: list[NutrientStatus]
    meal_requirements: list["MealRequirement"] = Field(default_factory=list)
    overall_status: Literal["pass", "warning", "fail"]
    selected_recipes: list[RecipeOut]


class RecommendationCandidate(BaseModel):
    recipe: RecipeOut
    score: float
    reasons: list[str]


class MealRequirementSuggestion(BaseModel):
    recipe: RecipeOut
    score: float
    reasons: list[str]


class MealRequirement(BaseModel):
    rule_key: str
    title: str
    status: Literal["pass", "warning", "fail"]
    message: str
    component_badges: list[str] = Field(default_factory=list)
    missing_component_badges: list[str] = Field(default_factory=list)
    details: list[str] = Field(default_factory=list)
    suggestions: list[MealRequirementSuggestion] = Field(default_factory=list)


class AutocompleteRequest(BaseModel):
    selected_recipe_ids: list[int]
    limit: int = 8


class RevisionRequest(BaseModel):
    selected_recipe_ids: list[int]
    limit: int = 8


class SimilarMenusRequest(BaseModel):
    selected_recipe_ids: list[int]
    limit: int = 5


class SimilarMenuOut(BaseModel):
    id: int
    name: str
    service_date: date
    passes_nutrition: bool
    similarity: float
    recipe_ids: list[int]
    notes: Optional[str] = None


class AnalyticsOut(BaseModel):
    top_recipes: list[dict[str, Any]]
    top_pairings: list[dict[str, Any]]
    category_counts: list[dict[str, Any]]
    meal_type_counts: list[dict[str, Any]]
