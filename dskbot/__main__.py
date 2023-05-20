from . import init


def main():
    ''' Starts the bot. '''
    app = init()
    app.run_polling()


if __name__ == '__main__':
    main()
