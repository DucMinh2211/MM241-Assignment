from policy import Policy
import numpy as np


class Policy2312059(Policy):
    def __init__(self):
        """
        Khởi tạo policy dựa trên AFPTAS.
        """
        self.epsilon = 0.5  # Tham số epsilon-greedy
        self.avg_stock_width = None
        self.max_stock_width = None
        self.min_stock_width = None
        self.current_stock = None
        self.threshold = None
        self.actions = []


    def get_action(self, observation, info):
        products = observation["products"]
        stocks = observation["stocks"]
        filled_ratio = info["filled_ratio"]

        if not self.avg_stock_width:
            self.avg_stock_width = sum(self._get_stock_size_(s)[0] for s in stocks) / len(stocks)
            self.max_stock_width = max(self._get_stock_size_(s)[0] for s in stocks)
            self.min_stock_width = min(self._get_stock_size_(s)[0] for s in stocks)

            self.epsilon = (
                (self.max_stock_width - self.min_stock_width) / self.avg_stock_width
            ) * (
                sum(p["size"][0] * p["size"][1] * p["quantity"] for p in products) / 
                sum(self._get_stock_size_(s)[0] * self._get_stock_size_(s)[1] for s in stocks)
            )
            # print(self.epsilon)

        if len(products) < 2:
            return self.best_fit_packing(products, stocks)

        # Phân loại sản phẩm
        wide_prods, narrow_prods = self.classify_items(products, self.avg_stock_width)

        if np.sum([p["quantity"] > 0 for p in wide_prods]) > 0: 
            action = self.first_fit_decreasing(wide_prods, stocks)
            # print("w")
        else:  # Nếu hết wide_prods -> sang narrow_prods
            if not self.current_stock:
                self.current_stock = 0
            for stock_idx, stock in enumerate(stocks[self.current_stock:], start=self.current_stock):
                action = self.fill_remaining_space(stock, narrow_prods, stock_idx)
                if action is not None:
                    self.actions.append(action)
                    break
            self.current_stock = stock_idx
        if not action:
            action = self.best_fit_packing(narrow_prods, stocks)

        if not action:
            return {"stock_idx": 0, "size": (0, 0), "position": (0, 0)}
        # print(action)
        return action


    def classify_items(self, products, avg_stock_width):
        """
        Phân loại sản phẩm thành wide và narrow dựa trên ngưỡng epsilon.
        """
        threshold = self.epsilon / (2 + self.epsilon) * avg_stock_width
        self.threshold = threshold
        wide_prods = [p for p in products if p["size"][0] > threshold]
        narrow_prods = [p for p in products if p["size"][0] <= threshold]
        # print({"len_nr_prods" : len(narrow_prods), "len_wi_prods" : len(wide_prods)})
        return wide_prods, narrow_prods

    def first_fit_decreasing(self, wide_prods, stocks):
        """
        Đóng gói sản phẩm 'wide' theo chiến lược First Fit Decreasing.
        """
        # Sắp xếp sản phẩm theo diện tích giảm dần
        sorted_wide_prods = sorted(wide_prods, key=lambda p: p["size"][0] * p["size"][1], reverse=True)

        for i, prod in enumerate(sorted_wide_prods):
            if prod["quantity"] <= 0:
                continue
            prod_w, prod_h = prod["size"]
            for stock_idx, stock in enumerate(stocks):
                position = self.find_position_min_waste(stock, (prod_w, prod_h))
                if position:
                    action = {
                        "type" : "wide",
                        "stock_idx": stock_idx,
                        "prod_idx" : i,
                        "size": prod["size"],
                        "position": position,
                    }
                    self.actions.append(action)
                    return action

    def fill_remaining_space(self, stock, narrow_prods, stock_idx):
        """
        Lấp đầy khoảng trống bằng các sản phẩm nhỏ.
        """
        for i, prod in enumerate(narrow_prods):
            if prod["quantity"] <= 0:
                continue
            prod_w, prod_h = prod["size"]
            position = self.find_position(stock, (prod_w, prod_h))
            if position:
                action = {
                    "type": "narrow",
                    "stock_idx": stock_idx,
                    "prod_idx" : i,
                    "size": prod["size"],
                    "position": position,
                }
                return action
        return None
    
    def greedy(self, narrow_prods, stocks):
        list_prods = narrow_prods

        prod_size = [0, 0]
        stock_idx = -1
        prod_idx = -1
        pos_x, pos_y = 0, 0

        # Pick a product that has quality > 0
        for i, prod in enumerate(list_prods):
            if prod["quantity"] > 0:
                prod_size = prod["size"]

                # Loop through all stocks
                for idx, stock in enumerate(stocks):
                    stock_w, stock_h = self._get_stock_size_(stock)
                    prod_w, prod_h = prod_size

                    if stock_w < prod_w or stock_h < prod_h:
                        continue

                    pos_x, pos_y = None, None
                    for x in range(stock_w - prod_w + 1):
                        for y in range(stock_h - prod_h + 1):
                            if self._can_place_(stock, (x, y), prod_size):
                                pos_x, pos_y = x, y
                                break
                        if pos_x is not None and pos_y is not None:
                            break

                    if pos_x is not None and pos_y is not None:
                        stock_idx = idx
                        prod_idx = i
                        break

                if pos_x is not None and pos_y is not None:
                    break
        return {"stock_idx": stock_idx, "prod_idx" : prod_idx,"size": prod_size, "position": (pos_x, pos_y)}

    def find_position(self, stock, prod_size):
        """
        Tìm vị trí khả thi đầu tiên trong kho cho sản phẩm.
        """
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size

        if prod_w > stock_w or prod_h > stock_h:
            return None

        # Duyệt qua toàn bộ không gian trong kho
        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    return (x, y)
        return None
    

    #
    # BEST_FIT_PACKING
    #
    def best_fit_packing(self, products, stocks):
        """
        Chiến lược đóng gói sản phẩm với tiêu chí Best Fit.
        """
        products = sorted(products, key=lambda p: p["size"][0] * p["size"][1], reverse=True)

        for i, prod in enumerate(products):
            if prod["quantity"] <= 0:
                continue
            prod_w, prod_h = prod["size"]

            best_stock_idx = None
            best_position = None
            best_score = float("inf")  # Score thấp nhất là tốt nhất
            
            for stock_idx, stock in enumerate(stocks):
                stock_w, stock_h = self._get_stock_size_(stock)

                # Bỏ qua kho nếu kích thước không phù hợp
                if prod_w > stock_w or prod_h > stock_h:
                    continue

                # Tìm vị trí phù hợp đầu tiên trong kho
                position = self.find_position_min_waste(stock, prod["size"])
                if position:
                    # Tính điểm dựa trên tiêu chí:
                    total_area = stock_w * stock_h
                    used_area = np.sum(stock >= 0) + prod_w * prod_h
                    waste = total_area - used_area
                    
                    score = waste

                    if score < best_score:
                        best_score = score
                        best_stock_idx = stock_idx
                        best_position = position

            if best_stock_idx is not None and best_position is not None:
                action = {
                    "stock_idx": best_stock_idx,
                    "size": prod["size"],
                    "prod_idx" : i,
                    "position": best_position,
                }
                self.actions.append(action)
                return action  # Trả về ngay khi tìm được
        return None

    def find_position_min_waste(self, stock, prod_size):
        """
        Tìm vị trí khả thi với lãng phí không gian tối thiểu.
        """
        stock_w, stock_h = self._get_stock_size_(stock)
        prod_w, prod_h = prod_size

        if prod_w > stock_w or prod_h > stock_h:
            return None

        best_position = None
        min_waste = float("inf")

        for x in range(stock_w - prod_w + 1):
            for y in range(stock_h - prod_h + 1):
                if self._can_place_(stock, (x, y), prod_size):
                    # Tính lãng phí không gian
                    total_area = stock_w * stock_h
                    used_area = np.sum(stock >= 0) + prod_w * prod_h
                    waste = total_area - used_area
                    if waste < min_waste:
                        min_waste = waste
                        best_position = (x, y)

        return best_position

    def filled_ratio(self, observation):
        stocks = observation["stocks"]
        used_area = 0
        total_area = 0
        used_stocks = np.sum(np.any(stock >= 0) for stock in stocks)

        for stock in stocks: 
            stock_w, stock_h = self._get_stock_size_(stock)
            if (np.any(stock >= 0)): total_area += stock_w * stock_h
            used_area += np.sum(stock >= 0)  # Số lượng ô đã sử dụng
        return (used_area, total_area, used_stocks) 
