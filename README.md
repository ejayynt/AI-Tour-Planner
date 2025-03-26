# AI-Tour-Planner
This project is an AI travel planning assistant that generates personalized travel itineraries based on user preferences. It refines input, fetches real-time activity suggestions, and structures a day-by-day itinerary using AI models and web searches.
Built with Python, Streamlit, and LangChain, it leverages Mistral AI for smart recommendations and Tavily API for up-to-date travel insights.

This project is also hosted on Streamlit cloud: [Link](https://ai-tour-planner.streamlit.app/)

## Input Prompt
As of now, the input prompt from the user must have these details specified:
1. Destination City
2. Source City
3. Budget (Budget/Moderate/Luxury)
4. Days of visit
5. Personal interests

Since this is a very basic implementation, the system fails to produce accurate results without these.

## Agents
Three AI agents are working together in this system to produce reliable results.
### Input Refinement Agent
This agent ensures that essential travel details like destination, budget, duration, etc., are present and properly structured. It refines the user input so that it can be worked on better. This agent is mainly responsible for personalized user input, which will make the system perform better for each user. 
### Activity Suggestion Agent
This agent helps find relevant details based on user input. It uses Tavily for real-time web scraping to find relevant details and recommendations. The prompt has been designed to ensure the results are clear and consistent. It finds details like top attractions, hidden gems, etc, in that destination.
### Itinerary Generation Agent
This final agent converts refined user inputs and activity suggestions into a structured travel itinerary. It converts the search results into proper meaningful format that the users can read. It also structures the data daily and shows the users places like top attractions and hidden gems so that the users can also take a look at them.


## API Keys
This project uses API keys from:
* [Mistral AI](https://mistral.ai/): LLM for the agents
* [Tavily](https://tavily.com/): For real-time web searching

## Future Improvements
* Be able to respond to vague or incomplete user inputs.
* Must provide more robust options like seasonal activities, etc.
* A better UI

