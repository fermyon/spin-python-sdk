"""
A WASI interface dedicated to performing inferencing for Large Language Models.
"""
from typing import TypeVar, Generic, Union, Optional, Union, Protocol, Tuple, List, Any, Self
from enum import Flag, Enum, auto
from dataclasses import dataclass
from abc import abstractmethod
import weakref

from ..types import Result, Ok, Err, Some


@dataclass
class InferencingParams:
    """
    Inference request parameters
    """
    max_tokens: int
    repeat_penalty: float
    repeat_penalty_last_n_token_count: int
    temperature: float
    top_k: int
    top_p: float


@dataclass
class ErrorModelNotSupported:
    pass


@dataclass
class ErrorRuntimeError:
    value: str


@dataclass
class ErrorInvalidInput:
    value: str


# The set of errors which may be raised by functions in this interface
Error = Union[ErrorModelNotSupported, ErrorRuntimeError, ErrorInvalidInput]

@dataclass
class InferencingUsage:
    """
    Usage information related to the inferencing result
    """
    prompt_token_count: int
    generated_token_count: int

@dataclass
class InferencingResult:
    """
    An inferencing result
    """
    text: str
    usage: InferencingUsage

@dataclass
class EmbeddingsUsage:
    """
    Usage related to an embeddings generation request
    """
    prompt_token_count: int

@dataclass
class EmbeddingsResult:
    """
    Result of generating embeddings
    """
    embeddings: List[List[float]]
    usage: EmbeddingsUsage


def infer(model: str, prompt: str, params: Optional[InferencingParams]) -> InferencingResult:
    """
    Perform inferencing using the provided model and prompt with the given optional params
    """
    raise NotImplementedError

def generate_embeddings(model: str, text: List[str]) -> EmbeddingsResult:
    """
    Generate embeddings for the supplied list of text
    """
    raise NotImplementedError

