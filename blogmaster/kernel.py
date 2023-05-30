from dotenv import load_dotenv
import yaml
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai.services.azure_chat_completion import AzureChatCompletion
from typing import Callable, Tuple
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("blogmaster")

logger_blocklist = [
    "azure.core.pipeline.policies.http_logging_policy",
]

def add_completion_service(kernel: sk.Kernel, service_id: str, engine: str, key: str, endpoint: str) -> sk.Kernel:
    logger.info(f"Adding completion service {service_id} with engine {engine} and key {key}")
    kernel = kernel.add_text_completion_service(service_id, AzureChatCompletion(deployment_name=engine, api_key=key, endpoint=endpoint), overwrite=False)
    return kernel

def get_openai_config(config_name: str) -> Tuple[str, str]:
    logger.info(f"Getting OpenAI config for {config_name}")
    # Get the API key and endpoint from the environment variables
    openai_key = os.getenv(f"{config_name}_API_KEY")
    openai_endpoint = os.getenv(f"{config_name}_ENDPOINT")
    return openai_key, openai_endpoint

def register_skeleton_function(kernel: sk.Kernel) -> Callable:
    logger.info("Registering skeleton function")
    return kernel.import_semantic_skill_from_directory("blogmaster_skills", "BloggingSkill")["CreateSkeleton"]

def register_generate_function(kernel: sk.Kernel) -> Callable:
    logger.info("Registering post function")
    return kernel.import_semantic_skill_from_directory("blogmaster_skills", "BloggingSkill")["ExpandOutline"]

def register_review_function(kernel: sk.Kernel) -> Callable:
    logger.info("Registering review function")
    return kernel.import_semantic_skill_from_directory("blogmaster_skills", "BloggingSkill")["ReviewGrammar"]

def register_title_function(kernel: sk.Kernel) -> Callable:
    logger.info("Registering title function")
    return kernel.import_semantic_skill_from_directory("blogmaster_skills", "BloggingSkill")["MakeTitle"]

def initialize_kernel() -> sk.Kernel:

    logger.info("Initializing kernel")
    kernel = sk.Kernel()

    # Initialize SK
    key_ms, env_ms = get_openai_config("OPENAI_USEAST2")
    key_eu, env_eu = get_openai_config("OPENAI_EUROPE")

    kernel = add_completion_service(kernel, service_id="gpt3", engine="gpt-35-turbo", key=key_eu, endpoint=env_eu)
    kernel = add_completion_service(kernel, service_id="gpt4", engine="gpt-4", key=key_ms, endpoint=env_ms)

    kernel.set_default_text_completion_service("gpt4")
    logger.info("Initializing skeleton function")
    kernel.generate_skeleton = register_skeleton_function(kernel)

    kernel.set_default_text_completion_service("gpt4")
    logger.info("Initializing post function")
    kernel.generate_post = register_generate_function(kernel)

    kernel.set_default_text_completion_service("gpt4")
    logger.info("Initializing review function")
    kernel.review_post = register_review_function(kernel)

    kernel.set_default_text_completion_service("gpt3")
    logger.info("Initializing title function")
    kernel.title_post = register_title_function(kernel)

    return kernel


