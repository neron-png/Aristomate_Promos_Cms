# Aristomate Promotions CMS
[![FastAPI](https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](#)
[![SQLite](https://img.shields.io/badge/SQLite-%2307405e.svg?logo=sqlite&logoColor=white)](#)

Content management system server which handles [Aristomate](https://github.com/acmauth/StudentCompanion)'s promotions system, whilst not compromising the user's privacy.
The goal is to serve the user relevant content (ie. Showcasing other student teams, events and promotions), based on their university department, semester and study level, whilst not processing any of that information on our end.

This repository contains a server and db written in python's FastAPI. It allows the creation, management, and display of promotional offers through a simple to use SQLite database. 
It also proxies the content (images and click-throughs) to measure a promotion's performance.

User privacy is ensured in an open manner through the service providing the app with a list of all currently available promotions and their filters, allowing it to perform filtering on the client side. Thus subsequent requests to the server to serve
the corresponding promotion banner to the user are abstracted by the selectivity of the promotion's filter.

## Features
- Create and manage promotions
- Track a promotion's performance
- Simple and fast

## Installation
```bash
$ git clone https://github.com/neron-png/Aristomate_Promos_Cms.git
$ cd Aristomate_Promos_Cms
$ pipenv shell
$ pipenv install
  ```

## Running
```bash
$ fastapi run server.py
```
_Server running on 0.0.0.0:8000_
