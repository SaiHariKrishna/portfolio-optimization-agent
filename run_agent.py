from bonds import load_portfolio
from agent import portfolio_agent

portfolio = load_portfolio()

initial_state = {
    "bonds": portfolio.to_dict(orient="records"),
    "target_duration": 4.0
}

result = portfolio_agent.invoke(initial_state)

print("Decision:", result["decision"])
print("Durations:", result["durations"])
print("Optimized Weights:", result["optimized_weights"])
