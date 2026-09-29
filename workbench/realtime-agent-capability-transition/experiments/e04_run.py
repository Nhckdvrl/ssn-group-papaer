"""E04 runner: tau2 text half-duplex with the user simulator's guidelines swapped to the VOICE-call
guidelines (disfluent, one utterance at a time, entities spelled out) while transcription stays perfect.
USER_STYLE=voice activates the swap; otherwise this is plain `tau2 run`."""
import os
import sys

import tau2.user.user_simulator as us

if os.environ.get("USER_STYLE") == "voice":
    us.get_global_user_sim_guidelines = lambda use_tools=False: us.get_global_user_sim_guidelines_voice(use_tools)

from tau2.cli import main

sys.exit(main())
