"""Module for working with the Spin large language model API"""

from dataclasses import dataclass
from typing import Optional, Sequence
from spin_sdk.wit.imports import llm as spin_llm

@dataclass
class InferencingParams:
    max_tokens: int = 100
    repeat_penalty: float = 1.1
    repeat_penalty_last_n_token_count: int = 64
    temperature: float = 0.8
    top_k: int = 40
    top_p: float = 0.9
    

def generate_embeddings(model: str, text: Sequence[str]) -> spin_llm.EmbeddingsResult:
    """
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_ModelNotSupported)` will be raised if the component does not have access to the specified model.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_RuntimeError(str))` will be raised if there are any runtime errors.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_InvalidInput(str))` will be raised if an invalid input is provided.
    """
    return spin_llm.generate_embeddings(model, text)

def infer_with_options(model: str, prompt: str, options: Optional[InferencingParams]) -> spin_llm.InferencingResult:
    """
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_ModelNotSupported)` will be raised if the component does not have access to the specified model.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_RuntimeError(str))` will be raised if there are any runtime errors.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_InvalidInput(str))` will be raised if an invalid input is provided.
    """
    options = options or InferencingParams
    return spin_llm.infer(model, prompt, options)

def infer(model: str, prompt: str) -> spin_llm.InferencingResult:
    """
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_ModelNotSupported)` will be raised if the component does not have access to the specified model.
    
    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_RuntimeError(str))` will be raised if there are any runtime errors.

    A `spin_sdk.wit.types.Err(spin_sdk.wit.imports.llm.Error_InvalidInput(str))` will be raised if an invalid input is provided.
    """
    options = InferencingParams
    return spin_llm.infer(model, prompt, options)

