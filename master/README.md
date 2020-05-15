## Current Structure

- `main.py` - As the name suggests, it is the main script of GFS Master. Anything going in and out of Master happens here first and only then gets delegated further to other scripts.

- `metadata.py` - Provides a functionality to update metadata records using the `Metadata` class

- `filemap.py` - Provides a structure for mapping files to chunks (+ any other mapping) and some helper methods using the `Filemap` class

- `logs.json` - As the name suggests, this file is used for keeping logs persistent in a logical order

- `master.json` - This one might also be referred to as `checkpoint.json`. It keeps the most recent PERSISTENT state of master