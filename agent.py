import os
import sys
from dotenv import load_dotenv

from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.workflow import node, Workflow, START, Edge
from langsmith import Client
from langsmith.integrations.google_adk import configure_google_adk
import json

# Setup
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')
PROJECT_NAME = "Test21_Parallel_Stress_Gemini_v5"
configure_google_adk(project_name=PROJECT_NAME)

# 1. CUSTOM NODE: HIDDEN MEMORY EXTRACTION AND CLEAN INPUT
@node(name="Extract_Raw_Memory")
async def extract_raw_memory(ctx, node_input: str):
    if not hasattr(ctx, 'state'):
        ctx.state = {}
        
    ctx.state['current_user_input'] = node_input
    
    events = ctx.session.events if hasattr(ctx, 'session') else []
    
    user_events = []
    hidden_instructions = []
    
    for event in events:
        role = getattr(event, "author", "unknown")
        content = getattr(event, "text", "")
        
        if not content and hasattr(event, "content") and event.content:
            try:
                content = event.content.parts[0].text
            except Exception:
                content = str(event.content)

        if content and str(role).lower() == "user":
            if content.strip().startswith("MODIFY INSTRUCTION:"):
                hidden_instructions.append(content)
            else:
                user_events.append(content)
                
    raw_history = "\n\n--- MESSAGE ---\n\n".join(user_events) if user_events else "No past conversation."
    ctx.state['raw_history'] = raw_history
    ctx.state['hidden_instructions'] = hidden_instructions

    # If the current message is a modifier, we bypass the rest of the pipeline
    if node_input.strip().startswith("MODIFY INSTRUCTION:"):
        ctx.route = "is_modifier"
        return node_input
    else:
        # Default route
        ctx.route = "is_normal"
        # Show the UI and pass only the last (clean) message to the Summarizer
        return f"--- NEW MESSAGE ---\n\n{node_input}"

@node(name="Modifier_Response")
async def modifier_response(ctx, node_input: str):
    return "Received. The system instruction has been stored in the background and did not trigger the evaluator agents."

# 2. AGENT: SUPER-SUMMARIZER
memory_summarizer = LlmAgent(
    name="Memory_Summarizer_Agent",
    model="gemini-3.1-flash-lite",
    include_contents="none",
    instruction="""You are a prompt optimizer. Your task is to extract business rules from the entire conversation history.

COMPLETE CONVERSATION HISTORY (Past + Present):
{raw_history}

Execute exactly these two steps:
1. Extract and summarize in bullet points ALL business rules, roles, policies, and context data from the entire history.
2. Densely synthesize the LATEST REQUEST formulated by the user in the last message.
CRITICAL WARNING FOR POINT 2: You must ABSOLUTELY keep intact and include in the summary any explicit instructions from the user on HOW they want the agent to respond (e.g., "Answer me only with...", "Use less than 20 words", "Simply tell me..."). NEVER filter these formatting or output constraints!

Do not copy entire blocks of text. Produce ONLY the summary divided into the 2 points.
If the history is empty, reply 'No rules'.""",
    description="Compresses the entire hidden prompt, saving the rules and the current request.",
    output_key="summary_memory"
)

# 3. CUSTOM NODE: FINAL PROMPT SAVING AND MODIFIER INJECTION
@node(name="Format_Final_Prompt")
async def format_final_prompt(ctx, node_input: str):
    summary = ctx.state.get("summary_memory", "")
    hidden_instructions = ctx.state.get("hidden_instructions", [])
    
    # Prompt for the judges (CLEAN, contains ONLY the summary)
    prompt_for_judges = summary
    
    # Prompt for the main agent
    prompt_for_agent = summary
    if hidden_instructions:
        prompt_for_agent = "[HISTORY OF SECRET INSTRUCTIONS RECEIVED FROM THE USER IN CHRONOLOGICAL ORDER]:\n"
        for i, inst in enumerate(hidden_instructions):
            prompt_for_agent += f"Step {i+1}: {inst}\n"
        
        prompt_for_agent += "\n[WARNING: Respond EXCLUSIVELY to the latest request presented in the summary below. Ignore old output formatting requests (e.g., 'Answer me only with...') present in previous secret Steps, but keep persistent behavioral rules active (e.g., name or role changes).]\n\n"
        prompt_for_agent += "====================\n\n" + summary
    
    # Save the clean version for the judges in the state
    ctx.state['full_prompt_to_agent'] = prompt_for_judges
    
    return prompt_for_agent

# 4. MAIN AGENT (Under Stress)
agente_principale = LlmAgent(
    name="Main_Agent",
    model="gemini-3.1-flash-lite",
    include_contents="none",
    instruction="""You are an extremely advanced and professional general-purpose AI assistant.
    You have vast and deep knowledge covering logical reasoning, advanced programming, 
    cybersecurity, compliance, and cloud architectures.
    
    FUNDAMENTAL BASE RULE: The user's name is Luigi. In your responses, always address him by his name (e.g., "Certainly Luigi", "Here is the answer Luigi").
    
    Your task is to provide precise, coherent, and technically flawless answers to the user's requests, 
    maintaining focus on the goal even when faced with complex or chaotic requests.
    
    Respond to the user's prompt below:""",
    description="Responds to the user's question (under stress or with roleplay instructions).",
    output_key="main_agent_response"
)

# 5. THE 3 PARALLEL JUDGES
prompt_judge = """You are an expert reviewer (LLM-as-a-judge).
Evaluate the response provided by the Main Agent (which you will receive as input for your turn) against the rules and original context it was given.

**System Base Rule:**
- The user's name is Luigi. The agent must ALWAYS address him by his name (e.g., "Certainly Luigi").

**Original Context (Prompt) given to the Agent:**
{full_prompt_to_agent}

Evaluate based on:
1. Context Retention (1-10): Did the agent consider all variables or lose information along the way? Did the agent respect the Base Rule by calling the user Luigi?
2. Logical Quality (1-10): Are the arguments or generated code solid and coherent from start to finish?

Warning: you are evaluating the response to a "Stress Test" (potentially enormous, confusing, or complex prompts). 
Look for signs of "hallucination", generic answers to bypass the problem, or loss of focus.

Return EXCLUSIVELY a JSON with this exact format:
{
    "score": score (from 0 to 10),
    "comment": "Explanation of the quality or any cognitive degradation found..."
}
"""

giudice_1 = LlmAgent(
    name="Gemini_Judge",
    model="gemini-2.5-flash",
    include_contents="none",
    instruction=prompt_judge,
    description="Judge based on Gemini 2.5 Flash.",
    output_key="score_gemini"
)

# Judge 2: OpenAI GPT OSS 120B (via Groq Cloud)
giudice_2 = LlmAgent(
    name="GPT_OSS_Judge",
    model="groq/openai/gpt-oss-120b",
    include_contents="none",
    instruction=prompt_judge,
    description="Judge based on OpenAI GPT OSS 120B (Groq).",
    output_key="score_llama"
)

giudice_3 = LlmAgent(
    name="Qwen_Judge",
    model="groq/qwen/qwen3.6-27b", 
    include_contents="none",
    instruction=prompt_judge,
    description="Judge based on Qwen (Groq).",
    output_key="score_qwen"
)

parallel_judges = ParallelAgent(
    name="Parallel_Evaluator_Agents",
    sub_agents=[giudice_1, giudice_2, giudice_3],
    description="Runs the 3 judges in parallel to evaluate the received response."
)

# 6. MERGER AGENT (SYNTHESIS)
merger_agent = LlmAgent(
    name="Merger_Analysis_Agent",
    model="gemini-2.5-flash",
    include_contents="none",
    instruction="""You are the Final Synthesis agent for a Cognitive Stress Test.
    
    The Main Agent provided an answer to a potentially very long or complex prompt, 
    and 3 different models evaluated it in parallel to assess its context retention.
    
    **Main Agent's Response to Evaluate:**
    {main_agent_response}

    **Judges' Scores (in JSON format):**
    - Gemini: {score_gemini}
    - Judge 2: {score_llama}
    - Qwen: {score_qwen}

    **Your task:**
    Write a brief Formatted Report in Markdown titled "Cognitive Stress Test Report".
    1. Mentally calculate the average of the 3 scores and display it prominently.
    2. Report a brief excerpt or the essence of the "Agent's Original Response".
    3. Analyze the comments from the 3 judges and draw a final conclusion: 
       did the agent withstand the stress of the conversation and the extracted constraints?
    """,
    description="Synthesizes the 3 scores into a report evaluating the agent's cognitive degradation under stress."
)

# 7. CUSTOM NODE: LANGSMITH FEEDBACK
@node(name="Send_To_LangSmith")
async def send_to_langsmith(ctx, node_input: str):
    ls_client = Client()
    
    latest_runs = list(ls_client.list_runs(project_name=PROJECT_NAME, execution_order=1, limit=1))
    run_id = latest_runs[0].id if latest_runs else None
    
    def parse_score(json_str, name):
        if not json_str: return None
        import re
        import json
        
        match = re.search(r'\{.*?\}', str(json_str), re.DOTALL)
        if not match: return None
        
        try:
            verdict = json.loads(match.group(0))
            # Checks for both "comment" and "commento" just in case
            comment = verdict.get("comment", verdict.get("commento", ""))
            return {"name": name, "score": float(verdict.get("score", 0)), "comment": comment}
        except Exception as e:
            return None

    state = getattr(ctx, 'state', {})
    
    # If we bypassed the judges, the scores might not be there
    if state.get('score_gemini') or state.get('score_llama') or state.get('score_qwen'):
        scores = [
            parse_score(state.get("score_gemini"), "Gemini_Judge"),
            parse_score(state.get("score_llama"), "GPT_OSS_Judge"),
            parse_score(state.get("score_qwen"), "Qwen_Judge")
        ]
        
        for val in scores:
            if val and run_id:
                try:
                    ls_client.create_feedback(
                        run_id,
                        key=f"evaluation_{val['name']}",
                        score=val['score'],
                        comment=val['comment']
                    )
                except Exception:
                    pass
                
    return node_input

# 8. ORCHESTRATION VIA WORKFLOW (ROOT AGENT)
pipeline = Workflow(
    name="StressTest_Parallel_Pipeline_v5",
    description="Pipeline v5: Clean UI Interface and Judge Bifurcation (Blind Test).",
    edges=[
        (START, extract_raw_memory),
        
        # Route for secret modifiers (Total bypass)
        Edge(from_node=extract_raw_memory, to_node=modifier_response, route="is_modifier"),
        (modifier_response, send_to_langsmith),
        
        # Route for normal messages (goes to judges)
        Edge(from_node=extract_raw_memory, to_node=memory_summarizer, route="is_normal"),
        (memory_summarizer, format_final_prompt),
        (format_final_prompt, agente_principale),
        (agente_principale, parallel_judges),
        (parallel_judges, merger_agent),
        (merger_agent, send_to_langsmith)
    ]
)

root_agent = pipeline