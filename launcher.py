"""Keep frozen multiprocessing dispatch before importing the application."""

import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    from shiwen.app import main

    main()
