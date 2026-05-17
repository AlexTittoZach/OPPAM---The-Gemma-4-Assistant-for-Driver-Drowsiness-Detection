                                                                      Project Overview
                                                                                    
OPPAM is an intelligent, low-latency driver monitoring system (DMS) built specifically for the Safety & Trust track.

By analyzing a live camera feed frame-by-frame, OPPAM monitors the driver’s biometric state. The moment it detects dangerous 
fatigue metrics—like prolonged eyelid closure or active yawning—it triggers a persistent audio alarm that repeats indefinitely.
The system silences itself instantly only when the driver snaps back to an alert, safe condition.

                                                               The Core Problem & Our Impact
                                                                              
Driver fatigue causes thousands of preventable highway accidents daily. While modern generative AI models possess the visual intelligence 
to detect drowsiness accurately under varying lighting and angles, running them on real-time video streams usually introduces massive processing lag.

OPPAM bridges this gap. It optimizes the interaction between edge streaming and cloud reasoning to deliver an active accident-prevention tool 
that responds in decent timeframes.

                                                        Technical Architecture & Engineering Choices
                                                        
To ensure the video display stays perfectly smooth while the AI runs in the background, the codebase relies on an Asynchronous Multi-Threaded Architecture:

* Prototype Camera Setup: The current prototype relies on a smartphone streaming live video to the laptop
  over the local network via the IP Webcam application.

* Asynchronous Dual-Lane I/O: The script splits operations into independent tasks.
  The Main Thread handles video capture and renders the user interface smoothly at 30 FPS without freezing.
  A separate, decoupled Background Scheduler manages cloud communications.

* In-Memory Frame Processing: To bypass disk storage speed limits, frames are never saved to the laptop's hard drive (cv2.imwrite was completely removed).
  Instead, raw video matrices are compressed directly inside system RAM arrays using cv2.imencode and sent over the network as a tiny, optimized binary payload.

* Deterministic Token Pruning: Large models like Gemma 4 are prone to generating conversational reasoning paragraphs.
  By setting temperature=0.0 and restricting max_output_tokens=30, we forced the model to behave like a strict binary sensor,
  cutting down processing times drastically.

* Fault-Tolerant Audio Engine: Local Python text-to-speech engines easily crash when flooded with rapid,
  overlapping loop commands. OPPAM isolates the alert system in its own thread, utilizing low-level hardware frequency tones (winsound.Beep)
  combined with structured speech loops to ensure non-stop alerts that stop immediately when safety conditions are met.


                                                         Real-World Challenges, Calibration, & Edge Failures
  
* Local Compute Failures: Initial testing used local Ollama instances. However, my i5 test machine lacked the required VRAM,
  causing immediate out-of-memory crashes with both Gemma 4 variants. To meet the deadline, I refactored the pipeline into an
  optimized cloud-assisted edge model.

* Night-Time Failure State: Standard camera sensors suffer from severe pixel noise in dark environments rendering the tracking
  ineffective at night. But production roadmap addresses this by upgrading to a dedicated infrared (IR) camera module with discrete IR LEDs.

* Stream Orientation Fix: The smartphone stream initially fed frames rotated 90 degrees sideways, breaking facial landmark tracking.
  I resolved this by embedding a localized cv2.ROTATE_90_CLOCKWISE step directly into the RAM buffer before processing.

* Output Stream Filtering: Gemma 4 naturally generated full paragraphs explaining its logic, causing conversational words to accidentally trigger
  false positives but rewrote the parser to split text blocks by line breaks and evaluate only the final line (lines[-1] == "TIRED").



                                                              Embedded Production Roadmap (Future Plan)
  
While the hackathon prototype utilizes a laptop as a development rig, OPPAM’s software footprint is intentionally engineered to run headless 
on low-power, localized edge hardware.

In production, the laptop is replaced by a small, hidden single-board computer such as a Raspberry Pi wired directly to a dedicated dashboard 
micro-camera. The code is designed to run silently as a background system service upon vehicle ignition, with its alert flags wired straight 
to the vehicle’s physical dashboard buzzer.


                                                                    Why Gemma 4?
                                                                    
* Alternative to Traditional CV Setups: Instead of relying on traditional computer vision frameworks that use rigid pixel-matching rules
  which frequently fail under changing angles or messy backgrounds—I wanted to test a different approach using deep visual intelligence.

* Decent Contextual Baseline: While a massive model like Gemma 4 is far from a perfect or optimized fit for a limited consumer hardware setup,
  its Mixture-of-Experts architecture yielded decent results in recognizing the contextual difference between a driver just talking versus a real yawn.






  Link to my kaggle writeup: 
