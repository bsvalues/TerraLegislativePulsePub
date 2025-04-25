from app import app

if __name__ == "__main__":
    # Launch application using config settings (DEBUG, PORT, HOST)
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    app.run(host=host, port=port, debug=debug)