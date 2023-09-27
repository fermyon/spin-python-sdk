import json
from spin_http import Response
from spin_llm import llm_infer, generate_embeddings


def handle_request(request):
    prompt="You are a stand up comedy writer. Tell me a joke."
    result=llm_infer("llama2-chat", prompt)
    
    embeddings = generate_embeddings("all-minilm-l6-v2", ["hat", "cat", "bat"])
    
    body = (f"joke: {result.text}\n\n"
            f"embeddings: {json.dumps(embeddings.embeddings)}\n"
            f"prompt token count: {embeddings.usage.prompt_token_count}")
    
    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(body, "utf-8"))
