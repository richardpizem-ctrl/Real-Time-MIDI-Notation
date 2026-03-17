#!/usr/bin/env python3

from core.app_controller import AppController
from core.logger import Logger


def main():
    Logger.info("Starting Real-Time MIDI Notation app...")

    app = AppController()

    try:
        app.start()
        Logger.info("AppController started successfully.")

        # Hlavná slučka – kým aplikácia beží
        app.run()

    except KeyboardInterrupt:
        Logger.info("KeyboardInterrupt received. Shutting down...")
    except Exception as e:
        Logger.error(f"Unhandled exception in main: {e}")
    finally:
        try:
            app.stop()
            Logger.info("AppController stopped cleanly.")
        except Exception as e:
            Logger.error(f"Error while stopping AppController: {e}")


if __name__ == "__main__":
    main()
