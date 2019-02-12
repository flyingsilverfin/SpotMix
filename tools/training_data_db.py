import sqlite3


class SimilarityBoundsException(Exception):
    pass

class TrackSimilarityDb():

    def __init__(self, db_file_path):
        self._conn = sqlite3.connect(db_file_path)
        self._create_tables()


    def _create_tables(self):
        """ Create a three column table - track id 1 (text), track id 2 (text), similarity (int between 0 and 9) """
        self._conn.execute("CREATE TABLE IF NOT EXISTS track_similarity (track_id_1 TEXT NOT NULL, track_id_2 TEXT NOT NULL, similarity INTEGER, PRIMARY KEY (track_id_1, track_id_2));")

    def add(self, track_id_1, track_id_2, similarity):
        if similarity < 0 or similarity > 9:
            raise SimilarityBoundsException("Similarity must be between 0 and 9 inclusive")
        self._conn.execute("INSERT INTO track_similarity VALUES (?, ?, ?)", [track_id_1, track_id_2, similarity])

    def get_all_similarities(self):
        c = self._conn.cursor()
        triples = []
        for id1, id2, sim in c.execute("SELECT * FROM track_similarity"):
            triples.append((id1, id2, sim))
        return triples








