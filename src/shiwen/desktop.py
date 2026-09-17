"""Keep GTK WebView callbacks from holding the process open after window close."""

import threading


def guard_evaluation(window, closing):
    # GTK may destroy its event loop before delivering evaluate_javascript's
    # callback. pywebview's non-daemon RPC thread would then wait forever.
    window.evaluate_js = _until_closed(window.evaluate_js, closing)
    window.run_js = _until_closed(window.run_js, closing)


def _until_closed(evaluate, closing):

    def evaluate_until_closed(*args, **kwargs):
        if closing.is_set():
            return None
        completed = threading.Event()
        result, errors = [], []

        def run():
            try:
                if not closing.is_set():
                    result.append(evaluate(*args, **kwargs))
            except Exception as error:
                errors.append(error)
            finally:
                completed.set()

        threading.Thread(target=run, name="shiwen-webview", daemon=True).start()
        while not completed.wait(0.05):
            if closing.is_set():
                return None
        if closing.is_set():
            return None
        if errors:
            raise errors[0]
        return result[0] if result else None

    return evaluate_until_closed
