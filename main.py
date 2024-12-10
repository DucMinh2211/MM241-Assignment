import gym_cutting_stock
import gymnasium as gym
from policy import GreedyPolicy, RandomPolicy
from student_submissions.s2312059.policy2312059_test import Policy2312059
import numpy as np

# Create the environment
env = gym.make(
    "gym_cutting_stock/CuttingStock-v0",
    render_mode="human",  # Comment this line to disable rendering
    min_w=50,
    min_h=50,
    max_w=100,
    max_h=100,
    num_stocks=15,
    max_product_type=10,
    max_product_per_type=15,
    seed=42,
)
NUM_EPISODES = 100

if __name__ == "__main__":
    # Reset the environment
    observation, info = env.reset(seed=42)

    # Test GreedyPolicy
    # gd_policy = GreedyPolicy()
    # ep = 0
    # while ep < NUM_EPISODES:
    #     action = gd_policy.get_action(observation, info)
    #     observation, reward, terminated, truncated, info = env.step(action)
    #     print(info)


    #     if terminated or truncated:
    #         observation, info = env.reset(seed=ep)
    #         print(info)
    #         ep += 1

    # # Reset the environment
    # observation, info = env.reset(seed=42)

    # # Test RandomPolicy
    # rd_policy = RandomPolicy()
    # ep = 0
    # while ep < NUM_EPISODES:
    #     action = rd_policy.get_action(observation, info)
    #     observation, reward, terminated, truncated, info = env.step(action)

    #     if terminated or truncated:
    #         observation, info = env.reset(seed=ep)
    #         print(info)
    #         ep += 1

    # Uncomment the following code to test your policy
    # Reset the environment
    observation, info = env.reset(seed=42)
    print(info)

    policy2312059 = Policy2312059()
    print("\n")
    print("-- THÔNG TIN ĐẦU VÀO --")
    print("- Products -")
    print("STT Product | Product Size | Quantity |")
    prod_quantities = 0
    for i, prod in enumerate(observation["products"]):
        print("product no." + str(i) + " | " + str(prod["size"]) + " | " + str(prod["quantity"]))
        prod_quantities += prod["quantity"] 

    print("- Stocks -")
    print("STT Stock | Size")
    for i, stock in enumerate(observation["stocks"]):
        print("Stock no." + str(i) + " | " + str([tuple(map(int, policy2312059._get_stock_size_(stock)))] ) )

    print("\n")

    for _ in range(2000):
        action = policy2312059.get_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)
        print(info)

        if terminated or truncated:
            used_area, total_area, used_stocks = policy2312059.filled_ratio(observation)
            print("\n")
            print("-- KẾT QUẢ --")
            print("Số lượng product còn lại: " + str(sum(p["quantity"] for p in observation["products"])) + " / " + str(prod_quantities))
            print("Số lượng stock sử dụng : " + str(used_stocks) + " / " + str(len(observation["stocks"])))
            print("Diện tích đã sử dụng : " + str(used_area))
            print("Diện tích các stock được sử dụng : " + str(total_area))
            print("Tỷ lệ diện tích sử dụng: " + str(used_area/total_area))
            print("- CỤ THỂ -")
            print("STT stock | các Products | chiến lược | Thừa |")
            strategy = {}
            for action in policy2312059.actions:
                stock_idx = action["stock_idx"]
                if stock_idx not in strategy: strategy[stock_idx] = []
                strategy[stock_idx].append(action["prod_idx"])
            for i, stock in enumerate(observation["stocks"]):
                if np.any(stock >= 0): 
                    product_sizes = ", ".join(
                        str(observation["products"][prod_idx]["size"]) for prod_idx in strategy[i]
                    )
                    print("No." + str(i) + " | " + str(strategy[i]) + " | " 
                    + product_sizes + " | " + str(np.sum(stock >= 0)))
                else: 
                    print("No." + str(i) + " ko dùng")
            print("END")
            observation, info = env.reset()
            break


env.close()
