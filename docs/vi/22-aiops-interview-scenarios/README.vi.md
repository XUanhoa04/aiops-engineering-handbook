# Chapter 22 — 70 câu hỏi phỏng vấn tình huống AIOps cho Intern/Junior

> Bộ câu hỏi này không tìm một ứng viên thuộc nhiều thuật ngữ nhất. Nó tìm người biết làm rõ vấn đề, kiểm tra input, tìm evidence, hành động an toàn, đo outcome và nói trung thực phần mình chưa biết.

---

## Cách luyện để không học thuộc lòng

Đừng cố nhớ nguyên văn 70 câu trả lời. Với mỗi scenario, hãy tự nói thành tiếng theo ba vòng: em biết gì, em chưa biết gì, và bước nhỏ an toàn tiếp theo là gì. Câu trả lời mẫu chỉ là một cách diễn đạt ở level Intern/Junior, không phải đáp án duy nhất.

Tỷ trọng của bộ câu hỏi:

- Khoảng 68% mindset, problem solving và cách làm việc.
- Khoảng 17% communication, teamwork, stakeholder và customer.
- Khoảng 15% technical AIOps vừa đủ để scenario giống công việc thật.

Một câu trả lời tốt thường không đoán đúng root cause ngay. Nó cho interviewer thấy ứng viên biết thu hẹp phạm vi, tìm evidence, kiểm chứng giả thuyết và cập nhật người liên quan.

## Mục lục nhanh

- [LEVEL 1 — Intern foundation](#level-1-intern-foundation): Câu 1–24.
- [LEVEL 2 — Real working situations](#level-2-real-working-situations): Câu 25–50.
- [LEVEL 3 — Difficult/ambiguous production cases](#level-3-difficultambiguous-production-cases): Câu 51–70.
- [15 nguyên tắc mindset](#a-15-nguyen-tac-mindset-aiops-intern-nen-nho).
- [Framework C-H-E-C-K-S](#b-framework-tra-loi-cau-hoi-tinh-huong-c-h-e-c-k-s).
- [Framework báo cáo FACTS](#c-framework-bao-cao-khi-chua-chac-chan-facts).
- [Framework dùng AI VERIFY-AI](#d-framework-dung-ai-trong-cong-viec-verify-ai).
- [Top 20 câu nên ôn](#e-top-20-cau-co-xac-suat-cao-xuat-hien-trong-interview-aiops-intern).

---

## LEVEL 1 — Intern foundation

### Câu 1 — Một tuần làm POC anomaly detection

**Interviewer hỏi:**

Em có một tuần làm POC anomaly detection nhưng chưa biết nhiều về AIOps. Em bắt đầu như thế nào?

**Interviewer đang muốn test gì:**

- Cách làm rõ yêu cầu và chia nhỏ task.
- Khả năng học có mục tiêu thay vì học lan man.
- Cách định nghĩa một MVP có thể kiểm chứng.

**Mindset tốt nên có:**

- Hỏi signal, service, người dùng output và tiêu chí thành công.
- Chọn một metric, một service, một historical incident nhỏ.
- Dùng baseline đơn giản, demo end-to-end và báo rủi ro sớm.

**Câu trả lời mẫu:**

Đầu tiên em sẽ hỏi POC cần chứng minh điều gì: phát hiện loại bất thường nào, trên service nào, ai sẽ xem kết quả và chấp nhận chậm hoặc false alert tới mức nào. Em sẽ xin một metric có ý nghĩa với user, một khoảng dữ liệu và vài incident cũ nếu có. Trong tuần đầu em không cố làm hệ thống hoàn chỉnh; em chọn một luồng nhỏ từ đọc dữ liệu, tạo baseline đơn giản, sinh anomaly, rồi hiển thị evidence. Em sẽ dành ngày đầu học đúng phần cần dùng qua tài liệu chính thức và một ví dụ nhỏ. Giữa tuần em demo sớm để mentor sửa hướng. Em ghi rõ giới hạn như dữ liệu thiếu nhãn hoặc chưa thử production traffic. Cuối tuần em báo kết quả bằng case bắt đúng, case báo sai, điều chưa biết và đề xuất bước tiếp theo.

**Điểm cộng nếu ứng viên nói thêm:**

- Có timeline từng ngày và mốc xin feedback.
- Giữ một baseline rule đơn giản để so sánh.
- Không hứa POC đã sẵn sàng cho production.

**Red flags:**

- Học toàn bộ ML trước rồi mới bắt đầu làm.
- Chọn thuật toán phức tạp trước khi hiểu use case.
- Đến cuối tuần mới báo rằng thiếu dữ liệu.

**Follow-up khó hơn:**

- Nếu mentor bận ba ngày đầu thì em tự unblock thế nào?
- Nếu tới ngày thứ tư dữ liệu mới có thì em đổi scope ra sao?

### Câu 2 — Requirement chỉ là “monitor hệ thống tốt hơn”

**Interviewer hỏi:**

Em nhận task với requirement “monitor hệ thống tốt hơn”. Em sẽ hỏi lại và chốt scope như thế nào?

**Interviewer đang muốn test gì:**

- Khả năng biến yêu cầu mơ hồ thành outcome đo được.
- Góc nhìn user và vận hành.
- Cách tránh tự suy diễn requirement.

**Mindset tốt nên có:**

- Hỏi vấn đề hiện tại, người ra quyết định và hành động sau alert.
- Gắn metric với service, SLO hoặc customer impact.
- Chốt phạm vi, success criteria và phần không làm.

**Câu trả lời mẫu:**

Em sẽ chưa mở dashboard hay chọn tool ngay. Em hỏi người giao task: hiện tại team đang bỏ lỡ sự cố nào, alert nào gây phiền, service và user journey nào quan trọng nhất, khi có tín hiệu thì ai cần quyết định gì. Sau đó em nhắc lại requirement bằng lời cụ thể, ví dụ “trong POC này, phát hiện latency checkout tăng kéo dài năm phút và đưa evidence cho on-call, chưa tự động remediation”. Em xin một baseline hiện có như SLO, incident history hoặc dashboard đang dùng để so sánh trước và sau. Em cũng chốt phạm vi dữ liệu, môi trường, deadline và tiêu chí demo. Nếu stakeholder chưa biết target, em đề xuất hai lựa chọn nhỏ cùng trade-off. Em gửi lại bản tóm tắt để mọi người xác nhận, nhờ vậy tránh làm một dashboard đẹp nhưng không giúp xử lý sự cố.

**Điểm cộng nếu ứng viên nói thêm:**

- Hỏi rõ definition of done và owner nghiệm thu.
- Nêu giả định và quyết định cần xác nhận bằng văn bản.
- Đề xuất đo thời gian phát hiện hoặc độ hữu ích của alert.

**Red flags:**

- Hiểu “tốt hơn” là thêm thật nhiều metric.
- Tự chọn mọi requirement mà không xác nhận.
- Chỉ hỏi nên dùng Prometheus hay một tool khác.

**Follow-up khó hơn:**

- Nếu Product và SRE muốn hai outcome khác nhau thì em xử lý sao?
- Nếu không có SLO hoặc incident history thì em bắt đầu ở đâu?

### Câu 3 — Công nghệ hoàn toàn mới trong một ngày

**Interviewer hỏi:**

Ngày mai em phải dùng Prometheus, SageMaker hoặc tracing nhưng chưa từng dùng. Em học thế nào trong một ngày?

**Interviewer đang muốn test gì:**

- Khả năng tự học có giới hạn và có đầu ra.
- Cách nhận biết lỗ hổng kiến thức.
- Biết hỏi mentor câu hỏi cụ thể.

**Mindset tốt nên có:**

- Xuất phát từ task, không học cả hệ sinh thái.
- Đọc concept và tài liệu chính thức, rồi làm ví dụ nhỏ.
- Ghi lại điều đã thử, lỗi và câu hỏi còn mở.

**Câu trả lời mẫu:**

Em bắt đầu bằng việc viết ra ngày mai em phải làm được hành động nào, chẳng hạn query một metric và kiểm tra missing data, chứ không đặt mục tiêu “biết hết Prometheus”. Em dành một khoảng ngắn đọc khái niệm chính và tài liệu chính thức, sau đó dựng ví dụ nhỏ trong sandbox với dữ liệu em hiểu expected output. Khi chạy được, em thay đổi input để xem tool phản ứng với zero, missing hoặc timestamp lệch ra sao. Em ghi lại command, kết quả và phần em chưa hiểu. Nếu bị kẹt, em hỏi mentor một câu cụ thể kèm những gì đã thử, thay vì nói chung rằng em không biết công nghệ. Cuối ngày em áp dụng vào một lát cắt của task và báo rõ phần nào em đã kiểm chứng, phần nào mới chỉ đọc. Em ưu tiên đủ kiến thức để làm an toàn rồi tiếp tục học trong lúc làm.

**Điểm cộng nếu ứng viên nói thêm:**

- Timebox việc đọc và việc thử nghiệm.
- Tạo note ngắn hoặc runbook để dùng lại.
- Không thử command nguy hiểm trên production.

**Red flags:**

- Xem video cả ngày nhưng không tạo ví dụ kiểm chứng.
- Copy lệnh đầu tiên trên mạng vào production.
- Giấu việc chưa hiểu vì sợ bị đánh giá.

**Follow-up khó hơn:**

- Nếu tài liệu nội bộ thiếu và ví dụ trên mạng khác version thì sao?
- Sau một ngày vẫn chưa chạy được example, em báo thế nào?

### Câu 4 — Giải thích anomaly detection trong hai phút

**Interviewer hỏi:**

Nếu mentor cho em hai phút giải thích anomaly detection cho một BA không biết ML, em sẽ nói gì?

**Interviewer đang muốn test gì:**

- Khả năng nói đơn giản và đúng bản chất.
- Biết gắn output kỹ thuật với quyết định.
- Không biến score thành sự thật tuyệt đối.

**Mindset tốt nên có:**

- Dùng ví dụ quen thuộc và giải thích baseline.
- Phân biệt bất thường với incident.
- Nói rõ false positive, false negative và feedback.

**Câu trả lời mẫu:**

Em sẽ nói anomaly detection giống như học nhịp hoạt động bình thường của một service rồi chỉ ra lúc hành vi lệch đáng kể. Ví dụ checkout thường có latency 200–300 ms vào buổi sáng; hôm nay tăng lên 900 ms trong khi traffic tương tự thì hệ thống đánh dấu cần chú ý. Dấu đó chưa khẳng định có incident và cũng chưa nói root cause là gì. Nó là tín hiệu để engineer xem thêm error, trace, deployment và ảnh hưởng người dùng. Nếu đặt quá nhạy, hệ thống báo nhiều nhưng làm on-call mệt; nếu đặt quá chậm, có thể bỏ sót lỗi. Vì vậy team phải chọn trade-off theo service quan trọng, thu feedback từ incident thật và đo alert có giúp quyết định nhanh hơn không. Mục tiêu không phải tạo một anomaly score đẹp mà là giúp con người phát hiện và xử lý vấn đề tốt hơn.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân biệt baseline theo giờ/ngày hoặc theo service.
- Hỏi BA muốn giải thích cho quyết định kinh doanh nào.
- Dùng một hình hoặc timeline đơn giản nếu được phép.

**Red flags:**

- Mở đầu bằng công thức hoặc tên hàng loạt thuật toán.
- Nói anomaly luôn đồng nghĩa với lỗi.
- Hứa model biết chính xác root cause.

**Follow-up khó hơn:**

- Em giải thích false negative cho customer thế nào?
- Nếu BA hỏi vì sao score là 0,95 thì em trả lời sao?

### Câu 5 — Chọn metric để biết AIOps “tốt”

**Interviewer hỏi:**

Em chọn metric nào để biết hệ thống AIOps của em tốt?

**Interviewer đang muốn test gì:**

- Tư duy end-to-end và định nghĩa success.
- Không quá tin một metric offline.
- Khả năng nối model output với outcome vận hành.

**Mindset tốt nên có:**

- Đo input, pipeline, output và outcome.
- Chọn metric theo use case và có denominator rõ.
- Kết hợp chất lượng phát hiện với độ hữu ích cho on-call.

**Câu trả lời mẫu:**

Em không chọn một metric duy nhất. Trước hết em cần biết use case: detector cảnh báo outage quan trọng sẽ khác hệ thống gợi ý RCA. Với detector, em theo dõi dữ liệu có fresh và đủ không, pipeline có chạy đúng hạn không, số alert, tỷ lệ alert hữu ích, sự cố bị bỏ lỡ và thời gian từ dấu hiệu đầu đến alert. Nếu có ground truth, em xem false positive và false negative theo từng service, không chỉ accuracy tổng. Ở mức outcome, em hỏi on-call có dùng alert không, thời gian tìm nguyên nhân có giảm không và customer impact có được hạn chế không. Em luôn ghi rõ khoảng thời gian, số incident làm mẫu và giới hạn của label. Một dashboard xanh về job success không đủ nếu alert vô ích; ngược lại một score model chưa đẹp vẫn có thể hữu ích nếu nó hỗ trợ đúng quyết định và được triển khai an toàn.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách business/SLO outcome khỏi technical health.
- Đo theo service tier hoặc loại incident.
- Theo dõi feedback “useful/not useful” của on-call.

**Red flags:**

- Chỉ nói accuracy mà không hỏi dữ liệu mất cân bằng.
- Chỉ đo pipeline job success.
- Không biết ai sử dụng output.

**Follow-up khó hơn:**

- Nếu chưa có ground truth, em báo chất lượng bằng gì?
- Metric nào có thể bị tối ưu đẹp nhưng làm trải nghiệm on-call tệ hơn?

### Câu 6 — Giai đoạn quan trọng nhất trong AIOps

**Interviewer hỏi:**

Trong chuỗi data → preprocess → baseline → detector → alert → RCA → action, theo em phần nào quan trọng nhất?

**Interviewer đang muốn test gì:**

- Khả năng reasoning theo context, không tìm keyword đúng.
- Hiểu hiệu ứng lỗi lan xuống downstream.
- Nhìn được success end-to-end.

**Mindset tốt nên có:**

- Input/data là nền móng nhưng không phải toàn bộ outcome.
- Điểm quan trọng thay đổi theo failure mode và maturity.
- Contract và verification giữa các bước đều cần quan sát.

**Câu trả lời mẫu:**

Nếu buộc chọn điểm bắt đầu, em ưu tiên data và hiểu đúng tín hiệu, vì input sai hoặc stale thì detector tốt đến đâu cũng cho output sai. Nhưng em không nghĩ có một giai đoạn luôn quan trọng nhất. Một detector đúng mà alert không tới on-call, hoặc remediation chạy xong nhưng user vẫn lỗi, thì dự án vẫn thất bại. Em sẽ nhìn bottleneck hiện tại: POC có thể cần chứng minh input và baseline; production có thể đang đau vì alert noise, RCA thiếu evidence hoặc action không verify outcome. Em muốn đặt check ở ranh giới mỗi bước: input nào vào, output expected là gì, version nào tạo ra và bước sau đã nhận chưa. Cuối cùng em đo end-to-end bằng việc hệ thống có giúp phát hiện, quyết định hoặc phục hồi nhanh hơn mà vẫn an toàn không. Câu trả lời của em sẽ đổi khi evidence cho thấy bottleneck đã đổi.

**Điểm cộng nếu ứng viên nói thêm:**

- Đề cập owner và contract giữa các stage.
- Phân biệt POC success với production success.
- Nêu ví dụ command success nhưng outcome fail.

**Red flags:**

- Khẳng định model luôn là phần quan trọng nhất.
- Chỉ quan tâm UI vì đó là thứ customer nhìn thấy.
- Cho rằng stage sau tự sửa được input sai.

**Follow-up khó hơn:**

- Nếu chỉ có hai ngày để cải thiện một stage, em chọn bằng evidence nào?
- Stage nào nên có fallback rõ nhất?

### Câu 7 — AI sinh detector và test đều pass

**Interviewer hỏi:**

AI generate cho em một detector hoặc script và test đều pass. Em làm sao biết nó thực sự đúng?

**Interviewer đang muốn test gì:**

- Phân biệt chạy được với đúng.
- Cách kiểm tra output do AI tạo.
- Nhận thức về production safety.

**Mindset tốt nên có:**

- Hiểu lại requirement và assumptions của code.
- Tự tạo expected cases, edge cases và baseline so sánh.
- Review, thử trong sandbox và ghi phần chưa chắc chắn.

**Câu trả lời mẫu:**

Em sẽ không dùng việc test do cùng AI tạo ra làm bằng chứng duy nhất, vì code và test có thể cùng hiểu sai requirement. Đầu tiên em tự diễn đạt detector phải làm gì và đọc từng bước xử lý, nhất là window, timestamp, missing value và threshold. Em tạo một bộ dữ liệu rất nhỏ mà em tính được expected output bằng tay: normal ổn định, một spike, toàn zero, thiếu điểm, traffic thấp và counter reset. Em so kết quả với rule hoặc implementation cũ nếu có, rồi thử historical incident và một giai đoạn known-good. Em kiểm tra test có thật sự fail khi cố tình làm sai logic hay không. Sau đó em nhờ review phần em chưa chắc, chạy shadow hoặc staging trước production và quan sát số alert. Nếu chưa hiểu một đoạn quan trọng, em nói rõ và không copy-paste nó vào đường auto-remediation.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra dependency, security và hiệu năng cơ bản.
- Lưu prompt, version và thay đổi do mình review.
- Có negative test và property đơn giản.

**Red flags:**

- AI nói đúng và test xanh nên merge ngay.
- Chỉ kiểm tra syntax hoặc HTTP status.
- Không đọc code vì “em không viết nó”.

**Follow-up khó hơn:**

- Nếu em không đủ kiến thức để hiểu một đoạn thì làm gì?
- Nếu AI test 100 case nhưng đều sinh từ cùng assumption sai thì phát hiện sao?

### Câu 8 — AI viết PromQL nhìn rất hợp lý

**Interviewer hỏi:**

Em nhờ AI viết PromQL cho error rate, query chạy được và dashboard có số. Em validate như thế nào?

**Interviewer đang muốn test gì:**

- Cách kiểm tra query và ý nghĩa dữ liệu.
- Khả năng phát hiện denominator, label và window sai.
- Cẩn thận với output trông hợp lý.

**Mindset tốt nên có:**

- Viết rõ tử số, mẫu số và scope mong đợi.
- Kiểm tra bằng case nhỏ và nguồn đối chiếu.
- Test traffic zero, counter reset, missing series và label mismatch.

**Câu trả lời mẫu:**

Em bắt đầu từ định nghĩa error rate bằng lời: lỗi nào được tính, tổng request nào làm mẫu số, theo service hay route, và cửa sổ bao lâu. Sau đó em đọc query AI tạo để xem label filter, phép rate, aggregation và time window có đúng định nghĩa đó không. Em chọn một khoảng ngắn có số request và error biết trước từ log hoặc test traffic, rồi tính gần đúng bằng tay để so. Em cũng thử lúc không có traffic, target mất scrape, counter reset và khi có nhiều pod để xem query trả zero, NaN hay làm mất series. Em kiểm tra dashboard đang query đúng environment và timezone. Nếu query mới sẽ dùng cho alert, em chạy song song với rule cũ hoặc staging, xem chênh lệch và nhờ SRE review. Có một con số trên màn hình chỉ chứng minh query hợp lệ về cú pháp, chưa chứng minh metric đúng nghĩa.

**Điểm cộng nếu ứng viên nói thêm:**

- Ghi chú unit và label cardinality.
- Dùng recording rule đã được review nếu có.
- Cảnh báo khi denominator quá nhỏ.

**Red flags:**

- Thấy graph mượt nên cho rằng query đúng.
- Không kiểm tra service, namespace hoặc status code filter.
- Dùng zero thay cho mọi trường hợp không có dữ liệu.

**Follow-up khó hơn:**

- Log count và PromQL lệch 20% thì em điều tra từ đâu?
- Nếu metric cardinality tăng mạnh sau query mới thì sao?

### Câu 9 — Gần như không có label anomaly

**Interviewer hỏi:**

Em được giao train anomaly detector nhưng dữ liệu gần như không có label normal/anomaly. Em làm và evaluate thế nào?

**Interviewer đang muốn test gì:**

- Trung thực về giới hạn ground truth.
- Biết tận dụng domain knowledge và evidence sẵn có.
- Cách bắt đầu nhỏ, thu feedback và không bịa metric.

**Mindset tốt nên có:**

- Hiểu chất lượng, seasonality và bối cảnh dữ liệu trước.
- Tận dụng incident/change ticket, known-good period và review mẫu.
- Shadow run, weak label và feedback loop.

**Câu trả lời mẫu:**

Đầu tiên em sẽ không giả vờ rằng mình có thể báo precision hay recall chính xác khi ground truth chưa tồn tại. Em khám phá dữ liệu, missing, traffic, nhịp ngày tuần và các lần deploy. Em tìm incident ticket, on-call note, SLO breach hoặc change event để ghép được một số khoảng có khả năng bất thường. Với normal, em xin SRE xác nhận vài khoảng known-good thay vì coi toàn bộ lịch sử là bình thường. Nếu vẫn ít label, em có thể dùng rule đơn giản tạo weak label hoặc thử cách không cần nhiều label, nhưng ghi rõ đó chỉ là proxy. Em lấy một sample nhỏ cho domain expert review, chạy detector ở shadow mode và thu phản hồi alert hữu ích hay không. Evaluation ban đầu sẽ gồm replay các case đã biết, kiểm tra false alert trong known-good period và coverage dữ liệu. Sau đó em cập nhật dataset dần từ incident thật.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách train period khỏi review/replay period.
- Lưu nguồn và độ tin cậy của từng label.
- Không để incident kéo dài làm bẩn baseline normal.

**Red flags:**

- Gắn toàn bộ dữ liệu chưa có ticket là normal.
- Báo accuracy rất cao mà không có ground truth.
- Train model phức tạp trước khi hiểu dữ liệu.

**Follow-up khó hơn:**

- Nếu label của engineer cũng không chắc thì em lưu và dùng thế nào?
- Nếu hoàn toàn không có incident history thì em tạo điểm bắt đầu ra sao?

### Câu 10 — Chỉ có 10–20 incident được label

**Interviewer hỏi:**

Nếu chỉ có 10–20 incident được label thì em làm gì để không overclaim kết quả?

**Interviewer đang muốn test gì:**

- Quản lý sample nhỏ và uncertainty.
- Cách thiết kế evaluation thực tế.
- Khả năng giao tiếp giới hạn của kết quả.

**Mindset tốt nên có:**

- Không chia dữ liệu ngẫu nhiên làm rò rỉ cùng incident.
- Review case-by-case và bổ sung known-good periods.
- Báo số đếm, khoảng tin cậy định tính và phạm vi áp dụng.

**Câu trả lời mẫu:**

Với 10–20 incident, em coi đây là bộ case để học và replay chứ chưa phải bằng chứng model tổng quát tốt. Em xem từng incident có đủ telemetry, timestamp và label đáng tin không; các cửa sổ thuộc cùng một incident phải đi cùng nhau, tránh để một phần vào train và một phần vào test. Em phân nhóm sơ bộ theo loại lỗi, service và mức impact để biết model đã thấy gì và chưa thấy gì. Em bổ sung các khoảng known-good để đo false alert, chạy shadow trên dữ liệu mới và xin SRE review những alert quan trọng. Khi báo cáo, em dùng số cụ thể như bắt được 12/16 incident trong sample và ba false alert mỗi ngày, kèm danh sách case bỏ lỡ, thay vì nói accuracy chung chung. Em ghi rõ kết quả chỉ đúng cho service, thời gian và incident type đã thử, rồi đề xuất cách thu thêm label production.

**Điểm cộng nếu ứng viên nói thêm:**

- Ưu tiên leave-one-incident-out hoặc replay theo thời gian.
- Theo dõi disagreement giữa người gắn label.
- Chọn baseline đơn giản để tránh overfit sample nhỏ.

**Red flags:**

- Nhân bản sample để tạo cảm giác dữ liệu nhiều hơn.
- Chọn threshold đúng hoàn hảo trên toàn bộ 20 incident.
- Hứa model áp dụng tốt cho mọi service.

**Follow-up khó hơn:**

- Nếu 15 incident đều là database issue thì sao?
- Nếu model bỏ lỡ một incident rất nghiêm trọng nhưng bắt các incident nhẹ thì đánh giá thế nào?

### Câu 11 — Không có cả incident history

**Interviewer hỏi:**

Nếu service không có label và cũng không có incident history đáng tin, em tạo điểm bắt đầu cho detector thế nào?

**Interviewer đang muốn test gì:**

- Khả năng tiến lên khi evidence rất ít.
- Cách dùng giả định mà không biến nó thành sự thật.
- Tư duy rollout và thu feedback an toàn.

**Mindset tốt nên có:**

- Bắt đầu từ SLO, domain expectation và known-good ngắn.
- Synthetic test hoặc fault injection chỉ là evidence bổ sung.
- Chạy shadow, review mẫu và xây ground truth dần.

**Câu trả lời mẫu:**

Em sẽ nói rõ đây là bài toán chưa có ground truth nên mục tiêu đầu tiên là tạo vòng feedback, không phải chứng minh accuracy cao. Em hỏi owner về hành vi mong đợi, SLO, giờ cao điểm, deploy gần đây và những tín hiệu họ đang tin. Em chọn một khoảng vận hành được owner xác nhận tương đối ổn làm reference tạm thời, nhưng đánh dấu nó có thể chứa lỗi. Em bắt đầu bằng rule hoặc baseline dễ giải thích và test với dữ liệu synthetic nhỏ; nếu được phép, team có thể fault injection trong staging để xem detector có phản ứng. Em chạy shadow, không page hay auto-action, rồi sampling cả output cao và thấp cho SRE review. Mỗi feedback được lưu cùng evidence và độ chắc chắn để dần thành dataset. Khi báo cáo em dùng các chỉ số như coverage, alert volume và review result, không gọi đó là precision/recall thật cho tới khi có label đủ tin cậy.

**Điểm cộng nếu ứng viên nói thêm:**

- Review cả case không alert để tìm false negative.
- Đặt thời hạn cho baseline tạm và đánh giá lại.
- Tách staging synthetic khỏi kết luận production.

**Red flags:**

- Coi mọi thời điểm không có ticket là normal.
- Tự tạo fault rồi tuyên bố model production chính xác.
- Bật page ngay để “thu dữ liệu nhanh”.

**Follow-up khó hơn:**

- SRE chỉ có 30 phút mỗi tuần để review thì em chọn sample nào?
- Làm sao tránh feedback chỉ tập trung vào alert lớn?

### Câu 12 — Prometheus bị missing data

**Interviewer hỏi:**

Prometheus thiếu dữ liệu đúng lúc detector cần chạy. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Có kiểm tra input trước khi tin model không.
- Phân biệt service failure và telemetry failure.
- Cách degrade an toàn và báo trạng thái.

**Mindset tốt nên có:**

- Kiểm tra scope, freshness, scrape health và query path.
- Không tự điền zero hoặc tiếp tục như data vẫn tốt.
- Gắn quality flag, fallback và quan sát recovery.

**Câu trả lời mẫu:**

Đầu tiên em xác định missing ở một series, một target, một cluster hay toàn query path. Em kiểm tra target scrape health, collector, label thay đổi, query range, timestamp và remote-write delay. Em đối chiếu log, Kubernetes event hoặc nguồn Prometheus khác để biết service thật sự im lặng hay chỉ telemetry bị đứt. Detector không nên tự coi missing là zero hoặc normal; em muốn output có cờ data_quality, tuổi datapoint và số sample thực tế. Nếu dữ liệu dưới mức tối thiểu, detector có thể trả trạng thái insufficient_data, giữ alert trước đó theo policy hoặc dùng fallback đã thống nhất, nhưng không tạo một kết luận tự tin giả. Em báo SRE cả impact của monitoring blind spot và service bị ảnh hưởng. Sau khi dữ liệu về lại, em kiểm tra backfill, duplicate hoặc spike giả trước khi mở lại decision bình thường và ghi nguyên nhân để tránh lặp lại.

**Điểm cộng nếu ứng viên nói thêm:**

- Có alert riêng cho telemetry freshness/coverage.
- Phân biệt event time với processing time.
- Không để recovery burst làm detector báo sai.

**Red flags:**

- Fill zero cho mọi điểm thiếu.
- Im lặng bỏ qua detector run bị thiếu input.
- Kết luận service down chỉ vì Prometheus không có sample.

**Follow-up khó hơn:**

- Nếu chỉ thiếu metric lỗi nhưng latency vẫn có thì detector nên làm gì?
- Khi nào missing data tự nó là một alert cần page?

### Câu 13 — Metric bằng 0: zero thật hay missing?

**Interviewer hỏi:**

Một metric đột nhiên bằng 0. Em làm sao phân biệt zero thật với missing data bị biến thành zero?

**Interviewer đang muốn test gì:**

- Hiểu ý nghĩa và provenance của metric.
- Biết dùng tín hiệu đối chiếu.
- Không kết luận từ một con số đơn lẻ.

**Mindset tốt nên có:**

- Kiểm tra metric type, query, raw series và scrape health.
- So với traffic, log, trace và deployment/change.
- Tạo test nhỏ để tái hiện hành vi no-data.

**Câu trả lời mẫu:**

Em sẽ xem metric này đo gì và query đã xử lý no-data thế nào. Em mở raw series thay vì chỉ nhìn panel đã dùng phép fill, kiểm tra last timestamp, sample count, target up và rule evaluation. Nếu là request count bằng 0, em đối chiếu traffic ở gateway, access log và trace; zero thật thường có evidence traffic cũng dừng, còn scrape hỏng có thể các nguồn khác vẫn hoạt động. Em kiểm tra có deploy đổi metric name hoặc label khiến query cũ không match không. Em cũng chạy query trên một khoảng biết chắc target mất scrape để hiểu dashboard hiển thị missing thành gì. Cho detector, em giữ riêng value, presence và freshness; không để phép biến đổi xóa mất sự khác biệt. Khi chưa đủ evidence, em báo “metric đang hiển thị zero nhưng chưa xác nhận là business traffic bằng zero” và tiếp tục kiểm tra data path trước khi kết luận outage.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra counter reset và rate window.
- Quan sát số series/cardinality trước và sau deploy.
- Thêm panel data freshness cạnh value.

**Red flags:**

- Thấy 0 là kết luận hệ thống hết traffic.
- Tin dashboard mà không xem query.
- Dùng coalesce/fill zero mà không ghi semantics.

**Follow-up khó hơn:**

- Nếu gateway cũng bằng 0 nhưng customer vẫn tạo order được thì sao?
- Một gauge zero và counter rate zero khác nhau thế nào trong cách kiểm tra?

### Câu 14 — Model trả anomaly_score bằng 0,95

**Interviewer hỏi:**

Model output anomaly_score=0.95. Em sẽ làm gì tiếp theo, và xem kết quả này ở đâu?

**Interviewer đang muốn test gì:**

- Không đồng nhất score với incident hoặc root cause.
- Khả năng tìm context và evidence.
- Hiểu đường đi của output tới alert/incident.

**Mindset tốt nên có:**

- Kiểm tra input, baseline, threshold, persistence và impact.
- Xem record detector, dashboard, log và incident timeline.
- Lưu version/provenance để debug được.

**Câu trả lời mẫu:**

Em chưa kết luận có incident chỉ từ 0,95. Em mở record của lần chạy đó để xem service, metric, cửa sổ thời gian, raw value, baseline, threshold, sample count, data freshness và model version. Em so score trước và sau để biết đây là một spike đơn hay kéo dài, đồng thời đối chiếu error, traffic, log, trace, deploy và SLO/customer impact. Em kiểm tra policy: score này đã qua persistence, suppression và route alert chưa; nếu chưa thì lý do gì. Kết quả nên xem được ở dashboard detector và incident timeline, còn record chi tiết nằm trong structured log hoặc output store để truy ngược. Em giữ run_id, feature/model/baseline version và link evidence. Nếu input stale hoặc traffic quá thấp, em hạ độ tin cậy hoặc đánh dấu insufficient data. Chỉ khi evidence và policy đủ, em mới tạo alert hoặc đề nghị SRE điều tra.

**Điểm cộng nếu ứng viên nói thêm:**

- Xem score calibration hoặc lịch sử score tương tự.
- Ghi cả suppression reason và downstream incident id.
- Phân biệt event timestamp với thời gian model xử lý.

**Red flags:**

- Score trên 0,9 nghĩa là 90% chắc chắn có outage.
- Restart service ngay.
- Chỉ chụp ảnh dashboard mà không giữ record/version.

**Follow-up khó hơn:**

- Nếu score 0,95 nhưng sample count chỉ là ba request thì sao?
- Nếu SLO đang breach nhưng score chỉ 0,4 thì em tin cái nào?

### Câu 15 — Detector báo anomaly, SRE nói bình thường

**Interviewer hỏi:**

Detector báo anomaly nhưng SRE nói hệ thống đang bình thường. Em xử lý ý kiến này thế nào?

**Interviewer đang muốn test gì:**

- Cách nhận feedback mà không phòng thủ.
- Khả năng phân biệt false positive với anomaly không impact.
- Cách biến phản hồi thành cải tiến có evidence.

**Mindset tốt nên có:**

- Xin scope và lý do SRE kết luận bình thường.
- Cùng xem input, baseline, change và customer impact.
- Label kết quả, tìm pattern và theo dõi sau tune.

**Câu trả lời mẫu:**

Em sẽ không cố bảo vệ model chỉ vì score cao. Em cảm ơn feedback và hỏi SRE đang dựa vào evidence nào: SLO, ticket, traffic, deploy hay kinh nghiệm về batch job định kỳ. Sau đó em cùng họ xem timestamp, raw metric, baseline, sample count và các tín hiệu liên quan. Có thể detector bắt một thay đổi thật nhưng thay đổi đó expected và không cần page; cũng có thể query hoặc baseline sai. Em ghi lại kết luận với nhãn phù hợp như false positive, expected change hoặc anomaly không có customer impact, thay vì chỉ xóa alert. Em tìm xem đây là một case riêng hay pattern lặp theo maintenance, low traffic hoặc service type. Trước khi đổi threshold toàn cục, em replay thay đổi trên lịch sử, canary cho đúng service và theo dõi cả alert noise lẫn incident bị bỏ lỡ. Feedback của SRE là evidence để cải thiện, không phải thất bại cần giấu.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách detection khỏi paging policy.
- Lưu reason code cho feedback.
- Đóng vòng bằng cách báo lại kết quả tune cho SRE.

**Red flags:**

- Nói model khách quan hơn con người nên SRE sai.
- Tắt alert ngay không điều tra.
- Tăng threshold mọi service chỉ từ một case.

**Follow-up khó hơn:**

- Nếu SRE chỉ nói “tôi biết nó bình thường” nhưng không có evidence thì sao?
- Nếu anomaly không impact hôm nay nhưng từng báo trước incident thì xử lý thế nào?

### Câu 16 — User lỗi nhưng detector không alert

**Interviewer hỏi:**

User báo hệ thống lỗi nhưng detector không alert. Em điều tra và phản hồi ra sao?

**Interviewer đang muốn test gì:**

- Thái độ với false negative và customer evidence.
- Cách debug end-to-end thay vì chỉ chỉnh model.
- Biết ưu tiên incident trước phân tích model.

**Mindset tốt nên có:**

- Xác nhận impact và hỗ trợ incident flow trước.
- Kiểm tra coverage từ telemetry đến routing/suppression.
- Tạo test/replay và bổ sung monitoring sau sự cố.

**Câu trả lời mẫu:**

Trước hết em coi complaint là tín hiệu cần xác minh, không trả lời rằng dashboard đang xanh. Em lấy thời gian, user journey, tenant hoặc region bị ảnh hưởng và phối hợp SRE kiểm tra SLO, log, trace; nếu incident đang diễn ra thì ưu tiên giảm impact. Sau đó em đi từng chặng: telemetry có thu đúng route đó không, data có trễ hay bị sampling, feature có tính đúng, score có tăng, threshold/persistence có chặn, alert có bị suppress hoặc route sai không. Em tìm record của detector run quanh thời điểm complaint và so expected với actual. Có thể model không thấy vì metric service-level đã che một route ít traffic, chứ không phải model nói hệ thống khỏe. Em ghi false negative cùng evidence, replay case sau khi sửa và kiểm tra không làm noise tăng quá mức. Với customer, em nói rõ điều đã xác nhận, phạm vi ảnh hưởng, biện pháp hiện tại và kế hoạch tránh bỏ lỡ tương tự.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra tenant/route/region dimension và sampling.
- Tách lỗi detection khỏi notification delivery.
- Thêm canary hoặc synthetic journey nếu telemetry không đủ.

**Red flags:**

- Bác complaint vì model không alert.
- Chỉ hạ threshold ngay.
- Che giấu false negative để bảo vệ KPI.

**Follow-up khó hơn:**

- Nếu không tái hiện được complaint thì em giữ case thế nào?
- Nếu route bị lỗi chỉ chiếm 0,1% traffic nhưng là khách hàng lớn thì sao?

### Câu 17 — API inference trả HTTP 200 nhưng output sai

**Interviewer hỏi:**

API inference trả HTTP 200 nhưng kết quả model sai. Em debug từ đâu?

**Interviewer đang muốn test gì:**

- Phân biệt transport success với semantic correctness.
- Cách lần theo contract input/output và version.
- Khả năng tạo test tái hiện.

**Mindset tốt nên có:**

- Lưu request an toàn, expected output và correlation id.
- Kiểm tra schema, preprocessing, version và post-processing.
- So từng stage và verify bản sửa bằng regression case.

**Câu trả lời mẫu:**

HTTP 200 chỉ cho em biết endpoint đã xử lý request theo giao thức, không chứng minh kết quả đúng nghiệp vụ. Em lấy một request cụ thể đã ẩn dữ liệu nhạy cảm, run_id và expected result do đâu xác định. Em kiểm tra schema, unit, thứ tự feature, missing value, timestamp và model version mà endpoint thực sự load. Sau đó em chạy cùng input qua từng bước preprocessing, model và post-processing để xem sai bắt đầu ở đâu; em so với offline notebook hoặc endpoint phiên bản cũ trên cùng dữ liệu. Em cũng kiểm tra cache, threshold và mapping label vì model score có thể đúng nhưng response bị đổi nghĩa. Nếu ảnh hưởng production, em đề xuất rollback hoặc route về baseline an toàn trong khi điều tra. Bản sửa phải có regression test từ case này, thử thêm edge case và theo dõi output distribution, không chỉ kiểm tra API tiếp tục trả 200.

**Điểm cộng nếu ứng viên nói thêm:**

- Ghi request/model/schema version và data hash.
- Kiểm tra online/offline preprocessing skew.
- Không log dữ liệu nhạy cảm nguyên bản.

**Red flags:**

- Restart endpoint vì status code vẫn xanh.
- Train lại model ngay mà chưa locate stage sai.
- Chỉ thêm test status=200.

**Follow-up khó hơn:**

- Nếu cùng request lúc đúng lúc sai thì em thêm kiểm tra gì?
- Nếu không còn artifact model cũ để so thì sao?

### Câu 18 — Log gì cho mỗi detector run?

**Interviewer hỏi:**

Em thiết kế output record cho mỗi lần detector chạy. Em sẽ ghi field gì để sau này debug được?

**Interviewer đang muốn test gì:**

- Tư duy observability cho chính hệ thống AIOps.
- Khả năng tái dựng một quyết định.
- Cân bằng đủ evidence với chi phí và bảo mật.

**Mindset tốt nên có:**

- Có identity, time, input quality, versions, decision và routing.
- Ghi reason/counter-evidence, không chỉ final label.
- Link tới evidence thay vì dump dữ liệu nhạy cảm.

**Câu trả lời mẫu:**

Em muốn từ một record trả lời được: lần chạy nào, dùng dữ liệu nào, phiên bản nào và vì sao ra quyết định đó. Em ghi run_id, service/metric/route, event window, thời gian xử lý và environment. Phần input có sample count, missing rate, freshness, traffic volume, schema hoặc feature version và link tới query/evidence; không nhất thiết dump raw data nhạy cảm. Phần processing có detector/model version, baseline version, threshold, latency, status và lỗi fallback. Phần output có raw value, expected range, anomaly score, label, confidence hoặc quality flag, reason codes và counter-evidence. Em cũng ghi alert có bị persistence/suppress không, incident_id nếu tạo, action đề xuất và outcome feedback về sau. Log cần structured để query được, có retention và quyền truy cập phù hợp. Em sẽ test bằng việc chọn một alert cũ và xem có tái dựng được decision hay không.

**Điểm cộng nếu ứng viên nói thêm:**

- Có trace/correlation id xuyên pipeline.
- Ghi model artifact/data lineage thay vì tên mơ hồ “latest”.
- Phân biệt event time, ingest time và inference time.

**Red flags:**

- Chỉ log anomaly=true hoặc false.
- Log toàn bộ customer payload không kiểm soát.
- Không ghi version và suppression reason.

**Follow-up khó hơn:**

- Nếu log quá lớn và tốn chi phí, em giữ field nào trước?
- Làm sao nối feedback của SRE quay lại đúng detector run?

### Câu 19 — Monitor chính AIOps pipeline

**Interviewer hỏi:**

Detector đang chạy rồi. Em monitor chính AIOps pipeline như thế nào?

**Interviewer đang muốn test gì:**

- Hiểu input, processing, output và outcome đều có thể hỏng.
- Không dùng “model có trả output” làm health check.
- Biết thiết kế meta-monitoring có hành động.

**Mindset tốt nên có:**

- Theo dõi freshness/coverage input và health từng stage.
- Theo dõi distribution, alert flow và feedback output.
- Có owner, alert và fallback cho chính pipeline.

**Câu trả lời mẫu:**

Em chia monitoring thành bốn lớp. Input: có data vào không, sample count, missing rate, delay, traffic, schema và service coverage. Processing: job success/fail, lần chạy gần nhất, latency, queue backlog, inference error, model và baseline version. Output: score distribution, tỷ lệ normal/anomaly/insufficient-data, alert count, suppression, incident được tạo và các thay đổi bất thường sau deploy. Outcome: SRE đánh giá alert hữu ích không, incident thật có bị bỏ lỡ, RCA có rút ngắn điều tra và remediation có cải thiện SLO không. Em đặt freshness alert độc lập để model không thể cứ trả output từ input cũ mà dashboard vẫn xanh. Mỗi alert của pipeline phải có owner và runbook; khi quality thấp, hệ thống degrade về detection-only hoặc baseline an toàn. Em cũng tạo canary input có expected behavior và định kỳ replay incident để phát hiện silent regression.

**Điểm cộng nếu ứng viên nói thêm:**

- Tránh pipeline tự monitor hoàn toàn bằng chính data path đang hỏng.
- Có SLO cho detection latency và coverage.
- Monitor drift theo service, không chỉ aggregate.

**Red flags:**

- Chỉ monitor CPU/RAM của endpoint.
- Job SUCCESS là đủ.
- Alert volume bằng zero được coi là hệ thống yên bình.

**Follow-up khó hơn:**

- Metric nào page on-call và metric nào chỉ tạo ticket?
- Nếu meta-monitoring cũng dùng Prometheus đang lỗi thì sao?

### Câu 20 — Accuracy cao có nghĩa AIOps tốt?

**Interviewer hỏi:**

Model accuracy 99%. Điều đó có nghĩa hệ thống AIOps tốt không?

**Interviewer đang muốn test gì:**

- Hiểu dữ liệu mất cân bằng và metric context.
- Phân biệt model metric với production outcome.
- Biết hỏi denominator và cost của lỗi.

**Mindset tốt nên có:**

- Hỏi cách tạo label, split và tỷ lệ anomaly.
- Xem false positive/negative theo severity.
- Đo latency, coverage, usefulness và customer outcome.

**Câu trả lời mẫu:**

Chưa chắc. Nếu 99% thời gian là normal, model luôn đoán normal cũng có thể đạt gần 99% nhưng bỏ lỡ mọi incident. Em sẽ hỏi accuracy tính trên dataset nào, label đáng tin không, split có rò rỉ cùng incident không và service nào được đại diện. Em xem confusion theo số đếm cụ thể, đặc biệt false negative của incident nghiêm trọng và false positive gây page. Sau đó em kiểm tra production: dữ liệu có giống offline không, alert có đúng hạn, on-call có thấy hữu ích và customer impact có giảm không. Một model bắt đúng anomaly sau khi incident đã kết thúc cũng không giúp nhiều. Em muốn so với baseline đơn giản và model cũ trên cùng replay, rồi chạy shadow/canary. Khi báo cáo, em không dùng 99% đứng một mình; em kèm phạm vi, denominator, các case bỏ lỡ và trade-off vận hành để stakeholder hiểu model thực sự giúp gì.

**Điểm cộng nếu ứng viên nói thêm:**

- Xem metric theo severity/service và detection delay.
- Kiểm tra calibration nếu output được hiểu như confidence.
- Đặt cost khác nhau cho các loại lỗi.

**Red flags:**

- 99% nghĩa là gần hoàn hảo.
- Không hỏi anomaly prevalence.
- Chỉ tối ưu leaderboard offline.

**Follow-up khó hơn:**

- Model accuracy thấp hơn nhưng bắt đủ incident P1 thì có thể tốt hơn không?
- Nếu label production trễ hai tuần, em monitor sớm bằng gì?

### Câu 21 — False positive hay false negative nguy hiểm hơn?

**Interviewer hỏi:**

False positive hay false negative nguy hiểm hơn trong AIOps?

**Interviewer đang muốn test gì:**

- Có reasoning theo use case thay vì trả lời tuyệt đối.
- Hiểu cost, severity và human trust.
- Biết thiết kế trade-off và guardrail.

**Mindset tốt nên có:**

- Trả lời “tùy use case” và nêu ví dụ.
- Xét service tier, action, giờ trực và blast radius.
- Dùng routing/persistence/human approval để quản lý trade-off.

**Câu trả lời mẫu:**

Theo em tùy use case và hậu quả của mỗi lỗi. Với cảnh báo cháy ở payment quan trọng, false negative có thể bỏ lỡ outage và mất giao dịch nên rất nguy hiểm. Nhưng nếu detector page on-call hàng trăm lần vô ích, false positive làm alert fatigue, mất niềm tin và cuối cùng con người cũng bỏ qua cảnh báo thật. Với auto-remediation, false positive còn nguy hiểm hơn vì có thể tác động production. Em sẽ hỏi service tier, loại incident, action sau output, thời gian cần phát hiện và khả năng có tín hiệu xác nhận khác. Sau đó em chọn threshold, persistence, routing và approval tương ứng: có thể detector nhạy nhưng chỉ đưa vào dashboard, còn page hoặc action cần thêm evidence. Em đo cả hai loại lỗi theo severity và review trade-off với SRE/Product. Không có threshold tốt tuyệt đối; điều quan trọng là cost được nói rõ và theo dõi sau thay đổi.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách detection sensitivity khỏi notification policy.
- Dùng nhiều mức cảnh báo theo confidence/impact.
- Định kỳ xem lại cost khi traffic hoặc product đổi.

**Red flags:**

- Luôn chọn false negative hoặc false positive mà không hỏi context.
- Chỉ tăng threshold để on-call hết phàn nàn.
- Không xét auto-action.

**Follow-up khó hơn:**

- Với fraud-like anomaly và batch job nội bộ, trade-off khác nhau ra sao?
- Ai nên tham gia quyết định cost của hai loại lỗi?

### Câu 22 — Pipeline SUCCESS có phải project success?

**Interviewer hỏi:**

Pipeline data → train → deploy chạy SUCCESS. Có nghĩa project AIOps thành công không?

**Interviewer đang muốn test gì:**

- Phân biệt execution status với semantic và business outcome.
- Tư duy verification end-to-end.
- Nhận ra silent failure.

**Mindset tốt nên có:**

- Kiểm tra artifact, data, evaluation và production behavior.
- Theo dõi output tới alert/decision/outcome.
- So với acceptance criteria đã chốt.

**Câu trả lời mẫu:**

Chưa. SUCCESS chỉ nói các stage không ném lỗi theo điều kiện kỹ thuật đã cấu hình. Pipeline vẫn có thể dùng nhầm dataset, feature toàn zero, label lệch, deploy sai model version hoặc tạo alert vô ích. Em sẽ kiểm tra lineage và version của data/model, sample output sau mỗi stage, evaluation trên case độc lập và endpoint thật đang load artifact nào. Sau deploy em so distribution, alert volume và một số request biết expected result với phiên bản cũ. Ở cuối luồng, em kiểm tra alert có tới đúng người, RCA có evidence và outcome người dùng có cải thiện không. Em đối chiếu với definition of done: POC có thể chỉ cần replay vài case, còn production cần safety, monitoring và rollback. Nếu chỉ dashboard orchestration xanh, em báo “pipeline execution thành công, chất lượng output và outcome vẫn đang được validate”, không gọi cả project đã hoàn tất.

**Điểm cộng nếu ứng viên nói thêm:**

- Có data contract và quality gate giữa stage.
- Pin version thay vì dùng latest.
- Có smoke test semantic sau deploy.

**Red flags:**

- Thấy toàn bộ stage màu xanh là đóng task.
- Không xem sample output.
- Không có acceptance criteria ngoài “deploy được”.

**Follow-up khó hơn:**

- Em thêm gate nào đầu tiên nếu pipeline thường silent fail?
- Khi nào nên tự động block deploy dù training job SUCCESS?

### Câu 23 — Solution mới chắc 60–70%

**Interviewer hỏi:**

Em có một solution nhưng chỉ chắc khoảng 60–70% là đúng. Em trình bày và hành động thế nào?

**Interviewer đang muốn test gì:**

- Communication of uncertainty.
- Khả năng tách fact, hypothesis và next test.
- Chọn hành động theo mức rủi ro.

**Mindset tốt nên có:**

- Nêu evidence support và counter-evidence.
- Không biến phần trăm cảm tính thành sự thật.
- Đề xuất test nhỏ, rollback hoặc xin review.

**Câu trả lời mẫu:**

Em sẽ không chỉ nói “em chắc 70%” vì con số đó có thể cảm tính. Em trình bày phần đã xác nhận, ví dụ input fresh, lỗi bắt đầu sau deploy và chỉ xảy ra ở model mới. Evidence đang nghiêng về hypothesis X, nhưng em chưa kết luận vì chưa kiểm tra feature version hoặc chưa tái hiện được case Y. Em đề xuất bước rẻ và an toàn nhất để giảm uncertainty, chẳng hạn replay cùng request trên old/new model hoặc canary một nhóm nhỏ. Nếu solution chỉ thay dashboard thì có thể thử có giám sát; nếu đụng production hoặc auto-remediation, em xin review/approval và chuẩn bị rollback. Em báo mốc cập nhật tiếp theo và phương án nếu test không xác nhận giả thuyết. Cách nói của em sẽ là: “đây là hướng có evidence tốt nhất hiện tại, không phải root cause đã được chứng minh”.

**Điểm cộng nếu ứng viên nói thêm:**

- Gắn mức confidence với chất lượng evidence.
- Nêu rõ blast radius và reversible action.
- Có điều kiện dừng hoặc rollback trước khi thử.

**Red flags:**

- Nói chắc chắn để trông tự tin.
- Không làm gì cho tới khi đạt 100% chắc chắn.
- Test trực tiếp toàn production để có câu trả lời nhanh.

**Follow-up khó hơn:**

- Nếu incident đang gây impact và không có thời gian validate đầy đủ thì sao?
- Evidence nào sẽ khiến em đổi sang hypothesis khác?

### Câu 24 — Mentor hỏi khi chưa validate xong

**Interviewer hỏi:**

Mentor hỏi kết quả nhưng em chưa validate xong model. Em trả lời thế nào?

**Interviewer đang muốn test gì:**

- Báo cáo tiến độ trung thực và hữu ích.
- Phân biệt result tạm với kết luận.
- Khả năng đưa next step và ETA.

**Mindset tốt nên có:**

- Nói goal, done, evidence, unknown, risk và need-help.
- Không chỉ nói “chưa xong”.
- Đưa mốc cập nhật và lựa chọn nếu deadline sát.

**Câu trả lời mẫu:**

Em sẽ báo phần đã biết thay vì chờ có kết luận hoàn hảo. Ví dụ: “Mục tiêu là giảm false alert cho payment. Em đã xác nhận pipeline và input không thiếu, replay 12 incident cho thấy threshold mới giảm 30% alert trong sample. Em chưa kết luận tốt hơn vì chưa review hai incident bị bỏ lỡ và chưa thử production-like traffic. Rủi ro hiện tại là giảm noise nhưng tăng false negative. Chiều nay em sẽ so hai case đó với SRE và chạy shadow; em cập nhật lúc 4 giờ. Nếu cần demo trước, em đề xuất trình bày đây là kết quả tạm và chưa rollout.” Em kèm link evidence hoặc bảng case, nói rõ điều gì cần mentor giúp quyết định. Như vậy mentor có thể sửa hướng sớm mà không hiểu nhầm một con số sơ bộ là kết quả cuối.

**Điểm cộng nếu ứng viên nói thêm:**

- Có recommendation thay vì đẩy toàn bộ quyết định lên mentor.
- Báo sớm khi ETA hoặc scope có nguy cơ đổi.
- Ghi rõ production-like chưa phải production validation.

**Red flags:**

- Nói model tốt rồi mới thú nhận chưa test.
- Chỉ nói “em vẫn đang làm”.
- Đợi deadline mới báo thiếu validation.

**Follow-up khó hơn:**

- Nếu mentor yêu cầu deploy ngay thì em phản hồi thế nào?
- Nếu em chưa có ETA đáng tin thì báo mốc ra sao?

---

## LEVEL 2 — Real working situations

### Câu 25 — Offline đẹp, production tệ

**Interviewer hỏi:**

Model production báo rất tệ nhưng offline evaluation lại đẹp. Em điều tra theo thứ tự nào?

**Interviewer đang muốn test gì:**

- Debug online/offline gap có hệ thống.
- Không vội train model khác.
- Biết kiểm tra data, code, version và feedback.

**Mindset tốt nên có:**

- Xác nhận cùng definition, input và artifact.
- Tìm leakage, drift, preprocessing skew và label delay.
- Compare old/new, shadow hoặc rollback theo impact.

**Câu trả lời mẫu:**

Em bắt đầu bằng việc xác nhận “tệ” nghĩa là gì trong production: nhiều false alert, bỏ lỡ incident hay score phân bố lạ. Em lấy vài case cụ thể rồi so cùng input qua offline và online. Em kiểm tra endpoint đang dùng đúng model, feature, schema, threshold và preprocessing version không; data production có missing, delay, traffic hoặc service mix khác tập đánh giá không. Em xem cách chia train/test có vô tình để cùng incident vào hai bên hoặc dùng thông tin tương lai không. Label offline cũng có thể sạch hơn feedback production. Nếu model mới gây ảnh hưởng, em giữ hoặc rollback baseline cũ, chạy model mới shadow trong lúc điều tra. Em sửa stage đã chứng minh sai thay vì train lại mù quáng. Cuối cùng em thêm regression case từ production, đánh giá theo service/severity và theo dõi alert usefulness sau thay đổi để xác nhận gap thực sự đóng.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra training-serving skew và artifact hash.
- So traffic cohort, seasonality và feature distribution.
- Xem detection latency, không chỉ label đúng/sai.

**Red flags:**

- Đổ lỗi production data rồi train lại ngay.
- Chỉ nhìn accuracy offline tổng.
- Không có cách quay về model cũ.

**Follow-up khó hơn:**

- Nếu cùng feature values nhưng online score vẫn khác thì em kiểm tra gì?
- Nếu production label không chắc chắn thì kết luận model tệ bằng evidence nào?

### Câu 26 — SageMaker training SUCCESS nhưng production không tốt

**Interviewer hỏi:**

SageMaker training job báo SUCCESS nhưng model production không tốt. Em debug từ đâu?

**Interviewer đang muốn test gì:**

- Hiểu job success không bảo đảm model quality.
- Khả năng isolate data, train, artifact, deploy và inference.
- Tư duy reproducibility và rollback.

**Mindset tốt nên có:**

- Kiểm tra dataset/model/feature/image version và evaluation artifact.
- Reproduce một case từ raw input tới endpoint.
- So model cũ, rollback và lưu evidence.

**Câu trả lời mẫu:**

Em xem SUCCESS là trạng thái thực thi, rồi kiểm tra artifact cụ thể job đã tạo. Em xác nhận dataset URI/version, schema, thời gian cắt dữ liệu, preprocessing code, training image, hyperparameter và random seed nếu có. Em xem evaluation có thật sự chạy trên tập tách biệt và có gate hay chỉ ghi metric. Tiếp theo em xác nhận model package nào được approve, endpoint đang load version nào và online feature có cùng cách tính với training không. Em chọn một production request sai, truy từ raw input qua preprocessing đến prediction rồi chạy lại với model cũ và mới. Nếu impact cao, em đề xuất rollback endpoint hoặc chuyển model mới sang shadow; training lại chưa phải bước đầu. Em lưu model/data/code version và case tái hiện để team ML cùng phân tích. Sau fix, em cần semantic smoke test và monitor output distribution, alert volume, không chỉ chờ console SageMaker xanh.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra model registry approval và endpoint deployment config.
- Giữ evaluation report như artifact có version.
- Có canary traffic và rollback trigger.

**Red flags:**

- Bấm retrain nhiều lần để thử vận may.
- Tin model endpoint đang dùng “latest”.
- Chỉ xem training loss.

**Follow-up khó hơn:**

- Nếu không tái tạo được kết quả training cũ thì em ưu tiên kiểm tra gì?
- Nếu rollback model nhưng lỗi vẫn còn thì hypothesis đổi thế nào?

### Câu 27 — Model mới làm alert tăng gấp 10

**Interviewer hỏi:**

Model version mới deploy xong thì alert tăng gấp 10 lần. Em làm gì trong giờ đầu tiên?

**Interviewer đang muốn test gì:**

- Incident response cho model change.
- Cân bằng giảm impact với giữ evidence.
- Không tune threshold mù quáng.

**Mindset tốt nên có:**

- Xác nhận timeline, scope và customer/on-call impact.
- So old/new trên cùng input, kiểm tra data/schema/threshold.
- Dừng rollout hoặc rollback bằng tiêu chí rõ.

**Câu trả lời mẫu:**

Em xác nhận alert tăng bắt đầu đúng thời điểm deploy không, tăng ở service nào và có incident thật hay chủ yếu noise. Em thông báo SRE rằng team đang điều tra model change để họ biết alert reliability đang giảm. Em giữ sample output, run_id, model/config version và cùng input chạy qua old/new model; đồng thời kiểm tra schema, missing, score distribution, threshold và suppression có thay đổi không. Nếu canary hoặc rollback criteria đã breach, em dừng rollout hoặc quay về model cũ thay vì tăng threshold vội. Nếu alert phản ánh outage thật cùng thời điểm, em không suppress toàn bộ mà phối hợp incident response. Sau khi ổn định, em phân loại alert tăng do model sensitivity, data shift hay routing duplication, replay các case và chỉ canary lại sau review. Em verify bằng alert rate, false alert sample và incident coverage, rồi ghi post-change note.

**Điểm cộng nếu ứng viên nói thêm:**

- Có change marker trên dashboard.
- Tách alert generation khỏi page delivery để giảm noise an toàn.
- Kiểm tra duplicate consumer hoặc retry.

**Red flags:**

- Tăng threshold toàn cục cho dashboard đẹp lại.
- Xóa log để giảm chi phí khi alert bùng nổ.
- Giữ model mới vì deploy đã được duyệt.

**Follow-up khó hơn:**

- Nếu model mới bắt thêm một incident thật mà model cũ bỏ lỡ thì rollback thế nào?
- Nếu không có model cũ khả dụng thì fallback là gì?

### Câu 28 — Model không tốt: sửa model hay kiểm tra data?

**Interviewer hỏi:**

Nếu model không tốt, em sửa model trước hay kiểm tra data trước?

**Interviewer đang muốn test gì:**

- Khả năng chọn bước debug hiệu quả.
- Tránh “model-first thinking”.
- Biết dùng case cụ thể để thu hẹp lỗi.

**Mindset tốt nên có:**

- Xác nhận metric “không tốt” và input/label trước.
- Kiểm tra pipeline/config trước khi đổi thuật toán.
- Chỉ thay model khi evidence chỉ về năng lực model.

**Câu trả lời mẫu:**

Thông thường em kiểm tra định nghĩa vấn đề và data trước, vì sửa model trên input hoặc label sai chỉ làm khó debug hơn. Em lấy các case false positive/negative cụ thể, xác nhận timestamp, label, missing, traffic, unit, schema và feature có đúng không. Em kiểm tra threshold, baseline contamination, preprocessing và production có chạy đúng version. Sau đó em so với một rule hoặc model cũ để biết lỗi thuộc toàn pipeline hay riêng model. Nếu data và contract đã ổn nhưng model vẫn không tách được hành vi của service, lúc đó em mới cùng ML Engineer xem feature, threshold, cách train hoặc model khác. Em thay một yếu tố mỗi lần và replay cùng bộ case để biết cái gì cải thiện. Trong production, em giữ fallback hoặc shadow/canary. “Kiểm tra data trước” không có nghĩa data luôn có lỗi; nó là bước rẻ và nền tảng để tránh tối ưu sai chỗ.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra label provenance và disagreement.
- Phân tách detector quality với alert policy.
- Có experiment log để tránh thay nhiều biến cùng lúc.

**Red flags:**

- Đổi sang thuật toán phức tạp hơn ngay.
- Luôn đổ lỗi data mà không đưa evidence.
- Tune trực tiếp trên production alert hiện tại.

**Follow-up khó hơn:**

- Evidence nào đủ để em kết luận model capacity là vấn đề?
- Nếu data issue không thể sửa sớm thì có fallback nào?

### Câu 29 — Tuần trước tốt, tuần này giảm

**Interviewer hỏi:**

Model hoạt động tốt tuần trước nhưng tuần này giảm rõ rệt. Em tìm nguyên nhân thế nào?

**Interviewer đang muốn test gì:**

- Nhận biết drift, change và pipeline regression.
- Kỹ năng so sánh hai khoảng thời gian.
- Không mặc định retraining là đáp án.

**Mindset tốt nên có:**

- Chốt thời điểm quality đổi và change timeline.
- So input quality, traffic mix, version và feedback.
- Tìm smallest changed factor, rollback/canary khi cần.

**Câu trả lời mẫu:**

Em xác định quality bắt đầu giảm từ lúc nào và bằng metric/case nào, rồi đặt timeline cạnh deploy ứng dụng, schema, collector, model, threshold và traffic campaign. Em so hai tuần về data freshness, missing rate, volume, service/route mix, feature distribution và score distribution. Em kiểm tra model thật sự có đổi không; đôi khi feature pipeline hoặc query thay đổi dù model version giữ nguyên. Em lấy vài case cùng loại ở hai khoảng để chạy lại, xem sai xuất hiện từ preprocessing hay decision. Nếu baseline cập nhật liên tục, em xem nó có bị incident hoặc traffic mới làm lệch không. Em chưa retrain ngay vì có thể retraining học luôn dữ liệu lỗi. Nếu một change có evidence mạnh và impact lớn, em rollback/cố định version trong lúc xác minh. Sau đó em thêm monitor cho change point và cập nhật test để lần sau phát hiện sớm hơn.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách real behavior change khỏi data collection change.
- Xem quality theo cohort/service thay vì aggregate.
- Kiểm tra calendar event hoặc seasonality.

**Red flags:**

- Schedule retrain là đủ để model tự khỏe.
- Không lưu version nên không biết có gì đổi.
- So chart bằng mắt mà không lấy case tái hiện.

**Follow-up khó hơn:**

- Nếu quality chỉ giảm ở giờ cao điểm thì sao?
- Nếu không có label tuần này, em nhận ra regression bằng proxy nào?

### Câu 30 — Incident kéo dài bị học thành normal

**Interviewer hỏi:**

Model bắt đầu coi một incident kéo dài là normal vì baseline đã thích nghi. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Hiểu baseline contamination ở mức thực tế.
- Biết bảo toàn incident state và safe fallback.
- Cách phòng ngừa sau sự cố.

**Mindset tốt nên có:**

- Không cho baseline học mù mọi dữ liệu mới.
- Giữ alert/incident state dựa trên impact và evidence.
- Freeze/exclude window rồi verify recovery trước khi học lại.

**Câu trả lời mẫu:**

Em không coi score quay về normal là bằng chứng service đã hồi phục. Em kiểm tra raw SLO, error, latency và user impact so với known-good reference. Nếu incident vẫn mở, em giữ trạng thái FIRING theo policy hoặc chuyển detector sang degraded mode, đồng thời freeze cập nhật baseline cho signal bị ảnh hưởng. Em xác định baseline đã học từ thời điểm nào, data window nào bị contamination và những service liên quan. Sau khi incident được xử lý, em chỉ cập nhật lại baseline từ một khoảng recovery đã được verify, hoặc khôi phục baseline version trước đó rồi replay. Về phòng ngừa, em đề xuất không học từ cửa sổ đang có incident/change lớn, có giới hạn tốc độ thích nghi và monitor khoảng cách giữa raw SLO với anomaly state. Baseline cần version và audit để rollback. Em báo rõ model đã mất độ nhạy trong khoảng nào để SRE không hiểu dashboard xanh là hệ thống khỏe.

**Điểm cộng nếu ứng viên nói thêm:**

- Có guardrail theo SLO độc lập với adaptive score.
- Dùng incident state để mask training window.
- Kiểm tra fault thứ hai có bị incident đầu che không.

**Red flags:**

- Đóng incident vì score đã bình thường.
- Xóa toàn bộ lịch sử và train lại.
- Cho baseline thích nghi nhanh hơn để “theo kịp”.

**Follow-up khó hơn:**

- Nếu traffic thật sự đổi dài hạn sau một product launch thì khi nào cho baseline học?
- Nếu không có baseline version cũ thì khôi phục bằng cách nào?

### Câu 31 — Service mới chưa có baseline

**Interviewer hỏi:**

Một service mới chưa đủ lịch sử để có baseline. Em monitor anomaly thế nào trong giai đoạn đầu?

**Interviewer đang muốn test gì:**

- Xử lý cold start và uncertainty.
- Biết kết hợp rule, SLO và peer reference thận trọng.
- Rollout theo độ trưởng thành của dữ liệu.

**Mindset tốt nên có:**

- Dùng guardrail đơn giản và expected behavior từ owner.
- Đánh dấu low confidence/insufficient history.
- Thu dữ liệu, review và chuyển dần sang baseline riêng.

**Câu trả lời mẫu:**

Em sẽ không giả vờ baseline của service mới đáng tin. Em hỏi Dev/SRE về SLO, capacity expectation, traffic rollout, dependency và các failure mode quan trọng. Ban đầu em dùng rule an toàn, health check, error budget hoặc synthetic journey; nếu có service tương tự thì dùng làm reference tạm nhưng ghi rõ khác biệt. Detector output cần kèm tuổi baseline, sample count và confidence thấp, có thể chỉ vào dashboard hoặc ticket thay vì page. Em loại các khoảng load test, deploy hoặc ramp-up đã biết khỏi dữ liệu học nếu chúng không đại diện vận hành bình thường. Khi traffic đủ, em review score/alert với owner theo từng tuần và chuyển dần sang baseline theo chính service, có version và mốc kích hoạt. Nếu service tier cao, em ưu tiên tín hiệu trực tiếp về user impact hơn model thích nghi. Mục tiêu cold start là coverage an toàn và học feedback, không phải ngay lập tức có detector tối ưu.

**Điểm cộng nếu ứng viên nói thêm:**

- Có minimum sample/traffic gate.
- Tách launch pattern khỏi incident.
- Đặt ngày review lại các rule tạm.

**Red flags:**

- Copy threshold của payment sang mọi service.
- Không monitor cho tới khi đủ 30 ngày dữ liệu.
- Page theo score chưa có đủ sample.

**Follow-up khó hơn:**

- Nếu service launch đúng dịp traffic cao nhất năm thì sao?
- Peer service khác stack và traffic, reference còn dùng thế nào?

### Câu 32 — Tốt với payment, tệ với search

**Interviewer hỏi:**

Một model tốt với payment nhưng tệ với search. Em xử lý ra sao?

**Interviewer đang muốn test gì:**

- Nhìn nhận hành vi đặc thù từng service.
- Tránh ép một model cho mọi nơi.
- Cách phối hợp domain owner và phân tích cohort.

**Mindset tốt nên có:**

- So semantics, traffic, seasonality, SLO và data quality.
- Tách config/model/baseline theo service khi có evidence.
- Giữ baseline tốt cho payment, canary thay đổi ở search.

**Câu trả lời mẫu:**

Em không kết luận model hỏng toàn bộ. Em tách kết quả theo service và lấy các case search báo sai/bỏ lỡ để hiểu khác biệt. Search có thể có traffic burst, query mix và latency distribution khác payment; metric cùng tên chưa chắc cùng ý nghĩa. Em kiểm tra coverage, sample, baseline, threshold, label và feature có đại diện search không, rồi trao đổi Dev/SRE của search về pattern expected như campaign hoặc indexing job. Em so model chung với một rule hoặc baseline riêng cho search. Nếu evidence cho thấy hành vi thật sự khác, em đề xuất service-specific config/threshold hoặc model riêng ở mức cần thiết, thay vì làm payment xấu đi để tối ưu trung bình. Thay đổi được chạy shadow/canary chỉ trên search, replay cả known-good và incident. Em báo metric theo từng cohort để aggregate không che vấn đề và ghi rõ phạm vi model hỗ trợ.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra label imbalance giữa hai service.
- Có default/fallback cho service chưa đủ dữ liệu.
- Tránh tạo quá nhiều model không thể vận hành.

**Red flags:**

- Tune một threshold toàn cục đến khi trung bình đẹp.
- Nói search team cung cấp data xấu nên không phải việc mình.
- Train model riêng ngay mà chưa phân tích semantics.

**Follow-up khó hơn:**

- Khi nào số model riêng trở thành gánh nặng vận hành?
- Nếu Product bắt buộc một trải nghiệm alert thống nhất thì sao?

### Câu 33 — Một threshold cho mọi service

**Interviewer hỏi:**

Một threshold dùng cho mọi service đang gây nhiều false alert. Em thay đổi thế nào?

**Interviewer đang muốn test gì:**

- Tư duy segmentation và controlled tuning.
- Không chữa noise bằng threshold toàn cục.
- Biết đo trước/sau và tránh bỏ fault thật.

**Mindset tốt nên có:**

- Phân loại alert theo service tier, metric và traffic.
- Tìm pattern, đề xuất ít nhóm dễ quản lý.
- Replay, canary và monitor false negative.

**Câu trả lời mẫu:**

Em lấy alert history và feedback để xem noise tập trung ở service, metric, traffic hay khung giờ nào. Em kiểm tra trước data quality, baseline và query vì threshold không sửa được input sai. Nếu hành vi khác nhau thật, em không tạo ngay hàng trăm threshold thủ công; em đề xuất vài nhóm có lý do rõ như service critical/high traffic, batch/periodic và low traffic, hoặc threshold theo baseline của từng signal. Em replay các candidate trên incident đã biết và known-good period, báo cả alert giảm lẫn case có nguy cơ bỏ lỡ. Sau đó canary cho một nhóm service, giữ rollback và theo dõi vài chu kỳ. Alert policy cũng có thể thêm persistence hoặc customer impact thay vì làm detector kém nhạy. Em document owner, lý do và review date cho config để tránh threshold thành con số bí mật không ai hiểu.

**Điểm cộng nếu ứng viên nói thêm:**

- Có minimum volume và hysteresis nếu phù hợp.
- Tách score threshold khỏi page threshold.
- Theo dõi config drift và override hết hạn.

**Red flags:**

- Tăng tất cả từ 0,8 lên 0,99.
- Tune theo một ngày noise duy nhất.
- Không replay incident bị bỏ lỡ.

**Follow-up khó hơn:**

- Nếu mỗi team đòi threshold riêng thì governance thế nào?
- Nếu giảm noise 80% nhưng bỏ lỡ một P1 thì em đánh giá ra sao?

### Câu 34 — Route ít traffic bị che ở service-level

**Interviewer hỏi:**

Một route ít traffic có anomaly nhưng metric toàn service vẫn bình thường. Em làm gì?

**Interviewer đang muốn test gì:**

- Hiểu aggregation có thể che lỗi cục bộ.
- Cân bằng visibility với cardinality/noise.
- Nhìn customer/tenant impact, không chỉ volume.

**Mindset tốt nên có:**

- Xác minh route, sample và mức quan trọng.
- Drill down theo dimension có kiểm soát.
- Dùng minimum volume, SLO hoặc synthetic evidence.

**Câu trả lời mẫu:**

Em xác nhận complaint hoặc trace có đúng route, tenant và khoảng thời gian đó không, rồi xem raw count để tránh kết luận từ một vài request ngẫu nhiên. Nếu route quan trọng dù ít traffic, service-level average không phải signal đủ. Em đề xuất theo dõi theo route hoặc nhóm journey quan trọng, nhưng kiểm soát cardinality bằng allowlist, template route và minimum sample. Với volume rất thấp, tỷ lệ lỗi dễ dao động nên em kết hợp absolute error count, synthetic check, trace/log và customer impact thay vì chỉ threshold phần trăm. Detector output cần ghi scope để on-call biết anomaly chỉ ở route nào. Em replay một case và known-good low-traffic period để tune, sau đó canary alert cho owner route. Em cũng giữ service-level view để thấy blast radius. Mục tiêu là không để aggregate che khách hàng quan trọng nhưng cũng không biến mỗi path thành một alert noisy.

**Điểm cộng nếu ứng viên nói thêm:**

- Dùng route template thay raw URL.
- Xét tenant tier/business impact trong routing.
- Theo dõi telemetry coverage của route.

**Red flags:**

- Bỏ qua vì chỉ ảnh hưởng 0,1% traffic.
- Thêm mọi URL làm label.
- Page từ một request lỗi duy nhất không có context.

**Follow-up khó hơn:**

- Nếu route ít traffic thuộc khách hàng lớn nhất thì policy thay đổi sao?
- Nếu không được thêm label route, em tìm evidence bằng cách nào?

### Câu 35 — Latency và CPU cùng tăng

**Interviewer hỏi:**

Latency tăng và CPU tăng cùng lúc. Em có kết luận CPU là root cause không?

**Interviewer đang muốn test gì:**

- Phân biệt correlation và causation.
- Biết dùng timeline, saturation, traffic và dependency.
- Cách hình thành/test hypothesis.

**Mindset tốt nên có:**

- Chưa vội kết luận; xem thứ tự và cơ chế hợp lý.
- Kiểm tra traffic, deploy, queue, GC, downstream và trace.
- Thử hành động nhỏ hoặc so cohort để xác minh.

**Câu trả lời mẫu:**

Em coi CPU là một hypothesis chứ chưa phải root cause. Cả CPU và latency có thể cùng là hậu quả của traffic spike, retry storm hoặc deploy mới. Em xem timeline chi tiết: tín hiệu nào đổi trước, CPU có thật sự chạm saturation/throttling không và latency nằm ở service hay downstream span. Em đối chiếu request rate, error, queue, pod count, GC, deployment và trace. Nếu chỉ một pod CPU cao và chậm trong khi pod khác bình thường, comparison đó tăng evidence; nếu latency dành chủ yếu ở database thì CPU ứng dụng có thể là symptom. Trong incident em ưu tiên action có blast radius nhỏ và đã có runbook, đồng thời quan sát SLO sau action. Em báo “CPU tương quan với latency, đang kiểm tra saturation và trace; chưa đủ evidence gọi là root cause”. Kết luận cần giải thích được cơ chế và sự phục hồi, không chỉ hai đường graph cùng đỏ.

**Điểm cộng nếu ứng viên nói thêm:**

- Xem throttling thay vì chỉ CPU utilization.
- So trước/sau traffic normalized.
- Tìm counter-evidence có thể bác hypothesis.

**Red flags:**

- Scale pod ngay vì CPU cao.
- Gọi metric xuất hiện cùng lúc là root cause.
- Chỉ nhìn một dashboard service.

**Follow-up khó hơn:**

- CPU tăng trước latency hai phút có đủ chứng minh không?
- Scale xong latency giảm thì đã chứng minh CPU root cause chưa?

### Câu 36 — RCA nói database nhưng trace không support

**Interviewer hỏi:**

RCA engine nói database là root cause nhưng trace không support. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Cách xử lý evidence mâu thuẫn.
- Không tin confidence/ranking mù quáng.
- Biết kiểm tra telemetry coverage trước khi bác bỏ.

**Mindset tốt nên có:**

- Xem trace coverage/sampling và bằng chứng RCA dùng.
- So timeline, dependency, DB metrics/logs và counter-evidence.
- Hạ confidence hoặc giữ nhiều hypothesis.

**Câu trả lời mẫu:**

Em chưa chấp nhận database là root cause chỉ vì đứng hạng một, nhưng cũng chưa loại bỏ ngay vì trace có thể bị sampling hoặc thiếu instrumentation. Em mở explanation của RCA: candidate dựa trên metric, log, topology hay change nào, timestamp có khớp và confidence được hiểu ra sao. Em kiểm tra trace coverage của request lỗi, child span tới database có tồn tại và latency nằm ở đâu. Em đối chiếu DB connection, query latency, error log và dependency khác. Nếu trace đủ tốt và liên tục chỉ về dependency khác, đó là counter-evidence mạnh; em hạ rank database, giữ hypothesis khác và báo SRE phần mâu thuẫn. Nếu trace thiếu, em nói rõ “không support” chưa đồng nghĩa “bác bỏ”. Sau incident em lưu case để replay RCA, sửa evidence weighting hoặc instrumentation. Mọi action lên database cần thêm xác nhận vì blast radius cao.

**Điểm cộng nếu ứng viên nói thêm:**

- Ghi evidence_for và evidence_against cho từng candidate.
- Kiểm tra service map/version và clock skew.
- Không ép hệ thống luôn có đúng một root cause.

**Red flags:**

- Model score cao nên bỏ qua trace.
- Trace không thấy nghĩa là database chắc chắn khỏe.
- Restart database để test hypothesis.

**Follow-up khó hơn:**

- Nếu trace chỉ sample 1% request thì em tăng độ tin cậy bằng gì?
- Nếu DB metric đỏ nhưng query latency bình thường thì sao?

### Câu 37 — AI-generated RCA có citation sai

**Interviewer hỏi:**

AI-generated RCA nghe rất hợp lý nhưng citation hoặc evidence nó dẫn ra lại sai. Em làm gì?

**Interviewer đang muốn test gì:**

- Không bị thuyết phục bởi văn phong tự tin của LLM.
- Cách validate claim-evidence.
- Safety khi output có thể dẫn tới action.

**Mindset tốt nên có:**

- Tách từng claim và mở nguồn gốc evidence.
- Gắn trạng thái unsupported, không sửa cho “có vẻ đúng”.
- Chặn auto-action, lưu case và cải thiện retrieval/prompt/test.

**Câu trả lời mẫu:**

Em coi explanation đó là không đáng tin cho tới khi từng claim quan trọng được đối chiếu. Em mở citation gốc, kiểm tra đúng service, environment, thời gian, query và nội dung có thực sự support câu nói không. Em tách fact như “error rate tăng lúc 10:05” khỏi inference như “deploy gây database overload”. Nếu citation sai, em đánh dấu output unsupported, báo cho SRE không dùng nó làm căn cứ auto-action và chuyển sang evidence dashboard/timeline thật. Em lưu prompt, model version, retrieved documents và run_id để tái hiện. Sau incident, em tạo regression test cho kiểu citation sai, kiểm tra retrieval filter, quyền truy cập, timestamp và yêu cầu hệ thống trả “không đủ evidence” khi nguồn không support. Em không chỉ viết lại câu văn cho hợp lý, vì lỗi cốt lõi là provenance. LLM có thể giúp tóm tắt nhưng authority vẫn là evidence được kiểm chứng và người chịu trách nhiệm quyết định.

**Điểm cộng nếu ứng viên nói thêm:**

- Hiển thị đoạn evidence và thời gian ngay cạnh claim.
- Có rule không citation thì không được thành RCA fact.
- Thu feedback “supported/unsupported” theo claim.

**Red flags:**

- Giữ RCA vì nội dung nghe đúng với kinh nghiệm.
- Thay citation thủ công nhưng không lưu lỗi.
- Cho LLM đề xuất action production từ claim chưa support.

**Follow-up khó hơn:**

- Nếu kết luận cuối cùng tình cờ đúng nhưng citation sai, em đánh giá output thế nào?
- Làm sao test hallucination mà không cần hàng nghìn incident?

### Câu 38 — Logs nói database, traces nói dependency khác

**Interviewer hỏi:**

Logs có nhiều dòng database error nhưng traces cho thấy một dependency khác chậm. Em tin cái nào?

**Interviewer đang muốn test gì:**

- Khả năng tổng hợp telemetry thay vì chọn phe.
- Kiểm tra scope, coverage, timeline và propagation.
- Biết logs có thể là symptom hoặc retry noise.

**Mindset tốt nên có:**

- Xác minh cùng request/service/time và chất lượng nguồn.
- Xây timeline, xem lỗi đầu tiên và causal path.
- Giữ nhiều hypothesis cho tới khi test được.

**Câu trả lời mẫu:**

Em không mặc định log hay trace luôn đáng tin hơn. Em kiểm tra chúng có nói về cùng request, route, pod và khoảng thời gian không; timestamp có lệch và trace sampling có bỏ phần lỗi không. Em dùng trace_id/correlation_id để nối case cụ thể. Database error có thể là hậu quả request timeout hoặc retry sau khi dependency kia chậm, nhưng cũng có thể trace chưa instrument đoạn DB. Em dựng timeline: dependency nào bắt đầu chậm trước, error xuất hiện ở đâu, request time dành tại span nào và các metric saturation nói gì. Em tìm counter-evidence như request không gọi dependency kia vẫn lỗi hay DB error đã xuất hiện trước. Nếu chưa đủ, em báo hai hypothesis cùng evidence_for/evidence_against và ưu tiên kiểm tra an toàn nhất. Sau khi xác định, em bổ sung instrumentation hoặc log field thiếu. Mục tiêu không phải chọn một nguồn thắng mà là tạo câu chuyện giải thích được propagation.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra log severity có bị lạm dụng.
- Xem clock sync và retry amplification.
- Nêu coverage/quality cạnh mỗi nguồn evidence.

**Red flags:**

- Log có chữ error nên database chắc chắn là root cause.
- Trace đẹp hơn nên bỏ toàn bộ log.
- Đếm số dòng lỗi để chọn nguyên nhân.

**Follow-up khó hơn:**

- Nếu không có correlation_id thì em thu hẹp ra sao?
- Nếu hai fault độc lập xảy ra cùng lúc thì hệ thống nên trình bày thế nào?

### Câu 39 — Incident xuất hiện sau deployment

**Interviewer hỏi:**

Incident xuất hiện ngay sau một deployment. Em có rollback luôn không?

**Interviewer đang muốn test gì:**

- Dùng change event mà không nhầm correlation với causation.
- Quyết định theo impact, reversibility và evidence.
- Biết rollback cũng có rủi ro.

**Mindset tốt nên có:**

- Xác nhận timeline, scope, canary và error signature.
- So old/new cohort, xem dependency và concurrent changes.
- Theo runbook/approval, verify outcome sau rollback.

**Câu trả lời mẫu:**

Deployment là hypothesis mạnh vì timing gần, nhưng em vẫn kiểm tra nó có chạm đúng service, region hoặc route đang lỗi không. Em xem canary so với instance cũ, error signature, config/feature flag và có change nào khác cùng lúc. Nếu impact lớn, rollback đã được chuẩn bị, blast radius thấp và evidence old version khỏe hơn, em sẽ đề xuất rollback sớm theo runbook thay vì chờ chứng minh tuyệt đối. Nhưng em không tự ý rollback một hệ thống không thuộc quyền của mình; em cung cấp evidence cho incident commander/owner và giữ snapshot log, trace, version trước khi đổi. Sau rollback, command SUCCESS chưa đủ: em verify SLO, error, traffic và customer journey thực sự hồi phục. Nếu không cải thiện, em phục hồi hypothesis list và tránh lặp rollback vô ích. Kết luận post-incident dựa trên replay/timeline, không chỉ “sau deploy nên do deploy”.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân biệt rollback application, config và feature flag.
- Có điều kiện abort nếu rollback làm tình hình xấu hơn.
- Lưu change id trong incident timeline.

**Red flags:**

- Mọi incident sau deploy đều rollback.
- Không giữ evidence trước khi thay đổi state.
- Rollback xong đóng incident vì command thành công.

**Follow-up khó hơn:**

- Nếu database migration không backward-compatible thì sao?
- Nếu rollback giảm lỗi 30% nhưng chưa phục hồi hoàn toàn thì kết luận gì?

### Câu 40 — Dashboard xanh, complaint tăng

**Interviewer hỏi:**

Dashboard trông bình thường nhưng số complaint của customer tăng. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Ưu tiên customer evidence hơn dashboard self-confidence.
- Tìm blind spot về scope/aggregation/coverage.
- Kỹ năng phối hợp Support, Product và SRE.

**Mindset tốt nên có:**

- Lấy mẫu complaint có thời gian, journey, tenant/region.
- Kiểm tra dashboard query, SLI coverage và telemetry gap.
- Tạo/đề xuất signal sát outcome hơn.

**Câu trả lời mẫu:**

Em coi complaint tăng là một tín hiệu production, không dùng dashboard xanh để bác bỏ. Em phối hợp Support/Product lấy mẫu có timestamp, tenant, region, phiên bản app và user journey; tránh chỉ nhìn tổng số ticket. Em thử tái hiện hoặc theo một request qua gateway, log và trace. Sau đó em kiểm tra dashboard có aggregate che route/tenant nhỏ, query sai environment, sampling bỏ lỗi hoặc chỉ đo server health trong khi client/DNS/payment partner lỗi không. Em so complaint timeline với deploy, feature flag và dependency. Nếu incident đang diễn ra, em báo SRE bằng evidence cụ thể và ưu tiên giảm impact. Sau đó em thêm SLI hoặc synthetic check gần customer journey, cập nhật detector coverage và tạo regression case. Em nói với customer phần đã xác nhận và phần đang kiểm tra, không hứa “monitoring cho thấy mọi thứ bình thường”. Dashboard là một góc nhìn; outcome người dùng mới là điều cần giải thích.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra support-ticket taxonomy có đổi không.
- Theo dõi client-side hoặc external dependency nếu phù hợp.
- Đo telemetry blind spot như một risk riêng.

**Red flags:**

- Nói customer dùng sai vì metric xanh.
- Thêm nhiều panel hạ tầng nhưng không có journey.
- Kết luận outage từ ticket count mà không sample.

**Follow-up khó hơn:**

- Nếu complaint tăng do một thay đổi UI chứ backend không lỗi thì AIOps hỗ trợ gì?
- Nếu customer không cung cấp timestamp thì em thu hẹp thế nào?

### Câu 41 — SRE phàn nàn model spam alert

**Interviewer hỏi:**

On-call nói model của team em spam alert: 100 alert/ngày nhưng chỉ khoảng 5 cái hữu ích. Em làm gì?

**Interviewer đang muốn test gì:**

- Lắng nghe user nội bộ và ownership.
- Cách đo, phân loại và giảm alert fatigue.
- Tránh suppression nguy hiểm.

**Mindset tốt nên có:**

- Acknowledge impact, lấy feedback theo reason code.
- Tìm source: data, detector, threshold, dedup, routing.
- Tune/replay/canary và theo dõi incident bị bỏ lỡ.

**Câu trả lời mẫu:**

Em thừa nhận 100 alert vô ích làm hỏng niềm tin, rồi xin SRE cùng review một sample thay vì tranh luận về model score. Em phân loại noise: duplicate cùng incident, transient spike, expected deploy, low traffic, stale data hay alert không có customer impact. Em kiểm tra từ input và baseline đến persistence, dedup, suppression và routing; có thể detector đúng nhưng page policy sai. Em đề xuất quick mitigation an toàn như group duplicate hoặc chuyển một loại alert xuống ticket, không suppress toàn bộ. Với thay đổi threshold/persistence, em replay lịch sử gồm cả incident thật, canary theo service và đặt rollback nếu false negative tăng. Em bổ sung feedback reason vào alert record và dashboard alert usefulness. Em cập nhật SRE về cái đã sửa, cái còn mở và ngày review. Success không chỉ là alert count giảm; những sự cố quan trọng vẫn phải được bắt đúng hạn và on-call phải hiểu evidence.

**Điểm cộng nếu ứng viên nói thêm:**

- Đo alerts per actionable incident và acknowledgment behavior.
- Có budget/review owner cho noisy rule.
- Tách informational anomaly khỏi paging alert.

**Red flags:**

- Nói SRE chưa hiểu AI.
- Tăng threshold mọi nơi cho hết phàn nàn.
- Chỉ tối ưu số alert thấp mà không đo miss.

**Follow-up khó hơn:**

- Nếu 5 alert hữu ích đều là P1 thì em giảm noise mà giữ chúng thế nào?
- SRE không có thời gian label 100 alert, em sampling ra sao?

### Câu 42 — Customer đòi 100% accuracy

**Interviewer hỏi:**

Customer yêu cầu hệ thống phát hiện anomaly chính xác 100%. Em trả lời thế nào?

**Interviewer đang muốn test gì:**

- Quản lý expectation và dịch technical thành impact.
- Không hứa điều không khả thi.
- Khả năng chuyển yêu cầu tuyệt đối thành target đo được.

**Mindset tốt nên có:**

- Hỏi loại lỗi quan trọng và cost của miss/noise.
- Giải thích coverage, ground truth và trade-off bằng ví dụ.
- Đề xuất SLO, guardrail, pilot và review.

**Câu trả lời mẫu:**

Em sẽ không hứa 100%, nhưng cũng không chỉ nói “không thể”. Em hỏi customer đang lo nhất việc bỏ lỡ incident nào, hay bị alert sai làm tốn người, và action nào sẽ theo sau. Em giải thích ngắn rằng anomaly không phải một đáp án tuyệt đối: hành vi mới hợp lệ có thể trông bất thường, còn lỗi cục bộ có thể không hiện trên metric tổng. Sau đó em đề xuất target đo được theo severity, ví dụ ưu tiên bắt các incident ảnh hưởng checkout trong một thời gian nhất định, giới hạn alert vô ích mỗi ngày và luôn có fallback SLO/rule cho case critical. Em đưa kết quả trên sample/replay kèm denominator và giới hạn, chạy pilot/shadow rồi review với họ. Với auto-action, tiêu chuẩn còn chặt hơn và cần approval/rollback. Mục tiêu thảo luận là reliability và quyết định tốt hơn, không phải một con số marketing không thể kiểm chứng.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân biệt detector coverage với toàn bộ hệ thống.
- Đưa option A/B cùng chi phí và trade-off.
- Có escalation khi model uncertain.

**Red flags:**

- Hứa 100% để giữ customer vui.
- Nói customer không hiểu ML.
- Đưa accuracy offline làm bảo đảm production.

**Follow-up khó hơn:**

- Nếu hợp đồng đã ghi “không bỏ lỡ incident” thì em báo rủi ro thế nào?
- Customer hỏi đối thủ quảng cáo 99,99%, em phản hồi sao?

### Câu 43 — Vừa alert cực nhanh vừa không false positive

**Interviewer hỏi:**

Customer muốn alert nhanh hơn rất nhiều nhưng cũng không muốn false positive. Em trade-off thế nào?

**Interviewer đang muốn test gì:**

- Giải thích latency-quality trade-off.
- Thiết kế nhiều mức phản ứng thay vì chọn một cực.
- Gắn quyết định với impact và user workflow.

**Mindset tốt nên có:**

- Làm rõ “nhanh” và “false positive” theo severity.
- Có early signal nhẹ, confirmation và page/action gate.
- Pilot, đo và cùng stakeholder chọn operating point.

**Câu trả lời mẫu:**

Em hỏi “nhanh” là bao nhiêu phút và alert đó dùng để nhìn dashboard, page người hay tự chạy action. Phát hiện từ một điểm dữ liệu sẽ nhanh nhưng dễ nhiễu; chờ persistence và thêm evidence sẽ chậm hơn nhưng đáng tin hơn. Em đề xuất hai tầng: early warning xuất hiện sớm với nhãn confidence thấp, không page; nếu tín hiệu kéo dài hoặc có SLO/error/trace support thì nâng thành actionable alert. Service critical có thể dùng synthetic/SLO rule độc lập để không phụ thuộc hoàn toàn vào model. Em replay nhiều threshold/window trên incident và known-good periods, báo số case bắt sớm hơn cùng số alert tăng, rồi để Product/SRE chọn trade-off theo cost. Em canary và theo dõi detection delay, false alert, missed incident. Em không hứa đồng thời tối ưu tuyệt đối cả hai; em biến trade-off thành lựa chọn có số liệu và guardrail.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân tầng severity và routing.
- Có hysteresis/dedup để giảm flapping.
- Đo time-to-useful-alert thay vì time-to-first-score.

**Red flags:**

- Nói chỉ cần model tốt hơn là có cả hai.
- Giảm window toàn bộ service mà không replay.
- Che trade-off khỏi customer.

**Follow-up khó hơn:**

- Nếu customer chỉ chấp nhận một loại alert thì chọn operating point ra sao?
- Em chứng minh alert nhanh hơn thực sự giảm impact bằng gì?

### Câu 44 — Customer không hiểu anomaly score

**Interviewer hỏi:**

Customer nói họ không quan tâm anomaly score, họ chỉ muốn biết service nào có vấn đề và cần làm gì. Em thay đổi output thế nào?

**Interviewer đang muốn test gì:**

- Khả năng thiết kế từ nhu cầu quyết định.
- Dịch output model thành evidence hữu ích.
- Không che uncertainty hoặc bịa action.

**Mindset tốt nên có:**

- Hỏi customer cần quyết định gì và trong bao lâu.
- Hiển thị impact, scope, evidence, confidence và owner/action.
- Giữ score ở drill-down/audit, không làm nội dung chính.

**Câu trả lời mẫu:**

Em đồng ý rằng score là chi tiết nội bộ nếu nó không giúp customer quyết định. Em hỏi họ thường cần biết: user journey nào ảnh hưởng, service/region nào, bắt đầu lúc nào, mức độ ra sao và ai đang xử lý. Output chính có thể là “checkout ở region A đang chậm, ảnh hưởng khoảng 18% request; payment là candidate cần kiểm tra, evidence gồm latency và trace; chưa tự động action”. Em đưa next safe step hoặc link runbook nếu đã được owner xác nhận. Anomaly score, model version và feature chi tiết vẫn giữ ở phần drill-down để engineer debug và audit, nhưng không biến 0,95 thành “95% chắc chắn root cause”. Em thử format với vài incident và xin customer/on-call feedback xem họ quyết định nhanh hơn không. Nếu chưa đủ evidence cho service/action, em nói rõ “đang điều tra” thay vì tạo câu trả lời chắc chắn cho đẹp dashboard.

**Điểm cộng nếu ứng viên nói thêm:**

- Có timestamp/freshness và status update.
- Phân biệt fact, hypothesis và recommendation bằng UI.
- Đo click/usefulness hoặc time-to-triage.

**Red flags:**

- Bảo customer phải học score.
- Ẩn mọi uncertainty để output dễ đọc.
- Đề xuất action chung chung không có owner/runbook.

**Follow-up khó hơn:**

- Nếu customer vẫn yêu cầu một đèn xanh/đỏ duy nhất thì sao?
- Em hiển thị hai root-cause candidate gần điểm nhau thế nào?

### Câu 45 — Dev không muốn thêm instrumentation

**Interviewer hỏi:**

Em thiếu trace/log field để validate RCA, nhưng Dev không muốn thêm instrumentation vì lo tốn hiệu năng. Em phối hợp thế nào?

**Interviewer đang muốn test gì:**

- Tôn trọng concern của team khác.
- Khả năng đưa request cụ thể, có evidence và trade-off.
- Không tự ý sửa hệ thống team khác.

**Mindset tốt nên có:**

- Nói rõ decision đang bị chặn và evidence thiếu.
- Đề xuất thay đổi nhỏ, sampling/canary và đo overhead.
- Có alternative, owner và review sau thử nghiệm.

**Câu trả lời mẫu:**

Em không nói “AIOps cần nên Dev phải làm”. Em đưa một incident cụ thể cho thấy thiếu field nào khiến không phân biệt được hai hypothesis và hậu quả là mất bao lâu điều tra. Em hỏi concern chính là CPU, chi phí lưu trữ, dữ liệu nhạy cảm hay workload của team. Sau đó em đề xuất thay đổi nhỏ nhất: thêm correlation_id hoặc span cho một critical path, sampling có kiểm soát, bật ở staging/canary và đo latency, CPU, volume trước/sau. Em cùng Dev thống nhất schema, không log payload nhạy cảm, retention và cách tắt nhanh. Nếu chưa thể thay code, em tìm evidence thay thế từ gateway, existing metrics hoặc synthetic test và ghi rõ RCA confidence bị giới hạn. Em nhờ SRE/Product giúp ưu tiên dựa trên incident impact, không escalates để đổ lỗi. Sau thử nghiệm, em chia sẻ kết quả overhead và giá trị điều tra để hai team quyết định rollout.

**Điểm cộng nếu ứng viên nói thêm:**

- Đưa acceptance criteria cho instrumentation.
- Có observability budget và owner.
- Dọn field không còn giá trị sau review.

**Red flags:**

- Tự merge agent/logging vào service của Dev.
- Nói Dev không hợp tác.
- Yêu cầu “thêm log chi tiết” không chỉ rõ câu hỏi cần trả lời.

**Follow-up khó hơn:**

- Nếu service quá nhạy cảm không được log ID thì correlation thế nào?
- Nếu overhead nhỏ nhưng Dev vẫn không có capacity trước deadline thì sao?

### Câu 46 — Data Engineer đổi schema

**Interviewer hỏi:**

Data Engineer thay schema khiến feature pipeline lỗi hoặc tệ hơn là vẫn chạy nhưng tính sai. Em xử lý và phối hợp ra sao?

**Interviewer đang muốn test gì:**

- Incident ownership xuyên team.
- Data contract, validation và backward compatibility.
- Không biến sự cố thành blame game.

**Mindset tốt nên có:**

- Xác định version/timeline/scope và dừng output không đáng tin.
- Phối hợp rollback/adapter theo blast radius.
- Thêm contract test, version và change notification.

**Câu trả lời mẫu:**

Em xác định schema nào đổi, từ thời điểm nào, consumer/service nào bị ảnh hưởng và pipeline fail rõ hay silent wrong. Em lấy sample trước/sau, kiểm tra field name, type, unit, null và mapping feature. Nếu output AIOps không còn đáng tin, em đánh dấu degraded, chặn deploy/action hoặc fallback về version input cũ theo policy. Em liên hệ Data Engineer bằng evidence cụ thể và hỏi change intent, khả năng rollback hoặc cung cấp song song hai version; không chỉ gửi ảnh lỗi rồi đổ trách nhiệm. Team cùng chọn adapter ở consumer hay producer dựa trên owner và blast radius. Sau khi sửa, em replay dữ liệu qua từng stage, so expected feature/model output và theo dõi backlog/backfill. Về phòng ngừa, em đề xuất schema version, compatibility window, contract test bằng sample thực và thông báo change trước. Em ghi incident timeline cùng phần AIOps affected để downstream hiểu khoảng output nào cần xem lại.

**Điểm cộng nếu ứng viên nói thêm:**

- Có quarantine/dead-letter cho record không hợp lệ.
- Kiểm tra late/backfill không tạo duplicate alert.
- Gắn schema version vào detector run.

**Red flags:**

- Sửa ép kiểu để pipeline xanh mà không hiểu semantics.
- Chờ team Data tự phát hiện.
- Train lại model trên schema mới ngay.

**Follow-up khó hơn:**

- Nếu không thể rollback producer vì consumer khác đã dùng schema mới thì sao?
- Làm sao phát hiện unit đổi nhưng type vẫn giống?

### Câu 47 — Bị team khác block trước deadline

**Interviewer hỏi:**

Task của em bị blocked bởi một team khác và deadline đang đến gần. Em làm gì?

**Interviewer đang muốn test gì:**

- Báo blocker sớm và quản lý dependency.
- Ownership không đồng nghĩa tự ý sửa hệ thống khác.
- Khả năng đưa option/MVP.

**Mindset tốt nên có:**

- Gửi request cụ thể, impact, deadline và owner.
- Tiếp tục phần không phụ thuộc, dùng mock/sample nếu an toàn.
- Báo status, risk, option A/B và revised ETA.

**Câu trả lời mẫu:**

Em kiểm tra blocker có thật sự cần cho MVP hay có thể tách nhỏ. Em gửi team kia yêu cầu cụ thể: cần field/data/quyền gì, format mong đợi, vì sao nó chặn validation và mốc cần, kèm sample để họ trả lời nhanh. Trong lúc chờ, em làm phần độc lập như contract test, pipeline với mock data hoặc dashboard skeleton, nhưng ghi rõ mock không chứng minh production. Em báo mentor sớm theo format: đã xong gì, blocker từ lúc nào, impact tới scope/ETA, những gì đã thử và cần ai hỗ trợ. Em đưa lựa chọn, ví dụ A giữ deadline nhưng demo với historical data; B lùi hai ngày để validate live input, cùng recommendation của em. Nếu cần escalation, em theo kênh và nhờ owner ưu tiên, không blame cá nhân. Khi dependency đến, em vẫn validate schema/freshness trước khi coi task unblocked.

**Điểm cộng nếu ứng viên nói thêm:**

- Có dependency milestone ngay từ đầu.
- Lưu quyết định/assumption để tránh hiểu khác nhau.
- Không dùng dữ liệu giả để báo kết quả thật.

**Red flags:**

- Im lặng chờ rồi trễ deadline.
- Tự truy cập/sửa data pipeline team khác.
- Chỉ nói “team Data chậm”.

**Follow-up khó hơn:**

- Nếu team kia không phản hồi sau hai lần nhắc thì em làm gì?
- Nếu manager muốn giữ deadline bằng cách bỏ validation thì sao?

### Câu 48 — Còn hai ngày, mới xong 60%

**Interviewer hỏi:**

Còn hai ngày nhưng task chỉ hoàn thành khoảng 60%. Em báo cáo và ưu tiên thế nào?

**Interviewer đang muốn test gì:**

- Deadline management và honest status.
- Phân biệt critical path với nice-to-have.
- Khả năng đề xuất scope/option cụ thể.

**Mindset tốt nên có:**

- Báo sớm done/not-done/blocker/risk.
- Ưu tiên vertical slice có thể validate.
- Chốt option, recommendation và ETA mới.

**Câu trả lời mẫu:**

Em không dùng “60%” đứng một mình vì nó khó kiểm chứng. Em liệt kê phần đã chạy và đã validate, phần chỉ mới code, phần chưa làm và critical path còn lại. Em đánh giá rủi ro: ví dụ detector đã chạy historical data nhưng chưa có freshness check và chưa shadow production, nên chưa thể gọi production-ready. Em báo mentor ngay, đưa hai lựa chọn: giữ deadline với MVP chỉ detection + evidence, bỏ auto-remediation và ghi rõ giới hạn; hoặc lùi mốc để thêm safety/production validation. Em đề xuất lựa chọn dựa trên mục tiêu business, không chỉ cố nhét tất cả. Hai ngày cuối em ưu tiên luồng end-to-end, test case quan trọng, rollback/fallback và tài liệu handoff; các UI đẹp hoặc optimization để sau. Em cập nhật theo mốc ngắn mỗi ngày. Nếu ETA còn uncertainty, em nêu điều kiện làm ETA thay đổi thay vì hứa chắc rồi trễ tiếp.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách “implemented” khỏi “verified”.
- Có demo sớm của vertical slice.
- Nêu debt/risk được chấp nhận bởi ai.

**Red flags:**

- Nói sẽ cố làm hết mà không đổi scope.
- Che phần chưa test trong phần “done”.
- Bỏ rollback/monitoring để kịp deadline nhưng không báo.

**Follow-up khó hơn:**

- Nếu bắt buộc go-live đúng ngày thì safe minimum là gì?
- Nếu 40% còn lại chính là data validation thì em có gọi MVP không?

### Câu 49 — Thử nhiều hướng đều fail

**Interviewer hỏi:**

Em đã thử ba hướng nhưng đều không giải quyết được vấn đề. Em report thế nào?

**Interviewer đang muốn test gì:**

- Biến thất bại thành evidence.
- Biết khi nào cần xin help.
- Báo cáo không vòng vo hoặc giấu lỗi.

**Mindset tốt nên có:**

- Nêu hypothesis, test, result và điều đã loại trừ.
- Trình bày blocker/unknown và next best tests.
- Hỏi mentor một quyết định/câu hỏi cụ thể.

**Câu trả lời mẫu:**

Em sẽ không chỉ nói “em thử nhiều cách mà chưa được”. Em báo mục tiêu và symptom có thể tái hiện, rồi tóm tắt từng hướng: hypothesis gì, em thay gì, evidence/result ra sao và nó giúp loại trừ điều gì. Ví dụ em đã kiểm tra threshold, missing data và model version; cả ba không giải thích được false positive vì cùng input old/new cho score giống nhau. Phần chưa biết còn nằm ở feature window hoặc label. Em gửi link log/run_id và giữ environment để mentor có thể xem lại, tránh làm lại từ đầu. Em đề xuất hai bước tiếp theo được ưu tiên theo chi phí, đồng thời hỏi cụ thể “anh/chị có thể review cách feature window được tạo không?” Nếu deadline rủi ro, em báo ngay cùng fallback hoặc scope giảm. Thử thất bại có giá trị nếu test rõ ràng và thu hẹp được không gian vấn đề; lặp ngẫu nhiên thì không.

**Điểm cộng nếu ứng viên nói thêm:**

- Timebox investigation và có escalation trigger.
- Ghi negative result vào investigation log.
- Không thay nhiều biến cùng lúc.

**Red flags:**

- Chỉ liệt kê tool/command đã chạy.
- Tiếp tục thử ngẫu nhiên để trông bận.
- Xóa branch/log thất bại nên không ai review được.

**Follow-up khó hơn:**

- Mentor cũng chưa biết nguyên nhân thì em làm gì tiếp?
- Khi nào em dừng một investigation không có thêm evidence?

### Câu 50 — Standup sau hai ngày chưa tìm ra false positive

**Interviewer hỏi:**

Em làm hai ngày vẫn chưa tìm ra nguyên nhân model false positive. Trong standup em báo thế nào?

**Interviewer đang muốn test gì:**

- Progress reporting ngắn nhưng có evidence.
- Giao tiếp uncertainty và next step.
- Khả năng yêu cầu hỗ trợ đúng người.

**Mindset tốt nên có:**

- Goal, verified, finding, uncertain, risk, next, help.
- Không biến standup thành kể mọi thao tác.
- Có mốc cập nhật và blocker cụ thể.

**Câu trả lời mẫu:**

Em sẽ nói: “Goal của em là tìm nguyên nhân false positive ở search. Hai ngày qua em đã xác nhận input fresh, schema và model version đúng; em replay được 18/20 alert sai. Noise tập trung ở route ít traffic sau 22 giờ, nên evidence hiện nghiêng về sample thấp hoặc baseline theo giờ, chưa kết luận vì em chưa so known-good cùng khung giờ. Hôm nay em sẽ tính sample count, so threshold theo traffic và review năm case với SRE search. Rủi ro là nếu tăng threshold chung có thể bỏ lỡ incident ban ngày, nên em chưa đổi production. Em cần Data Engineer xác nhận aggregation window trước 11 giờ; nếu không có, em dùng raw sample để tiếp tục. Em sẽ cập nhật kết quả lúc 4 giờ.” Báo cáo như vậy cho thấy tiến triển dù root cause chưa có và giúp team can thiệp đúng chỗ.

**Điểm cộng nếu ứng viên nói thêm:**

- Có số case/đường dẫn evidence cụ thể.
- Nêu quyết định đang tránh vì rủi ro.
- Phân biệt blocked hoàn toàn và vẫn còn việc làm.

**Red flags:**

- “Hôm qua em debug, hôm nay tiếp tục debug.”
- Báo đã gần xong dù chưa có evidence.
- Đổ lỗi model hoặc team Data trong standup.

**Follow-up khó hơn:**

- Nếu tới 4 giờ hypothesis vẫn sai thì update thế nào?
- Standup chỉ có một phút, em rút còn những ý nào?

---

## LEVEL 3 — Difficult/ambiguous production cases

### Câu 51 — AI đề xuất restart production pod

**Interviewer hỏi:**

AI đọc log rồi đề xuất chạy kubectl restart một pod production. Em có chạy không?

**Interviewer đang muốn test gì:**

- Production safety và thái độ với AI advice.
- Phân biệt suggestion, decision và execution.
- Biết xét quyền, blast radius, approval và rollback.

**Mindset tốt nên có:**

- Hiểu command và validate evidence/root-cause hypothesis.
- Theo runbook, least privilege và approval.
- Canary/smallest action, quan sát outcome và có fallback.

**Câu trả lời mẫu:**

Em không copy-paste command chỉ vì AI đưa ra. Em đọc để hiểu command tác động object nào, namespace nào, có restart nhiều replica hay làm mất state không. Em kiểm tra evidence: pod có unhealthy thật, lỗi có nằm ở pod đó, restart có trong runbook và đã từng an toàn cho service này không. Em xem PDB, replica, traffic, dependency và incident commander/owner có phê duyệt theo policy không. Nếu evidence chưa đủ, em dùng command read-only để kiểm tra và báo đây mới là recommendation. Nếu restart được phép và cần thiết, em chọn phạm vi nhỏ nhất, lưu state/evidence, theo dõi replacement pod, error, latency và customer SLO; chuẩn bị dừng hoặc rollback/fallback nếu xấu hơn. Command exit 0 chưa phải success. Sau đó em ghi ai đề xuất, ai duyệt, version/prompt nếu cần và outcome thật. Với Intern, em sẽ nhờ người có quyền review trước production mutation.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra command có context/namespace rõ và tránh wildcard.
- Có idempotency/concurrency guard.
- Không gửi secret/log nhạy cảm vào AI công cộng.

**Red flags:**

- AI đã phân tích log nên chạy ngay.
- Thử production vì restart pod “thường vô hại”.
- Chỉ kiểm tra command có chạy thành công.

**Follow-up khó hơn:**

- Nếu incident P1 và mentor chưa phản hồi thì em làm gì trong phạm vi quyền hạn?
- Nếu pod là singleton có local state thì decision thay đổi thế nào?

### Câu 52 — Command success nhưng customer vẫn lỗi

**Interviewer hỏi:**

Remediation command chạy thành công nhưng customer vẫn gặp lỗi. Em làm gì tiếp?

**Interviewer đang muốn test gì:**

- Phân biệt execution success với remediation success.
- Verification bằng outcome độc lập.
- Biết dừng, rollback hoặc đổi hypothesis.

**Mindset tốt nên có:**

- Kiểm tra SLO/journey thật, không chỉ resource state.
- So pre/post trong window đủ và xét telemetry delay.
- Reopen hypothesis, tránh lặp action vô ích.

**Câu trả lời mẫu:**

Em đánh dấu action executed nhưng remediation failed hoặc not verified, không đóng incident. Em kiểm tra target state đúng chưa, rồi quan sát các outcome độc lập như synthetic checkout, error rate, latency, queue và complaint; chờ đúng stabilization window nhưng không chờ mù nếu impact tăng. Em so trước/sau theo cùng traffic và region. Nếu action có side effect hoặc không cải thiện trong thời hạn đã định, em theo runbook rollback/fallback và báo incident commander. Kết quả này làm giảm confidence của root-cause hypothesis ban đầu, nên em quay lại evidence, xem còn dependency, tenant hoặc region nào chưa xét. Em tránh chạy lại cùng command nhiều lần chỉ vì lần đầu exit 0. Trong record, em lưu action_id, target/version, approval, start/end, technical result và outcome verification. Sau incident, em cập nhật detector/RCA test để recommendation tương tự cần evidence tốt hơn hoặc điều kiện success đúng với customer SLO.

**Điểm cộng nếu ứng viên nói thêm:**

- Có timeout/abort criteria và owner verify.
- Tách command ack, desired state và observed outcome.
- Kiểm tra monitoring path có stale không.

**Red flags:**

- Đóng ticket vì Kubernetes/API trả success.
- Chạy lại command mạnh hơn ngay.
- Đổ lỗi customer cache mà chưa kiểm tra.

**Follow-up khó hơn:**

- Nếu SLO cải thiện nhưng complaint vẫn tăng thì verify theo nguồn nào?
- Nếu rollback cũng không cải thiện thì action có phải nguyên nhân làm xấu không?

### Câu 53 — Automation thành công một nửa

**Interviewer hỏi:**

Auto-remediation scale 10 workload nhưng chỉ 6 cái thành công, 4 cái timeout. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Partial failure và state reconciliation.
- Idempotency, blast radius và safe stopping point.
- Communication trong tình huống state không chắc chắn.

**Mindset tốt nên có:**

- Dừng fan-out mới, xác minh actual state từng target.
- Không retry mù; kiểm tra idempotency và dependency.
- Rollback/complete theo policy rồi verify SLO.

**Câu trả lời mẫu:**

Em không coi timeout là failed tuyệt đối vì target có thể đã nhận action nhưng response bị mất. Em dừng phát thêm action, liệt kê đúng 10 target với action_id/idempotency key và đọc actual desired/observed state từng workload. Em kiểm tra 6 cái thành công có ổn định, 4 cái timeout đã scale thật hay chưa, đồng thời quan sát quota, scheduler, dependency và customer SLO. Em báo incident commander trạng thái partial, blast radius và rằng chưa an toàn để retry toàn bộ. Dựa trên runbook, team chọn reconcile tới desired state hoặc rollback 6 target; em không tự trộn hai hướng. Retry chỉ áp dụng target đã xác nhận chưa thực hiện và phải idempotent. Sau khi state nhất quán, em verify outcome end-to-end. Em lưu từng target result, thời gian và lỗi để sửa automation: bounded concurrency, precondition, timeout semantics và compensating action. Partial success là một state cần thiết kế, không phải ngoại lệ có thể bỏ qua.

**Điểm cộng nếu ứng viên nói thêm:**

- Có lock chống hai automation cùng sửa resource.
- Kiểm tra quota/capacity trước fan-out.
- Phân biệt unknown với failed.

**Red flags:**

- Retry cả 10 ngay.
- Chỉ rollback 4 cái timeout dù chưa biết actual state.
- Báo action success vì đa số thành công.

**Follow-up khó hơn:**

- Nếu mất kết nối control plane nên không đọc được actual state thì sao?
- Nếu 6 target đã cải thiện SLO nhưng rollback sẽ gây xấu thì quyết định thế nào?

### Câu 54 — Auto-remediation làm xấu hơn

**Interviewer hỏi:**

Auto-remediation vừa chạy thì error rate tăng mạnh. Em làm gì và report ra sao?

**Interviewer đang muốn test gì:**

- Khả năng phản ứng với action-induced incident.
- Ưu tiên stop/rollback và ownership.
- Giữ evidence, không giấu lỗi automation.

**Mindset tốt nên có:**

- Freeze action mới và kích hoạt kill switch theo policy.
- Xác minh timeline, rollback/compensate an toàn.
- Báo impact, state, uncertainty và next update.

**Câu trả lời mẫu:**

Em ưu tiên chặn blast radius: pause automation hoặc dùng kill switch theo quyền/runbook để không có action mới, rồi báo incident commander và service owner ngay. Em xác nhận action nào đã chạy, resource nào đang ở trạng thái changed/unknown, error tăng ở cùng scope và thời điểm không. Nếu rollback đã được thiết kế và precondition còn đúng, team thực hiện rollback theo approval; nếu không, em không bịa lệnh ngược mà reconcile actual state và chọn safe fallback. Em giữ audit log, model/RCA recommendation, approval, command result và telemetry trước/sau. Báo cáo của em nêu: customer impact, automation đã bị dừng, những target đã ảnh hưởng, điều chưa chắc và mốc update. Sau phục hồi, em không chỉ tune model; em tìm vì sao safety gate, canary, verification hoặc abort threshold không ngăn được. Chỉ mở lại auto-mode sau replay, review và canary có tiêu chí rõ.

**Điểm cộng nếu ứng viên nói thêm:**

- Chuyển hệ thống sang detection-only.
- Có independent guardrail không dựa vào model gây action.
- Xem cả concurrent human changes.

**Red flags:**

- Chờ model tự sửa vì action có confidence cao.
- Xóa audit để tránh bị quy trách nhiệm.
- Tiếp tục rollout để “đủ sample”.

**Follow-up khó hơn:**

- Nếu rollback có blast radius lớn hơn giữ nguyên thì sao?
- Ai được quyền mở lại auto-remediation và cần evidence gì?

### Câu 55 — Model đề xuất scale nhưng evidence yếu

**Interviewer hỏi:**

Model confidence cao và đề xuất scale service, nhưng em chỉ thấy latency tăng còn CPU bình thường. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Không đồng nhất confidence với truth.
- Kiểm tra action có giải quyết mechanism không.
- Safe decision dưới áp lực production.

**Mindset tốt nên có:**

- Xem queue, saturation, downstream, traffic và trace.
- Kiểm tra policy/precondition cho scale.
- Giữ suggestion ở human approval hoặc thử phạm vi nhỏ.

**Câu trả lời mẫu:**

Em chưa scale chỉ từ confidence cao, vì model có thể tự tin dựa trên pattern lịch sử nhưng case hiện tại khác. Em kiểm tra latency nằm ở compute, queue, connection pool hay downstream trace; CPU bình thường không loại trừ hết capacity issue nhưng cũng không support scale rõ. Em xem traffic, concurrency, pod throttling, memory, queue và dependency. Em mở explanation xem model dùng feature nào, có stale/missing không và action policy yêu cầu precondition gì. Nếu scale có runbook, reversible và blast radius nhỏ, incident commander có thể cho canary một phần với success/abort metric rõ; nhưng nếu downstream đang quá tải, scale upstream có thể làm nặng hơn. Khi evidence yếu, em giữ human approval và trình bày alternative như rate-limit hoặc điều tra dependency. Em verify bằng SLO/customer outcome, không phải replica count. Confidence là thuộc tính output model, không thay thế causal evidence và safety gate.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra downstream capacity before scale-out.
- Dùng counterfactual từ cohort/pod cũ nếu có.
- Lưu decision “không act” và lý do.

**Red flags:**

- Confidence trên 0,9 thì action tự động hợp lệ.
- CPU bình thường nên chắc chắn không cần scale.
- Scale tối đa vì action dễ rollback.

**Follow-up khó hơn:**

- Nếu queue tăng nhanh nhưng CPU thấp thì hypothesis nào xuất hiện?
- Canary scale cải thiện latency, đã đủ bật toàn bộ chưa?

### Câu 56 — Hai engineer có hai root-cause hypothesis

**Interviewer hỏi:**

Hai engineer đưa ra hai root-cause hypothesis khác nhau trong incident. Em giúp team tiến lên thế nào?

**Interviewer đang muốn test gì:**

- Điều phối dựa trên evidence, không dựa seniority.
- Biết chạy test song song có kiểm soát.
- Giao tiếp và tránh tranh luận kéo dài.

**Mindset tốt nên có:**

- Viết rõ prediction/evidence của từng hypothesis.
- Tìm test phân biệt nhanh và an toàn.
- Giữ incident mitigation tách khỏi RCA hoàn hảo.

**Câu trả lời mẫu:**

Em tóm tắt hai hypothesis bằng ngôn ngữ kiểm chứng được, không ghi “anh A nghĩ DB, chị B nghĩ network” rồi chọn theo chức danh. Với mỗi hướng, em hỏi nếu đúng thì ta phải thấy evidence nào, evidence nào sẽ bác bỏ và action test có blast radius gì. Em dựng chung một timeline từ symptom, change, metric, log và trace để tìm điểm bất đồng. Nếu có thể, team chia người kiểm tra song song nhưng dùng cùng time range/service scope và cập nhật vào incident channel. Em ưu tiên test nhanh, read-only hoặc comparison giữa region/pod; không chạy hai remediation xung đột. Trong khi RCA chưa chốt, incident commander vẫn có thể chọn mitigation an toàn dựa trên customer impact. Em báo confidence và counter-evidence của cả hai, sẵn sàng đổi hướng khi data mới đến. Sau incident, kết quả được lưu thành replay case, kể cả nếu có hai fault cùng lúc.

**Điểm cộng nếu ứng viên nói thêm:**

- Có một người giữ timeline/source of truth.
- Phân biệt hypothesis owner với incident commander.
- Không ép luôn có một root cause duy nhất.

**Red flags:**

- Chọn ý kiến của người senior nhất mà không xem evidence.
- Để hai người cùng thay production theo hai hướng.
- Cố chứng minh hypothesis của mình đúng.

**Follow-up khó hơn:**

- Nếu hai hypothesis đều giải thích một phần symptom thì sao?
- Nếu không có test phân biệt nhanh, mitigation được chọn theo tiêu chí nào?

### Câu 57 — Chỉ một region hoặc tenant lỗi

**Interviewer hỏi:**

Metric toàn hệ thống bình thường nhưng một region hoặc một tenant báo lỗi nặng. Em điều tra và thiết kế alert thế nào?

**Interviewer đang muốn test gì:**

- Nhận ra aggregate che localized failure.
- Tư duy scope, business impact và cardinality.
- Cách dùng comparison cohort.

**Mindset tốt nên có:**

- Xác minh identity, route, region/tenant và sample count.
- So affected với unaffected cohort, changes và dependencies.
- Bổ sung dimension có kiểm soát và routing theo owner/impact.

**Câu trả lời mẫu:**

Em lấy request/timestamp cụ thể và xác nhận lỗi có tập trung thật ở region/tenant đó hay do reporting bias. Em so affected cohort với region/tenant tương tự về app version, config, dependency endpoint, deployment, quota và telemetry coverage. Trace/log của cùng journey giúp tìm điểm phân kỳ; service-level average có thể bị phần traffic khỏe lấn át. Trong incident em thông báo blast radius cục bộ nhưng severity vẫn dựa trên business impact, không chỉ phần trăm traffic. Cho monitoring, em đề xuất SLI theo region và allowlist tenant tier quan trọng hoặc dynamic top cohorts, tránh biến mọi tenant thành label cardinality cao. Detector cần minimum sample, absolute errors và quality flag; low-volume có thể kết hợp synthetic check. Alert route đến đúng owner và ghi rõ scope. Em replay case cùng known-good cohorts để chắc segmentation mới không tạo hàng nghìn false alert, rồi canary trước rollout.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra data residency/routing và feature flag theo tenant.
- Có fallback query khi dimension thiếu.
- Xét customer tier trong severity mà vẫn minh bạch.

**Red flags:**

- Không incident vì global SLO chưa breach.
- Thêm tenant_id thẳng vào mọi metric.
- Cho rằng một tenant lỗi luôn do tenant config.

**Follow-up khó hơn:**

- Nếu tenant là 2% traffic nhưng 40% doanh thu thì severity tính sao?
- Nếu telemetry tenant dimension vi phạm privacy thì thiết kế alternative nào?

### Câu 58 — Ba metric cùng đỏ trong 15 phút đầu

**Interviewer hỏi:**

Em nhận alert latency, error rate và queue backlog cùng đỏ. Trong 15 phút đầu em ưu tiên nhìn gì và làm gì?

**Interviewer đang muốn test gì:**

- Incident triage dưới áp lực thời gian.
- Ưu tiên impact, scope, timeline và recent change.
- Không sa vào dashboard hunting.

**Mindset tốt nên có:**

- Xác nhận customer impact và alert/data freshness.
- Chốt scope, onset, change và dependency critical path.
- Mitigate theo runbook, giao tiếp và giữ evidence.

**Câu trả lời mẫu:**

Trong vài phút đầu em xác nhận alert có fresh, SLO/customer journey có bị ảnh hưởng và scope là service, route, region hay toàn hệ thống. Em ghi onset time rồi nhìn traffic, recent deploy/config và dependency health để tạo timeline. Ba metric đỏ không có nghĩa có ba root cause: queue có thể tăng trước, rồi latency và timeout/error theo sau; hoặc retry từ downstream làm cả ba tăng. Em dùng trace/log sample của request lỗi để thu hẹp, đồng thời theo incident process: báo on-call/commander, cập nhật impact và không tự chạy action ngoài quyền. Nếu có mitigation đã biết, reversible và evidence phù hợp, team thực hiện với success/rollback condition rõ; còn em giữ snapshot/dashboard links trước change. Mỗi vài phút em cập nhật fact, hypothesis và next check. Sau action, em verify customer SLO và queue drain, không chỉ một metric giảm. Mục tiêu 15 phút đầu là ổn định và thu hẹp, không phải viết RCA hoàn chỉnh.

**Điểm cộng nếu ứng viên nói thêm:**

- Chỉ định người giao tiếp và người điều tra.
- Kiểm tra retry amplification/backpressure.
- Không quên telemetry pipeline health.

**Red flags:**

- Tìm root cause hoàn hảo rồi mới báo incident.
- Restart mọi component có metric đỏ.
- Chỉ nhìn CPU vì dễ hiểu.

**Follow-up khó hơn:**

- Nếu queue backlog là expected batch nhưng error vẫn tăng thì thứ tự hypothesis đổi sao?
- Nếu dashboard chậm 10 phút thì em lấy signal real-time từ đâu?

### Câu 59 — Timestamp giữa metric, log, trace bị lệch

**Interviewer hỏi:**

Metric, log và trace dường như kể ba timeline khác nhau; em nghi timestamp bị lệch. Em xử lý RCA ra sao?

**Interviewer đang muốn test gì:**

- Nhận biết clock/data-time problem.
- Không tạo causality từ timeline sai.
- Biết giữ uncertainty và sửa observability.

**Mindset tốt nên có:**

- Phân biệt event, ingest và processing time.
- Kiểm tra timezone, NTP, collector delay và query window.
- Chuẩn hóa/đánh dấu skew, hạ confidence RCA.

**Câu trả lời mẫu:**

Em chưa dùng thứ tự hiện tại để kết luận root cause. Em kiểm tra mỗi nguồn đang hiển thị event time, ingest time hay processing time; timezone, clock host, collector buffering, retry và query window có giống nhau không. Em tìm event có mốc chung như deployment id hoặc request/trace id để ước lượng skew giữa nguồn. Nếu xác định một host lệch hai phút, em không sửa mất raw timestamp mà ghi offset/quality flag và dựng timeline đã hiệu chỉnh kèm uncertainty. Evidence từ nguồn lệch hoặc đến muộn được giảm độ tin cậy; RCA engine không nên nói A xảy ra trước B nếu khoảng sai số chồng nhau. Trong incident, em báo rõ timeline chưa chắc và ưu tiên evidence không phụ thuộc thứ tự quá sát. Sau đó em phối hợp SRE sửa NTP/collector và monitor clock skew/ingest delay. Em replay incident sau khi chuẩn hóa để xem ranking RCA thay đổi thế nào.

**Điểm cộng nếu ứng viên nói thêm:**

- Giữ original timestamp và provenance để audit.
- Kiểm tra late data/backfill không sửa lịch sử im lặng.
- Hiển thị uncertainty window trên incident timeline.

**Red flags:**

- Kéo graph bằng mắt cho khớp rồi kết luận.
- Dùng ingest time như event time mà không ghi rõ.
- Chọn nguồn có timeline hợp hypothesis của mình.

**Follow-up khó hơn:**

- Nếu không có event chung để ước lượng skew thì sao?
- RCA có nên chạy khi clock skew vượt ngưỡng không?

### Câu 60 — Output đều mỗi 45 giây nhưng input stale 30 phút

**Interviewer hỏi:**

Model vẫn trả output mỗi 45 giây, dashboard pipeline xanh, nhưng input telemetry đã stale 30 phút. Em phát hiện bằng cách nào và ngăn việc này lặp lại ra sao?

**Interviewer đang muốn test gì:**

- Meta-monitoring và silent failure.
- Phân biệt processing liveness với data freshness.
- Thiết kế output quality/fail-safe.

**Mindset tốt nên có:**

- So max event timestamp với current processing time.
- Ghi input age/sample/window vào mọi run.
- Alert độc lập, trả insufficient_data và chặn action.

**Câu trả lời mẫu:**

Em phát hiện bằng metric freshness: lấy timestamp mới nhất thực sự của input trừ thời gian hiện tại hoặc inference time, không dùng “job vừa chạy” làm proxy. Mỗi detector run phải ghi input_window, max_event_time, sample_count, missing rate và input_age; dashboard hiển thị age/coverage cạnh output score. Em đặt SLO và alert riêng cho telemetry delay, tốt nhất có đường monitor độc lập với pipeline đang lỗi. Khi age vượt ngưỡng, detector không lặp lại kết luận normal từ cửa sổ cũ; nó trả insufficient_data/degraded, đóng băng confidence, gắn reason và chặn auto-remediation. Alert/incident đang mở được xử lý theo policy chứ không tự resolve. Em điều tra collector, queue, query cache hoặc watermark để tìm nguồn stale, rồi kiểm tra backfill không tạo alert giả khi phục hồi. Cuối cùng em thêm canary data với timestamp expected và test cố tình dừng input để bảo đảm dashboard chuyển đỏ dù scheduler vẫn chạy đều.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân biệt per-service freshness với aggregate freshness.
- Monitor watermark/queue lag và newest event id.
- Có fallback SLO rule không dùng stale feature path.

**Red flags:**

- Endpoint trả đều nên pipeline khỏe.
- Tiếp tục output score nhưng thêm một warning nhỏ.
- Auto-resolve incident vì model vẫn nói normal.

**Follow-up khó hơn:**

- Nếu chỉ một trong mười feature stale thì policy quyết định thế nào?
- Nếu backfill làm max timestamp mới nhưng dữ liệu có gap thì freshness metric đủ chưa?

### Câu 61 — SageMaker pipeline fail trước deadline

**Interviewer hỏi:**

SageMaker pipeline fail giữa chừng, dataset version chưa rõ và deadline còn một ngày. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Debug từng stage dưới deadline pressure.
- Reproducibility và scope management.
- Không bỏ quality gate để lấy trạng thái xanh.

**Mindset tốt nên có:**

- Xác định stage đầu tiên sai và giữ run metadata.
- Không rerun mù trên dataset “latest”.
- Báo option demo/MVP, risk và revised ETA.

**Câu trả lời mẫu:**

Em khóa lại thông tin run hiện tại trước: execution id, stage fail, input URI, code/image, parameter và log. Nếu dataset chỉ tên “latest”, em tìm manifest, object timestamp/hash hoặc upstream run để xác định chính xác nó là gì; em không rerun rồi vô tình đổi thêm một biến. Em đọc lỗi ở stage đầu tiên thất bại và kiểm tra output stage trước có hợp lệ, thay vì bắt đầu từ deploy. Em thử tái hiện phần nhỏ trong môi trường an toàn, sửa một yếu tố và rerun từ checkpoint nếu pipeline hỗ trợ. Đồng thời em báo mentor deadline risk: phần nào đã verify, blocker là data lineage, lựa chọn A demo bằng artifact/version cũ đã biết; B lùi mốc để chạy lại end-to-end, cùng recommendation. Em không bỏ evaluation chỉ để pipeline xanh. Sau khi chạy lại, em kiểm tra semantic output và ghi version rõ; rồi thêm manifest/validation để lỗi “không rõ dataset” không lặp lại.

**Điểm cộng nếu ứng viên nói thêm:**

- Không overwrite artifact cũ còn dùng được.
- Có stage-level retry chỉ khi operation idempotent.
- Phân biệt POC demo với production deploy.

**Red flags:**

- Bấm rerun toàn bộ nhiều lần.
- Đổi dataset cho tới khi job pass.
- Báo xong task vì pipeline lần sau xanh.

**Follow-up khó hơn:**

- Nếu artifact cũ cũng không biết data version thì demo thế nào cho trung thực?
- Nếu stage evaluation fail target nhưng deploy stage vẫn có thể chạy, em làm gì?

### Câu 62 — Late data tạo anomaly muộn

**Interviewer hỏi:**

Data Engineer báo telemetry thường đến muộn 8–10 phút, trong khi detector chạy mỗi phút và tạo alert sai. Em xử lý thế nào?

**Interviewer đang muốn test gì:**

- Hiểu event time, processing time và completeness.
- Phối hợp Data Engineer thay vì chỉ tune model.
- Cân bằng detection delay với correctness.

**Mindset tốt nên có:**

- Đo delay distribution theo source/service.
- Dùng watermark/completeness/quality state.
- Không sửa lịch sử incident im lặng khi late data về.

**Câu trả lời mẫu:**

Em lấy số liệu delay thực tế theo source và service, không dùng một con số trung bình chung. Em kiểm tra detector đang gán dữ liệu theo event time hay processing time và window có đóng khi dữ liệu chưa đủ không. Cùng Data Engineer, em xác định watermark hoặc completeness signal: một window chỉ được quyết định khi đủ dữ liệu theo ngưỡng, hoặc output sớm phải mang trạng thái preliminary/low quality. Đây là trade-off: chờ 10 phút giảm alert sai nhưng có thể phát hiện quá chậm, nên service critical có thể có fast path bằng SLO/synthetic signal và deep validation đến sau. Khi late data tới, hệ thống ghi revision thay vì xóa quyết định cũ, tránh duplicate/auto-resolve sai. Em replay delay pattern để chọn grace period, monitor queue lag/input age và canary policy. Em báo SRE rõ alert nào preliminary và đo cả detection delay lẫn false alert sau thay đổi.

**Điểm cộng nếu ứng viên nói thêm:**

- Dùng event id/dedup cho backfill.
- Có source-specific lateness budget.
- Giữ audit của output revision.

**Red flags:**

- Tăng window lên 10 phút cho mọi service.
- Gán late record vào phút nó đến.
- Bỏ toàn bộ late data để pipeline đơn giản.

**Follow-up khó hơn:**

- Nếu delay thỉnh thoảng lên 30 phút thì watermark chọn thế nào?
- Nếu alert đã page rồi late data chứng minh nó sai, feedback được ghi ra sao?

### Câu 63 — Suppress noise nhưng có nguy cơ bỏ fault thật

**Interviewer hỏi:**

Team muốn suppress một nhóm alert noisy, nhưng nhóm đó từng chứa một incident thật. Em đề xuất gì?

**Interviewer đang muốn test gì:**

- Alert fatigue trade-off và safety.
- Không coi suppression là xóa dữ liệu.
- Controlled rollout và escape hatch.

**Mindset tốt nên có:**

- Phân loại lý do noise và đặc điểm incident thật.
- Group/reroute/context-aware suppress trước hard mute.
- Replay, canary, expiry và monitor miss.

**Câu trả lời mẫu:**

Em sẽ không hard-mute cả nhóm. Em review sample noise và incident thật để tìm đặc điểm phân biệt: duration, SLO impact, route, traffic, deploy hay tín hiệu xác nhận khác. Có thể giữ detection nhưng group duplicate, hạ notification xuống ticket hoặc suppress chỉ trong maintenance có change id; nếu error/SLO vượt ngưỡng thì phải có escape hatch vẫn page. Em replay policy mới trên known-good và incident, báo rõ alert giảm bao nhiêu và case nào có nguy cơ bị chậm. Em canary theo một service, đặt ngày hết hạn/review cho suppression và giữ counter “suppressed alerts” cùng reason để vẫn quan sát được. Em theo dõi false negative từ incident/postmortem và cho SRE cách xem các anomaly bị suppress. Nếu không tìm được điều kiện an toàn, em đề xuất chấp nhận một phần noise tạm thời và sửa nguồn như data/baseline trước, thay vì đổi rủi ro vô hình thành outage bị bỏ lỡ.

**Điểm cộng nếu ứng viên nói thêm:**

- Có suppression owner, TTL và audit.
- Phân biệt silence theo planned change với model tuning.
- Đo time-to-detect của escape hatch.

**Red flags:**

- Tắt alert vì đa số là false positive.
- Suppress nghĩa là không lưu output.
- Không báo on-call policy đã đổi.

**Follow-up khó hơn:**

- Nếu không có label để replay incident thật thì phê duyệt suppression bằng gì?
- Nếu maintenance kéo dài quá TTL thì policy xử lý sao?

### Câu 64 — Mentor muốn tăng threshold cho hết noise

**Interviewer hỏi:**

Mentor đề nghị tăng threshold ngay để hết noise, nhưng em lo bỏ lỡ incident. Em phản hồi thế nào?

**Interviewer đang muốn test gì:**

- Biết đưa evidence và phản biện tôn trọng.
- Khả năng đề xuất thử nghiệm an toàn.
- Không vâng lời mù quáng hoặc tranh cãi cảm tính.

**Mindset tốt nên có:**

- Đồng ý mục tiêu, làm rõ phạm vi và risk.
- Đưa dữ liệu alert/incident, option nhỏ hơn.
- Replay/canary/rollback và review outcome.

**Câu trả lời mẫu:**

Em sẽ nói em đồng ý noise cần giảm, rồi trình bày concern bằng case thay vì nói “em cảm thấy nguy hiểm”. Em lấy distribution score của alert sai và incident thật; nếu chúng chồng nhau, tăng threshold toàn cục có thể bỏ cả hai. Em đề xuất kiểm tra nguồn noise trước và các option ít rủi ro hơn: persistence, dedup, low-traffic gate, threshold riêng cho nhóm hoặc chỉ đổi notification policy. Nếu mentor vẫn muốn thử threshold, em đề nghị replay trên incident/known-good, canary một service, giữ model cũ/config rollback và theo dõi alert rate cùng missed/late incident proxy. Em chốt success và abort criteria trước. Nếu quyết định cuối cùng vẫn tăng, em ghi assumption/risk và thực hiện đúng approval, không âm thầm chống lại. Sau rollout em chủ động báo outcome. Phản biện tốt là giúp team thấy trade-off và có cách thử an toàn, không phải chứng minh mentor sai.

**Điểm cộng nếu ứng viên nói thêm:**

- Dùng decision log ngắn.
- Tách urgent mitigation khỏi long-term fix.
- Nêu customer/SLO impact của miss.

**Red flags:**

- Tăng ngay vì mentor chịu trách nhiệm.
- Từ chối làm nhưng không có data/alternative.
- Chỉ đo alert giảm sau thay đổi.

**Follow-up khó hơn:**

- Nếu không đủ thời gian replay trước ca trực tối nay thì mitigation nào ít rủi ro?
- Nếu threshold mới giảm noise nhưng SRE vẫn không tin model thì sao?

### Câu 65 — Confidence thấp nhưng bị yêu cầu chọn action

**Interviewer hỏi:**

RCA có ba candidate gần điểm nhau, confidence thấp, nhưng stakeholder muốn em chọn ngay một remediation. Em làm gì?

**Interviewer đang muốn test gì:**

- Quản lý uncertainty dưới áp lực.
- Chọn action theo reversibility và shared benefit.
- Không giả certainty để làm hài lòng stakeholder.

**Mindset tốt nên có:**

- Trình bày candidate/evidence/counter-evidence ngắn gọn.
- Ưu tiên mitigation không phụ thuộc root cause nếu có.
- Xin approval, phạm vi nhỏ, verify/abort rõ.

**Câu trả lời mẫu:**

Em nói rõ RCA chưa phân biệt được ba candidate và vì sao, không chọn candidate đầu chỉ để có câu trả lời. Em tóm tắt evidence_for/evidence_against cùng action tương ứng và blast radius. Em tìm mitigation giúp giảm customer impact mà không đòi root cause chắc chắn, như giảm traffic vào path lỗi, failover đã có runbook hoặc tắt feature bằng flag, nhưng vẫn cần owner/incident commander quyết định. Nếu phải test một hypothesis, em chọn action nhỏ nhất, reversible, có prediction rõ: nếu X đúng thì metric/outcome nào phải cải thiện trong bao lâu; nếu không thì abort/rollback. Em giữ các team khác không chạy action xung đột và cập nhật timeline. Nếu tất cả action đều rủi ro cao, em khuyến nghị tiếp tục điều tra nhanh thay vì biến uncertainty thành mutation lớn. Sau action, evidence mới cập nhật ranking; command success không tự chứng minh hypothesis đúng.

**Điểm cộng nếu ứng viên nói thêm:**

- Phân biệt mitigation với permanent fix.
- Dùng read-only/discriminating test trước action.
- Ghi lý do decision và người approve.

**Red flags:**

- Chọn candidate có score cao hơn 0,01.
- Nói chắc để stakeholder yên tâm.
- Chạy lần lượt cả ba remediation.

**Follow-up khó hơn:**

- Nếu không có mitigation chung và impact tăng nhanh thì chọn theo tiêu chí nào?
- Action cải thiện một metric nhưng làm metric khác xấu thì verify sao?

### Câu 66 — Bug không nằm trong code của em

**Interviewer hỏi:**

Em phát hiện bug nằm ở dependency của team khác, không phải code của em. Ownership của em tới đâu?

**Interviewer đang muốn test gì:**

- Ownership không đồng nghĩa vượt quyền.
- Khả năng cung cấp evidence và phối hợp owner.
- Theo dõi tới outcome thay vì “chuyển ticket là xong”.

**Mindset tốt nên có:**

- Xác minh scope và tạo reproduction/evidence package.
- Báo owner, impact, priority và hỗ trợ điều tra.
- Không tự sửa/deploy hệ thống khác; theo dõi/fallback phần mình.

**Câu trả lời mẫu:**

Em không nói “không phải code em” rồi đóng việc. Em xác nhận bug bằng request/run_id, timeline và expected/actual; kiểm tra nó thật sự bắt đầu ở contract của dependency chứ không phải cách team em gọi sai. Em gửi owner một report nhỏ có impact, cách tái hiện, log/trace đã lọc dữ liệu nhạy cảm và mốc cần hỗ trợ. Trong phạm vi hệ thống AIOps, em có thể thêm guard, fallback hoặc đánh dấu output degraded theo review để giảm impact, nhưng không tự sửa/deploy service của họ. Em giữ liên lạc trong incident, giúp test fix trên staging/canary và verify customer/SLO sau rollout. Nếu priority khác nhau, em nhờ Product/SRE owner quyết định dựa trên impact thay vì blame. Ownership của em là đưa vấn đề tới đúng người, hỗ trợ evidence và theo tới khi outcome được xác nhận; quyền thay đổi vẫn thuộc team sở hữu và process phê duyệt.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra contract/compatibility để phòng lặp lại.
- Ghi workaround có expiry và owner.
- Chia sẻ post-incident learning hai chiều.

**Red flags:**

- Chuyển ticket rồi không theo dõi.
- Tự patch production của team khác.
- Dùng incident channel để quy trách nhiệm.

**Follow-up khó hơn:**

- Nếu owner phủ nhận bug dù evidence nghiêng mạnh thì em làm gì?
- Nếu workaround của team em có risk riêng thì ai phê duyệt?

### Câu 67 — Handover model giữa chừng

**Interviewer hỏi:**

Em nhận handover một model do người khác train, tài liệu thiếu và họ đã rời dự án. Em tiếp quản thế nào?

**Interviewer đang muốn test gì:**

- Kỹ năng phục hồi context và quản lý unknown.
- Reproducibility, version và safe ownership.
- Không giả vờ hiểu hệ thống.

**Mindset tốt nên có:**

- Inventory data/code/artifact/config/owners và current behavior.
- Tái hiện một run/case trước khi thay đổi.
- Gắn risk, bổ sung monitoring/runbook từng bước.

**Câu trả lời mẫu:**

Em bắt đầu bằng inventory: use case và user của output, repo/commit, dataset/feature version, model artifact, endpoint/config, threshold, pipeline schedule, dashboard, alert owner và rollback hiện có. Em không assume tên “latest” hay notebook là source of truth; em đối chiếu actual production version và log run gần nhất. Em chọn một input nhỏ hoặc historical incident, chạy qua pipeline để xem có tái tạo được output; chỗ nào không tái hiện được em ghi là risk, không che bằng cách train mới. Em phỏng vấn SRE/ML/Data/Dev còn liên quan về behavior expected và pain hiện tại, nhưng phân biệt ký ức với evidence. Trước khi sửa, em thêm freshness/version/output monitoring và bảo đảm có fallback. Em viết runbook tối thiểu, decision log và danh sách unknown theo priority. Handover hoàn tất không phải khi em đọc hết code, mà khi team biết hệ thống đang chạy gì, kiểm chứng/rollback ra sao và ai chịu trách nhiệm.

**Điểm cộng nếu ứng viên nói thêm:**

- Kiểm tra secret/access/expiry và scheduled jobs.
- Freeze risky change cho tới khi có observability tối thiểu.
- Tạo golden cases cho regression.

**Red flags:**

- Train lại từ đầu vì tài liệu thiếu.
- Tin notebook cuối cùng chính là production.
- Nhận ownership nhưng không nêu unknown/risk.

**Follow-up khó hơn:**

- Nếu production model artifact không còn trong registry thì sao?
- Nếu tái tạo output cũ không được nhưng hệ thống đang ổn, em có deploy lại không?

### Câu 68 — Customer muốn tự restart mọi service bị anomaly

**Interviewer hỏi:**

Customer muốn hệ thống tự restart mọi service khi có anomaly để “khỏi cần on-call”. Em trao đổi và đề xuất gì?

**Interviewer đang muốn test gì:**

- Dịch mong muốn automation thành risk/guardrail.
- Quản lý expectation về detection, RCA và action.
- Thiết kế maturity path an toàn.

**Mindset tốt nên có:**

- Hỏi pain/outcome: giảm MTTR hay giảm page.
- Giải thích anomaly không chỉ ra restart sẽ giúp.
- Đề xuất detection-only → recommend → approve → limited auto.

**Câu trả lời mẫu:**

Em hỏi mục tiêu thật là giảm thời gian phục hồi, giảm ca trực hay xử lý một lỗi restart đã biết. Em giải thích anomaly chỉ nói hành vi khác thường; restart có thể không giúp database/downstream issue, làm mất state hoặc tạo retry storm. Em đề xuất maturity path: trước hết hệ thống cung cấp alert + evidence; sau đó recommendation gắn runbook và human approval; chỉ auto cho một số failure mode đã được chứng minh, resource stateless, blast radius nhỏ và có precondition. Mỗi action cần allowlist, rate limit, canary, idempotency, approval policy, rollback/kill switch và verify customer SLO. Em dùng historical replay/fault test staging và pilot một service để đưa số liệu về success/failure, thay vì tranh luận lý thuyết. Với service không đủ evidence, fallback là page owner. Automation tốt không phải số restart nhiều mà là action đúng giúp outcome phục hồi an toàn và audit được.

**Điểm cộng nếu ứng viên nói thêm:**

- Tách recommendation confidence khỏi action authorization.
- Có action budget/cooldown chống loop.
- Tính cả toil mới do automation failure.

**Red flags:**

- Đồng ý vì restart thường tự hồi phục.
- Từ chối automation hoàn toàn không đưa lộ trình.
- Dùng model confidence làm safety gate duy nhất.

**Follow-up khó hơn:**

- Failure mode nào có thể là pilot hợp lý và vì sao?
- Nếu restart thành công 95% nhưng 5% gây outage lớn thì đánh giá sao?

### Câu 69 — BA/Product chưa chốt KPI

**Interviewer hỏi:**

BA nói “RCA phải hữu ích hơn”, Product muốn demo đẹp, SRE muốn giảm thời gian điều tra. Em giúp team chốt KPI và scope thế nào?

**Interviewer đang muốn test gì:**

- Điều phối stakeholder có ngôn ngữ/mục tiêu khác nhau.
- Chuyển “hữu ích” thành hành vi đo được.
- Tránh tối ưu demo thay outcome.

**Mindset tốt nên có:**

- Hỏi người dùng output cần quyết định gì.
- Chọn proxy gần outcome và định nghĩa denominator/process review.
- Chốt MVP, non-goal và cách nghiệm thu.

**Câu trả lời mẫu:**

Em tổ chức một buổi ngắn dùng vài incident thật. Em hỏi SRE hiện mất thời gian ở bước nào và RCA output nào sẽ thay đổi quyết định; BA/Product cần customer nhìn thấy giá trị gì. Em đề xuất định nghĩa “hữu ích” bằng review: top candidate có evidence đúng, giúp loại trừ/ưu tiên bước điều tra, và giảm time-to-first-useful-hypothesis so với baseline. Em cũng đo unsupported claim và tỷ lệ SRE chọn useful/not useful, kèm số incident/loại incident rõ. Demo có thể trình bày timeline đẹp nhưng không được tính success nếu citation sai. MVP chốt cho một critical journey, chỉ recommendation có evidence, chưa auto-action; non-goal là tìm đúng tuyệt đối mọi root cause. Em gửi acceptance criteria, sample output, owner label và lịch review để mọi bên xác nhận. Nếu target xung đột, em đưa option với trade-off và recommendation ưu tiên outcome của người xử lý incident.

**Điểm cộng nếu ứng viên nói thêm:**

- Đo inter-reviewer disagreement.
- Có baseline manual/current tool để so.
- Phân biệt leading metric với customer outcome.

**Red flags:**

- Chọn anomaly/RCA score vì dễ dashboard.
- Để Product nghiệm thu bằng một happy-path demo.
- Hứa “RCA đúng 90%” khi chưa có definition/label.

**Follow-up khó hơn:**

- Nếu SRE nói RCA sai candidate đầu nhưng vẫn hữu ích thì label thế nào?
- Nếu KPI giảm thời gian nhưng incident severity mix đổi thì so ra sao?

### Câu 70 — AI tóm tắt incident nhưng bỏ phần chưa chắc chắn

**Interviewer hỏi:**

AI tạo bản cập nhật incident rất mạch lạc để gửi customer, nhưng nó viết root cause như fact và bỏ phần team chưa validate. Em làm gì?

**Interviewer đang muốn test gì:**

- Human accountability khi dùng AI để communication.
- Tách fact, hypothesis, action và uncertainty.
- Phối hợp incident team trước external update.

**Mindset tốt nên có:**

- Đối chiếu mọi claim với incident source of truth.
- Sửa nội dung, giữ uncertainty và xin owner/commander review.
- Lưu feedback để cải thiện template/guardrail.

**Câu trả lời mẫu:**

Em không gửi nguyên văn vì câu chữ trôi chảy có thể làm customer hiểu hypothesis là kết luận chính thức. Em đối chiếu từng mốc, impact, action và claim với incident timeline, dashboard/evidence và update của owner. Em viết lại theo bốn phần: điều đã xác nhận, impact hiện tại, action đã làm và outcome, phần đang điều tra cùng mốc cập nhật tiếp theo. Ví dụ: “Evidence hiện nghiêng về database connection saturation; chưa kết luận root cause vì trace của hai route chưa đủ.” Em bỏ chi tiết nhạy cảm và nhờ incident commander/communication owner duyệt trước khi gửi. Nếu AI bịa timestamp/citation, em gắn case unsupported, lưu model/prompt/version và không dùng output đó làm source of truth. Sau incident, em cập nhật template bắt buộc phân biệt fact/hypothesis và test trên case chưa kết luận. AI giúp rút ngắn soạn thảo; người gửi vẫn chịu trách nhiệm về độ đúng và mức chắc chắn.

**Điểm cộng nếu ứng viên nói thêm:**

- Giữ cadence và audience phù hợp, không dump kỹ thuật.
- Không nói “resolved” trước khi customer outcome được verify.
- Có approved data sources cho AI summary.

**Red flags:**

- Gửi vì AI viết chuyên nghiệp hơn mình.
- Xóa uncertainty để customer bớt lo.
- Đưa log/customer data nhạy cảm vào công cụ chưa được duyệt.

**Follow-up khó hơn:**

- Nếu customer yêu cầu root cause ngay nhưng team mới có hypothesis thì nói thế nào?
- Nếu AI summary khác update của SRE, nguồn nào thắng và em xử lý conflict ra sao?

---

## A. 15 nguyên tắc mindset AIOps Intern nên nhớ

1. **Input sai thì downstream thông minh đến đâu cũng sai.** Luôn kiểm tra freshness, coverage, schema, sample và ý nghĩa dữ liệu trước.
2. **Chạy được không đồng nghĩa đúng.** Job SUCCESS, test xanh hay API 200 chỉ xác nhận một lớp kỹ thuật.
3. **Anomaly không đồng nghĩa incident.** Cần persistence, impact, context và policy trước khi page người.
4. **Correlation không đồng nghĩa causation.** Hai metric cùng đỏ chỉ tạo hypothesis; timeline và cơ chế mới tăng evidence.
5. **Model confidence không phải sự thật.** Score cao vẫn có thể dựa trên input stale, sample thấp hoặc pattern chưa từng thấy.
6. **Alert chỉ có giá trị khi giúp người xử lý.** Một alert không có scope, evidence, owner hoặc next step dễ trở thành noise.
7. **Không đủ evidence thì nói chưa đủ evidence.** Trung thực về uncertainty tốt hơn một root cause tự tin nhưng sai.
8. **Tìm bước sai đầu tiên, không sửa triệu chứng cuối cùng.** Đi từ input → processing → output → delivery → outcome.
9. **Production change phải có blast radius, approval và rollback.** Reversible/small action được ưu tiên khi uncertainty cao.
10. **Command success không phải remediation success.** Chỉ gọi thành công khi SLO hoặc customer journey thật sự phục hồi.
11. **Báo blocker sớm tốt hơn giấu tới deadline.** Một status tốt có done, unknown, risk, option và mốc cập nhật.
12. **AI là trợ lý, không phải authority.** Hiểu, inspect, test, đối chiếu và review trước khi dùng output.
13. **Ownership không có nghĩa vượt quyền.** Theo vấn đề tới outcome, nhưng không tự ý sửa hệ thống của team khác.
14. **Một metric/model/threshold hiếm khi phù hợp mọi service.** Luôn xem semantics, traffic, tier và cost của lỗi.
15. **Production success phải đo end-to-end.** Model tốt offline chưa đủ nếu alert vô ích, RCA không support hoặc action không cải thiện user impact.

---

## B. Framework trả lời câu hỏi tình huống: C-H-E-C-K-S

C-H-E-C-K-S là một khung nhớ nhanh, không phải checklist phải đọc máy móc trong mọi câu trả lời.

| Bước | Câu hỏi tự hỏi | Cách nói tự nhiên trong interview |
|---|---|---|
| **C — Clarify** | Goal, scope, user, deadline và success là gì? | “Đầu tiên em sẽ làm rõ alert này phục vụ ai và cần quyết định gì.” |
| **H — Health of input** | Data có đúng, đủ, fresh, đúng version và đúng context không? | “Trước khi tin model, em kiểm tra input age, sample và schema.” |
| **E — Evidence & hypotheses** | Fact nào đã có, hypothesis nào hợp lý, counter-evidence là gì? | “Evidence đang nghiêng về X, nhưng em chưa kết luận vì Y.” |
| **C — Controlled action** | Bước nhỏ, an toàn, reversible nào giảm uncertainty hoặc impact? | “Em sẽ thử trên staging/canary và chuẩn bị rollback.” |
| **K — Keep verifying** | Expected outcome là gì; actual có thật sự cải thiện không? | “Command chạy xong em vẫn verify SLO và journey của user.” |
| **S — Share & save** | Ai cần biết, phần nào chưa chắc, evidence nào phải lưu? | “Em cập nhật mentor về done, risk, next step và lưu run_id/version.” |

Một câu trả lời ngắn có thể dùng khung này như sau:

> “Đầu tiên em làm rõ scope và impact. Em kiểm tra input có fresh và đúng service không, rồi lập hai hypothesis từ timeline. Em chọn test read-only nhỏ nhất để phân biệt chúng. Nếu cần thay production, em xin approval và chuẩn bị rollback. Sau action em verify bằng SLO/customer outcome, rồi cập nhật team phần đã biết và phần còn chưa chắc.”

---

## C. Framework báo cáo khi chưa chắc chắn: FACTS

| Phần | Nội dung cần có |
|---|---|
| **F — Facts** | Điều đã xác nhận bằng evidence. |
| **A — Assessment** | Hypothesis hoặc kết quả evidence đang nghiêng về. |
| **C — Caveat** | Điều chưa verify và lý do chưa thể kết luận. |
| **T — Test/Time** | Bước đang kiểm tra và mốc cập nhật tiếp theo. |
| **S — Support/Selection** | Cần ai giúp hoặc cần chọn giữa option nào. |

Mẫu nói tự nhiên:

> “Hiện tại em đã xác nhận được A và B bằng run_id/dashboard này. Evidence đang nghiêng về X. Tuy nhiên em chưa kết luận vì C chưa được verify và data của region Y đang trễ. Em đang kiểm tra D, sẽ cập nhật lúc 4 giờ. Nếu tới lúc đó vẫn chưa đủ evidence, em đề xuất chọn giữa E là giữ model cũ an toàn và F là kéo dài shadow test thêm hai ngày; recommendation của em là E vì blast radius thấp hơn.”

Mẫu standup 30 giây:

> “Goal là giảm false alert payment. Em đã loại trừ missing data và sai model version. Noise hiện tập trung ở low traffic, nhưng chưa xác nhận baseline theo giờ. Hôm nay em replay 20 case và review với SRE. Chưa đổi production vì có risk bỏ lỡ P1. Em cần Data xác nhận aggregation window trước 11 giờ.”

---

## D. Framework dùng AI trong công việc: VERIFY-AI

| Bước | Em cần làm gì? |
|---|---|
| **V — Verify requirement** | Tự nói lại expected behavior; không để AI tự đặt requirement. |
| **E — Examine output** | Đọc code/query/RCA/command, kiểm tra assumption, scope, version và quyền. |
| **R — Run small known cases** | Dùng input nhỏ có expected result tự tính hoặc đã được domain expert xác nhận. |
| **I — Investigate edge cases** | Test missing, zero, stale, low traffic, timestamp lệch, counter reset và invalid input phù hợp use case. |
| **F — Find a reference** | So với rule cũ, model cũ, log/trace, historical incident hoặc tài liệu chính thức. |
| **Y — Yield to safe review** | Chạy sandbox/staging/shadow; xin human/domain review cho phần rủi ro hoặc chưa hiểu. |
| **A — Act gradually** | Canary, least privilege, approval, rollback; không copy-paste mutation production. |
| **I — Inspect outcome** | Monitor output distribution, alert usefulness, SLO/customer impact và lưu feedback/version. |

Mẫu trả lời dùng được cho code, query, test, RCA và command do AI sinh:

> “Em xem AI output là bản nháp. Em tự xác nhận requirement, đọc output và kiểm tra assumptions. Em tạo case nhỏ có expected result, thêm edge case và so với nguồn độc lập. Phần chưa hiểu em hỏi mentor hoặc tài liệu chính thức. Em chỉ thử ở sandbox/staging, review blast radius và có rollback trước production. Sau rollout nhỏ em monitor outcome và ghi lại model/prompt/code version. Việc code chạy hoặc test do AI tạo đều pass chưa đủ chứng minh đúng.”

---

## E. Top 20 câu có xác suất cao xuất hiện trong interview AIOps Intern

Mức ưu tiên dưới đây là thứ tự ôn, không phải độ khó tuyệt đối.

| Ưu tiên | Câu | Vì sao nên chuẩn bị |
|---|---|---|
| **Must prepare** | **Câu 1 — Một tuần làm POC anomaly detection** | Kiểm tra requirement, tự học, scope MVP và deadline trong một câu. |
| **Must prepare** | **Câu 2 — “Monitor hệ thống tốt hơn”** | Requirement mơ hồ là tình huống Intern gặp rất thường xuyên. |
| **Must prepare** | **Câu 7 — AI sinh detector và test đều pass** | Đo khả năng phân biệt chạy được với đúng và cách làm việc với AI. |
| **Must prepare** | **Câu 9 — Gần như không có label** | Bài toán cốt lõi của anomaly detection thực tế. |
| **Must prepare** | **Câu 14 — anomaly_score=0,95** | Kiểm tra cách đọc output, evidence và đường từ anomaly tới incident. |
| **Must prepare** | **Câu 16 — User lỗi nhưng detector không alert** | Đo thái độ với false negative và customer evidence. |
| **Must prepare** | **Câu 18 — Log mỗi detector run** | Thể hiện observability cho chính AIOps system. |
| **Must prepare** | **Câu 19 — Monitor AIOps pipeline** | Câu meta-monitoring rất dễ phân biệt tư duy production. |
| **Must prepare** | **Câu 21 — False positive hay false negative** | Đáp án tốt phải reasoning “tùy use case”. |
| **Must prepare** | **Câu 25 — Offline đẹp, production tệ** | Kiểm tra debug data/model/pipeline mà không train lại mù quáng. |
| **Must prepare** | **Câu 35 — Latency và CPU cùng tăng** | Câu kinh điển về correlation và causation. |
| **Must prepare** | **Câu 41 — SRE phàn nàn spam alert** | Bao phủ alert fatigue, teamwork, trust và controlled tuning. |
| **Must prepare** | **Câu 48 — Còn hai ngày, mới xong 60%** | Đánh giá reporting, ưu tiên, scope và ownership. |
| **Must prepare** | **Câu 51 — AI đề xuất restart production pod** | Kiểm tra safety, approval, blast radius và verification. |
| **Good to prepare** | **Câu 12 — Prometheus missing data** | Input quality thường là nguyên nhân silent failure. |
| **Good to prepare** | **Câu 26 — SageMaker SUCCESS nhưng production tệ** | Đủ technical để thực tế nhưng trọng tâm vẫn là reasoning. |
| **Good to prepare** | **Câu 37 — AI-generated RCA citation sai** | Kiểm tra LLM skepticism và evidence provenance. |
| **Good to prepare** | **Câu 42 — Customer đòi 100% accuracy** | Đo expectation management và khả năng nói trade-off. |
| **Bonus** | **Câu 56 — Hai root-cause hypothesis** | Cho thấy cách cộng tác và test hypothesis dưới incident pressure. |
| **Bonus** | **Câu 60 — Output đều nhưng input stale** | Case khó, rất mạnh để thể hiện meta-monitoring end-to-end. |

---

## Lời nhắc cuối trước interview

Interviewer không nhất thiết chờ em đoán đúng công nghệ hay root cause. Họ đang quan sát cách em đi từ một tình huống mơ hồ tới bước tiếp theo có căn cứ.

Khi bí, hãy quay lại sáu câu:

1. User hoặc on-call đang cần quyết định gì?
2. Input và context có đáng tin không?
3. Fact nào em đã có, hypothesis nào em đang kiểm tra?
4. Bước nhỏ, an toàn và reversible nhất là gì?
5. Em sẽ biết action thành công bằng outcome nào?
6. Em cần báo ai về phần đã biết, chưa biết và mốc tiếp theo?

Một Intern tốt không cần biết ngay mọi đáp án. Em cần cho thấy mình biết thu hẹp vấn đề, tìm evidence, kiểm chứng, hành động an toàn, đo kết quả và giao tiếp rõ ràng.
