from policy import Policy
import numpy as np

class Policy2312059(Policy):
    def __init__(self):
        # Student code here
        self.epsilon = 0.01
        pass

    def get_action(self, observation, info):
        # Student code here

        list_prods = observation["products"]
        stocks = observation["stocks"]

        prod_size = [0, 0]
        stock_idx = -1
        pos_x, pos_y = None, None

        # Step 1: Classify products into wide and narrow dynamically
        wide_prods = []
        narrow_prods = []
        threshold = self.epsilon / (2 + self.epsilon)
        for prod in list_prods:
            if prod["quantity"] > 0:
                if prod["size"][0] > threshold:
                    wide_prods.append(prod)
                else:
                    narrow_prods.append(prod)

        # Step 2: Attempt to place wide products first
        for prod in wide_prods:
            prod_size = prod["size"]

            for i, stock in enumerate(stocks):
                stock_w, stock_h = self._get_stock_size_(stock)
                prod_w, prod_h = prod_size

                if stock_w < prod_w or stock_h < prod_h:
                    continue

                for x in range(stock_w - prod_w + 1):
                    for y in range(stock_h - prod_h + 1):
                        if self._can_place_(stock, (x, y), prod_size):
                            stock_idx = i
                            pos_x, pos_y = x, y
                            break
                    if pos_x is not None and pos_y is not None:
                        break

                if pos_x is not None and pos_y is not None:
                    break

            if pos_x is not None and pos_y is not None:
                break

        # Step 3: If no wide product can be placed, try narrow products
        if pos_x is None and pos_y is None:
            for prod in narrow_prods:
                prod_size = prod["size"]

                for i, stock in enumerate(stocks):
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod_size

                    if stock_w < prod_w or stock_h < prod_h:
                        continue

                    for x in range(stock_w - prod_w + 1):
                        for y in range(stock_h - prod_h + 1):
                            if self._can_place_(stock, (x, y), prod_size):
                                stock_idx = i
                                pos_x, pos_y = x, y
                                break
                        if pos_x is not None and pos_y is not None:
                            break

                    if pos_x is not None and pos_y is not None:
                        break

                if pos_x is not None and pos_y is not None:
                    break

        # Return the action
        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}
        pass

    # Student code here
    # You can add more functions if needed

class Policy2312055(Policy):
    def __init__(self, epsilon=0.1):
        """
        Khởi tạo chính sách AFPTAS với tham số epsilon.
        """
        self.epsilon = epsilon  # Sai số gần đúng
        self.actions = []  # Danh sách các hành động sẽ thực hiện

    def get_action(self, observation, info):
        """
        Trả về hành động tiếp theo dựa trên danh sách hành động đã sinh ra.
        Nếu danh sách hành động trống, tạo mới bằng thuật toán AFPTAS.
        """
        if not self.actions:
            self.actions = self.generate_all_actions(observation, info)

        # Trả về hành động đầu tiên trong danh sách
        if self.actions:
            print(self.actions[0])
            return self.actions.pop(0)
        else:
            return {"stock_idx": -1, "size": (0, 0), "position": (0, 0)}

    def generate_all_actions(self, observation, info):
        """
        Sinh ra toàn bộ danh sách hành động bằng thuật toán AFPTAS.
        """
        products = observation["products"]
        stocks = observation["stocks"]

        # Phân loại sản phẩm
        wide_prods, narrow_prods = self.classify_items(products, stocks)

        # Gom nhóm sản phẩm nhỏ
        avg_stock_width = sum(self._get_stock_size_(s)[0] for s in stocks) / len(stocks)
        grouped_narrow_prods = self.group_small_items(narrow_prods, avg_stock_width)

        # Tạo danh sách hành động
        actions = []

        # Đóng gói sản phẩm lớn bằng First Fit Decreasing
        actions += self.first_fit_decreasing(wide_prods, stocks)

        # Lấp đầy không gian trống với sản phẩm nhỏ
        for stock_idx, stock in enumerate(stocks):
            actions += self.fill_remaining_space(stock, grouped_narrow_prods, stock_idx)

        return actions

    def classify_items(self, products, stocks):
        """
        Phân loại sản phẩm thành wide và narrow dựa trên ngưỡng epsilon.
        """
        avg_stock_width = sum(self._get_stock_size_(s)[0] for s in stocks) / len(stocks)
        threshold = self.epsilon / (2 + self.epsilon) * avg_stock_width

        wide_prods = [p for p in products if p["size"][0] > threshold]
        narrow_prods = [p for p in products if p["size"][0] <= threshold]

        return wide_prods, narrow_prods

    def group_small_items(self, narrow_prods, max_width):
        """
        Gom nhóm sản phẩm nhỏ thành các khối lớn hơn để đóng gói hiệu quả.
        """
        grouped_items = []
        current_width, max_height = 0, 0

        for prod in narrow_prods:
            prod_w, prod_h = prod["size"]
            if current_width + prod_w > max_width:
                grouped_items.append({"size": (current_width, max_height)})
                current_width, max_height = 0, 0
            current_width += prod_w
            max_height = max(max_height, prod_h)

        if current_width > 0:
            grouped_items.append({"size": (current_width, max_height)})

        return grouped_items

    def first_fit_decreasing(self, items, stocks):
        """
        Đóng gói sản phẩm lớn theo chiến lược First Fit Decreasing.
        """
        actions = []
        items = sorted(items, key=lambda x: x["size"][0] * x["size"][1], reverse=True)
        pos_x, pos_y = 0, 0

        for item in items:
            if item["quantity"] <= 0: continue
            for stock_idx, stock in enumerate(stocks):
                stock_w, stock_h = self._get_stock_size_(stock)
                item_w, item_h = item["size"]
                
                if stock_w < item_w or stock_h < item_h:
                        continue
                
                pos_x, pos_y = None, None
                for x in range(stock_w - item_w + 1):
                    for y in range(stock_h - item_h + 1):
                        if self._can_place_(stock, (x, y), item["size"]):
                            pos_x, pos_y = x, y
                            break
                    if pos_x is not None and pos_y is not None:
                        break

                if pos_x is not None and pos_y is not None:
                    actions.append({
                        "stock_idx": stock_idx,
                        "size": item["size"],
                        "position": (pos_x, pos_y),
                    })
                    break
   
            if pos_x is not None and pos_y is not None:
                break
        return actions

    def fill_remaining_space(self, stock, small_items, stock_idx):
        """
        Lấp đầy khoảng trống bằng các sản phẩm nhỏ.
        """
        actions = []
        stock_w, stock_h = self._get_stock_size_(stock)

        for item in small_items:
            item_w, item_h = item["size"]

            if stock_w < item_w or stock_h < item_h:
                continue

            pos_x, pos_y = None, None
            for x in range(stock_w - item_w + 1):
                for y in range(stock_h - item_h + 1):
                    if self._can_place_(stock, (x, y), item["size"]):
                        actions.append({
                            "stock_idx": stock_idx,
                            "size": item["size"],
                            "position": (x, y),
                        })
                        break
        return actions