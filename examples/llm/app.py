from spin_http import Response
from spin_llm import llm_infer


def handle_request(request):
    prompt="You are a stand up comedy writer. Tell me a joke."
    result=llm_infer("llama2-chat", prompt)
    return Response(200,
                    {"content-type": "text/plain"},
                    bytes(result.text, "utf-8"))
