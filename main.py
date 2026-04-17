from defense.pipeline import DefensePipeline


# Example usage:
pipeline = DefensePipeline()
result = pipeline.process("I like cheese. Yes.", user_id="user")
print(result)