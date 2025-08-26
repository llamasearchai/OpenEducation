from __future__ import annotations

import asyncio
import json

from .tools import agent_tools


def conductor_agent(cfg_json: str, push: bool = False) -> str:
    """Conductor agent that orchestrates the full pipeline based on a config file."""
    try:
        cfg = json.loads(cfg_json)
        print("Conductor agent received config:", json.dumps(cfg, indent=2))

        # --- Dynamic Step Execution ---
        step_outputs = {}
        for i, step in enumerate(cfg.get("steps", [])):
            agent_name = step["agent"]
            prompt = step["prompt"]
            inputs = {key: step_outputs.get(val, val) for key, val in step["inputs"].items()}
            outputs = step["outputs"]
            
            print(f"--- Running Step {i+1}: {agent_name} ---")
            
            if agent_name not in agent_tools:
                raise ValueError(f"Unknown agent: {agent_name}")

            # Execute the tool associated with the agent
            tool_function = agent_tools[agent_name]
            result_path = tool_function(prompt=prompt, **inputs)
            
            # Store the output path for the next step
            output_key = list(outputs.keys())[0]
            step_outputs[output_key] = result_path
            print(f"   -> Step completed. Output at: {result_path}")

        # --- Final Deck Assembly ---
        final_cards_path = step_outputs.get("cards")
        if not final_cards_path:
            raise ValueError("The pipeline did not produce a final 'cards' output.")

        deck_props = cfg.get("deck_properties", {})
        apkg_path = agent_tools["assemble_deck"](
            cards_path=final_cards_path,
            deck_name=deck_props.get("name", "OpenEducation Deck"),
            styling=deck_props.get("styling")
        )
        print(f"✓ Assembled final deck: {apkg_path}")

        if push:
            result = agent_tools["push_to_anki"](apkg_path)
            print(f"✓ Pushed to Anki: {result}")
            return f"Pipeline completed successfully. {result}"

        return f"Pipeline completed successfully. Deck saved at: {apkg_path}"

    except Exception as e:
        # Re-raise the exception to get a full traceback
        raise e

async def run_pipeline(cfg_json: str, push: bool = False) -> str:
    """Run the full pipeline asynchronously."""
    try:
        # Use run_in_executor to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, conductor_agent, cfg_json, push)
        return result
    except Exception as e:
        return f"Pipeline failed: {type(e).__name__}: {str(e)}"
