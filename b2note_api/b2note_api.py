from eve import Eve
from settings import mongo_settings

app = Eve(settings=mongo_settings)

if __name__ == '__main__':
    app.run()
