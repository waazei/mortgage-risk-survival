# Hướng dẫn đọc dashboard Mortgage Risk & Survival

Tài liệu này giải thích các trang, chỉ số và biểu đồ đang có trong dashboard. Đây là hướng dẫn đọc kết quả, không phải hướng dẫn dùng mô hình để quyết định cấp tín dụng.

## 1. Dự án phân tích điều gì?

Dự án dùng dữ liệu Freddie Mac về các khoản vay mua nhà để mô tả thời gian từ khi khoản vay được theo dõi đến khi khoản vay **vỡ nợ**, **trả trước/tất toán sớm**, hoặc **kết thúc theo dõi mà chưa quan sát hai sự kiện đó**. Default và prepayment cạnh tranh nhau: khoản vay đã trả trước thì không còn có thể vỡ nợ sau đó trong cùng tiến trình.

Dashboard hiển thị thống kê lịch sử và kết quả các mô hình đã chạy. Nó không phải hệ thống chấm điểm hay dự báo PD cá nhân đã hiệu chỉnh cho một ngân hàng.

## 2. Thứ tự nên đọc

1. **Tổng quan**: quy mô mẫu và các xác suất tích lũy.
2. **Danh mục & dữ liệu → Chất lượng & kiểm tra**: phạm vi và kiểm tra dữ liệu.
3. **Rủi ro cạnh tranh**: CIF, Kaplan–Meier và tuổi khoản vay.
4. **Yếu tố rủi ro / Mô hình & hệ số / Từ điển biến**: liên hệ ước lượng.
5. **Vintage**: so sánh nhóm khoản vay theo năm phát hành.
6. **Phương pháp / Chẩn đoán / Bằng chứng & hàm ý**: giả định, giới hạn và mức độ bằng chứng.
7. **ECL & kịch bản**: phép tính minh họa.

## 3. Điều hướng chung

- **2016 — 2026 Q1** là khoảng thời gian dữ liệu được dashboard mô tả. Không phải mọi khoản vay đều được theo dõi đủ khoảng thời gian đó; khoản vay mới có follow-up ngắn hơn.
- Nút mũi tên xoay **tải lại các tệp kết quả** mà máy chủ dashboard đang đọc; nó không chạy pipeline hay fit lại mô hình.
- Workspace bên trái là các nhóm trang; tab nhỏ phía dưới nhóm mở trang con.
- Dấu **—** hoặc ô trống thường có nghĩa là kết quả/mốc chưa có trong tệp hoặc chưa đủ theo dõi, không nên tự hiểu là 0.
- Số liệu phụ thuộc vào các tệp kết quả trong thư mục data/results. Thời điểm cập nhật cho biết dashboard đọc dữ liệu lúc nào, không nhất thiết là lúc mô hình được chạy lại.

## 4. Tổng quan

- **Khoản vay**: số Loan ID độc lập trong bảng loan-level.
- **Vỡ nợ / Trả trước**: số khoản vay có kết cục tương ứng trong dữ liệu.
- **Tỷ lệ quan sát**: số sự kiện chia tổng khoản vay. Đây là tỷ lệ thô, không phải PD tại một kỳ hạn và không điều chỉnh thời gian theo dõi khác nhau.
- **Default CIF 60 tháng**: xác suất tích lũy vỡ nợ trước tháng 60, có tính đến trả trước là sự kiện cạnh tranh. Dùng chỉ số này để mô tả rủi ro theo thời gian phù hợp hơn tỷ lệ thô.
- Các thanh 12, 24, 36, 60 tháng cho biết default CIF ở từng mốc; nhấn vào mốc để mở trang survival.

## 5. Danh mục & dữ liệu

### Danh mục

- **Cơ cấu trạng thái**: số lượng/tỷ trọng khoản vay kiểm duyệt, vỡ nợ hoặc trả trước.
- **Bao phủ theo quý / số tệp theo năm**: tệp quý hiện có và quy mô quan sát theo thời gian.
- Bộ chọn **Chỉ số** đổi biểu đồ quý giữa số khoản vay, lượt quan sát, dòng Loan ID–tuổi bị trùng, thiếu lãi suất hoặc thiếu LTV.
- **Khoản vay** là mã độc lập; **lượt quan sát** là số dòng theo thời gian. Một khoản vay có thể có nhiều lượt quan sát trong panel quý.
- **Dòng trùng Loan ID–tuổi** là chỉ báo chất lượng/ghép panel; đọc cùng định nghĩa trong bảng kiểm tra quý.
- **Thiếu lãi suất/LTV** là dữ liệu thiếu, không đồng nghĩa giá trị bằng 0.

### Chất lượng & kiểm tra

- **PASS**: kiểm tra cụ thể đã đạt điều kiện kỹ thuật được lập trình, như tệp tồn tại, mã sự kiện nhất quán, Loan ID duy nhất, hoặc đồng nhất thức CIF.
- **FAIL**: điều kiện đó không đạt và cần xem chi tiết.
- **UNVERIFIED**: dự án chưa hoàn tất kiểm chứng phương pháp tương ứng; không được tính là đạt.
- Điểm và huy hiệu audit chỉ tóm tắt kiểm tra nội bộ. Chúng không chứng minh mô hình đúng, thiết kế nghiên cứu hợp lệ, dự báo chính xác hay quan hệ nhân quả.
- **Kiểm tra theo quý** mô tả panel/chất lượng dữ liệu; không chứng minh Cox biến thiên theo thời gian đã được fit.

### Tải kết quả

Lọc và tải CSV do pipeline tạo, như bảng CIF, hệ số, kiểm tra giả định và audit. Đây là bảng phân tích, không phải dữ liệu khoản vay gốc. Hãy xem tiêu đề cột và phương pháp trước khi dùng con số.

## 6. Survival và competing risks

### Biểu đồ

- Trục ngang là **tuổi khoản vay tính bằng tháng**, không phải năm lịch.
- Chế độ **CIF** vẽ xác suất tích lũy vỡ nợ và trả trước. Trục trái dùng cho vỡ nợ, trục phải cho trả trước; hai trục có thang riêng nên không so độ cao đường trực tiếp bằng mắt.
- Có thể bật/tắt đường và giới hạn tuổi khoản vay để phóng vào đoạn đầu.
- Chế độ **KM** vẽ sống sót all-cause: xác suất chưa gặp kết cục kết thúc khoản vay. Khi có competing risks, 1 − KM **không bằng** xác suất vỡ nợ; dùng default CIF cho xác suất tích lũy vỡ nợ.

### Bảng mốc và risk set

- Bảng 12/24/36/60 tháng đặt cạnh **Default CIF**, **Prepayment CIF** và **KM survival** để phân biệt ba đại lượng.
- **PD CIF** là ước lượng tích lũy trong mẫu, không phải PD cá nhân hoặc PD đã hiệu chỉnh theo chuẩn ngân hàng.
- Bảng khoản vay còn ở risk set và số sự kiện theo tuổi cho biết bao nhiêu khoản vay vẫn được theo dõi/nguy cơ ngay trước từng mốc. Ở phần đuôi, risk set thường nhỏ hơn nên ước lượng có thể kém ổn định.

### Đồng nhất thức CIF

Aalen–Johansen có đồng nhất thức gần đúng:

    S(t) + CIF_default(t) + CIF_prepayment(t) ≈ 1

S(t) là xác suất chưa có kết cục kết thúc nào đến thời điểm t. Sai khác nhỏ có thể do làm tròn/tính toán; audit kiểm tra biểu thức này với dung sai đặt trước.

## 7. Yếu tố rủi ro và mô hình

### Forest plot

- Mỗi hàng là một biến; điểm là **HR (hazard ratio)**, thanh ngang là **khoảng tin cậy 95%**.
- HR = 1 là mốc không khác biệt về hazard tương đối. HR lớn hơn 1 biểu thị hazard sự kiện cao hơn; nhỏ hơn 1 biểu thị hazard thấp hơn, khi giữ các biến khác trong mô hình cố định.
- Nếu khoảng tin cậy chứa 1, chưa thấy khác biệt rõ ở mức 5% theo kiểm định thông thường. Điều này không chứng minh hiệu ứng bằng 0.
- Với biến chuẩn hóa, HR thường ứng với thay đổi **một độ lệch chuẩn**, không phải một đơn vị gốc.
- Bộ chọn đổi giữa Cox vỡ nợ, Cox trả trước và Fine–Gray vỡ nợ. Lọc “chỉ có ý nghĩa” và sắp xếp chỉ đổi cách hiển thị, không đổi mô hình.
- Biểu đồ so sánh HR đặt các mô hình cạnh nhau. Chỉ so sánh thận trọng khi mẫu, biến, chuẩn hóa và quy ước mã hóa tương thích.

### Bảng hệ số

- **β / coefficient**: hệ số log-hazard; trong Cox thường có HR = exp(β).
- **HR**: hệ số ở thang tỷ số hazard.
- **SE**: sai số chuẩn, thể hiện độ bất định của hệ số.
- **z**: hệ số chia sai số chuẩn; **p-value** đo mức độ tương thích của dữ liệu với giả thuyết hệ số bằng 0 theo kiểm định được dùng.
- **CI thấp/cao**: hai cận khoảng tin cậy 95%.
- **Converged**: thuật toán báo hội tụ. Đây là điều kiện tính toán cần thiết, không tự chứng minh mô hình được đặc tả đúng.
- **Complete case**: phân tích chỉ dùng dòng đủ dữ liệu; mẫu có thể nhỏ/khác mẫu chính nên khác biệt hệ số có thể do cả mẫu và cách xử lý thiếu.
- **Đối chiếu với** thêm HR của mô hình khác để so sánh mô tả, không phải kiểm định chính thức chênh lệch.
- Nút **Tải CSV** lưu bảng mô hình đang chọn.

### Fine–Gray: cần thận trọng

Fine–Gray liên hệ trực tiếp hơn với CIF thông qua subdistribution hazard. Implementation trong dự án được tự xây. Cho đến khi đối chiếu độc lập với implementation đã được xác thực trên cùng quan sát, quy ước sự kiện/kiểm duyệt và cách tính sai số chuẩn, hãy xem HR Fine–Gray là **thăm dò/chưa kiểm chứng**, không dùng làm kết luận chính.

## 8. Vintage

- **Vintage** gom khoản vay theo năm phát hành/nhóm khởi tạo và so sánh CIF theo tuổi khoản vay.
- Có thể chọn đường default CIF, prepayment CIF hoặc survival, rồi bật/tắt các năm phát hành.
- So sánh cùng tuổi khoản vay cho thấy cohort có quỹ đạo khác nhau nhưng không tự giải thích nguyên nhân. Khác biệt có thể do đặc điểm khoản vay, chính sách cấp tín dụng, thời kỳ kinh tế hoặc thời gian theo dõi.
- Vintage mới thường chưa đủ 60 tháng quan sát. Mốc trống/— nghĩa là **chưa đủ follow-up**, không phải CIF bằng 0.
- Quy mô khoản vay, số event và độ dài theo dõi có thể khác nhau giữa vintage; thận trọng ở phần đuôi.

## 9. Từ điển biến

Trang này giải thích biến, cho phép tìm kiếm, và hiển thị trung bình, độ lệch chuẩn cùng HR theo mô hình.

- **credit_score**: điểm tín dụng khi khởi tạo; điểm cao thường gắn với hồ sơ tín dụng mạnh hơn, nhưng hệ số vẫn chỉ là liên hệ trong mẫu.
- **original_ltv**: tỷ lệ khoản vay ban đầu trên giá trị tài sản bảo đảm (loan-to-value).
- **original_dti**: tỷ lệ nghĩa vụ nợ trên thu nhập khi cấp khoản vay (debt-to-income).
- **original_interest_rate**: lãi suất hợp đồng ban đầu.
- **original_loan_term**: kỳ hạn ban đầu, thường tính bằng tháng.
- **Trung bình / độ lệch chuẩn**: mô tả phân phối trong mẫu tham chiếu. Z-score = (giá trị − trung bình) / độ lệch chuẩn, cho biết một quan sát cách trung bình bao nhiêu độ lệch chuẩn.
- CI trong ngoặc của ma trận là khoảng tin cậy HR. Ô trống nghĩa là không có ước lượng tương ứng trong kết quả đã nạp.

## 10. Tra cứu khoản vay

- Nhập **đúng Loan ID** hoặc chọn mã mẫu. Lần đầu máy chủ có thể quét cột ID trong Parquet; các lần sau có thể dùng bộ nhớ đệm cục bộ.
- Hồ sơ hiển thị trường có sẵn như tuổi khoản vay, trạng thái kết cục cuối, biến lúc khởi tạo và lãi suất/đặc điểm trong bảng tổng hợp.
- **Trạng thái cuối** là kết cục quan sát tại điểm kết thúc dữ liệu, không phải dự báo tương lai.
- Biểu đồ **Feature profile** so sánh đặc điểm khoản vay với phân phối mẫu bằng Z-score. Đây không phải xác suất vỡ nợ cá nhân.
- Dataset không có đủ lịch sử thanh toán hay số dư dư nợ, nên không thể dựng đầy đủ lịch sử hoặc tính PD/ECL thực tế cho khách hàng.

## 11. ECL & kịch bản

**ECL sandbox là máy tính giả định, không phải đầu ra IFRS 9.**

- **EAD** (Exposure at Default): dư nợ phơi nhiễm giả định khi vỡ nợ, nhập bằng USD.
- **LGD** (Loss Given Default): tỷ lệ tổn thất nếu vỡ nợ, nhập theo phần trăm.
- **Horizon**: 12/24/36/60 tháng; PD dùng là default CIF danh mục đúng mốc đó.
- **Chiết khấu năm r**: tỷ lệ chiết khấu giả định.
- **Kịch bản nhẹ / stress · PD ×**: nhân CIF cơ sở với hệ số người dùng nhập; kết quả được chặn tối đa 100%.
- Phép tính tại mốc đang chọn là EAD × LGD × PD_CIF(horizon) / (1 + r)^(horizon/12).
- Bảng và biểu đồ hiển thị giá trị bốn kỳ hạn dưới kịch bản nhẹ, cơ sở và stress. Đây là độ nhạy số học trên cùng CIF danh mục, không phải ba mô hình dự báo độc lập.

Không bao gồm staging (12-month/lifetime ECL), kịch bản kinh tế forward-looking có trọng số xác suất, term structure PD cá nhân, phân bổ thời điểm vỡ nợ/cash flow, EAD biến đổi, LGD theo thời gian, hay chiết khấu dòng tiền theo lãi suất hiệu lực của quy trình kế toán đầy đủ.

## 12. Phương pháp

- **Aalen–Johansen / CIF**: xác suất tích lũy của từng loại sự kiện, có tính competing event.
- **Cause-specific Cox**: hazard tức thời của sự kiện mục tiêu; sự kiện cạnh tranh rời risk set khi xảy ra. HR là liên hệ có điều kiện, không phải nhân quả.
- **Fine–Gray**: mô hình subdistribution hazard; implementation tự xây trong dự án cần benchmark như lưu ý ở trên.
- **Kaplan–Meier**: đường sống sót; cấu hình tại đây tính sống sót khỏi mọi kết cục kết thúc, nên 1 − KM không phải default CIF.
- **Proportional hazards (PH)**: giả định HR không đổi theo thời gian. Kiểm tra Schoenfeld giúp phát hiện xu hướng nhưng không thay thế đánh giá mô hình tổng thể.

## 13. Chẩn đoán và audit

- **Schoenfeld residual**: phần dư dùng để xem ảnh hưởng của biến có đổi theo thời gian không.
- **p-value**: tín hiệu kiểm định xu hướng; với hàng triệu khoản vay, p-value có thể rất nhỏ dù xu hướng thực tế yếu.
- **R²** ở biểu đồ chẩn đoán mô tả mức độ xu hướng thời gian giải thích biến thiên residual. Đọc cùng p-value và biểu đồ, không chỉ nhìn một số.
- Đồ thị Schoenfeld theo biến cho thấy residual và xu hướng; mẫu hình rõ có thể gợi ý PH không phù hợp, cần phân tích tiếp.
- Audit kiểm tra các điều kiện đã lập trình: tệp, ID, mã và tính nhất quán sự kiện, hội tụ Cox, đồng nhất thức CIF.
- Audit **không thay thế** đối chiếu implementation độc lập, đánh giá dự báo ngoài mẫu, xác nhận thiết kế nghiên cứu hay phản biện thống kê.
- **Cox biến thiên theo thời gian chưa được fit/đưa vào kết quả cuối** theo trạng thái dự án hiện tại. Kiểm tra dữ liệu quý chỉ mô tả panel, không phải kết quả mô hình.

## 14. Bằng chứng & hàm ý

- Trang liệt kê năm bài nghiên cứu và báo cáo FCIC làm tài liệu nền. Đây là điểm xuất phát; nhóm vẫn cần đọc toàn văn và tự tổng hợp thành câu hỏi/lập luận.
- Hàm ý hiện có bị giới hạn bởi dữ liệu: default và prepayment cạnh tranh; có thể theo dõi CIF/vintage; giá nhà, thất nghiệp, negative equity và securitization chưa được mô hình hóa đầy đủ.
- **Bài học 2008** chỉ là bối cảnh về quản trị, chuẩn cho vay và chứng khoán hóa từ báo cáo FCIC. Dữ liệu bắt đầu 2016 nên không thể kiểm định hay tái hiện khủng hoảng 2008.
- Lộ trình kiểm chứng ghi các việc còn thiếu: benchmark Fine–Gray; tạo interval start–stop và fit Cox biến thiên theo thời gian; đánh giá ngoài mẫu theo thời gian bằng calibration/discrimination.
- **Khung bảo vệ** là dàn ý và câu hỏi luyện tập, chưa phải slide hay bài thuyết trình hoàn chỉnh.
- Bảng tiêu chí môn học ghi trọng số: tổng quan tài liệu 15%, dữ liệu/tái lập 20%, phương pháp 25%, hàm ý tài chính 25%, trình bày/phản biện 15%. Nhóm vẫn phải hoàn thiện tổng hợp tài liệu, slide, phân vai, nhật ký AI và phản biện chéo.

## 15. Từ điển thuật ngữ

| Thuật ngữ | Nghĩa dễ hiểu |
|---|---|
| Loan ID | Mã định danh khoản vay. |
| Censored / kiểm duyệt | Kết thúc theo dõi chưa ghi nhận default hay prepayment; không có nghĩa khoản vay sẽ không bao giờ gặp sự kiện. |
| Competing risk | Sự kiện khiến một sự kiện khác không thể xảy ra tiếp theo trong cùng tiến trình, như trả trước trước vỡ nợ. |
| Survival S(t) | Xác suất chưa có kết cục kết thúc nào đến thời điểm t. |
| CIF | Xác suất tích lũy của một loại sự kiện đến t, có tính competing events. |
| Hazard | Tốc độ/nguy cơ tức thời xảy ra sự kiện trong nhóm còn có nguy cơ ngay trước thời điểm đó. |
| HR | Tỷ số hazard theo mô hình; không phải tỷ số xác suất trực tiếp. |
| 95% CI | Khoảng bất định theo phương pháp đã dùng; chứa HR=1 thường nghĩa là chưa thấy khác biệt rõ ở mức 5%. |
| Vintage | Nhóm khoản vay theo năm phát hành/kỳ khởi tạo. |
| PD | Xác suất vỡ nợ; cần nói rõ kỳ hạn, quần thể và phương pháp. |
| EAD / LGD / ECL | Phơi nhiễm khi vỡ nợ / tỷ lệ tổn thất khi vỡ nợ / tổn thất tín dụng kỳ vọng. |
| PH | Giả định tỷ số hazard không đổi theo thời gian. |
| Complete case | Ước lượng chỉ dùng quan sát đủ dữ liệu ở các trường bắt buộc. |

## 16. Khi trình bày kết quả, nhớ

1. Ghi rõ mốc và đại lượng, ví dụ “default CIF 60 tháng”, không chỉ nói “PD”.
2. Không gọi tỷ lệ thô là PD kỳ hạn; không gọi 1 − KM là default CIF.
3. HR là liên hệ có điều kiện trong mô hình, không chứng minh nguyên nhân hay xác suất cá nhân.
4. Nêu CI, kích thước risk set và giới hạn phần đuôi.
5. Nói rõ Fine–Gray tự cài chưa benchmark, Cox biến thiên theo thời gian chưa fit, và dự báo chưa đánh giá ngoài mẫu.
6. Audit PASS chỉ có nghĩa phép kiểm tra cụ thể đạt, không phải nghiên cứu đã được xác thực toàn diện.
7. Không suy luận nguyên nhân khủng hoảng 2008 từ mẫu dữ liệu bắt đầu năm 2016.

