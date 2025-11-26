# sql_queries.py

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS ultra_marathon_results (
     year_of_event INT NOT NULL,
    event_dates DATE,
    event_name TEXT NOT NULL,
    event_distance_length FLOAT,
    event_number_of_finishers INT,
    athlete_performance TEXT,
    athlete_club TEXT,
    athlete_country TEXT,
    athlete_year_of_birth INT,
    athlete_gender TEXT,
    athlete_age_category TEXT,
    athlete_average_speed FLOAT,
    athlete_id TEXT NOT NULL,
    PRIMARY KEY (year_of_event, event_name, athlete_id)
);
"""

INSERT_SQL = """
INSERT INTO ultra_marathon_results (
    year_of_event,
    event_dates,
    event_name,
    event_distance_length,
    event_number_of_finishers,
    athlete_performance,
    athlete_club,
    athlete_country,
    athlete_year_of_birth,
    athlete_gender,
    athlete_age_category,
    athlete_average_speed,
    athlete_id
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
