from typing import Optional

sessions = {}


def save_session(
    contact_no: str,
    flow: Optional[str] = None,
    step: Optional[str] = None,
    **kwargs,
):
    if contact_no not in sessions:
        sessions[contact_no] = {
            "flow": None,
            "step": None,
            "data": {}
        }
    session = sessions[contact_no]
    if flow is not None:
        session["flow"] = flow
    if step is not None:
        session["step"] = step
    if kwargs:
        session["data"].update(kwargs)
    return session


def get_session(contact_no: str):
    return sessions.get(contact_no)


def has_session(contact_no: str) -> bool:
    return contact_no in sessions


def delete_session(contact_no: str):
    sessions.pop(contact_no, None)


def clear_session_data(contact_no: str):
    session = sessions.get(contact_no)
    if session:
        session["data"] = {}


def update_step(contact_no: str, step: str):
    if contact_no in sessions:
        sessions[contact_no]["step"] = step


def update_flow(contact_no: str, flow: str):
    if contact_no in sessions:
        sessions[contact_no]["flow"] = flow


def get_step(contact_no: str):
    session = sessions.get(contact_no)
    if session:
        return session["step"]
    return None


def get_flow(contact_no: str):
    session = sessions.get(contact_no)
    if session:
        return session["flow"]
    return None


def get_data(contact_no: str):
    session = sessions.get(contact_no)
    if session:
        return session["data"]
    return None


def print_sessions():
    from pprint import pprint
    pprint(sessions)
