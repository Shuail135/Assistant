from tts_controller import reload_model


def run(request_input):
    reload_model()
    return "Reloaded Model."
