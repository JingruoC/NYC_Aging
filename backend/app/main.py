from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select

from .db import SessionLocal, ensure_sqlite_schema
from .models import HistoricalMenu, HistoricalMenuItem, HomeUpdate, Menu, MenuComment, MenuItem, Recipe, RecipeAttachment, RecipeComment, RecipeHomeCategorySetting, ResourceFile
from .recipe_exports import build_nutrition_workbook, build_recipe_submission_workbook
from .schemas import (
    AnalyticsOut,
    AutocompleteRequest,
    HistoricalMenuDetailOut,
    HistoricalMenuItemOut,
    HistoricalMenuSummaryOut,
    HomeUpdateCreate,
    HomeUpdateOut,
    MenuAnalysisOut,
    MenuAnalysisRequest,
    MenuCommentCreate,
    MenuCommentOut,
    MenuCreate,
    MenuItemOut,
    MenuOut,
    MenuSummaryOut,
    RecipeCreate,
    RecipeAttachmentOut,
    RecipeCommentCreate,
    RecipeCommentOut,
    RecipeHomeCategorySettingOut,
    RecipeHomeCategorySettingUpdate,
    RecipeOut,
    RecipeUpdate,
    ResourceFileOut,
    RevisionRequest,
    SimilarMenusRequest,
)
from .seed import seed_database
from .services import (
    analytics_summary,
    analyze_menu,
    autocomplete_recommendations,
    get_recipes,
    log_recommendation,
    revision_recommendations,
    search_recipes,
    similar_menus,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_sqlite_schema()
    if os.getenv("AUTO_SEED_DB", "true").lower() == "true":
        seed_database()
    yield


app = FastAPI(title="NYC Aging Menu Planning MVP", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5050",
        "http://127.0.0.1:5050",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/resources", response_model=list[ResourceFileOut])
def list_resource_files():
    with SessionLocal() as db:
        resources = db.scalars(
            select(ResourceFile).order_by(ResourceFile.last_updated.desc(), ResourceFile.title.asc())
        ).all()
        return [ResourceFileOut.model_validate(resource) for resource in resources]


@app.post("/resources", response_model=ResourceFileOut)
async def upload_resource_file(
    title: str = Form(...),
    resource_type: str = Form(...),
    description: str = Form(default=""),
    audience: str = Form(default="Staff + Providers"),
    last_updated: date | None = Form(default=None),
    uploaded_by: str = Form(default="NYC Aging Nutrition Unit"),
    file: UploadFile = File(...),
):
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Resource files are limited to 20 MB per file")
    if not content:
        raise HTTPException(status_code=400, detail="Resource file cannot be empty")

    with SessionLocal() as db:
        resource = ResourceFile(
            title=title.strip(),
            resource_type=resource_type.strip(),
            description=description.strip(),
            audience=audience.strip(),
            last_updated=last_updated or date.today(),
            uploaded_by=uploaded_by.strip(),
            file_name=file.filename or "resource-file",
            content_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            content=content,
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        return ResourceFileOut.model_validate(resource)


@app.get("/resources/{resource_id}/file")
def download_resource_file(resource_id: int, download: bool = Query(default=False)):
    with SessionLocal() as db:
        resource = db.get(ResourceFile, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource file not found")
        disposition = "attachment" if download else "inline"
        safe_name = resource.file_name.replace('"', "")
        return Response(
            content=resource.content,
            media_type=resource.content_type,
            headers={"Content-Disposition": f'{disposition}; filename="{safe_name}"'},
        )


@app.delete("/resources/{resource_id}", status_code=204)
def delete_resource_file(resource_id: int):
    with SessionLocal() as db:
        resource = db.get(ResourceFile, resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource file not found")
        db.delete(resource)
        db.commit()
        return Response(status_code=204)


@app.get("/", include_in_schema=False)
def frontend_redirect():
    return RedirectResponse(os.getenv("FRONTEND_URL", "http://127.0.0.1:5050"))


@app.get("/home-updates", response_model=list[HomeUpdateOut])
def list_home_updates():
    with SessionLocal() as db:
        return db.scalars(select(HomeUpdate).order_by(HomeUpdate.published_on.desc(), HomeUpdate.id.desc())).all()


@app.get("/home-updates/{update_id}", response_model=HomeUpdateOut)
def get_home_update(update_id: int):
    with SessionLocal() as db:
        update = db.get(HomeUpdate, update_id)
        if update is None:
            raise HTTPException(status_code=404, detail="Home update not found")
        return HomeUpdateOut.model_validate(update)


@app.post("/home-updates", response_model=HomeUpdateOut)
def create_home_update(payload: HomeUpdateCreate):
    with SessionLocal() as db:
        values = payload.model_dump()
        values["content"] = (values.get("content") or values["summary"]).strip()
        update = HomeUpdate(**values)
        db.add(update)
        db.commit()
        db.refresh(update)
        return HomeUpdateOut.model_validate(update)


@app.get("/recipe-home-categories", response_model=list[RecipeHomeCategorySettingOut])
def list_recipe_home_categories():
    with SessionLocal() as db:
        return db.scalars(select(RecipeHomeCategorySetting).order_by(RecipeHomeCategorySetting.category_key)).all()


@app.put("/recipe-home-categories/{category_key}", response_model=RecipeHomeCategorySettingOut)
def update_recipe_home_category(category_key: str, payload: RecipeHomeCategorySettingUpdate):
    with SessionLocal() as db:
        setting = db.get(RecipeHomeCategorySetting, category_key)
        if setting is None:
            setting = RecipeHomeCategorySetting(
                category_key=category_key,
                is_visible=payload.is_visible,
                display_label=payload.display_label,
                description=payload.description,
            )
            db.add(setting)
        else:
            setting.is_visible = payload.is_visible
            if payload.display_label is not None:
                setting.display_label = payload.display_label
            if payload.description is not None:
                setting.description = payload.description
        db.commit()
        db.refresh(setting)
        return RecipeHomeCategorySettingOut.model_validate(setting)


@app.get("/recipes", response_model=list[RecipeOut])
def list_recipes(approved_only: bool = Query(default=False)):
    with SessionLocal() as db:
        return get_recipes(db, only_approved=approved_only)


@app.get("/recipes/search", response_model=list[RecipeOut])
def find_recipes(q: str = ""):
    with SessionLocal() as db:
        return search_recipes(db, q)


@app.post("/recipes", response_model=RecipeOut)
def create_recipe(payload: RecipeCreate):
    with SessionLocal() as db:
        recipe = Recipe(**payload.model_dump())
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return RecipeOut.model_validate(recipe)


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return RecipeOut.model_validate(recipe)


@app.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, payload: RecipeUpdate):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(recipe, key, value)
        db.add(recipe)
        db.commit()
        db.refresh(recipe)
        return RecipeOut.model_validate(recipe)


@app.get("/recipes/{recipe_id}/comments", response_model=list[RecipeCommentOut])
def list_recipe_comments(recipe_id: int):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        comments = db.scalars(
            select(RecipeComment)
            .where(RecipeComment.recipe_id == recipe_id)
            .order_by(RecipeComment.created_at.desc(), RecipeComment.id.desc())
        ).all()
        return [RecipeCommentOut.model_validate(comment) for comment in comments]


@app.post("/recipes/{recipe_id}/comments", response_model=RecipeCommentOut)
def create_recipe_comment(recipe_id: int, payload: RecipeCommentCreate):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        comment = RecipeComment(recipe_id=recipe_id, **payload.model_dump())
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return RecipeCommentOut.model_validate(comment)


@app.get("/recipes/{recipe_id}/attachments", response_model=list[RecipeAttachmentOut])
def list_recipe_attachments(recipe_id: int):
    with SessionLocal() as db:
        if db.get(Recipe, recipe_id) is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        attachments = db.scalars(
            select(RecipeAttachment)
            .where(RecipeAttachment.recipe_id == recipe_id)
            .order_by(RecipeAttachment.uploaded_at.desc(), RecipeAttachment.id.desc())
        ).all()
        return [RecipeAttachmentOut.model_validate(attachment) for attachment in attachments]


@app.post("/recipes/{recipe_id}/attachments", response_model=RecipeAttachmentOut)
async def upload_recipe_attachment(
    recipe_id: int,
    file_kind: str = Query(default="supporting_document"),
    file: UploadFile = File(...),
):
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Recipe attachments are limited to 20 MB per file")
    with SessionLocal() as db:
        if db.get(Recipe, recipe_id) is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        attachment = RecipeAttachment(
            recipe_id=recipe_id,
            file_name=file.filename or "recipe-attachment",
            content_type=file.content_type or "application/octet-stream",
            file_kind=file_kind,
            file_size=len(content),
            content=content,
        )
        db.add(attachment)
        db.commit()
        db.refresh(attachment)
        return RecipeAttachmentOut.model_validate(attachment)


@app.get("/recipes/{recipe_id}/attachments/{attachment_id}")
def download_recipe_attachment(recipe_id: int, attachment_id: int, download: bool = Query(default=False)):
    with SessionLocal() as db:
        attachment = db.get(RecipeAttachment, attachment_id)
        if attachment is None or attachment.recipe_id != recipe_id:
            raise HTTPException(status_code=404, detail="Recipe attachment not found")
        disposition = "attachment" if download else "inline"
        safe_name = attachment.file_name.replace('"', "")
        return Response(
            content=attachment.content,
            media_type=attachment.content_type,
            headers={"Content-Disposition": f'{disposition}; filename="{safe_name}"'},
        )


@app.get("/recipes/{recipe_id}/export/submission.xlsx")
def export_recipe_submission(recipe_id: int):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return Response(
            content=build_recipe_submission_workbook(recipe),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="recipe-{recipe_id}-submission.xlsx"'},
        )


@app.get("/recipes/{recipe_id}/export/nutrition.xlsx")
def export_recipe_nutrition(recipe_id: int):
    with SessionLocal() as db:
        recipe = db.get(Recipe, recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")
        return Response(
            content=build_nutrition_workbook(recipe),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="recipe-{recipe_id}-nutrition-analysis.xlsx"'},
        )


@app.get("/menus", response_model=list[MenuSummaryOut])
def list_menus():
    with SessionLocal() as db:
        menus = db.scalars(select(Menu).order_by(Menu.created_at.desc(), Menu.id.desc())).all()
        summaries: list[MenuSummaryOut] = []
        for menu in menus:
            items = db.scalars(select(MenuItem).where(MenuItem.menu_id == menu.id).order_by(MenuItem.position.asc())).all()
            recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_([item.recipe_id for item in items]))).all()
            recipe_map = {recipe.recipe_id: recipe for recipe in recipe_rows}
            start_date = menu.start_date or menu.service_date
            summaries.append(
                MenuSummaryOut(
                    id=menu.id,
                    name=menu.name,
                    contract_name=menu.contract_name,
                    program_type=menu.program_type,
                    meal_type=menu.meal_type,
                    menu_coverage=menu.menu_coverage,
                    diet_type=menu.diet_type,
                    menu_format=menu.menu_format,
                    menu_duration_type=menu.menu_duration_type,
                    meal_served_format=menu.meal_served_format,
                    menu_tags=menu.menu_tags or [],
                    cycle=menu.cycle,
                    cycle_start_date=menu.cycle_start_date,
                    cycle_end_date=menu.cycle_end_date,
                    contracts=menu.contracts or [],
                    sample_menu_id=menu.sample_menu_id,
                    completed_weeks=menu.completed_weeks or [],
                    submitted_programs=menu.submitted_programs or [],
                    status=menu.status,
                    status_date=menu.status_date,
                    submitted_to=menu.submitted_to,
                    submitted_to_nyc_aging_on=menu.submitted_to_nyc_aging_on,
                    nutrition_advisor=menu.nutrition_advisor,
                    created_by=menu.created_by,
                    service_date=menu.service_date,
                    start_date=start_date,
                    end_date=menu.end_date or start_date,
                    days_per_week=menu.days_per_week,
                    cycle_week=menu.cycle_week,
                    created_at=menu.created_at,
                    notes=menu.notes,
                    returned_comments=menu.returned_comments,
                    approval_notes=menu.approval_notes,
                    is_favorite=bool(menu.is_favorite),
                    item_count=len(items),
                    recipe_names=[recipe_map[item.recipe_id].recipe_name for item in items if item.recipe_id in recipe_map],
                )
            )
        return summaries


@app.get("/sample-menus", response_model=list[HistoricalMenuSummaryOut])
def list_sample_menus():
    with SessionLocal() as db:
        menus = db.scalars(select(HistoricalMenu).order_by(HistoricalMenu.service_date.desc(), HistoricalMenu.id.desc())).all()
        summaries: list[HistoricalMenuSummaryOut] = []
        for menu in menus:
            items = db.scalars(select(HistoricalMenuItem).where(HistoricalMenuItem.historical_menu_id == menu.id).order_by(HistoricalMenuItem.position.asc())).all()
            recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_([item.recipe_id for item in items]))).all()
            summaries.append(
                HistoricalMenuSummaryOut(
                    id=menu.id,
                    name=menu.name,
                    service_date=menu.service_date,
                    program_type=menu.program_type,
                    meal_type=menu.meal_type,
                    menu_coverage=menu.menu_coverage,
                    diet_type=menu.diet_type,
                    menu_duration_type=menu.menu_duration_type,
                    meal_served_format=menu.meal_served_format,
                    menu_tags=menu.menu_tags or [],
                    cycle=menu.cycle,
                    days_per_week=menu.days_per_week,
                    contracts=menu.contracts or [],
                    sample_category=menu.sample_category,
                    passes_nutrition=menu.passes_nutrition,
                    notes=menu.notes,
                    item_count=len(items),
                    recipe_names=[recipe.recipe_name for recipe in recipe_rows],
                )
            )
        return summaries


@app.get("/sample-menus/{menu_id}", response_model=HistoricalMenuDetailOut)
def get_sample_menu(menu_id: int):
    with SessionLocal() as db:
        menu = db.get(HistoricalMenu, menu_id)
        if menu is None:
            raise HTTPException(status_code=404, detail="Sample menu not found")
        items = db.scalars(
            select(HistoricalMenuItem).where(HistoricalMenuItem.historical_menu_id == menu.id).order_by(HistoricalMenuItem.position.asc())
        ).all()
        recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_([item.recipe_id for item in items]))).all()
        recipe_map = {recipe.recipe_id: recipe for recipe in recipe_rows}
        return HistoricalMenuDetailOut(
            id=menu.id,
            name=menu.name,
            service_date=menu.service_date,
            program_type=menu.program_type,
            meal_type=menu.meal_type,
            menu_coverage=menu.menu_coverage,
            diet_type=menu.diet_type,
            menu_duration_type=menu.menu_duration_type,
            meal_served_format=menu.meal_served_format,
            menu_tags=menu.menu_tags or [],
            cycle=menu.cycle,
            days_per_week=menu.days_per_week,
            contracts=menu.contracts or [],
            sample_category=menu.sample_category,
            passes_nutrition=menu.passes_nutrition,
            notes=menu.notes,
            items=[
                HistoricalMenuItemOut(
                    recipe_id=item.recipe_id,
                    position=item.position,
                    day_index=item.day_index,
                    meal_slot=item.meal_slot,
                    component_key=item.component_key or item.meal_slot,
                    is_alternate=item.is_alternate,
                    source_type=item.source_type,
                    recipe=RecipeOut.model_validate(recipe_map[item.recipe_id]),
                )
                for item in items
                if item.recipe_id in recipe_map
            ],
        )


@app.post("/menus", response_model=MenuOut)
def create_menu(payload: MenuCreate):
    with SessionLocal() as db:
        start_date = payload.start_date
        end_date = payload.end_date or (start_date + timedelta(days=max(payload.days_per_week - 1, 0)))
        menu = Menu(
            name=payload.name,
            contract_name=payload.contract_name,
            program_type=payload.program_type,
            meal_type=payload.meal_type,
            menu_coverage=payload.menu_coverage,
            diet_type=payload.diet_type,
            menu_format=payload.menu_format,
            menu_duration_type=payload.menu_duration_type,
            meal_served_format=payload.meal_served_format,
            menu_tags=payload.menu_tags,
            cycle=payload.cycle,
            cycle_start_date=payload.cycle_start_date,
            cycle_end_date=payload.cycle_end_date,
            contracts=payload.contracts,
            sample_menu_id=payload.sample_menu_id,
            completed_weeks=payload.completed_weeks,
            submitted_programs=payload.submitted_programs,
            status=payload.status,
            status_date=payload.status_date or start_date,
            submitted_to=payload.submitted_to,
            submitted_to_nyc_aging_on=payload.submitted_to_nyc_aging_on,
            nutrition_advisor=payload.nutrition_advisor,
            created_by=payload.created_by,
            service_date=start_date,
            start_date=start_date,
            end_date=end_date,
            days_per_week=payload.days_per_week,
            cycle_week=payload.cycle_week,
            notes=payload.notes,
            returned_comments=payload.returned_comments,
            approval_notes=payload.approval_notes,
            is_favorite=payload.is_favorite,
        )
        db.add(menu)
        db.flush()
        menu_items_input = payload.items
        if not menu_items_input and payload.recipe_ids:
            menu_items_input = [
                {"recipe_id": recipe_id, "position": index, "day_index": 0, "meal_slot": None}
                for index, recipe_id in enumerate(payload.recipe_ids, start=1)
            ]

        recipe_ids = [item.recipe_id if hasattr(item, "recipe_id") else item["recipe_id"] for item in menu_items_input]
        recipes = db.scalars(select(Recipe).where(Recipe.recipe_id.in_(recipe_ids))).all()
        recipe_map = {recipe.recipe_id: recipe for recipe in recipes}
        created_items = []
        for index, item in enumerate(menu_items_input, start=1):
            recipe_id = item.recipe_id if hasattr(item, "recipe_id") else item["recipe_id"]
            position = item.position if hasattr(item, "position") else item.get("position", index)
            day_index = item.day_index if hasattr(item, "day_index") else item.get("day_index", 0)
            meal_slot = item.meal_slot if hasattr(item, "meal_slot") else item.get("meal_slot")
            component_key = item.component_key if hasattr(item, "component_key") else item.get("component_key")
            is_alternate = item.is_alternate if hasattr(item, "is_alternate") else item.get("is_alternate", False)
            source_type = item.source_type if hasattr(item, "source_type") else item.get("source_type", "manual")
            if recipe_id not in recipe_map:
                raise HTTPException(status_code=400, detail=f"Recipe {recipe_id} not found")
            menu_item = MenuItem(
                menu_id=menu.id,
                recipe_id=recipe_id,
                position=position,
                day_index=day_index,
                meal_slot=meal_slot or "selected",
                component_key=component_key,
                is_alternate=is_alternate,
                source_type=source_type,
            )
            created_items.append(menu_item)
            db.add(menu_item)
        db.commit()
        db.refresh(menu)
        created_items = db.scalars(select(MenuItem).where(MenuItem.menu_id == menu.id).order_by(MenuItem.position.asc())).all()
        items = [
            MenuItemOut(
                recipe_id=item.recipe_id,
                position=item.position,
                day_index=item.day_index,
                meal_slot=item.meal_slot,
                component_key=item.component_key,
                is_alternate=item.is_alternate,
                source_type=item.source_type,
                recipe=RecipeOut.model_validate(recipe_map[item.recipe_id]),
            )
            for item in sorted(created_items, key=lambda item: item.position)
        ]
        return MenuOut(
            id=menu.id,
            name=menu.name,
            contract_name=menu.contract_name,
            program_type=menu.program_type,
            meal_type=menu.meal_type,
            menu_coverage=menu.menu_coverage,
            diet_type=menu.diet_type,
            menu_format=menu.menu_format,
            menu_duration_type=menu.menu_duration_type,
            meal_served_format=menu.meal_served_format,
            menu_tags=menu.menu_tags or [],
            cycle=menu.cycle,
            cycle_start_date=menu.cycle_start_date,
            cycle_end_date=menu.cycle_end_date,
            contracts=menu.contracts or [],
            sample_menu_id=menu.sample_menu_id,
            completed_weeks=menu.completed_weeks or [],
            submitted_programs=menu.submitted_programs or [],
            status=menu.status,
            status_date=menu.status_date,
            submitted_to=menu.submitted_to,
            submitted_to_nyc_aging_on=menu.submitted_to_nyc_aging_on,
            nutrition_advisor=menu.nutrition_advisor,
            created_by=menu.created_by,
            service_date=menu.service_date,
            start_date=menu.start_date,
            end_date=menu.end_date,
            days_per_week=menu.days_per_week,
            cycle_week=menu.cycle_week,
            created_at=menu.created_at,
            notes=menu.notes,
            returned_comments=menu.returned_comments,
            approval_notes=menu.approval_notes,
            is_favorite=bool(menu.is_favorite),
            items=items,
        )


@app.patch("/menus/{menu_id}/favorite", response_model=MenuSummaryOut)
def update_menu_favorite(menu_id: int, payload: dict):
    with SessionLocal() as db:
        menu = db.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(status_code=404, detail="Menu not found")

        menu.is_favorite = bool(payload.get("is_favorite", False))
        db.commit()
        db.refresh(menu)

        items = db.scalars(select(MenuItem).where(MenuItem.menu_id == menu.id).order_by(MenuItem.position.asc())).all()
        recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_([item.recipe_id for item in items]))).all()
        start_date = menu.start_date or menu.service_date
        return MenuSummaryOut(
            id=menu.id,
            name=menu.name,
            contract_name=menu.contract_name,
            program_type=menu.program_type,
            meal_type=menu.meal_type,
            menu_coverage=menu.menu_coverage,
            diet_type=menu.diet_type,
            menu_format=menu.menu_format,
            menu_duration_type=menu.menu_duration_type,
            meal_served_format=menu.meal_served_format,
            menu_tags=menu.menu_tags or [],
            cycle=menu.cycle,
            cycle_start_date=menu.cycle_start_date,
            cycle_end_date=menu.cycle_end_date,
            contracts=menu.contracts or [],
            sample_menu_id=menu.sample_menu_id,
            completed_weeks=menu.completed_weeks or [],
            submitted_programs=menu.submitted_programs or [],
            status=menu.status,
            status_date=menu.status_date,
            submitted_to=menu.submitted_to,
            submitted_to_nyc_aging_on=menu.submitted_to_nyc_aging_on,
            nutrition_advisor=menu.nutrition_advisor,
            created_by=menu.created_by,
            service_date=menu.service_date,
            start_date=start_date,
            end_date=menu.end_date or start_date,
            days_per_week=menu.days_per_week,
            cycle_week=menu.cycle_week,
            created_at=menu.created_at,
            notes=menu.notes,
            returned_comments=menu.returned_comments,
            approval_notes=menu.approval_notes,
            is_favorite=bool(menu.is_favorite),
            item_count=len(items),
            recipe_names=[recipe.recipe_name for recipe in recipe_rows],
        )


@app.get("/menus/{menu_id}/comments", response_model=list[MenuCommentOut])
def list_menu_comments(menu_id: int):
    with SessionLocal() as db:
        menu = db.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(status_code=404, detail="Menu not found")

        comments = db.scalars(
            select(MenuComment).where(MenuComment.menu_id == menu_id).order_by(MenuComment.created_at.desc(), MenuComment.id.desc())
        ).all()
        return [MenuCommentOut.model_validate(comment) for comment in comments]


@app.post("/menus/{menu_id}/comments", response_model=MenuCommentOut)
def create_menu_comment(menu_id: int, payload: MenuCommentCreate):
    with SessionLocal() as db:
        menu = db.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(status_code=404, detail="Menu not found")

        comment = MenuComment(
            menu_id=menu_id,
            action=payload.action,
            author=payload.author,
            role=payload.role,
            body=payload.body,
            visibility=payload.visibility,
            badge_class=payload.badge_class,
            is_user_comment=payload.is_user_comment,
            target_type=payload.target_type,
            target_label=payload.target_label,
            day_index=payload.day_index,
            meal_slot=payload.meal_slot,
            component_key=payload.component_key,
            recipe_id=payload.recipe_id,
            nutrient_key=payload.nutrient_key,
            review_status=payload.review_status,
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return MenuCommentOut.model_validate(comment)


@app.get("/menus/{menu_id}", response_model=dict)
def get_menu(menu_id: int):
    with SessionLocal() as db:
        menu = db.get(Menu, menu_id)
        if menu is None:
            raise HTTPException(status_code=404, detail="Menu not found")
        items = db.scalars(select(MenuItem).where(MenuItem.menu_id == menu.id).order_by(MenuItem.position.asc())).all()
        recipe_rows = db.scalars(select(Recipe).where(Recipe.recipe_id.in_([item.recipe_id for item in items]))).all()
        recipe_map = {recipe.recipe_id: recipe for recipe in recipe_rows}
        selected_ids = [item.recipe_id for item in items]
        analysis = analyze_menu(
            db,
            selected_ids,
            menu_items=[
                {
                    "recipe_id": item.recipe_id,
                    "position": item.position,
                    "day_index": item.day_index,
                    "meal_slot": item.meal_slot,
                    "component_key": item.component_key,
                    "is_alternate": item.is_alternate,
                    "source_type": item.source_type,
                }
                for item in items
            ],
        )
        start_date = menu.start_date or menu.service_date
        end_date = menu.end_date or start_date
        return {
            "menu": {
                "id": menu.id,
                "name": menu.name,
                "contract_name": menu.contract_name,
                "program_type": menu.program_type,
                "meal_type": menu.meal_type,
                "menu_coverage": menu.menu_coverage,
                "diet_type": menu.diet_type,
                "menu_format": menu.menu_format,
                "menu_duration_type": menu.menu_duration_type,
                "meal_served_format": menu.meal_served_format,
                "menu_tags": menu.menu_tags or [],
                "cycle": menu.cycle,
                "cycle_start_date": menu.cycle_start_date,
                "cycle_end_date": menu.cycle_end_date,
                "contracts": menu.contracts or [],
                "sample_menu_id": menu.sample_menu_id,
                "completed_weeks": menu.completed_weeks or [],
                "submitted_programs": menu.submitted_programs or [],
                "status": menu.status,
                "status_date": menu.status_date,
                "submitted_to": menu.submitted_to,
                "submitted_to_nyc_aging_on": menu.submitted_to_nyc_aging_on,
                "nutrition_advisor": menu.nutrition_advisor,
                "created_by": menu.created_by,
                "service_date": menu.service_date,
                "start_date": start_date,
                "end_date": end_date,
                "days_per_week": menu.days_per_week,
                "cycle_week": menu.cycle_week,
                "created_at": menu.created_at,
                "notes": menu.notes,
                "returned_comments": menu.returned_comments,
                "approval_notes": menu.approval_notes,
                "is_favorite": bool(menu.is_favorite),
                "items": [
                    {
                        "recipe_id": item.recipe_id,
                        "position": item.position,
                        "day_index": item.day_index,
                        "meal_slot": item.meal_slot,
                        "component_key": item.component_key,
                        "is_alternate": item.is_alternate,
                        "source_type": item.source_type,
                        "recipe": RecipeOut.model_validate(recipe_map[item.recipe_id]).model_dump(),
                    }
                    for item in items
                ],
            },
            "analysis": analysis,
            "autocomplete": autocomplete_recommendations(db, selected_ids),
            "revisions": revision_recommendations(db, selected_ids)["suggestions"],
            "similar_menus": similar_menus(db, selected_ids),
        }


@app.post("/menus/analyze", response_model=MenuAnalysisOut)
def analyze(payload: MenuAnalysisRequest):
    with SessionLocal() as db:
        result = analyze_menu(db, payload.recipe_ids, payload.thresholds, [item.model_dump() for item in payload.items])
        log_recommendation(db, "menus/analyze", payload.recipe_ids, len(result["statuses"]))
        return result


@app.post("/recommendations/autocomplete")
def autocomplete(payload: AutocompleteRequest):
    with SessionLocal() as db:
        result = autocomplete_recommendations(db, payload.selected_recipe_ids, payload.limit)
        log_recommendation(db, "recommendations/autocomplete", payload.selected_recipe_ids, len(result))
        return {"items": result}


@app.post("/recommendations/revisions")
def revisions(payload: RevisionRequest):
    with SessionLocal() as db:
        result = revision_recommendations(db, payload.selected_recipe_ids, payload.limit)
        log_recommendation(db, "recommendations/revisions", payload.selected_recipe_ids, sum(len(v) for v in result["suggestions"].values()))
        return result


@app.post("/recommendations/similar-menus")
def similar(payload: SimilarMenusRequest):
    with SessionLocal() as db:
        result = similar_menus(db, payload.selected_recipe_ids, payload.limit)
        log_recommendation(db, "recommendations/similar-menus", payload.selected_recipe_ids, len(result))
        return {"items": result}


@app.get("/analytics", response_model=AnalyticsOut)
def analytics():
    with SessionLocal() as db:
        return analytics_summary(db)
