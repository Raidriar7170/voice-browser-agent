# Keep Voice-to-Browser Agent separate from browser-use-vision

The Voice-to-Browser Agent is a separate application project that depends on `browser-use-vision` as its Visual Grounding Engine instead of copying its code or adding voice features to the plugin repository. The new project owns Spoken Command Execution, while `browser-use-vision` remains a reusable visual grounding component.
