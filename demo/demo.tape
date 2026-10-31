Output demo.gif
Set Shell bash
Set FontSize 15
Set Width 1500
Set Height 400
Set Padding 24
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms

Hide
Type `eval "$(bash /work/setup.sh)" && cd "$DEMO_DIR" && export PS1='$ ' && clear` Enter
Sleep 1s
Show

Type "# One policy file for a support agent. Is it valid?" Enter
Sleep 600ms
Type "opengpl validate support-agent.gpl" Enter
Sleep 2s
Type "# The app checks every prompt and reply, and logs each decision" Enter
Sleep 600ms
Type "python app.py" Enter
Sleep 3s
Type "clear" Enter
Type "# Turn the policy and its decision log into OSCAL evidence" Enter
Sleep 600ms
Type "opengpl audit support-agent.gpl --framework FedRAMP-Moderate --decisions decisions.jsonl" Enter
Sleep 3s
Type "# Each control says how much the SDK really does: enforced, heuristic or declared" Enter
Sleep 600ms
Type "controls support-agent-component-definition.json" Enter
Sleep 6s
