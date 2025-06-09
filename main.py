# main.py
#from command import handle_command
import os
import soundfile as sf
from TTS.config import load_config
from TTS.utils.synthesizer import Synthesizer


def take_command():
    input_command = input("Command: ")
    return input_command

def test():
    # Paths
    model_path = "best_model.pth"
    config_path = "config.json"
    output_path = "output.wav"

    # Initialize synthesizer
    synthesizer = Synthesizer(
        model_path,  # checkpoint
        config_path,  # config
        None,  # speaker_manager
        False  # use_cuda
    )

    # Generate waveform
    text = "This is your custom-trained GlowTTS model speaking!"
    wav = synthesizer.tts(text)

    # Save to file
    sf.write(output_path, wav, synthesizer.output_sample_rate)

    print("✅ Done! Saved to", output_path)


if __name__ == "__main__":
    test()
    #while True:
    #    command = take_command()
    #    handle_command(command)
