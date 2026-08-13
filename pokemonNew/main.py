from engine.app import App


def main():
    app = App(headless=False)
    app.boot()
    app.run()


if __name__ == "__main__":
    main()
