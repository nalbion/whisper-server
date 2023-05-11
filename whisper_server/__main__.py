from .app import main

try:
    main()
except KeyboardInterrupt:
    print("Whisper interrupted by keyboard")
    pass
