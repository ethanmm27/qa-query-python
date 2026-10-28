# QA Bug Report Analyzer

A command-line tool that loads QA bug-report spreadsheets into MongoDB and answers common questions about them: which bugs block a release, what a given tester worked on, and who hasn't reported on a particular build.

Built with **Python**, **MongoDB (PyMongo)**, and **pandas**. Originally developed for a university course.

## Features

- Loads one or two Excel (`.xlsx`) bug-report files into MongoDB collections
- Merges both collections at query time with MongoDB's `$unionWith` aggregation stage
- Normalizes messy yes/no values (`Yes`, `y`, ` YES `, ...) so filters behave consistently
- Five report queries, each written to a text file with a total entry count
- Prompts for database credentials in the terminal (password hidden)
- Unit tests that run without a database, plus a GitHub Actions workflow

## Setup

```bash
git clone https://github.com/ethanmm27/qa-query-python.git
cd qa-query-python
pip install -r requirements.txt
```

You'll need a MongoDB database, such as a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster. The tool asks for the details when it starts:

```
Enter your MongoDB connection details.
Cluster host (e.g. mycluster.abc123.mongodb.net):
Username:
Password (hidden):
Database name [mydatabase]:
```

To skip the prompts (handy while developing), copy `.env.example` to `.env` and set `MONGODB_URI`.

## Options

| Option | Description |
|---|---|
| `--load` | Clear the collections and load the spreadsheets before querying |
| `--file-one`, `--file-two` | Paths to the two Excel files to load |
| `--blocker` | List all blocker bugs |
| `--blocker --repeatable` | List bugs that are both blocker and repeatable |
| `--user NAME` | List all work by a tester (case-insensitive exact match); also writes a CSV |
| `--builddate DATE` | List all reports for a build date (e.g. `2026-09-15`) |
| `--builddate DATE --reportedUsers` | List testers who did **not** submit a report for that build date |

### Expected spreadsheet columns

`Test Owner`, `Build #` (a date), `Blocker?`, `Repeatable?`. Any other columns are stored and included in the output.

## Project structure

```
├── qa_tool.py        # CLI and query logic
├── requirements.txt
├── requirements-dev.txt
```

## License

MIT, see [LICENSE](LICENSE).