"""LLM service for natural language query processing."""
import re
from typing import Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.prompts import (
    DATABASE_SCHEMA,
    SQL_GENERATION_SYSTEM_PROMPT,
    RESPONSE_FORMATTING_PROMPT,
    SQL_VALIDATION_PROMPT,
)
from app.core.config import settings


class LLMQueryService:
    """Service for processing natural language queries using LLM."""

    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
        )
        self.schema = DATABASE_SCHEMA

    async def process_query(
        self, user_query: str, db: AsyncSession
    ) -> dict[str, Any]:
        """
        Process natural language query and return results.

        Args:
            user_query: Natural language query from user
            db: Database session

        Returns:
            Dictionary containing query, SQL, results, and explanation

        Raises:
            ValueError: If query is unsafe or invalid
        """
        # Generate SQL from natural language
        sql_query = await self._generate_sql(user_query)

        # Validate SQL for safety
        await self._validate_sql(sql_query)

        # Execute SQL query
        results = await self._execute_query(sql_query, db)

        # Generate natural language response
        explanation = await self._format_response(user_query, results)

        return {
            "query": user_query,
            "sql": sql_query,
            "result_count": len(results),
            "results": results,
            "explanation": explanation,
        }

    async def _generate_sql(self, query: str) -> str:
        """
        Convert natural language to SQL query.

        Args:
            query: Natural language query

        Returns:
            SQL query string
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SQL_GENERATION_SYSTEM_PROMPT.format(schema=self.schema)),
                ("user", "{query}"),
            ]
        )

        chain = prompt | self.llm
        response = await chain.ainvoke({"query": query})

        # Extract SQL from response
        sql = response.content.strip()

        # Remove markdown code blocks if present
        sql = re.sub(r"```sql\n?", "", sql)
        sql = re.sub(r"```\n?", "", sql)

        return sql.strip()

    async def _validate_sql(self, sql: str) -> None:
        """
        Validate SQL query for safety.

        Args:
            sql: SQL query to validate

        Raises:
            ValueError: If SQL is unsafe
        """
        # Basic validation
        sql_lower = sql.lower()

        # Check for dangerous operations
        dangerous_keywords = [
            "drop",
            "delete",
            "update",
            "insert",
            "alter",
            "create",
            "truncate",
            "grant",
            "revoke",
        ]

        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                raise ValueError(
                    f"Unsafe SQL operation detected: {keyword.upper()} not allowed"
                )

        # Ensure it's a SELECT query
        if not sql_lower.strip().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        # Use LLM for additional validation
        prompt = ChatPromptTemplate.from_template(SQL_VALIDATION_PROMPT)
        chain = prompt | self.llm
        response = await chain.ainvoke({"sql": sql})

        validation_result = response.content.strip()
        if not validation_result.startswith("SAFE"):
            raise ValueError(f"SQL validation failed: {validation_result}")

    async def _execute_query(
        self, sql: str, db: AsyncSession
    ) -> list[dict[str, Any]]:
        """
        Execute SQL query and return results.

        Args:
            sql: SQL query to execute
            db: Database session

        Returns:
            List of result dictionaries
        """
        try:
            result = await db.execute(text(sql))
            rows = result.fetchall()

            # Convert rows to dictionaries
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            return []

        except Exception as e:
            raise ValueError(f"Query execution failed: {str(e)}")

    async def _format_response(
        self, query: str, results: list[dict[str, Any]]
    ) -> str:
        """
        Format query results as natural language response.

        Args:
            query: Original user query
            results: Query results

        Returns:
            Natural language explanation
        """
        # Limit results in prompt to prevent token overflow
        results_preview = results[:5] if len(results) > 5 else results

        prompt = ChatPromptTemplate.from_template(RESPONSE_FORMATTING_PROMPT)
        chain = prompt | self.llm

        response = await chain.ainvoke(
            {"query": query, "results": str(results_preview)}
        )

        explanation = response.content.strip()

        # Add result count info if truncated
        if len(results) > 5:
            explanation += f"\n\nNote: Showing summary of {len(results)} total results."

        return explanation


async def get_llm_service() -> LLMQueryService:
    """Dependency for LLM service."""
    return LLMQueryService()
