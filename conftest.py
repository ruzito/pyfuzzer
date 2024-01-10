import os
from hypothesis import settings, Verbosity, Phase

cover_phases=[Phase.explicit, Phase.reuse, Phase.generate, Phase.target]
explain_phases=[Phase.explicit, Phase.reuse, Phase.shrink, Phase.explain]

settings.register_profile("cover", max_examples=1000, phases=cover_phases)
settings.register_profile("explain", phases=explain_phases)
settings.register_profile("debug", max_examples=10, phases=cover_phases, verbosity=Verbosity.verbose)

# settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))