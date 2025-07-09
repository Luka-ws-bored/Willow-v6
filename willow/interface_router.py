import logging
from willow.intent_router import IntentRouter
from willow.plugin_loader import load_plugins
from willow.rag_router import RAGRouter
from willow.memory import MemoryManager

logger = logging.getLogger(__name__)

def launch_interface(config, memory):
    mode = config.get('interface_mode', 'cli').lower()
    if mode == 'cli':
        _launch_cli_mode(config, memory)
    else:
        _launch_gui_mode(config, memory)

def _launch_cli_mode(config, memory):
    logger.info("Launching CLI mode")
    # Load plugins and RAG
    plugins = load_plugins(config.get('config_path', 'config.yaml'))
    rag = RAGRouter(config)
    intent_router = IntentRouter(plugins, rag, memory)

    logger.info("Starting CLI interaction. Type 'exit' to quit.")
    while True:
        user_input = input('> ').strip()
        if user_input.lower() in ('exit', 'quit'):
            logger.info("Exiting CLI loop.")
            break

        # Route via IntentRouter
        result = intent_router.route(user_input)
        route, output = result['route'], result['output']
        # Display
        if route:
            print(f"[{','.join(route)}] {output}")
        else:
            print(output)

    logger.info("CLI mode closed.")

def _launch_gui_mode(config, memory):
    from willow.gui_interface import launch_gui_placeholder
    launch_gui_placeholder() 