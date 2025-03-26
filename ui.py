import streamlit as st
from main import TravelPlannerOrchestrator


def main():
    st.title("AI Travel Planner")
    planner = TravelPlannerOrchestrator()
    user_input = st.text_area("Describe your travel plans:")

    if st.button("Generate Travel Plan"):
        if user_input:
            with st.spinner("Crafting your personalized travel experience..."):
                try:
                    result = planner.plan_trip(user_input)

                    if result["status"] == "success":
                        st.subheader("Detailed Itinerary")
                        st.markdown(result["itinerary"])

                        st.subheader("Trip Highlights")
                        if "activity_suggestions" in result:
                            suggestions = result["activity_suggestions"]

                            st.markdown("#### Top Attractions")
                            for attraction in suggestions.get("top_attractions", []):
                                st.markdown(f"- {attraction}")

                            st.markdown("#### Hidden Gems")
                            for gem in suggestions.get("hidden_gems", []):
                                st.markdown(f"- {gem}")

                            st.markdown("#### Budget-Friendly Options")
                            for option in suggestions.get(
                                "budget_friendly_options", []
                            ):
                                st.markdown(f"- {option}")

                        with st.expander("Trip Details"):
                            st.json(result["refined_context"])

                    elif result["status"] == "needs_clarification":
                        st.warning("We need more information:")
                        for question in result["missing_info"]:
                            st.write(f"- {question}")

                    elif result["status"] == "error":
                        st.error(f"An error occurred: {result['message']}")

                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please enter your travel details")


if __name__ == "__main__":
    main()
