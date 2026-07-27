from google.adk.models.lite_llm import LiteLlm
from my_agent.config import IS_LITELLM, LLM_MODEL_API_KEY, LLM_MODEL_NAME
def get_llm_model():
    """Build the model based on IS_LITELLM configuration."""
    print(IS_LITELLM)
    if IS_LITELLM:
        print("inside litellm")

        return LiteLlm(model=LLM_MODEL_NAME, api_key=LLM_MODEL_API_KEY)
    else:
        return LLM_MODEL_NAME