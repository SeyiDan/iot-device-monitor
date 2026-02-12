"""AI-powered natural language query endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.ai.llm_service import LLMQueryService, get_llm_service
from app.database import get_db


router = APIRouter()


class NaturalLanguageQuery(BaseModel):
    """Natural language query request."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language query about device data",
        examples=["Show all devices with high temperature"],
    )


class QueryResponse(BaseModel):
    """Query response with results and explanation."""

    query: str
    sql: str
    result_count: int
    results: list[dict]
    explanation: str


@router.post("/query", response_model=QueryResponse, status_code=200)
async def natural_language_query(
    request: NaturalLanguageQuery,
    db: AsyncSession = Depends(get_db),
    llm_service: LLMQueryService = Depends(get_llm_service),
):
    """
    Query device data using natural language.

    This endpoint converts natural language queries to SQL,
    executes them safely, and returns results with explanations.

    Example queries:
    - "Show all devices"
    - "Devices with temperature above 80 degrees"
    - "What's the average battery level per location?"
    - "Show critical readings from today"
    - "Which device has the highest temperature?"
    """
    try:
        result = await llm_service.process_query(request.query, db)
        return QueryResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Query processing failed: {str(e)}"
        )


@router.get("/examples", response_model=dict)
async def get_query_examples():
    """
    Get example natural language queries.

    Returns common query examples that users can try.
    """
    return {
        "examples": [
            {
                "category": "Device Queries",
                "queries": [
                    "Show all devices",
                    "List active devices",
                    "Show devices in Server Room",
                ],
            },
            {
                "category": "Temperature Queries",
                "queries": [
                    "Devices with temperature above 80",
                    "Show critical temperature readings",
                    "What's the highest temperature recorded?",
                ],
            },
            {
                "category": "Battery Queries",
                "queries": [
                    "Show devices with low battery",
                    "What's the average battery level?",
                    "Devices with battery below 20%",
                ],
            },
            {
                "category": "Aggregation Queries",
                "queries": [
                    "Average temperature per device",
                    "Count devices by location",
                    "Show humidity statistics",
                ],
            },
            {
                "category": "Time-Based Queries",
                "queries": [
                    "Show readings from today",
                    "Recent high temperature alerts",
                    "Latest reading for each device",
                ],
            },
        ]
    }
