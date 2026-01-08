from typing import List
from models import ConversationMessage, OperatorResponse, ImpactAnalysis


def generate_initial_question(impact: ImpactAnalysis) -> str:
    """
    Generate the initial question to ask the operator about a disruption.
    Varies based on severity and impact characteristics.
    """
    # Varied greetings based on severity and context
    if impact.severity_score >= 8:
        if impact.high_priority_count > 2:
            greeting = "Critical alert – we have multiple high-priority shipments at risk."
        else:
            greeting = "Urgent situation detected. Immediate attention required."
    elif impact.severity_score >= 6:
        greeting = "Heads up – moderate disruption flagged for review."
    else:
        greeting = "New disruption detected. Low severity, but worth monitoring."
    
    # Build impact summary with better spacing
    question = f"{greeting}\n\n"
    question += "**Impact Overview:**\n\n"
    question += f"• {impact.total_shipments_impacted} shipments affected\n"
    question += f"• {impact.high_priority_count} high-priority items\n"
    question += f"• {len(impact.affected_routes)} routes impacted\n"
    question += f"• Severity score: {impact.severity_score:.1f}/10\n\n"
    
    # Context-aware urgency message
    if impact.high_priority_count > 0:
        if impact.high_priority_count == 1:
            question += (
                "**Priority Concern:**\n\n"
                "One high-priority shipment needs a decision. Rerouting will increase costs "
                "but could prevent significant delays.\n\n"
            )
        elif impact.high_priority_count <= 3:
            question += (
                f"**Priority Concern:**\n\n"
                f"{impact.high_priority_count} high-priority shipments require immediate decisions. "
                f"Alternative routing is available but will impact operational costs.\n\n"
            )
        else:
            question += (
                f"**Critical Priority:**\n\n"
                f"{impact.high_priority_count} high-priority shipments are at risk. "
                f"This situation requires careful cost-benefit analysis for rerouting options.\n\n"
            )
    
    # Clear, structured questions
    question += "**Decision Points:**\n\n"
    question += "1. **Rerouting Authorization** – Approve alternative routes? (increases costs)\n"
    question += "2. **Cost Threshold** – Maximum acceptable cost increase? (percentage)\n"
    question += "3. **Priority Handling** – Focus on high-priority shipments first?\n\n"
    question += "Provide your guidance and I'll generate an optimized action plan."
    
    return question


def generate_decision_summary(
    decisions: List,
    operator_response: OperatorResponse
) -> str:
    """
    Generate a summary of all decisions made.
    Varies based on decision mix and operator constraints.
    """
    reroute_count = sum(1 for d in decisions if d.action.value == "reroute")
    delay_count = sum(1 for d in decisions if d.action.value == "delay")
    escalate_count = sum(1 for d in decisions if d.action.value == "escalate")
    
    # Varied opening based on decision distribution
    if reroute_count > 0 and delay_count > 0 and escalate_count > 0:
        opening = "Analysis complete – mixed strategy recommended"
    elif reroute_count > delay_count + escalate_count:
        opening = "Analysis complete – aggressive rerouting strategy"
    elif delay_count > reroute_count + escalate_count:
        opening = "Analysis complete – conservative delay strategy"
    elif escalate_count > 0:
        opening = "Analysis complete – management review required"
    else:
        opening = "Analysis complete – action plan ready"
    
    summary = f"**{opening}**\n\n"
    summary += f"Processed {len(decisions)} shipments within your constraints:\n\n"
    
    # Decision breakdown with context
    if reroute_count > 0:
        summary += f"**Reroute:** {reroute_count} shipment{'s' if reroute_count != 1 else ''}\n"
    if delay_count > 0:
        summary += f"**Delay:** {delay_count} shipment{'s' if delay_count != 1 else ''}\n"
    if escalate_count > 0:
        summary += f"**Escalate:** {escalate_count} shipment{'s' if escalate_count != 1 else ''}\n"
    
    summary += "\n---\n\n"
    
    # Detailed rationale with varied explanations
    if reroute_count > 0:
        cost_limit = operator_response.max_cost_increase_percent
        if reroute_count == 1:
            summary += (
                f"**Rerouting Decision:**\n\n"
                f"One shipment redirected to alternative route. Time-critical delivery "
                f"justifies the cost increase (within {cost_limit}% threshold).\n\n"
            )
        else:
            summary += (
                f"**Rerouting Decisions:**\n\n"
                f"{reroute_count} shipments redirected to alternative routes. All reroutes "
                f"stay within your {cost_limit}% cost threshold while maintaining delivery commitments.\n\n"
            )
    
    if delay_count > 0:
        if delay_count == 1:
            summary += (
                "**Delay Decision:**\n\n"
                "One shipment scheduled to wait. Sufficient buffer time available, "
                "making this the most cost-effective approach.\n\n"
            )
        elif delay_count <= 3:
            summary += (
                f"**Delay Decisions:**\n\n"
                f"{delay_count} shipments can absorb the disruption delay. Their tolerance "
                f"windows accommodate waiting, avoiding unnecessary rerouting costs.\n\n"
            )
        else:
            summary += (
                f"**Delay Decisions:**\n\n"
                f"{delay_count} shipments have adequate delay tolerance. Cost-benefit analysis "
                f"favors waiting over immediate rerouting for these items.\n\n"
            )
    
    if escalate_count > 0:
        if escalate_count == 1:
            summary += (
                "**Escalation Required:**\n\n"
                "One shipment flagged for management review. Complex constraints or "
                "lack of viable alternatives require senior decision-making.\n\n"
            )
        else:
            summary += (
                f"**Escalations Required:**\n\n"
                f"{escalate_count} shipments need management review. These cases involve "
                f"complex trade-offs or insufficient routing alternatives.\n\n"
            )
    
    # Clear next steps
    summary += "**Next Steps:**\n\n"
    summary += "Review action tickets in the right panel. Each ticket contains detailed "
    summary += "rationale and required actions for implementation."
    
    return summary


def parse_operator_input(user_message: str) -> dict:
    """
    Parse operator's natural language input.
    In a full implementation, this would use NLP/AI.
    For now, we use simple keyword matching.
    """
    message_lower = user_message.lower()
    
    # Default values
    allow_reroute = True
    max_cost_increase = 25.0
    prioritize_high_priority = True
    
    # Parse reroute permission
    if any(word in message_lower for word in ["no reroute", "don't reroute", "avoid reroute"]):
        allow_reroute = False
    
    # Parse cost tolerance (look for numbers followed by %)
    import re
    cost_match = re.search(r'(\d+(?:\.\d+)?)\s*%', user_message)
    if cost_match:
        max_cost_increase = float(cost_match.group(1))
    
    # Parse priority preference
    if any(word in message_lower for word in ["all shipments", "treat equally", "no priority"]):
        prioritize_high_priority = False
    
    return {
        "allow_reroute": allow_reroute,
        "max_cost_increase_percent": max_cost_increase,
        "prioritize_high_priority": prioritize_high_priority
    }


def create_conversation_message(role: str, content: str) -> ConversationMessage:
    """Create a conversation message"""
    return ConversationMessage(
        role=role,
        content=content
    )
