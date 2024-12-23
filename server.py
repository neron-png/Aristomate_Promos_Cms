from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from sqlmodel import SQLModel, create_engine, Session, select, Field, JSON, DATETIME, DateTime
import os
import json
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./promos.db"
engine = create_engine(DATABASE_URL)

class Promo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    promo_id: str = Field(index=True, unique=True, foreign_key="promocampaign.promo_id")
    query_count: int = Field(default=0)
    click_count: int = Field(default=0)

class PromoCampaign(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    promo_id: str = Field(index=True, unique=True)
    filters: str = Field(default="[]") #JSON string
    title: str = Field(default="")
    description: str = Field(default="")
    link: str = Field(default="")

class PromoActive(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    promo_id: str = Field(index=True, unique=True, foreign_key="promocampaign.promo_id")
    active: bool = Field(default=True)
    start_date: str = Field(default="")
    end_date: str = Field(default="")


SQLModel.metadata.create_all(engine)

PROMOS_FOLDER = os.path.join(os.path.dirname(__file__), "promos")


def incremate_query_count(promo_id):
    with Session(engine) as session:
        statement = select(Promo).where(Promo.promo_id == promo_id)
        promo = session.exec(statement).first()
        if not promo:
            promo = Promo(promo_id=promo_id)
        promo.query_count += 1
        session.add(promo)
        session.commit()


def increment_click_count(promo_id):
    with Session(engine) as session:
        statement = select(Promo).where(Promo.promo_id == promo_id)
        promo = session.exec(statement).first()
        if not promo:
            promo = Promo(promo_id=promo_id)
        promo.click_count += 1
        session.add(promo)
        session.commit()


def checkActive(promo_id):
    # Check if the promo is active and if it is within the start and end date.
    # Also if the promo is active and no start and end date is provided, it is considered active.
    # And also create it if it does not exist.
    with Session(engine) as session:
        statement = select(PromoActive).where(PromoActive.promo_id == promo_id)
        promo = session.exec(statement).first()
        if not promo:
            promo = PromoActive(promo_id=promo_id, active=True)
            session.add(promo)
            session.commit()
        if promo.active:
            current_date = datetime.now()
            start_date = datetime.strptime(promo.start_date, "%Y-%m-%d") if promo.start_date else None
            end_date = datetime.strptime(promo.end_date, "%Y-%m-%d") if promo.end_date else None
            if (not start_date and not end_date) or start_date <= current_date <= end_date:
                return True
        return False

@app.get("/promo/image/{promo_id}")
def get_promo(promo_id: str):
    with Session(engine) as session:

        newStatement = select(PromoCampaign).where(PromoCampaign.promo_id == promo_id)
        campaign = session.exec(newStatement).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Promo not found")
        
        incremate_query_count(promo_id)

        file_path = os.path.join(PROMOS_FOLDER, f"{promo_id}.webp")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(file_path)

@app.get("/promo/link/{promo_id}")
def get_promo_link(promo_id: str):
    with Session(engine) as session:

        newStatement = select(PromoCampaign).where(PromoCampaign.promo_id == promo_id)
        campaign = session.exec(newStatement).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Promo not found")
        
        increment_click_count(promo_id)
        
        return RedirectResponse(url=campaign.link)

@app.get("/promos")
def get_promos():
    with Session(engine) as session:
        campaigns = session.exec(select(PromoCampaign)).all()

        # Changing the filters from JSON string to JSON object
        parsed_campaigns = []
        for campaign in campaigns:
            if not checkActive(campaign.promo_id):
                continue
            parsed_campaigns.append(jsonable_encoder(campaign))
            content = {
                "title": campaign.title,
                "description": campaign.description,
                "image": f"/promo/image/{campaign.promo_id}",
                "link": f"/promo/link/{campaign.promo_id}",
            }
            parsed_campaigns[-1]["filters"] = json.loads(parsed_campaigns[-1]["filters"])
            parsed_campaigns[-1]["content"] = content

        return parsed_campaigns

# templates = Jinja2Templates(directory="templates")
# @app.get("/display_promos", response_class=HTMLResponse)
# async def get_all_promos(Request: Request):
#     return templates.TemplateResponse("alltogether.html", {"request": Request})
    