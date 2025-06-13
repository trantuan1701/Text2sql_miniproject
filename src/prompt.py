from langchain.prompts import PromptTemplate

sql_prompt = PromptTemplate(
    input_variables=["plan", "question"],
    template="""
Nhiệm vụ của bạn là sinh ra câu SQL truy vấn để trả lời câu hỏi của khách hàng và kế hoạch được cung cấp
Câu hỏi của khách hàng là {question}
Những trường dữ liệu và hướng dẫn sinh SQL : {plan}
Lưu ý: Ưu tiên ngắn gọn, **Tuyệt đối** tuân thủ hướng dẫn trên, không làm phép tính nếu hướng dẫn không yêu cầu( trường đề xuất trong hướng dẫn là đủ)
Chỉ trả về câu lệnh SQL hoàn chỉnh, không kèm lời giải thích.
"""
)


sql_prompt_no_planner = PromptTemplate(
    input_variables=["question", "m_schema", "service"],
    template="""
You are a SQL expert.
Given the table schema (M-Schema):
{m_schema}

Note:
- PARTITION_DATE is stored as an INT in YYYYMMDD format (e.g., 20240630).
- For QUARTER_VALUE (cumulative quarterly revenue), the record date is always the **last day of the quarter**. 
  So for Q2 2024, PARTITION_DATE = 20240630.
- Therefore, filter by `PARTITION_DATE = 20240630`, do not use date functions.

- SPY_DELTA: absolute growth of YEAR_VALUE compared to previous year.
- SPY_PERCENT: percentage growth of YEAR_VALUE compared to previous year.
If the question asks “tăng trưởng bao nhiêu” (absolute growth), use SPY_DELTA.
If it asks “tăng trưởng bao nhiêu phần trăm” (percent growth), use SPY_PERCENT.
The user asked: "{question}"

The target primary key in this table is: {service_pk}.

Translate the question into a SQL query on table CHATBOT_KTDL_TARGETS_REVENUE,
filtering by SERVICE_PK = '{service_pk}',
and selecting the columns needed to answer the question. 
Answer with the complete SQL only.
"""
)


planner_prompt = PromptTemplate(
    input_variables=["question", "m_schema", "service_pk", "comparison"],
    template="""
Bạn là **Planner_Agent** trong hệ Text-to-SQL đa tác nhân.
Nhiệm vụ: 
*) Từ mô tả cơ sở dữ liệu chọn những cột phù hợp nhất để trả lời câu hỏi của người dùng.
*) Cung cấp ngữ cảnh đầy đủ về cơ sở dữ liệu và liên hệ với câu hỏi của người dùng
*) Mục tiêu: Ưu tiên dùng những trường có sẵn có, cung cấp đầy đủ thông tin ngữ cảnh
Bạn được cung cấp:
*) Mô tả cơ sở dữ liệu: {m_schema}
*) Câu hỏi của người dùng: {question}
*) Mã chỉ tiêu người dùng quan tâm được xác định: {service_pk}
*) Mối quan hệ giữa 2 khoảng thời gian mà người dùng yêu cầu: {comparison}

Lưu ý về dữ liệu 
*) Doanh thu lũy kế giữa 2 giai đoạn luôn có thể được tính bằng SUM(DAY_VALUE)
*) Chắc chắn có bản ghi tại tất cả các ngày, không cần phải thử.
*) Nếu người dùng hỏi về một khoảng thời gian tháng/quý/năm nhưng không cung cấp ngày cụ thể. Hãy lấy ngày cuối cùng của khoảng thời gian đó chính là Doanh thu trong toàn bộ thời gian đó
*) Nếu người dùng yêu cầu tính chênh lệch, tăng trưởng giữa 2 tháng/quý/ngày liên tiếp, tháng/quý này năm nay so với năm trước, **ưu tiên dùng các cột đã có sẳn trong bảng**, hạn chế tính thủ công
*) Nếu người dùng hỏi về dữ liệu của 2 ngày lấy dữ liệu khác nhau, lưu ý mối quan hệ của hai ngày đó(ví dụ: cách 1 năm/quý/tháng,...)
*) Ưu tiên viết SQL đơn giản, tối ưu

Đầu ra bắt buộc:

Tên bảng: CHATBOT_KTDL_TARGETS_REVENUE
Các cột liên quan: - Tên cột - kiểu dữ liệu- mô tả- ví dụ, ...
Lưu ý dựa theo ngữ cảnh, ghi rõ phép tính nếu cần tính. 
Hướng dẫn chi tiết tạo truy vấn SQL.

""")

intent_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
Bạn là bộ phân loại mục đích câu hỏi, chỉ có 2 nhãn: 
- “business”: các câu hỏi liên quan đến định nghĩa, tên gọi, mô tả quy trình/nghiệp vụ, cách tính chỉ tiêu (định tính), về nghiệp vụ.  
- “sql”: các câu hỏi muốn truy xuất số liệu, yêu cầu tính tổng/đếm/trung bình/nhóm/lọc trên dữ liệu (định lượng).
    
Bạn cần xác định mục đích của câu hỏi:
- Hỏi về *mã chỉ tiêu* của doanh thu -> trả lời: "business"
- Nếu người dùng muốn tìm hiểu định nghĩa, tên gọi, hoặc mô tả của một mã chỉ tiêu, câu hỏi định tính -> trả lời: "business"
- Nếu người dùng muốn truy xuất dữ liệu, hỏi về số liệu, số lượng, tổng, trung bình, hỏi về doanh thu trong một khoảng thời gian, câu hỏi định lượng -> trả lời: "sql"
Câu sau đây là từ người dùng: "{question}"

Chỉ trả lời đúng 1 từ: "business" hoặc "sql".
"""
)


pk_prompt = PromptTemplate(
    input_variables=["mapping", "question"],
    template="""
Dưới đây là danh sách mã chỉ tiêu và mô tả:
{mapping}

Hỏi: {question}

Hãy xác định các thông tin sau dựa vào câu hỏi. Nếu không chắc chắn, hoặc không đề cập tới, để null.

Lưu ý: Nếu người dùng đề cập đến cụm như "chênh lệch lũy kế năm", "tăng trưởng lũy kế năm", hoặc "so với cùng kỳ năm ngoái" mà không nêu rõ ngày cụ thể, thì nên mặc định chọn "comparison": "cùng kỳ năm trước", ngay cả khi không có từ "cùng kỳ" rõ ràng.

Kết quả trả về dạng JSON:
```json
{{
  "service_pk": "<mã chỉ tiêu phù hợp>",
  "difference_type": "<DELTA|PERCENT|null>",
  "date1": "<ngày gần hiện tại cần so sánh - định dạng YYYY-MM-DD|null>",
  "date2": "<ngày quá khứ cần so sánh - định dạng YYYY-MM-DD|null>",
  "comparison": "<2 tháng liên tiếp|2 quý liên tiếp|cùng kỳ năm trước|null>"
}}
```

Gợi ý:

- **"difference_type"**: 
  - Chỉ chọn \"PERCENT\" nếu có từ như \"Tăng trường\" \"tỷ lệ\", \"phần trăm\", \"%\" trong câu hỏi. Nếu không có, mặc định là \"DELTA\".
  - Chênh lệch bao nhiêu bao nhiêu chọn \"DELTA"\, DELTA là sự chênh lệch tuyệt đối
- **"comparison"**:
  - Nếu trong câu hỏi có cụm từ như: "tháng trước", "quý trước", "kỳ trước" → chọn "2 tháng liên tiếp" hoặc "2 quý liên tiếp" tương ứng.
  - Nếu có cụm như: "cùng kỳ năm trước", "năm ngoái cùng kỳ" → chọn "cùng kỳ năm trước".
  - Nếu câu hỏi có cụm **"chênh lệch lũy kế năm"**, **"tăng trưởng lũy kế năm"**, hoặc **"so với cùng kỳ năm ngoái"** mà không chỉ rõ ngày cụ thể, thì phải mặc định chọn "cùng kỳ năm trước".
  - Nếu câu hỏi chỉ cung cấp 2 mốc thời gian cụ thể (date1, date2), thì không tự suy luận, để "comparison": null.

- **"date1" và "date2"**:
  - Nếu câu hỏi có chứa 2 mốc thời gian rõ ràng, hãy trích xuất và chuẩn hóa sang định dạng YYYY-MM-DD.
  - Trong đó, `date1` là mốc thời gian gần hiện tại hơn (thường là ngày được cập nhật), `date2` là mốc cũ hơn.
  - Nếu không xác định được rõ ràng 2 ngày, để null.

Ví dụ:
```json
{{
  "service_pk": "CT_VDS_DT_DV_TH_HEALTHCARE",
  "difference_type": "DELTA",
  "date1": "2024-06-20",
  "date2": "2024-05-20",
  "comparison": null
}}
```
"""
)