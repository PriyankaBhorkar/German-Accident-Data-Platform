from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy import text
from database import SessionLocal
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

tags_metadata = [
    
    { "name": "🗂 Metadata",},
    {"name": "📊 Counts and Filters",},
    {"name": "⏳ Time Analytics",},
    {"name": "🏆 Rates & Rankings",},
    {"name": "🔗 Cross-source Analytics"}
] 

# =========================
# FASTAPI APP
# =========================
app = FastAPI(
  title="Accident Data API",
  description="Integrated German road accident and regional statistics platform.",
  version="1.0",
  docs_url=None,
  redoc_url=None,
  openapi_tags=tags_metadata
)
# =========================
# DATA LICENCE METADATA
# =========================

LICENSE_METADATA = {
    "license_name": "Datenlizenz Deutschland – Namensnennung – Version 2.0 (DL-DE BY 2.0)",
    "license_code": "dl-by-de/2.0",
    "license_url": "http://www.dcat-ap.de/def/licenses/dl-by-de/2.0"
}

# =========================
# CUSTOM SWAGGER UI
# =========================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():

    custom_css = """
/* Hide top bar */
.swagger-ui .topbar {
    display: none;
}

/* Center title section */
.swagger-ui .information-container {
    text-align: center !important;
    padding-top: 50px !important;
    padding-bottom: 30px !important;
}

/* Main title */
.swagger-ui .info .title {
    width: 100%;
    text-align: center !important;
    font-size: 48px !important;
    font-weight: 800 !important;
    color: #111827 !important;
    margin-top: 1px;
}

/* Subtitle / description */
.swagger-ui .info p {
    text-align: center !important;
    font-size: 20px !important;
    color: #4b5563 !important;
    max-width: 1000px;
    margin: auto;
    margin-top: 5px;
}

/*background for website*/
/* Animated scientific background */

body {
    background:
        radial-gradient(circle at 20% 20%, rgba(53,13,246,0.08), transparent 25%),
        radial-gradient(circle at 80% 30%, rgba(16,18,129,0.2), transparent 25%),
        radial-gradient(circle at 50% 80%, rgba(53,13,246,0.08), transparent 25%),
        linear-gradient(135deg, #f8fafc, #eef2ff);

    background-size: cover;
    animation: backgroundMove 18s ease infinite;
}

/* subtle grid overlay */

body::before {
    content: "";
    position: fixed;
    inset: 0;

    background-image:
        linear-gradient(rgba(148,163,184,0.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148,163,184,0.08) 1px, transparent 1px);

    background-size: 40px 40px;

    pointer-events: none;
    z-index: -1;
}

/* floating blur circles */

body::after {
    content: "";
    position: fixed;
    width: 700px;
    height: 700px;
    top: -200px;
    right: -150px;

    background: radial-gradient(circle, rgba(59,130,246,0.12), transparent 70%);

    filter: blur(60px);

    animation: floatBlob 14s ease-in-out infinite alternate;

    z-index: -1;
}

/* animations */

@keyframes backgroundMove {
    0% {
        background-position: 0% 50%;
    }
    50% {
        background-position: 100% 50%;
    }
    100% {
        background-position: 0% 50%;
    }
}

@keyframes floatBlob {
    from {
        transform: translateY(0px) translateX(0px);
    }
    to {
        transform: translateY(60px) translateX(-40px);
    }
}

"""

    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="German Accident Data API Docs"
    )

    content = html.body.decode("utf-8")

    content = content.replace(
        "</head>",
        f"""
        <style>
        {custom_css}
        </style>
        </head>
        """
    )

    return HTMLResponse(content=content)

STATE_NAMES = {
    "01": "Schleswig-Holstein",
    "02": "Hamburg",
    "03": "Niedersachsen",
    "04": "Bremen",
    "05": "Nordrhein-Westfalen",
    "06": "Hessen",
    "07": "Rheinland-Pfalz",
    "08": "Baden-Württemberg",
    "09": "Bayern",
    "10": "Saarland",
    "11": "Berlin",
    "12": "Brandenburg",
    "13": "Mecklenburg-Vorpommern",
    "14": "Sachsen",
    "15": "Sachsen-Anhalt",
    "16": "Thüringen"
}

class RankingOrder(str, Enum):
    top = "top"
    bottom = "bottom"

class RegionLevel(str, Enum):
    state = "state"
    district = "district"
    municipality = "municipality"

class ParticipantType(str, Enum):
    pedestrian = "pedestrian"
    bicycle = "bicycle"
    motorcycle = "motorcycle"
    car = "car"

class AccidentCategory(int, Enum):
    fatal = 1
    serious_injury = 2
    minor_injury = 3

# =========================
# RESPONSE MODELS
# =========================

class LicenseMetadata(BaseModel):
    license_name: str
    license_code: str
    license_url: str

class RootInfo(BaseModel):
    name: str
    version: str
    status: str
    documentation: str

class SourceItem(BaseModel):
    source_id: int
    name: str
    source_type: Optional[str] = None
    url: Optional[str] = None
    license: Optional[str] = None

class ImportRunItem(BaseModel):
    run_id: int
    source_name: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    records_imported: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class RegionRate(BaseModel):
    ags: str
    region_name: str
    year: int
    accidents_per_10000_inhabitants: float

class AccidentRatesResponse(BaseModel):
    metadata: LicenseMetadata
    year: int
    results: List[RegionRate]

class CategoryFilters(BaseModel):
    year: Optional[int] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    accident_category: Optional[AccidentCategory] = None
    participant: Optional[ParticipantType] = None

class FilterByCategoryResponse(BaseModel):
    metadata: LicenseMetadata
    filters: CategoryFilters
    accident_count: int

class StateEarliestResponse(BaseModel):
    metadata: LicenseMetadata
    state_code: str
    state_name: str
    earliest_year: int

class EarliestYearResponse(BaseModel):
    metadata: LicenseMetadata
    earliest_year: Optional[int] = None

class FatalDistrictResult(BaseModel):
    rank: int
    district_code: str
    district_name: str
    total_accidents: int
    fatal_accidents: int
    accidents_per_10000_inhabitants: float

class FatalDistrictsResponse(BaseModel):
    metadata: LicenseMetadata
    question: str
    year: int
    datasets_combined: List[str]
    results: List[FatalDistrictResult]

class BicycleRiskResult(BaseModel):
    rank: int
    district_code: str
    district_name: str
    total_accidents: int
    bicycle_accidents: int
    bicycle_accident_share_percent: float
    accidents_per_10000_inhabitants: float

class BicycleRiskResponse(BaseModel):
    metadata: LicenseMetadata
    question: str
    year: int
    minimum_accidents: int
    datasets_combined: List[str]
    results: List[BicycleRiskResult]

# --- Counts & filters: by region level ---
class RegionCountResponse(BaseModel):
    metadata: LicenseMetadata
    level: RegionLevel
    code: str
    year: int
    accident_count: int

# --- Counts & filters: by time ---
class TimeFilters(BaseModel):
    year: Optional[int] = None
    month: Optional[int] = None
    weekday: Optional[int] = None
    hour: Optional[int] = None

class TimeFilterResponse(BaseModel):
    metadata: LicenseMetadata
    filters: TimeFilters
    accident_count: int

# --- Temporal: year-over-year ---
class TrendPoint(BaseModel):
    year: int
    accident_count: int
    change_from_previous_year: Optional[int] = None

class YearOverYearResponse(BaseModel):
    metadata: LicenseMetadata
    state_code: str
    state_name: str
    trend_summary: List[TrendPoint]

# --- Rates & rankings: top/bottom districts ---
class DistrictRankItem(BaseModel):
    district_code: str
    district_name: str
    year: int
    accident_count: int

class DistrictRankingsResponse(BaseModel):
    metadata: LicenseMetadata
    year: int
    ranking_type: RankingOrder
    results: List[DistrictRankItem]

# --- Rates & rankings: region comparison ---
class YearCount(BaseModel):
    year: int
    accident_count: int

class RegionComparison(BaseModel):
    region_code: str
    region_name: Optional[str] = None
    values: List[YearCount]

class CompareRegionsResponse(BaseModel):
    metadata: LicenseMetadata
    start_year: int
    end_year: int
    regions: List[RegionComparison]
# =========================
# ROOT
# =========================

@app.get(
    "/",response_model=RootInfo,
    tags=["🗂 Metadata"],
    summary="Service to retrieve API information",
    description="""
Provides basic information about the Accident Data API.

This endpoint acts as the entry point of the API and provides
links to available documentation.
"""
)
def root():
    return {
        "name": "DBW Accident Data API",
        "version": "1.0",
        "status": "running",
        "documentation": "/docs"
    }

# =========================
# SOURCES
# =========================

@app.get(
    "/metadata/sources",
    response_model=List[SourceItem],
    tags=["🗂 Metadata"],
    summary="Service to retrieve available data sources",
    description="""
Returns metadata information about all datasets used in the Accident Data API.

The response contains:
- Source identifier
- Dataset name
- Source type
- Original data URL
- License information

This endpoint helps users understand the origin and licensing
of the integrated datasets.
""",
    responses={
        200: {
            "description": "Successfully retrieved dataset source metadata"
        },
        500: {
            "description": "Database error while retrieving source information"
        }
    }
)
def sources(db: Session = Depends(get_db)):

        rows = db.execute(text("""
            SELECT
                source_id,
                name,
                source_type,
                url,
                license
            FROM sources
        """)).fetchall()

        return [
            {
                "source_id": r[0],
                "name": r[1],
                "source_type": r[2],
                "url": r[3],
                "license": r[4]
            }
            for r in rows
        ]

@app.get(
    "/import-runs",
    response_model=List[ImportRunItem],
    tags=["🗂 Metadata"],
    summary="Service to retrieve dataset import history",
    description="""
Returns the history of dataset import operations performed in the system.

Each import run contains:
- The imported dataset source
- Start and finish timestamps
- Number of imported records
- Import status
- Additional notes

The results are ordered by import run identifier.
""",
    responses={
        200: {
            "description": "Successfully retrieved import run history"
        },
        500: {
            "description": "Database error while retrieving import information"
        }
    }
)
def import_runs(db: Session = Depends(get_db)):

        result = db.execute(text("""
            SELECT
                ir.run_id,
                s.name,
                ir.started_at,
                ir.finished_at,
                ir.records_imported,
                ir.status,
                ir.notes
            FROM import_runs ir
            JOIN sources s ON ir.source_id = s.source_id
            ORDER BY ir.run_id
        """))

        rows = result.fetchall()

        return [
            {
                "run_id": row[0],
                "source_name": row[1],
                "started_at": row[2],
                "finished_at": row[3],
                "records_imported": row[4],
                "status": row[5],
                "notes": row[6]
            }
            for row in rows
        ]

   

# ---------------------------------------------------------------------------
#  Accident rates (accidents per 10 000 inhabitants) for one year
# ---------------------------------------------------------------------------

@app.get(
    "/statistics/rates/{year}",
    response_model=AccidentRatesResponse,
     tags=["🏆 Rates & Rankings"],
    summary="Service to retrieve regional accident rates for a specific year",
    description="""
Returns regional accident statistics for the selected year.

The endpoint provides accident rates normalized by population,
allowing comparison between different regions.

The response contains:
- AGS regional identifier
- Region name
- Analysed year
- Number of accidents per 10,000 inhabitants

The accident rate is calculated based on regional population data
and accident statistics for the requested year.
""",
    responses={
        200: {
            "description": "Successfully retrieved regional accident rates"
        },
        404: {
            "description": "No accident rate data available for the requested year"
        },
        500: {
            "description": "Database error while retrieving accident rates"
        }
    }
)
def accident_rates(year: int, limit: int = 10,db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT
            r.ags,
            r.name,
            iv.value AS rate_per_10000
        FROM indicator_values iv
        JOIN indicators i ON iv.indicator_id = i.indicator_id
        JOIN regions r ON iv.region_id = r.region_id
        WHERE i.code = 'ACCIDENTS_PER_10000_INHABITANTS'
        AND iv.year = :year
        ORDER BY iv.value DESC
        LIMIT :limit
    """), {
        "year": year,
        "limit": limit
    })

    rows = result.fetchall()
    
    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No accident-rate data available for {year}. "
                   f"Try a year present in the indicator dataset, such as 2023."
        )

    return {
    "metadata": LICENSE_METADATA,
    "year": year,
    "results": [
        {
            "ags": row[0],
            "region_name": row[1],
            "year": year,
            "accidents_per_10000_inhabitants": float(row[2])
        }
        for row in rows
    ]
}

# @app.get("/statistics/top-regions/{year}", tags=["🏆 Rates & Rankings"])
# def top_regions(year: int, limit: int = 10):

#     db = SessionLocal()

#     result = db.execute(text("""
#         SELECT
#             r.ags,
#             r.name,
#             COUNT(*) AS accident_count
#         FROM accidents a
#         JOIN regions r
#             ON a.region_id = r.region_id
#         WHERE a.year = :year
#         GROUP BY r.ags, r.name
#         ORDER BY accident_count DESC
#         LIMIT :limit
#     """), {
#         "year": year,
#         "limit": limit
#     })

#     rows = result.fetchall()

#     db.close()

#     return [
#         {
#             "ags": row[0],
#             "region_name": row[1],
#             "year": year,
#             "accident_count": row[2]
#         }
#         for row in rows
#     ]

@app.get("/statistics/district-rankings/{year}", summary="Service to display Top or bottom districts by accident count for a year",
    responses={404: {"description": "No district data for the requested year"},
               500: {"description": "Database error while ranking districts"}}, response_model=DistrictRankingsResponse,tags=["🏆 Rates & Rankings"])
def district_rankings(
    year: int,
    order: RankingOrder = RankingOrder.top,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    sort_order = "DESC" if order == RankingOrder.top else "ASC"   # enum-constrained, safe to interpolate

    rows = db.execute(text(f"""
        WITH district_counts AS (
            SELECT LEFT(r.ags, 5) AS district_code, COUNT(*) AS accident_count
            FROM accidents a
            JOIN regions r ON a.region_id = r.region_id
            WHERE a.year = :year AND LENGTH(r.ags) = 8
            GROUP BY LEFT(r.ags, 5)
        )
        SELECT dc.district_code, rd.name AS district_name, dc.accident_count
        FROM district_counts dc
        JOIN regions rd ON rd.ags = dc.district_code AND LENGTH(rd.ags) = 5
        ORDER BY dc.accident_count {sort_order}
        LIMIT :limit
    """), {"year": year, "limit": limit}).fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No district accident data available for {year}.")

    return {
        "metadata": LICENSE_METADATA,
        "year": year,
        "ranking_type": order,
        "results": [
            {"district_code": r[0], "district_name": r[1], "year": year, "accident_count": r[2]}
            for r in rows
        ],
    }

@app.get("/statistics/compare-regions", summary="Service to compare accident counts across regions over a year range",
    responses={500: {"description": "Database error while comparing regions"}},response_model=CompareRegionsResponse,tags=["🏆 Rates & Rankings"])
def compare_regions(
    region_codes: str = Query(..., description="Comma-separated AGS prefixes, e.g. 14,11,05"),
    start_year: int = Query(..., description="First year (inclusive)"),
    end_year: int = Query(..., description="Last year (inclusive)"),
    db: Session = Depends(get_db)
):
   

    codes = [c.strip() for c in region_codes.split(",") if c.strip()]
    regions = []
    for code in codes:
        rows = db.execute(text("""
            SELECT a.year, COUNT(*) AS accident_count
            FROM accidents a
            JOIN regions r ON a.region_id = r.region_id
            WHERE r.ags LIKE :region_prefix
              AND a.year BETWEEN :start_year AND :end_year
            GROUP BY a.year
            ORDER BY a.year
        """), {"region_prefix": code + "%", "start_year": start_year, "end_year": end_year}).fetchall()

        regions.append({
            "region_code": code,
            "region_name": STATE_NAMES.get(code),   # set for 2-digit state codes, null otherwise
            "values": [{"year": r[0], "accident_count": r[1]} for r in rows],
        })

    return {
        "metadata": LICENSE_METADATA,
        "start_year": start_year,
        "end_year": end_year,
        "regions": regions,
    }



@app.get("/accidents/filter-by-region", summary="Service to display accident count for region by level (state, district, municipality)",
    responses={500: {"description": "Database error while counting accidents"}},response_model=RegionCountResponse, tags=["📊 Counts and Filters"])
def accidents_by_region(
    level: RegionLevel,
    code: str = Query(
        ...,
        description="""
State examples:
01(Schleswig-Holstein)

District examples:
01002(Kiel)

Municipality examples:
01002000(Kiel municipality)
"""
    ),
    year: int = Query(
        2023,
        description="Accident year"
    ),
    db: Session = Depends(get_db),
):
   

    prefix_len = {RegionLevel.state: 2, RegionLevel.district: 5, RegionLevel.municipality: 8}[level]
    prefix = code[:prefix_len]

    count = db.execute(text("""
        SELECT COUNT(*)
        FROM accidents a
        JOIN regions r ON a.region_id = r.region_id
        WHERE r.ags LIKE :prefix
          AND a.year = :year
    """), {"prefix": prefix + "%", "year": year}).scalar()

    return {
        "metadata": LICENSE_METADATA,
        "level": level,
        "code": code,
        "year": year,
        "accident_count": count,
    }

@app.get("/accidents/filter-by-time",summary="Service to display accident count filtered by year, month, weekday and/or hour",
    responses={500: {"description": "Database error while processing request"}}, response_model=TimeFilterResponse,tags=["📊 Counts and Filters"])
def filter_accidents_by_time(
    year: int | None = Query(None, description="e.g. 2023"),
    month: int | None = Query(None, ge=1, le=12, description="Month 1-12"),
    weekday: int | None = Query(None, description="Weekday code as stored in your data"),
    hour: int | None = Query(None, ge=0, le=23, description="Hour 0-23"),
    db: Session = Depends(get_db),
):
    
    query = """SELECT COUNT(*) FROM accidents WHERE 1=1 """
    params = {}

    if year is not None:
        query += " AND year = :year"
        params["year"] = year

    if month is not None:
        query += " AND month = :month"
        params["month"] = month

    if weekday is not None:
        query += " AND weekday = :weekday"
        params["weekday"] = weekday

    if hour is not None:
        query += " AND hour = :hour"
        params["hour"] = hour

    result = db.execute(text(query), params)
    count = result.scalar()

    return {
        "metadata": LICENSE_METADATA,
        "filters": {"year": year, "month": month, "weekday": weekday, "hour": hour},
        "accident_count": count,
    }

@app.get(
    "/accidents/filter-by-category",
    response_model=FilterByCategoryResponse,
    tags=["📊 Counts and Filters"],
    summary="Service to retrieve accident count filtered by year, state, category, and participant type",
    description="""
Returns the total number of road accidents based on multiple optional filters.

This endpoint allows flexible filtering of accident data using:
- Year of occurrence
- German federal state (via AGS state code)
- Accident severity category
- Involvement of specific participant types (car, bicycle, pedestrian, motorcycle)

If no filters are provided, it returns the total accident count across all data.
""",
    responses={
        200: {
            "description": "Successfully retrieved accident count based on filters"
        },
        400: {
            "description": "Invalid filter values provided"
        },
        500: {
            "description": "Database error while processing request"
        }
    }
)
def filter_by_category(
    year: int | None = Query(None, description="Filter accidents by year (e.g., 2023, 2022)"),
    state_code: str | None = Query(None, description="AGS prefix: two digits for a state (14 = Saxony), or a longer prefix for a district/municipality"),
    accident_category: AccidentCategory | None = Query(None, description="1 = Fatal, 2 = Serious injury, 3 = Minor injury"),
    participant: ParticipantType | None = Query(None),
    db: Session = Depends(get_db),
):
   
    query = """
    SELECT COUNT(*)
    FROM accidents a
    JOIN regions r ON a.region_id = r.region_id
    WHERE 1=1
"""

    params = {}

    if year is not None:
        query += " AND a.year = :year"
        params["year"] = year

    if state_code is not None:
       query += " AND r.ags LIKE :state_prefix"
       params["state_prefix"] = state_code + "%"

    if accident_category is not None:
        query += " AND a.accident_category = :accident_category"
        params["accident_category"] = accident_category.value

    participant_columns = {
    ParticipantType.pedestrian: "pedestrian_involved",
    ParticipantType.bicycle: "bicycle_involved",
    ParticipantType.motorcycle: "motorcycle_involved",
    ParticipantType.car: "car_involved"
}

    if participant is not None:
     query += f" AND a.{participant_columns[participant]} = true"
    result = db.execute(text(query), params)

    count = result.scalar()

    return {
    "metadata": LICENSE_METADATA,
    "filters": {
        "year": year,
        "state_code": state_code,
        "state_name": STATE_NAMES.get(state_code, None) if state_code else None,
        "accident_category": accident_category,
        "participant": participant
    },
    "accident_count": count
}

 # =========================
 # Flexible count/filter endpoint
# =========================
# @app.get("/accidents/count", tags=["📊 Counts and Filters"])
# def accident_count(
#     year: int | None = None,
#     state_code: str | None = None,
#     month: int | None = None,
#     weekday: int | None = None,
#     hour: int | None = None,
#     accident_category: int | None = None,
#     pedestrian: bool | None = None,
#     bicycle: bool | None = None,
#     motorcycle: bool | None = None,
#     car: bool | None = None
# ):
#     db = SessionLocal()

#     query = """
#         SELECT COUNT(*)
#         FROM accidents a
#         JOIN regions r ON a.region_id = r.region_id
#         WHERE 1=1
#     """

#     params = {}

#     if year is not None:
#         query += " AND a.year = :year"
#         params["year"] = year

#     if state_code is not None:
#         query += " AND r.ags LIKE :state_prefix"
#         params["state_prefix"] = state_code + "%"

#     if month is not None:
#         query += " AND a.month = :month"
#         params["month"] = month

#     if weekday is not None:
#         query += " AND a.weekday = :weekday"
#         params["weekday"] = weekday

#     if hour is not None:
#         query += " AND a.hour = :hour"
#         params["hour"] = hour

#     if accident_category is not None:
#         query += " AND a.accident_category = :accident_category"
#         params["accident_category"] = accident_category

#     if pedestrian is not None:
#         query += " AND a.pedestrian_involved = :pedestrian"
#         params["pedestrian"] = pedestrian

#     if bicycle is not None:
#         query += " AND a.bicycle_involved = :bicycle"
#         params["bicycle"] = bicycle

#     if motorcycle is not None:
#         query += " AND a.motorcycle_involved = :motorcycle"
#         params["motorcycle"] = motorcycle

#     if car is not None:
#         query += " AND a.car_involved = :car"
#         params["car"] = car

#     result = db.execute(text(query), params)
#     count = result.scalar()

#     db.close()

#     return {
#         "filters": params,
#         "accident_count": count
#     }

# =================================
# EARLIEST YEAR PER FEDERAL STATE
# =================================

@app.get(
    "/statistics/state-earliest/{state_code}",
    response_model=StateEarliestResponse,
    tags=["⏳ Time Analytics"],
    summary="Service to get the earliest recorded accident year for a German federal state",
    description="""
Returns the earliest year in which accident data is available for a given German federal state.

This endpoint helps identify the historical coverage of accident records per region.

It uses AGS (Amtlicher Gemeindeschlüssel) state codes to filter data.

Example:
- 05 → Nordrhein-Westfalen
- 13 → Mecklenburg-Vorpommern
- 14 → Sachsen

If no data exists for the given state, the response will contain a null value.
""",
    responses={
        200: {
            "description": "Successfully retrieved earliest accident year for the state"
        },
        404: {
            "description": "State code not found or no accident data available"
        },
        500: {
            "description": "Database error while retrieving data"
        }
    }
)
def earliest_year_by_state(state_code: str,db: Session = Depends(get_db)):

    if state_code not in STATE_NAMES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown state code '{state_code}'. Valid codes are 01–16 "
                   f"(e.g. 05 = Nordrhein-Westfalen, 14 = Sachsen)."
        )

    result = db.execute(text("""
        SELECT MIN(a.year)
        FROM accidents a
        JOIN regions r
            ON a.region_id = r.region_id
        WHERE r.ags LIKE :state_prefix
    """), {
        "state_prefix": state_code + "%"
    })

    year = result.scalar()

    if year is None:
            raise HTTPException(
                status_code=404,
                detail=f"No accident data available for state {state_code} "
                    f"({STATE_NAMES[state_code]})."
            )

    
    return {
        "metadata": LICENSE_METADATA,
        "state_code": state_code,
        "state_name": STATE_NAMES[state_code],
        "earliest_year": year
    }

# =========================
# EARLIEST YEAR
# =========================

@app.get(
    "/statistics/earliest-year",
    response_model=EarliestYearResponse,
    tags=["⏳ Time Analytics"],
    summary="Service to get the earliest available accident year in the entire dataset",
    description="""
This endpoint helps understand the historical range of the dataset and determines from which year accident records are available across all regions in Germany.

It does not filter by region or category, it considers the complete dataset.

""",
    responses={
        200: {
            "description": "Successfully retrieved earliest available year in dataset"
        },
        500: {
            "description": "Database error while retrieving earliest year"
        }
    }
)
def earliest_year(db: Session = Depends(get_db)):


    result = db.execute(text("""SELECT MIN(year) FROM accidents"""))

    year = result.scalar()


    return {
        "metadata": LICENSE_METADATA,
        "earliest_year": year
    }

# =========================================
# YEAR-OVER-YEAR CHANGES OR TREND SUMMARIES
# =========================================

@app.get("/statistics/year-over-year/{state_code}",response_model=YearOverYearResponse, summary="Service to display Year-over-year accident trend for a federal state",
    responses={404: {"description": "Unknown state code or no data for the state"},
               500: {"description": "Database error while building the trend"}},tags=["⏳ Time Analytics"])
def year_over_year_changes(state_code: str,db: Session = Depends(get_db)):

    if state_code not in STATE_NAMES:
        raise HTTPException(status_code=404,
            detail=f"Unknown state code '{state_code}'. Valid codes are 01-16.")
    
    result = db.execute(text("""
        SELECT
            a.year,
            COUNT(*) AS accident_count
        FROM accidents a
        JOIN regions r
            ON a.region_id = r.region_id
        WHERE r.ags LIKE :state_prefix
        GROUP BY a.year
        ORDER BY a.year
    """), {
        "state_prefix": state_code + "%"
    })
    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404,
            detail=f"No accident data available for state {state_code} ({STATE_NAMES[state_code]}).")

    trend = []

    previous = None
    for row in rows:
        year, count = row[0], row[1]
        change = None if previous is None else count - previous
        trend.append({"year": year, "accident_count": count, "change_from_previous_year": change})
        previous = count

    return {
        "metadata": LICENSE_METADATA,
        "state_code": state_code,
        "state_name": STATE_NAMES[state_code],
        "trend_summary": trend,
    }
   
@app.get(
    "/statistics/integrated/fatal-districts/{year}",
    response_model=FatalDistrictsResponse,
    tags=["🔗 Cross-source Analytics"],
    summary="Service to retireve highest number of fatal accidents for a given year",
    description="""
Returns a ranked list of districts with the highest number of fatal accidents for a given year.
""",
    responses={
        200: {
            "description": "Successfully retrieved ranked fatal accident districts"
        },
        404: {
            "description": "No matching data found for the selected year or dataset mismatch"
        },
        500: {
            "description": "Database error during multi-source data aggregation"
        }
    }
)
def fatal_districts_with_rate(
    year: int,
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    
    
        result = db.execute(text("""
            WITH district_accidents AS (
                SELECT
                    LEFT(r_event.ags, 5) AS district_code,
                    COUNT(*) AS total_accidents,
                    COUNT(*) FILTER (
                        WHERE a.accident_category = 1
                    ) AS fatal_accidents
                FROM accidents a
                JOIN regions r_event
                    ON a.region_id = r_event.region_id
                WHERE a.year = :year
                  AND LENGTH(r_event.ags) = 8
                GROUP BY LEFT(r_event.ags, 5)
            )
            SELECT
                da.district_code,
                r_indicator.name AS district_name,
                da.total_accidents,
                da.fatal_accidents,
                iv.value AS accidents_per_10000_inhabitants
            FROM district_accidents da
            JOIN regions r_indicator
                ON r_indicator.ags = da.district_code
               AND LENGTH(r_indicator.ags) = 5
            JOIN indicator_values iv
                ON iv.region_id = r_indicator.region_id
               AND iv.year = :year
            JOIN indicators i
                ON i.indicator_id = iv.indicator_id
            WHERE i.code = 'ACCIDENTS_PER_10000_INHABITANTS'
              AND da.fatal_accidents > 0
            ORDER BY da.fatal_accidents DESC,
                     iv.value DESC
            LIMIT :limit
        """), {
            "year": year,
            "limit": limit
        })

        rows = result.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No matching integrated district data was found. "
                    "Use a year available in both accident events and "
                    "the regional indicator dataset, such as 2023."
                )
            )

        return {
            "metadata": LICENSE_METADATA,
            "question": (
                "Which districts recorded the highest number of fatal "
                "accidents, and what was their official accident rate?"
            ),
            "year": year,
            "datasets_combined": [
                "Unfallatlas accident event data",
                "Regional accident-rate indicator data",
                "AGS/GV-ISys regional reference"
            ],
            "results": [
                {
                    "rank": index,
                    "district_code": row[0],
                    "district_name": row[1],
                    "total_accidents": row[2],
                    "fatal_accidents": row[3],
                    "accidents_per_10000_inhabitants": float(row[4])
                }
                for index, row in enumerate(rows, start=1)
            ]
        }

    

@app.get(
    "/statistics/integrated/bicycle-risk-districts/{year}",
    response_model=BicycleRiskResponse,
    tags=["🔗 Cross-source Analytics"],
    summary="Service to retrieve districts with the highest bicycle accident share for a given year",
    description="""
Returns districts with the highest bicycle accident share for a given year, combined with official accident rate data.
""",
    responses={
        200: {
            "description": "Successfully retrieved bicycle risk ranking by district"
        },
        404: {
            "description": "No matching data found for the selected year or threshold"
        },
        500: {
            "description": "Database error during bicycle risk analysis"
        }
    }
)
def bicycle_risk_districts(
    year: int,
    limit: int = Query(10, ge=1, le=50),
    minimum_accidents: int = Query(
        100,
        ge=1,
        description=(
            "Minimum number of total accidents required to avoid rankings "
            "based on very small samples."
        )
    ),
    db: Session = Depends(get_db)
):
    

        result = db.execute(text("""
            WITH district_accidents AS (
                SELECT
                    LEFT(r_event.ags, 5) AS district_code,
                    COUNT(*) AS total_accidents,
                    COUNT(*) FILTER (
                        WHERE a.bicycle_involved = true
                    ) AS bicycle_accidents
                FROM accidents a
                JOIN regions r_event
                    ON a.region_id = r_event.region_id
                WHERE a.year = :year
                  AND LENGTH(r_event.ags) = 8
                GROUP BY LEFT(r_event.ags, 5)
            )
            SELECT
                da.district_code,
                r_indicator.name AS district_name,
                da.total_accidents,
                da.bicycle_accidents,
                ROUND(
                    (
                        100.0 * da.bicycle_accidents
                        / NULLIF(da.total_accidents, 0)
                    )::numeric,
                    2
                ) AS bicycle_share_percent,
                iv.value AS accidents_per_10000_inhabitants
            FROM district_accidents da
            JOIN regions r_indicator
                ON r_indicator.ags = da.district_code
               AND LENGTH(r_indicator.ags) = 5
            JOIN indicator_values iv
                ON iv.region_id = r_indicator.region_id
               AND iv.year = :year
            JOIN indicators i
                ON i.indicator_id = iv.indicator_id
            WHERE i.code = 'ACCIDENTS_PER_10000_INHABITANTS'
              AND da.total_accidents >= :minimum_accidents
              AND da.bicycle_accidents > 0
            ORDER BY bicycle_share_percent DESC,
                     iv.value DESC
            LIMIT :limit
        """), {
            "year": year,
            "minimum_accidents": minimum_accidents,
            "limit": limit
        })

        rows = result.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No matching integrated district data was found. "
                    "Try year 2023 or reduce minimum_accidents."
                )
            )

        return {
            "metadata": LICENSE_METADATA,
            "question": (
                    "Which districts had the highest bicycle accident share, "
                    "and what was their official accidents per 10,000 inhabitants indicator?"
                ),
            "year": year,
            "minimum_accidents": minimum_accidents,
            "datasets_combined": [
                "Unfallatlas accident event data",
                "Regional accident-rate indicator data",
                "AGS/GV-ISys regional reference"
            ],
            "results": [
                {
                    "rank": index,
                    "district_code": row[0],
                    "district_name": row[1],
                    "total_accidents": row[2],
                    "bicycle_accidents": row[3],
                    "bicycle_accident_share_percent": float(row[4]),
                    "accidents_per_10000_inhabitants": float(row[5])
                }
                for index, row in enumerate(rows, start=1)
            ]
        }
