from langgraph.graph import StateGraph, END
from app.graph.nodes import (
    route_message,
    chef_agent,
    nutritionist_agent,
    groceries_agent,
    merge_responses,
)

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("router", route_message)
    graph.add_node("chef", chef_agent)
    graph.add_node("nutritionist", nutritionist_agent)
    graph.add_node("groceries", groceries_agent)
    graph.add_node("merge", merge_responses)

    graph.set_entry_point("router")

    def route_to_agents(state: dict):
        agents = state.get("agents", ["chef"])
        # Return first agent — parallel execution handled by sequential calls
        return agents[0]

    graph.add_conditional_edges(
        "router",
        route_to_agents,
        {
            "chef": "chef",
            "nutritionist": "nutritionist",
            "groceries": "groceries",
        }
    )

    # After each agent, check if more agents needed
    def check_more_agents(state: dict):
        agents = state.get("agents", [])
        done = state.get("agents_done", [])
        remaining = [a for a in agents if a not in done]
        if len(remaining) > 1:
            next_agent = remaining[1]
            state.setdefault("agents_done", []).append(agents[0])
            return next_agent
        return "merge"

    graph.add_conditional_edges("chef", check_more_agents, {
        "nutritionist": "nutritionist",
        "groceries": "groceries",
        "merge": "merge"
    })

    graph.add_conditional_edges("nutritionist", check_more_agents, {
        "chef": "chef",
        "groceries": "groceries",
        "merge": "merge"
    })

    graph.add_conditional_edges("groceries", check_more_agents, {
        "chef": "chef",
        "nutritionist": "nutritionist",
        "merge": "merge"
    })

    graph.add_edge("merge", END)

    return graph.compile()

recommendation_graph = build_graph()