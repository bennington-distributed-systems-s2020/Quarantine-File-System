#!/usr/bin/env python3
"""
    main.py - Provides a Flask API to server request and to manipulate metadata
    Date: 5/12/2020
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def example():
    return "Flask!"
