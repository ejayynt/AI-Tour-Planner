import os
import json
from typing import Dict, Any, List
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "HKJsGPwbtKiYM1jvKybKKyueMeH975Uu")
TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY", "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"
)


class ActivitySuggestions(BaseModel):
    top_attractions: List[str] = Field(description="Must-visit locations")
    hidden_gems: List[str] = Field(description="Lesser-known unique experiences")
    budget_friendly_options: List[str] = Field(description="Low-cost activities")


class InputRefinementAgent:
    def __init__(self, llm):
        self.llm = llm

    def refine_input(self, user_input: str) -> Dict[str, Any]:
        refinement_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Analyze the travel input and extract comprehensive details:
        
        Core Travel Details:
        - destination: Exact city/region (REQUIRED)
        - trip_duration: Precise number of days (REQUIRED)
        - budget_range: Specific budget category (REQUIRED)
        - departure_city: Starting location

        Detailed Preferences:
        - specific_interests: Traveler's key interests
        - additional_notes: Any special requirements or preferences

        Ensure you extract these details directly from the user's input. If any information is missing, return the most probable interpretation.
        """,
                ),
                ("human", "{user_input}"),
                (
                    "system",
                    """Please return a JSON-formatted response with the following keys:
        - destination
        - trip_duration
        - budget_range
        - departure_city
        - specific_interests
        """,
                ),
            ]
        )

        try:

            class TravelDetails(BaseModel):
                destination: str
                trip_duration: int
                budget_range: str
                departure_city: str
                specific_interests: List[str]

            parser = PydanticOutputParser(pydantic_object=TravelDetails)

            chain = refinement_prompt | self.llm | parser

            parsed_result = chain.invoke({"user_input": user_input})

            return parsed_result.model_dump()

        except Exception as e:
            raise ValueError(f"Could not parse travel details: {str(e)}")


class ActivitySuggestionAgent:
    def __init__(self, llm, tavily_client):
        self.llm = llm
        self.tavily = tavily_client

    def generate_suggestions(self, refined_context: Dict[str, Any]) -> Dict[str, Any]:
        search_query = f"Top {' and '.join(refined_context.get('specific_interests', ['tourist']))} attractions in {refined_context.get('destination', 'destination')}"
        search_results = self.tavily.search(query=search_query, max_results=7)
        parser = PydanticOutputParser(pydantic_object=ActivitySuggestions)
        suggestions_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Based on the web search results, create a comprehensive activity suggestion list:

            Provide suggestions for:
            - Top attractions 
            - Hidden gems
            - Budget-friendly options

            Format:
            {format_instructions}
            """,
                ),
                ("human", "Search Results: {search_results}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        chain = suggestions_prompt | self.llm | parser

        suggestions = chain.invoke({"search_results": search_results["results"]})

        return {
            "top_attractions": suggestions.top_attractions,
            "hidden_gems": suggestions.hidden_gems,
            "budget_friendly_options": suggestions.budget_friendly_options,
        }


class ItineraryGenerationAgent:
    def __init__(self, llm):
        self.llm = llm

    def create_itinerary(
        self, refined_context: Dict[str, Any], activity_suggestions: Dict[str, Any]
    ) -> str:
        itinerary_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Create a comprehensive {duration}-day travel itinerary for {destination}.

            Detailed Guidelines:
            - Departure City: {departure_city}
            - Traveler Interests: {interests}
            - Budget Range: {budget}

            Itinerary Format:
            ## Day-by-Day Breakdown
            Each day should include:
            - Morning activities
            - Lunch recommendations
            - Afternoon explorations
            - Evening entertainment/dining
            - Transportation details
            """,
                ),
                ("human", "Generate detailed itinerary"),
            ]
        )

        chain = itinerary_prompt | self.llm
        return chain.invoke(
            {
                "duration": refined_context.get("trip_duration", "5"),
                "destination": refined_context.get("destination", "Dubai"),
                "departure_city": refined_context.get("departure_city", "New Delhi"),
                "interests": ", ".join(
                    refined_context.get("specific_interests", ["leisure"])
                ),
                "budget": refined_context.get("budget_range", "moderate"),
            }
        ).content


class TravelPlannerOrchestrator:
    def __init__(self):
        self.llm = ChatMistralAI(
            model="mistral-large-latest", api_key=MISTRAL_API_KEY, temperature=0.3
        )
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY)

        self.input_refinement_agent = InputRefinementAgent(self.llm)
        self.activity_suggestion_agent = ActivitySuggestionAgent(self.llm, self.tavily)
        self.itinerary_generation_agent = ItineraryGenerationAgent(self.llm)

    def plan_trip(self, user_input: str) -> Dict[str, Any]:
        refined_context = self.input_refinement_agent.refine_input(user_input)

        activity_suggestions = self.activity_suggestion_agent.generate_suggestions(
            refined_context
        )

        itinerary = self.itinerary_generation_agent.create_itinerary(
            refined_context, activity_suggestions
        )

        return {
            "status": "success",
            "refined_context": refined_context,
            "activity_suggestions": activity_suggestions,
            "itinerary": itinerary,
        }


if __name__ == "__main__":
    planner = TravelPlannerOrchestrator()
    result = planner.plan_trip()
    print(result)
