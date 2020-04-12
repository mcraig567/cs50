SELECT name FROM people WHERE people.id IN (SELECT directors.person_id from directors WHERE directors.movie_id IN (SELECT ratings.movie_id from ratings WHERE rating >= "9.0"));
