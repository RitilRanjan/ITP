with open("app.py", "r") as f:
    code = f.read()

target = """                        hideClickInput();
                        setInterval(hideClickInput, 100);"""

repl = """                        hideClickInput();
                        setInterval(hideClickInput, 100);
                        
                        if (!window.parent.scrollEnforcerStarted) {
                            window.parent.scrollEnforcerStarted = true;
                            
                            // Catch all Enter presses
                            window.parent.addEventListener('keydown', function(e) {
                                if (e.key === 'Enter') {
                                    window.parent.itpShouldScroll = Date.now() + 1500;
                                }
                            }, true);
                            
                            function enforceScroll() {
                                if (window.parent.itpShouldScroll && Date.now() < window.parent.itpShouldScroll) {
                                    const mainArea = window.parent.document.querySelector('.main') || window.parent.document.querySelector('section[data-testid="stMain"]');
                                    if (mainArea) mainArea.scrollTop = mainArea.scrollHeight;
                                    const bc = window.parent.document.querySelector('.block-container');
                                    if (bc) bc.scrollIntoView({ behavior: 'auto', block: 'end' });
                                }
                                requestAnimationFrame(enforceScroll);
                            }
                            enforceScroll();
                        }"""

code = code.replace(target, repl)

with open("app.py", "w") as f:
    f.write(code)

print("Patched app.py scroll fix")
