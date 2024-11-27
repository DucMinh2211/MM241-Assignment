from policy import Policy


def Policy2210xxx(Policy):
    def __init__(self):
        # Student code here
        pass

    def get_action(self, observation, info):
        # Student code here
        pass

    # Student code here
    # You can add more functions if needed
    def fractional_strip_packing(rectangles, strip_width):
        """
        Áp dụng Fractional Strip Packing cho nhóm hình chữ nhật rộng.
        Parameters:
            rectangles (list): Danh sách các hình chữ nhật (width, height).
            strip_width (float): Chiều rộng cố định của tấm vật liệu.
        Returns:
            tuple: (chiều cao ước tính, tổng diện tích).
        """
        total_area = sum(width * height for width, height in rectangles)
        height = math.ceil(total_area / strip_width)
        print(f"Fractional Strip Packing: Tổng diện tích = {total_area}, Chiều cao gần tối ưu = {height}")
        return height, total_area

    def next_fit_decreasing_height(rectangles, strip_width, start_height):
        """
        Sử dụng thuật toán NFDH để đóng gói các hình chữ nhật hẹp.
        Parameters:
            rectangles (list): Danh sách các hình chữ nhật (width, height).
            strip_width (float): Chiều rộng cố định của tấm vật liệu.
            start_height (float): Chiều cao bắt đầu để đóng gói.
        Returns:
            float: Chiều cao sử dụng sau khi thêm hình chữ nhật hẹp.
        """
        rectangles.sort(key=lambda x: x[1], reverse=True)  # Sắp xếp theo chiều cao giảm dần
        current_width = 0
        current_height = start_height
        max_height_in_level = 0

        print("\nThêm hình chữ nhật hẹp bằng Next-Fit-Decreasing-Height:")
        for width, height in rectangles:
            if current_width + width <= strip_width:  # Đặt hình vào mức hiện tại
                print(f"  Đặt hình ({width}, {height}) vào mức hiện tại.")
                current_width += width
                max_height_in_level = max(max_height_in_level, height)
            else:  # Tạo mức mới
                print(f"  Tạo mức mới do ({width}, {height}) không vừa trong mức hiện tại.")
                current_width = width
                current_height += max_height_in_level
                max_height_in_level = height

        print(f"Chiều cao sau khi thêm hình chữ nhật hẹp = {current_height + max_height_in_level}")
        return current_height + max_height_in_level

    def two_dimensional_cutting_stock(rectangles, strip_width, epsilon=0.1):
        """
        Thuật toán giải bài toán 2D Cutting Stock Problem gần tối ưu.
        Parameters:
            rectangles (list): Danh sách các hình chữ nhật (width, height).
            strip_width (float): Chiều rộng cố định của tấm vật liệu.
            epsilon (float): Tham số điều chỉnh độ chính xác.
        Returns:
            float: Chiều cao sử dụng tối ưu gần đúng.
        """
        print("\n=== Bắt đầu giải bài toán 2D Cutting Stock Problem ===")

        # Bước 1: Phân loại hình chữ nhật
        threshold = epsilon / (2 + epsilon)
        wide_rectangles = [r for r in rectangles if r[0] > threshold]
        narrow_rectangles = [r for r in rectangles if r[0] <= threshold]
        print(f"Phân loại: {len(wide_rectangles)} hình chữ nhật rộng, {len(narrow_rectangles)} hình chữ nhật hẹp.")

        # Bước 2: Gom nhóm các hình chữ nhật rộng
        wide_rectangles.sort(key=lambda x: x[0], reverse=True)
        num_groups = min(math.ceil(1 / threshold), len(wide_rectangles))  # Đảm bảo số nhóm <= số hình
        grouped_widths = [wide_rectangles[i::num_groups] for i in range(num_groups)]

        grouped_rectangles = []
        for group in grouped_widths:
            if group:  # Kiểm tra nhóm không rỗng
                max_width = max(r[0] for r in group)
                grouped_rectangles.extend([(max_width, r[1]) for r in group])
        print(f"Đã gom nhóm hình chữ nhật rộng thành {len(grouped_rectangles)} hình.")

        # Bước 3: Áp dụng Fractional Strip Packing
        fractional_height, total_area = fractional_strip_packing(grouped_rectangles, strip_width)

        # Bước 4: Chuyển nghiệm phân số thành nghiệm nguyên
        integral_height = math.ceil(fractional_height)
        print(f"Nghiệm phân số chuyển thành chiều cao nguyên: {integral_height}")

        # Bước 5: Thêm các hình chữ nhật hẹp
        final_height = next_fit_decreasing_height(narrow_rectangles, strip_width, integral_height)

        print(f"\n=== Kết quả cuối cùng ===")
        print(f"Chiều cao sử dụng gần tối ưu: {final_height}")
        return final_height
# Ví dụ sử dụng
rectangles = [
    (0.3, 0.5), (0.7, 0.2), (0.4, 0.8), (0.6, 0.4),
    (0.2, 0.6), (0.5, 0.5), (0.1, 0.3), (0.8, 0.1)
]
strip_width = 1.0
epsilon = 0.1

result_height = two_dimensional_cutting_stock(rectangles, strip_width, epsilon)
print(f"\nChiều cao tối ưu gần đúng: {result_height}")