from google.genai import types
from agent.services.agent_services import ensure_session, get_runner, get_session_service


async def get_response_from_llm(query, id, _session_id):
    print(f"\n>>> User Query: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    _runner = get_runner("MY APP")
    await ensure_session(
        app_name="MY APP", session_id=_session_id, user_id=id)
    final_response_text = "Agent did not produce a final response."  # Default
    if query is not None:
        async for event in _runner.run_async(user_id=id, session_id=_session_id, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    # Assuming text response in the first part
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks here if needed (e.g., specific error codes)
                # break  # Stop processing events once the final response is found

    # print(f"<<< Agent Response: {final_response_text}")
    return final_response_text
