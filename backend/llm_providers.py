import subprocess

class OllamaLLM:
    def __init__(self, model="mistral"):
        self.model = model

    def stream(self, messages, temperature=0.7):
        # Extract the latest user message
        user_message = messages[-1]["content"]

        # Run Ollama command
        process = subprocess.Popen(
            ["ollama", "run", self.model],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send the prompt to Ollama
        process.stdin.write(user_message)
        process.stdin.close()

        # Stream output line by line
        for line in process.stdout:
            yield line.strip()


def load_llm():
    """
    Returns an instance of the LLM (Ollama with the mistral model by default).
    """
    return OllamaLLM("mistral")
