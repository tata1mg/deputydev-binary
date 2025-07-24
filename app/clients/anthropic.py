import anthropic

class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def count_tokens(self, model: str, messages: str):
        """
        model: str - Model to use
        messages: str - Messages to count tokens for
        Count the number of tokens in the given messages
        """
        response = self.client.messages.count_tokens(
            model=model,
            system="Sample system",
            messages=[{
                "role": "user",
                "content": messages
            }],
        )
        return response
