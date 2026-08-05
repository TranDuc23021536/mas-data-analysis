from app.core.workflow import workflow

result = workflow.invoke({
    "question": "Doanh thu theo từng danh mục sản phẩm là bao nhiêu?",
    "chat_history": [],
    "retry_count": 0,
})

print("Final answer:", result["final_answer"])
print("Retry count:", result["retry_count"])
print("Is valid:", result["is_valid"])