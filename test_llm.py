from app.generation.llm import generate_answer


question = "What is the capital of Nigeria?"

context = "The capital of France is Paris."


answer = generate_answer(
    question,
    context,
)


print("Answer:")
print(answer)