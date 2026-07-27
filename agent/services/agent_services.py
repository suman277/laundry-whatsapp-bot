from google.adk.sessions import InMemorySessionService
from google.adk import Runner
from agent.agent import root_agent

_session_service = None
_runner = None


def get_session_service():
    global _session_service

    if _session_service is None:
        _session_service = InMemorySessionService()

    return _session_service


def get_runner(app_name: str):
    global _runner

    if _runner is None:
        _runner = Runner(
            app_name=app_name,
            agent=root_agent,
            session_service=get_session_service(),
        )

    return _runner


async def ensure_session(app_name, session_id, user_id):
    session_service = get_session_service()
    session= await session_service.get_session(app_name=app_name, session_id=session_id, user_id=user_id)
    if session is None:
        session = await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id = session_id
        )
    return session